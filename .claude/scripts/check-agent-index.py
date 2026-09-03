#!/usr/bin/env python3
"""自检 agent-index.md 与 agent-manifest.json 的角色名是否一致。

双向检查：
1. index 里出现、但 manifest 里没有的 name（索引多记了 / 角色已删）
2. manifest 里有、但 index 没收录的 name（索引漏了 / 新增角色未同步）

退出码：
  0  = 完全一致
  1  = 存在不一致（供主程序据此提示用户同步，而不是静默放行）

注意：manifest 的 strategy 目录下的项（QUICKSTART / phase-* / scenario-* 等）
是内部运营文档，不是角色。它们在 index 末尾的「附：非角色项」里单列，
不参与「索引 vs manifest」的漏检比对（但会单独核对它们是否仍存在于 manifest）。
非角色项以 manifest 里 `role_path` 前缀为 `strategy/` 自动识别，无需硬编码清单。
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent  # .claude/
MANIFEST = REPO / "agent-manifest.json"
INDEX = REPO / "agent-index.md"

# manifest 中明确不是角色的 name：以 `role_path` 前缀为 `strategy/` 的项为准，
# 从数据源动态识别（而非硬编码清单），避免 strategy 目录增删运营文档时漏改。
# 这些项在 index 末尾的「附：非角色项」里单列，不参与「索引 vs manifest」的漏检比对
# （但会单独核对它们是否仍存在于 manifest）。

# 索引里「预期合法」出现在 manifest 之外的名字——不报错：
#   general-purpose 是 Claude Code 内置通用 agent（harness 自带，项目 manifest 里没有）。
# 注意：第 23 组的「留空占位」只用描述、不再写死角色名，因此这里无需为占位角色单列白名单；
#       一旦某个领域后来补进了真实角色，它就会出现在 manifest，自检自然对得上，无需改这里。
EXPECTED_OUTSIDE_MANIFEST = {
    "general-purpose",
}


def load_manifest():
    """读取 manifest，返回原始数据 list（含 name 与 role_path，供识别非角色项）。"""
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def load_manifest_names(data):
    return {r["name"] for r in data}


def load_non_role_names(data):
    """从 manifest 数据里识别非角色项：role_path 落在 strategy/ 目录下的项。"""
    return {
        r["name"]
        for r in data
        if isinstance(r, dict)
        and str(r.get("role_path", "")).startswith("strategy/")
    }


def load_index_names():
    """从 index.md 提取「角色条目」里的 name，作为「索引里出现的名字」。

    只扫描以 `- ` 开头的 bullet 行，取该行内**所有**反引号包裹的 token（一条 bullet
    可能并列多个角色，如 `` `a` / `b` ``）。这样能彻底排除正文/注释里被反引号包住
    的普通词（如 `depends_on`、`max_rounds`）被误当成角色名——因为它们几乎不会出现在
    bullet 行的反引号里；而角色 name 约定写在列表条目开头的反引号中，可被稳定捕获。
    """
    text = INDEX.read_text(encoding="utf-8")
    head = text.split("附：非角色项", 1)[0]
    names = set()
    for line in head.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            # 只认 bullet 条目；标题、说明、占位描述一律不扫
            continue
        names.update(re.findall(r"`([a-zA-Z0-9_-]+)`", stripped))
    return names


def main():
    data = load_manifest()
    manifest_names = load_manifest_names(data)
    non_role_names = load_non_role_names(data)
    index_names = load_index_names()

    real_manifest = manifest_names - non_role_names  # 真正的角色

    # 索引里出现、但 manifest 里不存在的（剔除预期例外后才是真问题）
    in_index_not_manifest = sorted(
        index_names - manifest_names - EXPECTED_OUTSIDE_MANIFEST
    )

    # manifest 有、索引没收录的（漏了）
    in_manifest_not_index = sorted(real_manifest - index_names)

    problems = []
    if in_index_not_manifest:
        problems.append(
            "索引里出现、但 manifest 里不存在的 name（可能是误加反引号的普通词，或角色已删）：\n  "
            + ", ".join(in_index_not_manifest)
        )
    if in_manifest_not_index:
        problems.append(
            "manifest 里有、但索引未收录（新增角色未同步 / 索引漏了）：\n  "
            + ", ".join(in_manifest_not_index)
        )

    print(f"manifest 真实角色数: {len(real_manifest)}")
    print(f"索引收录角色数:   {len(index_names)}")
    print(f"非角色项（已排除）: {len(non_role_names)}")
    print()

    if problems:
        print("⚠️  索引与 manifest 不一致：")
        for p in problems:
            print(p)
        return 1
    else:
        print("✅ 索引与 manifest 完全一致，可放心使用。")
        return 0


if __name__ == "__main__":
    sys.exit(main())
