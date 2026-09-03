#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compose 任务流可视化 + Web 端编排本地服务。

启动：python3 viewer/server.py [端口]  （默认 8765）
访问：http://127.0.0.1:8765

端点：
  GET  /                       -> viewer/index.html（静态页面）
  GET  /api/cases              -> cases/ 下所有任务摘要列表
  GET  /api/case/<dir>         -> 单个 case 的完整结构化数据
  POST /api/compose/start      -> 发起一次编排（body: {"requirement": "..."}）
  GET  /api/compose/events?run_id=xxx  -> SSE 订阅某次编排的事件流
  POST /api/compose/stop       -> 取消某次编排（body: {"run_id": "..."}）
"""
import json
import queue
import signal
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parse_case  # noqa: E402
import runner  # noqa: E402

VIEWER_DIR = Path(__file__).resolve().parent
INDEX_PATH = VIEWER_DIR / "index.html"

# run_id -> {queue, cancel_event, status, thread}
RUNS = {}
RUNS_LOCK = threading.Lock()
# 事件队列上限，防止前端断开时内存暴涨
MAX_QUEUE = 5000
# 订阅者全部离开后，延迟取消的宽限期（秒）：
# 页面刷新会立刻带着 run_id 重连 SSE，给这段时间避免误杀正在跑的编排
SUBSCRIBER_GRACE = 8
# 已结束 run 的保留个数（每个最多 MAX_QUEUE 条事件），防止 RUNS 无限增长
KEEP_FINISHED_RUNS = 20


def _make_run():
    return {
        "queue": queue.Queue(maxsize=MAX_QUEUE),
        "cancel_event": threading.Event(),
        "status": "pending",
        "requirement": "",
        "thread": None,
        "exit_code": None,
        "log": [],  # 追加式完整日志，供刷新后回放（进程内存，重启即清）
        "next_seq": 1,      # 事件单调序号：前端回放日志后据此跳过已看过的事件
        "started_at": None, # run 启动时间（epoch 秒）：前端据此识别归属本 run 的 case 目录
        "subscribers": 0,   # 当前 SSE 订阅者数
        "cancel_timer": None,  # 「无人订阅则延迟取消」的计时器
    }


def _cancel_if_unsubscribed(run_id):
    """宽限期到点：仍无任何订阅者且仍在运行，才真正取消（杀 claude 进程组）。"""
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        if not run:
            return
        run["cancel_timer"] = None
        if run["subscribers"] <= 0 and run["status"] == "running":
            run["cancel_event"].set()


def _evict_finished_runs(keep_run_id):
    """把最早结束的已完成 run 淘汰出 RUNS（还有订阅者在看的除外），控制内存。"""
    with RUNS_LOCK:
        finished = [
            rid for rid, r in RUNS.items()
            if rid != keep_run_id and r["status"] in ("done", "error")
        ]
        excess = len(finished) - (KEEP_FINISHED_RUNS - 1)
        for rid in finished[:max(0, excess)]:
            if RUNS[rid]["subscribers"] <= 0:
                del RUNS[rid]


def _shutdown_runs():
    """退出前取消所有仍在运行的编排：置位取消信号并等 runner 杀掉 claude 进程组。

    claude 子进程用 start_new_session=True 放在独立进程组，server 退出不会自动
    带走它——不在这里显式取消，就会留下继续烧 token 的孤儿进程。
    """
    with RUNS_LOCK:
        runs = list(RUNS.values())
    for run in runs:
        if run["status"] == "running":
            run["cancel_event"].set()
    for run in runs:
        t = run.get("thread")
        if t is not None and t.is_alive():
            t.join(timeout=10)


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, body: bytes, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/":
            if INDEX_PATH.exists():
                self._send_html(INDEX_PATH.read_bytes())
            else:
                self._send_html(b"<h1>viewer/index.html not found</h1>", 404)
            return

        if path == "/api/cases":
            self._send_json(parse_case.list_cases())
            return

        if path.startswith("/api/case/"):
            case_dir = path[len("/api/case/"):].strip("/")
            if not case_dir:
                self._send_json({"error": "missing case dir"}, 400)
                return
            target = parse_case.CASES_DIR / case_dir
            if not target.exists() or not target.is_dir():
                self._send_json({"error": f"case not found: {case_dir}"}, 404)
                return
            try:
                role_map = parse_case._load_role_map()
                self._send_json(parse_case.parse_case(target, role_map))
            except Exception as e:  # noqa: BLE001 —— 解析失败也要返回可读错误
                self._send_json({"error": f"parse failed: {e}"}, 500)
            return

        if path == "/api/compose/logs":
            run_id = (parse_qs(parsed.query).get("run_id") or [""])[0]
            with RUNS_LOCK:
                run = RUNS.get(run_id)
            if not run:
                self._send_json({"error": "run not found"}, 404)
                return
            self._send_json({
                "run_id": run_id,
                "requirement": run["requirement"],
                "status": run["status"],
                "exit_code": run["exit_code"],
                "started_at": run["started_at"],
                "log": run["log"],
            })
            return

        if path == "/api/compose/events":
            self._handle_sse(parse_qs(parsed.query))
            return

        self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/api/compose/start":
            body = self._read_body()
            requirement = (body.get("requirement") or "").strip()
            if not requirement:
                self._send_json({"error": "需求不能为空"}, 400)
                return
            run_id = self._start_run(requirement)
            self._send_json({"run_id": run_id})
            return

        if path == "/api/compose/stop":
            body = self._read_body()
            run_id = body.get("run_id", "")
            with RUNS_LOCK:
                run = RUNS.get(run_id)
            if not run:
                self._send_json({"error": "run not found"}, 404)
                return
            run["cancel_event"].set()
            self._send_json({"ok": True})
            return

        self._send_json({"error": "not found"}, 404)

    def _start_run(self, requirement):
        run_id = uuid.uuid4().hex[:12]
        run = _make_run()
        run["requirement"] = requirement
        run["started_at"] = time.time()
        with RUNS_LOCK:
            RUNS[run_id] = run
        run["status"] = "running"

        def _emit(event):
            # 附单调序号：刷新恢复时前端回放了完整日志，重连 SSE 后据此跳过
            # 队列里残留的旧事件，避免同一条日志出现两遍
            event = dict(event)
            event["seq"] = run["next_seq"]
            run["next_seq"] += 1
            # 追加到可回放日志（刷新后恢复用）
            run["log"].append(event)
            # 回放日志与实时队列都裁剪到 MAX_QUEUE 上限，淘汰最老事件，
            # 保证两条通道读到的一致、且不会因长时间运行而无限占用内存。
            if len(run["log"]) > MAX_QUEUE:
                run["log"] = run["log"][-MAX_QUEUE:]
            try:
                run["queue"].put_nowait(event)
            except queue.Full:
                # 队列已满：淘汰最老一条再放，保证「实时流」与「回放日志」
                # 两者都保留最新事件、且都在 MAX_QUEUE 阈值内裁剪，行为一致。
                try:
                    run["queue"].get_nowait()
                except queue.Empty:
                    pass
                try:
                    run["queue"].put_nowait(event)
                except queue.Full:
                    pass

        def _work():
            rc = runner.run_compose(requirement, _emit, run["cancel_event"])
            run["exit_code"] = rc
            run["status"] = "done" if rc == 0 else "error"
            _evict_finished_runs(run_id)
            # 末尾补一个哨兵，SSE 据此关闭连接
            try:
                run["queue"].put_nowait({"event": "_eof_"})
            except queue.Full:
                pass

        run["thread"] = threading.Thread(target=_work, daemon=True)
        run["thread"].start()
        return run_id

    def _handle_sse(self, query):
        run_id = (query.get("run_id") or [""])[0]
        with RUNS_LOCK:
            run = RUNS.get(run_id)
            if run:
                run["subscribers"] += 1
                # 有人订阅了：撤销「无人订阅则延迟取消」的计时器
                timer = run.get("cancel_timer")
                if timer:
                    timer.cancel()
                    run["cancel_timer"] = None
        if not run:
            self._send_json({"error": "run not found"}, 404)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        try:
            while True:
                try:
                    event = run["queue"].get(timeout=2)
                except queue.Empty:
                    # 短心跳：既保持连接，又能在 2 秒内探测到客户端断开
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    continue
                if event.get("event") == "_eof_":
                    break
                data = json.dumps(event, ensure_ascii=False)
                self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass  # 前端断开
        finally:
            with RUNS_LOCK:
                run["subscribers"] -= 1
                if run["subscribers"] <= 0 and run["status"] == "running":
                    # 所有订阅者都断开：若是页面刷新，新连接会在宽限期内重连；
                    # 真没人看了，到点才取消（杀掉 claude 进程，避免孤儿进程烧 token）
                    timer = threading.Timer(
                        SUBSCRIBER_GRACE, _cancel_if_unsubscribed, args=(run_id,))
                    timer.daemon = True
                    run["cancel_timer"] = timer
                    timer.start()

    def log_message(self, fmt, *args):
        # 精简访问日志
        sys.stderr.write("[viewer] %s\n" % (fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    # SIGTERM 也走优雅退出（Ctrl+C 是 SIGINT；kill <pid> 默认 SIGTERM）。
    # 不能在 handler 里调 server.shutdown()——它与 serve_forever() 同在主线程会死锁，
    # 这里改为抛 KeyboardInterrupt，与 Ctrl+C 走完全相同的退出路径。
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    print(f"Compose 任务流可视化已启动：http://127.0.0.1:{port}")
    print("按 Ctrl+C 停止。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
    finally:
        # 退出前杀掉仍在运行的编排进程，避免遗留孤儿 claude 进程
        _shutdown_runs()


if __name__ == "__main__":
    main()