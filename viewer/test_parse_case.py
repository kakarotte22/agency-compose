#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""viewer/parse_case.py 纯函数的单元测试（标准库 unittest，零第三方依赖）。

运行：python3 viewer/test_parse_case.py
覆盖：执行日志表格解析、总览提取、产出文件匹配、轮次标记、
      missing_roles 归一化、显示名提取。
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parse_case  # noqa: E402


LOG_TABLE = """# 20-执行日志

| 步骤 | 角色 | 输入来源 | 产出文件 | 状态 | 循环 | 关键结论 |
|------|------|---------|---------|------|------|---------|
| S1 新闻情报 | intel-news-briefing | 无 | S1-新闻情报.md | success | - | 收集完成 |
| S2 趋势研判 | intel-trend-research | S1 | S2-趋势研判.md | partial | 2 轮 | 部分达成 |
| S3 复盘 | risk-strategy-analyst | S2 | S3-复盘.md | failure | - | 任务失败 |
"""


class ParseLogTableTest(unittest.TestCase):
    def test_full_table(self):
        rows = parse_case._parse_log_table(LOG_TABLE)
        self.assertEqual(len(rows), 3)
        r0, r1, r2 = rows
        self.assertEqual(r0["order"], "S1")
        self.assertEqual(r0["title"], "S1 新闻情报")
        self.assertEqual(r0["role"], "intel-news-briefing")
        self.assertEqual(r0["status"], "success")
        self.assertIsNone(r0["rounds"])
        self.assertEqual(r0["conclusion"], "收集完成")

        self.assertEqual(r1["order"], "S2")
        self.assertEqual(r1["status"], "partial")
        self.assertEqual(r1["rounds"], 2)

        self.assertEqual(r2["status"], "failure")

    def test_no_header_table_keeps_data_rows(self):
        text = "| S1 | role-a |\n| S2 | role-b |\n"
        rows = parse_case._parse_log_table(text)
        # 无表头时 order 列取第 0 列原文
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["order"], "S1")
        self.assertEqual(rows[1]["role"], "role-b")

    def test_empty(self):
        self.assertEqual(parse_case._parse_log_table(""), [])
        self.assertEqual(parse_case._parse_log_table("随便一段文字\n没有表格\n"), [])

    def test_unknown_status_dropped(self):
        text = "| 步骤 | 角色 | 状态 |\n|---|---|---|\n| S1 | r | doing |\n"
        rows = parse_case._parse_log_table(text)
        self.assertEqual(rows[0]["status"], "")


class ExtractOverviewTest(unittest.TestCase):
    def test_full(self):
        md = "- **目标**：写一份报告\n- **结论**：可行\n- **任务形状**：含回路由\n- **起止时间**：08-26 15:32 - 16:00\n"
        info, missing = parse_case._extract_overview(md)
        self.assertEqual(info["objective"], "写一份报告")
        self.assertEqual(info["verdict"], "可行")
        self.assertEqual(info["shape"], "含回路由")
        self.assertEqual(info["started"], "08-26 15:32 - 16:00")
        self.assertEqual(missing, [])

    def test_missing_fields_reported(self):
        info, missing = parse_case._extract_overview("- **目标**：x\n")
        self.assertEqual(info["objective"], "x")
        self.assertIn("verdict", missing)
        self.assertIn("shape", missing)

    def test_colon_variants(self):
        md = "- **目标**：中文冒号\n- **结论**： 英文冒号带空格\n"
        info, _ = parse_case._extract_overview(md)
        self.assertEqual(info["objective"], "中文冒号")
        self.assertEqual(info["verdict"], "英文冒号带空格")


class MatchOutputFilesTest(unittest.TestCase):
    def test_single_and_multi_round(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "S1-检索知识.md").write_text("A", encoding="utf-8")
            (d / "S2-分析-第1轮.md").write_text("B1", encoding="utf-8")
            (d / "S2-分析-第2轮.md").write_text("B2", encoding="utf-8")
            (d / "S3.txt").write_text("ignored", encoding="utf-8")
            (d / "随便.md").write_text("ignored", encoding="utf-8")

            files = parse_case._match_output_files(d)
            self.assertEqual(set(files.keys()), {1, 2})
            self.assertIn("S1-检索知识.md", files[1][0])
            self.assertEqual(files[1][1], "A")
            # 多轮：主稿在前，额外轮次以「轮次」标记分段追加
            self.assertIn("S2-分析-第1轮.md", files[2][0])
            self.assertTrue(files[2][1].startswith("B1"))
            self.assertIn("第2轮", files[2][1])
            self.assertTrue(files[2][1].endswith("B2"))

    def test_missing_dir(self):
        with tempfile.TemporaryDirectory() as td:
            files = parse_case._match_output_files(Path(td) / "不存在")
            self.assertEqual(files, {})


class RoundTagTest(unittest.TestCase):
    def test_chinese_round(self):
        self.assertEqual(parse_case._round_tag("S8-多空辩论-第2轮"), "第2轮")

    def test_english_round(self):
        self.assertEqual(parse_case._round_tag("S8-debate-round2"), "round2")

    def test_fallback(self):
        self.assertEqual(parse_case._round_tag("S1-检索知识"), "S1-检索知识")


class NormalizeMissingRolesTest(unittest.TestCase):
    def test_role_sought_normalized_to_role(self):
        roles = [
            {"role": "a", "type": "feasibility", "reason": "why"},
            {"role_sought": "b"},
            "not-a-dict",
        ]
        out = parse_case._normalize_missing_roles(roles)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0], {"role": "a", "type": "feasibility", "reason": "why"})
        self.assertEqual(out[1], {"role": "b", "type": "", "reason": ""})

    def test_none(self):
        self.assertEqual(parse_case._normalize_missing_roles(None), [])


class DisplayNameTest(unittest.TestCase):
    def test_strip_timestamp(self):
        self.assertEqual(
            parse_case._case_display_name("商业航天行业分析-20260826-153245"),
            "商业航天行业分析")

    def test_no_timestamp_fallback(self):
        self.assertEqual(parse_case._case_display_name("没有时间戳的名字"), "没有时间戳的名字")

    def test_name_containing_timestamp_pattern(self):
        # 任务名里带两组连字符，仍只剥掉末尾时间戳
        self.assertEqual(
            parse_case._case_display_name("A-B-20260826-153245"),
            "A-B")


if __name__ == "__main__":
    unittest.main(verbosity=2)