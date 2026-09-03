#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 compose 命令落盘的 case 目录解析成结构化 JSON，供可视化页面消费。

输入：cases/<任务名-时间戳>/ 目录，以及 .claude/agent-manifest.json 的中文名映射。
输出：一个 dict（见 main() 的返回结构），JSON 序列化后给前端。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "cases"
MANIFEST_PATH = ROOT / ".claude" / "agent-manifest.json"


def _load_role_map():
    """name -> {cn_name, category}。查不到返回 None。"""
    if not MANIFEST_PATH.exists():
        return {}
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {
        item.get("name"): {
            "cn_name": item.get("cn_name", ""),
            "category": item.get("category", ""),
        }
        for item in data
        if isinstance(item, dict) and item.get("name")
    }


def _read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


HEADER_KEYWORDS = ("步骤", "角色", "输入来源", "产出文件", "状态", "循环", "关键结论", "报错")


def _is_header_cell(cell):
    """判断表格单元是否为表头列名（含「步骤/角色/状态…」等约定关键词）。"""
    return any(k in cell for k in HEADER_KEYWORDS)


def _parse_log_table(md_text):
    """解析 20-执行日志.md 的 markdown 表格，返回 list[dict]。

    每行 {order, title, role, status, rounds, conclusion}。
    表格列：| 步骤 | 角色 | 输入来源 | 产出文件 | 状态 | 循环 | 关键结论 |
    """
    rows = []
    header = None
    for line in md_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # 表头分隔行
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if header is None and any(_is_header_cell(c) for c in cells):
            header = cells  # 第一行表头（按关键词识别，无表头时不吞数据行）
            continue
        # 表头已设（或该行不是表头），后续都是数据行
        if len(cells) >= 2:
            rows.append(cells)
    # 表头列名定位（用于稳健取列）
    # 预期列：步骤 | 角色 | 输入来源 | 产出文件 | 状态 | 循环 | 关键结论/报错
    col_idx = {"order": 0, "role": 1, "status": None, "rounds": None, "conclusion": None}
    if header:
        for i, h in enumerate(header):
            hh = h or ""
            if "状态" in hh:
                col_idx["status"] = i
            elif "循环" in hh:
                col_idx["rounds"] = i
            elif "结论" in hh or "报错" in hh:
                col_idx["conclusion"] = i

    def _cell(cells, key):
        i = col_idx[key]
        if i is not None and i < len(cells):
            return cells[i]
        return ""

    parsed = []
    for cells in rows:
        # 步骤列取 S 序号（如 "S1 新闻情报" -> "S1"）
        order_cell = _cell(cells, "order")
        m = re.match(r"(S\d+)", order_cell or "")
        rec = {
            "order": m.group(1) if m else order_cell,
            "title": order_cell,
            "role": _cell(cells, "role"),
        }
        # 状态列
        status_cell = _cell(cells, "status")
        rec["status"] = status_cell if status_cell in ("success", "partial", "escalated", "failed", "failure") else ""
        # 循环列
        rounds = None
        rounds_cell = _cell(cells, "rounds")
        mm = re.search(r"(\d+)\s*轮", rounds_cell or "")
        if mm:
            rounds = int(mm.group(1))
        rec["rounds"] = rounds
        rec["conclusion"] = _cell(cells, "conclusion")
        parsed.append(rec)
    return parsed


def _extract_overview(md_text):
    """从 00-总览.md 提取目标/结论/任务形状/起止时间。稳健降级。

    返回 (info, missing)：info 为字段 dict；missing 为「未解析到」的字段名列表，
    供上层给出轻提示（而非静默取空），便于发现总览格式漂移。
    """
    info = {"objective": "", "verdict": "", "shape": "", "started": ""}
    for line in md_text.splitlines():
        line = line.strip()
        m = re.match(r"-\s*\*\*目标\*\*\s*[:：]\s*(.*)", line)
        if m:
            info["objective"] = m.group(1).strip()
        m = re.match(r"-\s*\*\*结论\*\*\s*[:：]\s*(.*)", line)
        if m:
            info["verdict"] = m.group(1).strip()
        m = re.match(r"-\s*\*\*任务形状\*\*\s*[:：]\s*(.*)", line)
        if m:
            info["shape"] = m.group(1).strip()
        m = re.match(r"-\s*\*\*起止时间\*\*\s*[:：]\s*(.*)", line)
        if m:
            info["started"] = m.group(1).strip()
    missing = [k for k, v in info.items() if not v]
    return info, missing


