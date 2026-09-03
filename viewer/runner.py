#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拉起 claude CLI 真实执行 /compose 编排，流式解析事件。

被 server.py 调用，负责：
  1. 用 subprocess 启动 `claude -p "<需求>" --output-format=stream-json --verbose`
  2. 逐行读 stdout，把 stream-json 事件原样透传（附加上下文注解）
  3. 进程结束/失败时发出终态事件

事件协议（每行一个 JSON，由 server.py 用 SSE 推给前端）：
  {"event":"lifecycle","phase":"starting","payload":{...}}   # 进程已启动
  {"event":"stream","payload":{...原始 stream-json 事件...}}   # 透传的 claude 事件
  {"event":"log","payload":{"kind":..., "text":..., ...}}      # 后端派生的可读日志
  {"event":"lifecycle","phase":"done","payload":{...}}        # 进程正常结束
  {"event":"lifecycle","phase":"error","payload":{...}}       # 进程异常
"""
import json
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

# 单次编排的总超时（秒）：防止 claude 进程卡死时 SSE 连接永久挂住
COMPOSE_TIMEOUT = 3600

ROOT = Path(__file__).resolve().parent.parent

# 角色 name -> 中文名 映射（复用 parse_case 的加载逻辑）
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from parse_case import _load_role_map
except Exception as e:  # noqa: BLE001
    _load_role_map = None
    _ROLE_MAP_LOAD_ERROR = e


def _build_prompt(requirement):
    """把用户需求包成指示 claude 按 compose.md 流程执行的 prompt。

    不内联 compose.md 内容，而是让 claude 自己 Read 它并按其执行——
    最贴合现有机制，未来 compose.md 改动自动生效。
    """
    return (
        "请严格按照 `.claude/commands/compose.md` 中定义的「多智能体编排」流程，"
        "作为统帅执行以下用户需求。先 Read 该文件理解完整流程（设计 → 执行 → 留痕），"
        "再按它真实调度角色完成编排，并把全程过程数据存档到 cases/。\n\n"
        f"用户需求：{requirement}\n\n"
        "注意：务必完整走完 compose.md 的第 5 节「运行留痕」，确保 cases/ 下有可查看的存档。"
    )


def run_compose(requirement, emit, cancel_event):
    """启动 claude 进程并流式解析。

    emit(event_dict): 回调，每解析到一条事件就调用一次。
    cancel_event: threading.Event，置位时终止进程。
    返回进程退出码。
    """
    cmd = [
        "claude",
        "-p",
        _build_prompt(requirement),
        "--output-format=stream-json",
        "--verbose",
    ]

    emit({"event": "lifecycle", "phase": "starting", "payload": {"cmd": cmd[0]}})

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
            # 独立进程组：取消时能 killpg 杀掉 claude 及其 Agent 子代理，
            # 避免 terminate 只杀外层、子代理变孤儿继续烧 token
            start_new_session=True,
        )
    except FileNotFoundError:
        emit({"event": "lifecycle", "phase": "error",
              "payload": {"error": "未找到 claude 命令，请确认已安装并在 PATH 中"}})
        return 127

    if _load_role_map is not None:
        role_map = _load_role_map()
    else:
        # 兜底不静默：日志里可见「中文名注解不可用」，便于发现 import 已悄悄坏掉
        role_map = {}
        emit({"event": "log",
              "payload": {"kind": "error",
                          "text": f"role_map 加载失败，角色中文名注解不可用：{_ROLE_MAP_LOAD_ERROR}"}})

    # 进程级超时：用一个独立 Event 表示「绝对超时」。计时线程到点只置位 + 杀进程组，
    # 不参与终态判定——判定「是否真的超时」放在 reader 收尾处，依据「进程是否被信号
    # 杀死（returncode < 0）且超时标记已置位」双重条件，避免「进程恰好正常跑完（rc==0）
    # 而计时器在微秒级窗口内也触发了」被误判成超时。
    timeout_event = threading.Event()

    def _reader():
        # 拨表：COMPOSE_TIMEOUT 秒一到，置位 + 强制终止进程组（杀 claude 及其子代理）
        def _on_timeout():
            timeout_event.set()
            _kill_process_group(proc)

        timer = threading.Timer(COMPOSE_TIMEOUT, _on_timeout)
        timer.daemon = True
        timer.start()
        try:
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    emit({"event": "log",
                          "payload": {"kind": "raw", "text": line}})
                    continue
                emit({"event": "stream", "payload": evt})
                # 派生可读日志（附带角色中文名等注解）
                _derive_log(evt, role_map, emit)
        finally:
            timer.cancel()

        # stdout 读完，等待进程结束
        rc = proc.wait()
        # 超时判定：必须是「计时器确实触发」且「进程确是被信号杀死的（returncode < 0）」。
        # 二者单独成立都不足以判超时——前者会误伤「恰好正常跑完、计时器在微秒级窗口内
        # 也触发了」的场景；后者会把被 cancel 杀死的进程也当成超时。
        timed_out = timeout_event.is_set() and rc < 0

        if cancel_event.is_set():
            emit({"event": "lifecycle", "phase": "done",
                  "payload": {"exit_code": rc, "cancelled": True}})
        elif timed_out:
            emit({"event": "lifecycle", "phase": "error",
                  "payload": {"exit_code": rc, "error": f"编排超时（>{COMPOSE_TIMEOUT}s），已强制终止"}})
        elif rc == 0:
            emit({"event": "lifecycle", "phase": "done",
                  "payload": {"exit_code": 0}})
        else:
            emit({"event": "lifecycle", "phase": "error",
                  "payload": {"exit_code": rc}})

    def _canceller():
        cancel_event.wait()
        _kill_process_group(proc)

    reader_t = threading.Thread(target=_reader, daemon=True)
    cancel_t = threading.Thread(target=_canceller, daemon=True)
    reader_t.start()
    cancel_t.start()
    reader_t.join()
    return proc.returncode


def _kill_process_group(proc):
    """杀掉 claude 及其 Agent 子代理所在的整个进程组，返回退出码。

    优先 SIGTERM 给一次优雅收尾机会，短暂等待后仍未退出则 SIGKILL；
    组内进程（含孤儿子代理）一并终止，不残留烧 token 的进程。
    """
    if proc.poll() is not None:
        return proc.returncode
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    return proc.returncode


def _derive_log(evt, role_map, emit):
    """从原始 stream-json 事件派生可读日志事件。"""
    etype = evt.get("type")
    subtype = evt.get("subtype", "")

    # 阶段标记
    if etype == "system" and subtype == "init":
        model = evt.get("model", "")
        emit({"event": "log",
              "payload": {"kind": "phase", "text": "会话已初始化", "model": model}})
        return

    if etype == "assistant":
        msg = evt.get("message", {})
        content = msg.get("content", [])
        for c in content:
            if not isinstance(c, dict):
                continue
            ct = c.get("type")
            if ct == "text" and c.get("text", "").strip():
                emit({"event": "log",
                      "payload": {"kind": "narrate", "text": c["text"]}})
            elif ct == "tool_use":
                name = c.get("name", "")
                if name == "Agent":
                    st = c.get("input", {}).get("subagent_type", "")
                    cn = role_map.get(st, {}).get("cn_name", "") if st else ""
                    emit({"event": "log",
                          "payload": {"kind": "dispatch",
                                      "role": st,
                                      "role_cn": cn}})
                elif name == "TaskOutput":
                    emit({"event": "log",
                          "payload": {"kind": "wait",
                                      "text": "等待子代理完成…"}})
                elif name:
                    emit({"event": "log",
                          "payload": {"kind": "tool",
                                      "text": f"工具调用：{name}"}})

    elif etype == "result":
        is_err = evt.get("is_error", False)
        cost = evt.get("total_cost_usd")
        turns = evt.get("num_turns")
        emit({"event": "log",
              "payload": {"kind": "result",
                          "ok": not is_err,
                          "cost": cost,
                          "turns": turns}})

    elif etype == "system" and subtype in ("error",):
        emit({"event": "log",
              "payload": {"kind": "error",
                          "text": json.dumps(evt, ensure_ascii=False)[:500]}})