def _match_output_files(outputs_dir):
    """列出 30-步骤产出/ 下的 .md 文件，返回 {S序号(int): (文件名, 全文)}。

    同一步骤可能有多轮产出（循环），文件名如 S8-多空辩论-第2轮.md。
    此时取编号最小的一版作为「主产出」，正文里按「第 N 轮」分段追加，避免丢失轮次。
    """
    files = {}
    groups = {}
    if not outputs_dir.exists():
        return files
    for f in sorted(outputs_dir.iterdir()):
        if f.suffix.lower() != ".md":
            continue
        m = re.match(r"^S(\d+)(?:[-_]|$)", f.stem)
        if not m:
            continue
        seq = int(m.group(1))
        groups.setdefault(seq, []).append(f)

    for seq, fs in groups.items():
        fs.sort(key=lambda f: f.name)  # 稳定排序，主稿在前
        main = fs[0]
        text = _read_text(main)
        # 追加多轮产出：每个额外文件用「轮次」标记分段
        for extra in fs[1:]:
            round_tag = _round_tag(extra.stem)
            text += f"\n\n---\n\n**{round_tag}**：{extra.name}\n\n" + _read_text(extra)
        files[seq] = (main.name, text)
    return files


def _round_tag(stem):
    """从文件名提取「第 N 轮」标记，如 'S8-多空辩论-第2轮' -> '第2轮'，找不到则返回原始名。"""
    m = re.search(r"(第\s*\d+\s*轮|round\s*\d+)", stem, re.IGNORECASE)
    return m.group(1) if m else stem


def _normalize_missing_roles(roles):
    """把 missing_roles 数组归一化为 schema 约定字段：role / type / reason。

    架构师历史产出曾出现过两种写「缺失角色名」的字段名——`role`（schema 约定，
    主流）与 `role_sought`（个别 case 的离群写法）。二者语义相同，这里统统归一
    到 `role`，保证下游（含前端、check_contract）拿到稳定结构，不因历史离群数据
    而脱节。
    """
    normalized = []
    for item in roles or []:
        if not isinstance(item, dict):
            continue
        role = item.get("role") or item.get("role_sought") or ""
        normalized.append({
            "role": role,
            "type": item.get("type", ""),
            "reason": item.get("reason", ""),
        })
    return normalized


def parse_case(case_dir: Path, role_map: dict):
    """解析单个 case 目录。返回完整结构化 dict。"""
    dag_file = case_dir / "10-DAG方案.json"
    log_file = case_dir / "20-执行日志.md"
    overview_file = case_dir / "00-总览.md"
    deviations_file = case_dir / "90-遗留与偏差.md"
    outputs_dir = case_dir / "30-步骤产出"
    final_file = case_dir / "50-最终报告.md"

    # 1. DAG 方案（唯一真源）
    dag = {}
    if dag_file.exists():
        try:
            dag = json.loads(dag_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            dag = {}

    raw_steps = dag.get("steps", [])
    topology = dag.get("topology", "")

    # 2. 执行日志
    log_rows = _parse_log_table(_read_text(log_file))
    log_by_order = {r["order"]: r for r in log_rows if r["order"]}
    log_by_role = {r["role"]: r for r in log_rows if r["role"]}

    # 3. 步骤产出文件
    output_files = _match_output_files(outputs_dir)

    # 4. 总览 & 偏差
    overview, overview_missing = _extract_overview(_read_text(overview_file))
    deviations = _read_text(deviations_file)
    final_report = _read_text(final_file)

    # 5. 组装步骤
    steps = []
    for idx, s in enumerate(raw_steps, start=1):
        role = s.get("role", "")
        rmeta = role_map.get(role, {})
        loop = s.get("loop") or {}
        step = {
            "id": s.get("id", f"step-{idx}"),
            "order": f"S{idx}",
            "role": role,
            "role_cn": rmeta.get("cn_name", ""),
            "category": rmeta.get("category", ""),
            "input": s.get("input", ""),
            "output_contract": s.get("output", ""),
            "output_md": "",
            "depends_on": s.get("depends_on", []),
            "fallback": s.get("fallback", ""),
            "loop": {
                "enabled": bool(loop.get("enabled", False)),
                "mode": loop.get("mode", "self"),
                "group": loop.get("group", ""),
                "max_rounds": loop.get("max_rounds", None),
                "converge_when": loop.get("converge_when", ""),
                "partners": loop.get("partners", []) or [],
                "affected_downstream": loop.get("affected_downstream", []) or [],
                "fix": loop.get("fix", ""),
            },
            "status": None,
            "rounds": None,
            "conclusion": "",
        }
        # 回填执行日志（优先 S 序号，其次 role 名兜底）
        logrec = log_by_order.get(step["order"]) or log_by_role.get(role)
        if logrec:
            step["status"] = logrec.get("status") or None
            step["rounds"] = logrec.get("rounds")
            step["conclusion"] = logrec.get("conclusion", "")
        # 回填产出全文
        if idx in output_files:
            step["output_md"] = output_files[idx][1]
        steps.append(step)

    # 6. 边（分两类输出）：
    #    - edges：前向依赖边，沿用 [from, to] 旧格式（前端布局/高亮逻辑不变）
    #    - loop_edges：回路边（回退边 backedge / 辩论边 debate），格式 {from, to, kind}
    edges = []
    loop_edges = []
    for s in steps:
        for dep in s["depends_on"]:
            edges.append([dep, s["id"]])
    for s in steps:
        lp = s["loop"] or {}
        if not lp.get("enabled"):
            continue
        mode = lp.get("mode", "self")
        partners = lp.get("partners", []) or []
        group = lp.get("group", "") or ""
        if mode == "backedge":
            # 回退边：本步骤 -> 被回退的上游目标步骤
            for target in partners:
                loop_edges.append({"from": s["id"], "to": target, "kind": "backedge", "group": group})
        elif mode == "debate":
            # 辩论边：本步骤与每个对立步骤互连（攻防边）
            for p in partners:
                if p == s["id"]:
                    continue
                loop_edges.append({"from": s["id"], "to": p, "kind": "debate", "group": group})

    # 7. 概览 meta
    total = len(steps)
    statuses = [s["status"] for s in steps if s["status"]]
    success = statuses.count("success")
    failed = sum(1 for st in statuses if st in ("failed", "failure", "escalated"))
    loop_count = sum(1 for s in steps if s["loop"]["enabled"])

    return {
        "case": {
            "dir": case_dir.name,
            "name": _case_display_name(case_dir.name),
            "objective": overview["objective"],
            "verdict": overview["verdict"],
            "shape": overview["shape"] or topology,
            "started": overview["started"],
            "overview_missing": overview_missing,
            "meta": {
                "total_steps": total,
                "success": success,
                "failed": failed,
                "loop_count": loop_count,
            },
        },
        "steps": steps,
        "edges": edges,
        "loop_edges": loop_edges,
        "missing_roles": _normalize_missing_roles(dag.get("missing_roles", [])),
        "merge": dag.get("merge", ""),
        "final_role": dag.get("final_role", ""),
        "deviations": deviations,
        "final_report": final_report,
    }


def _case_display_name(dirname):
    """从目录名 '<任务名>-YYYYMMDD-HHMMSS' 提取任务名；退化返回原目录名。"""
    m = re.match(r"^(.*?)-\d{8}-\d{6}$", dirname)
    return m.group(1) if m else dirname


# ---------------------------------------------------------------------------
# 前后端字段契约自测
#
# index.html 消费 parse_case() 产出的字段清单。这里是「单一真源」：一旦
# parse_case 的输出字段（或前端读取字段）要变，先改这里，再跑 --check，
# 能立刻发现 parser 与前端脱节。
# ---------------------------------------------------------------------------

# 顶层对象必须具备的字段
TOP_KEYS = {
    "case", "steps", "edges", "loop_edges", "missing_roles",
    "merge", "final_role", "deviations", "final_report",
}
# case 对象必须具备的字段
CASE_KEYS = {"dir", "name", "objective", "verdict", "shape", "started", "overview_missing", "meta"}
META_KEYS = {"total_steps", "success", "failed", "loop_count"}
# 每个 step 对象必须具备的字段
STEP_KEYS = {
    "id", "order", "role", "role_cn", "category", "input", "output_contract",
    "output_md", "depends_on", "fallback", "loop", "status", "rounds", "conclusion",
}
LOOP_KEYS = {"enabled", "mode", "group", "max_rounds", "converge_when", "partners", "affected_downstream", "fix"}
# missing_roles 数组中每一项必须具备的字段
MISSING_ROLE_KEYS = {"role", "type", "reason"}


def check_contract():
    """校验 parse_case 输出与 index.html 读取的字段契约是否一致。

    返回进程退出码：0=一致（或无可测 case，跳过），1=不一致。
    """
    role_map = _load_role_map()
    dirs = [d for d in CASES_DIR.iterdir() if d.is_dir()] if CASES_DIR.exists() else []
    if not dirs:
        print("⚠️  cases/ 下暂无 case，跳过契约自测（无可测对象）。")
        return 0

    problems = []
    tested = 0
    total_steps = 0
    for target in sorted(dirs):
        try:
            data = parse_case(target, role_map)
        except Exception as e:  # noqa: BLE001 —— 单个 case 解析崩溃不影响其余 case 的检查
            problems.append(f"[{target.name}] 解析抛异常: {e}")
            continue
        tested += 1
        total_steps += len(data.get("steps", []))
        problems.extend(_check_case_contract(target.name, data))

    if problems:
        print(f"❌ 字段契约不一致（已测 {tested} 个 case，共 {total_steps} 步）：")
        for p in problems:
            print(f"  - {p}")
        print("\n说明：请同步 parse_case.py 与 viewer/index.html 的字段定义。")
        return 1

    print(f"✅ 字段契约一致（已测 {tested} 个 case，共 {total_steps} 步）。")
    return 0


def _check_case_contract(case_name, data):
    """校验单个 case 的 parse_case 输出与 index.html 读取的字段契约是否一致。"""
    problems = []

    # 顶层键
    for k in TOP_KEYS:
        if k not in data:
            problems.append(f"[{case_name}] 顶层缺少字段: {k}")

    # case 键
    case = data.get("case", {})
    for k in CASE_KEYS:
        if k not in case:
            problems.append(f"[{case_name}] case 缺少字段: {k}")
    meta = case.get("meta", {})
    for k in META_KEYS:
        if k not in meta:
            problems.append(f"[{case_name}] case.meta 缺少字段: {k}")

    # step 键
    for i, s in enumerate(data.get("steps", []), 1):
        for k in STEP_KEYS:
            if k not in s:
                problems.append(f"[{case_name}] steps[{i}] 缺少字段: {k}")
        lp = s.get("loop") or {}
        for k in LOOP_KEYS:
            if k not in lp:
                problems.append(f"[{case_name}] steps[{i}].loop 缺少字段: {k}")

    # missing_roles 项键
    for i, mr in enumerate(data.get("missing_roles", []), 1):
        for k in MISSING_ROLE_KEYS:
            if k not in mr:
                problems.append(f"[{case_name}] missing_roles[{i}] 缺少字段: {k}")

    return problems


def list_cases():
    """扫描 cases/ 返回任务列表摘要。"""
    result = []
    if not CASES_DIR.exists():
        return result
    for d in sorted(CASES_DIR.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        dag_file = d / "10-DAG方案.json"
        try:
            dag = json.loads(dag_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            dag = {}
        log_text = _read_text(d / "20-执行日志.md")
        # 计数
        total = len(dag.get("steps", []))
        log_rows = _parse_log_table(log_text)
        success_row = any(r["status"] == "success" for r in log_rows)
        # 时间戳从目录名提取
        m = re.search(r"-(\d{8}-\d{6})$", d.name)
        ts = m.group(1) if m else ""
        result.append({
            "dir": d.name,
            "name": _case_display_name(d.name),
            "ts": ts,
            "total_steps": total,
            "topology": dag.get("topology", ""),
            "has_result": success_row,
        })
    return result


def main(argv):
    """CLI 入口，便于单独调试。python3 parse_case.py <dir> [--list]"""
    role_map = _load_role_map()
    if argv and argv[0] == "--list":
        print(json.dumps(list_cases(), ensure_ascii=False, indent=2))
    elif argv and argv[0] in ("--schema", "--check"):
        rc = check_contract()
        sys.exit(rc)
    elif argv:
        target = CASES_DIR / argv[0]
        print(json.dumps(parse_case(target, role_map), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(list_cases(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])