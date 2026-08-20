"""高退研判取数脚本 —— 子订单 110206066421203954
说明：这是 S4 实际执行、并经真实 schema 探查纠偏后的最终版。
关键纠偏点（相对 S3 数据工程师初稿）：
  1. sub_order_no 是 BIGINT（不是 STRING），直接用数字查询
  2. 所有表必须带分区 pt（否则报 full scan 错误）
  3. 退仓富化表字段齐全（含 spu_id/sku_id/seller_ue/sku销），不缺字段
  4. 水位表 du_risk_trade 无 Select 权限（商品参考价取不到，是唯一数据缺口）
  5. 默认连接 project 是 du_risk_training_dev
"""
from odps import ODPS
import os
from dotenv import load_dotenv

load_dotenv('/Users/admin/.env', override=True)
o = ODPS(
    os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
    os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
    project=os.getenv('PROJECT'),
    endpoint=os.getenv('ENDPOINT'),
)

ORDER = 110206066421203954   # BIGINT
BUYER = '1382333954'
SELLER = '1755204970'


def run_sql(sql):
    hints = {'odps.instance.priority': 1, 'odps.sql.type.system.odps2': 'true'}
    with o.execute_sql(sql, hints=hints).open_reader() as r:
        cols = [c.name for c in r._schema.columns]
        rows = [list(row.values) for row in r]
    return cols, rows


# 1. 定位订单（rdm 源表，pt=下单日 20260617）
q1 = """
SELECT sub_order_no, buyer_user_id, seller_user_id, create_time, pay_time,
       spu_id, sku_id, sku_price, refund_type_desc, refund_status, aftersalestype, close_type_desc
FROM du_risk.rdm_risk_sub_order_detail_df
WHERE pt = '20260617' AND sub_order_no = 110206066421203954
"""

# 2. 退仓富化表（四维度核心字段，pt=最新 20260816）
q2 = """
SELECT sub_order_no, buyer_user_id, seller_user_id, spu_id, sku_id, create_time, pay_time, close_time,
       sku_price, total_price, refund_type_desc, refund_status, close_type_desc, aftersalestype, is_xiao_cang_seller,
       buyer_ue_90d, buyer_ue_365d, seller_ue_90d, seller_ue_365d,
       has_risk_action, event_list_properties, sku_pay_order_cnt_90d, sku_pay_order_cnt_30d, pt
FROM merchant_rank.refund_risk_dapan_sw_order_df
WHERE sub_order_no = '110206066421203954' AND pt >= '20260617'
ORDER BY pt DESC LIMIT 3
"""

# 3. 行为风险分V2（pt=下单日）
q3 = """
SELECT order_id, pred_prob, pt
FROM du_risk_training.order_click_action_risk_score_v2_di_v4_with_emb256
WHERE pt IN ('20260616','20260617','20260618','20260619','20260620')
  AND order_id = '110206066421203954'
"""

# 4. 高准团表（买卖家 continent_id，hr='00'）
q4 = """
SELECT user_id, continent_id, hr
FROM merchant_rank.user_nodes_myu_simple_py_hf
WHERE hr='00' AND user_id IN ('1382333954','1755204970')
"""

# 5. 黑灰产团伙表（买卖家 group_id/entity）
q5 = """
SELECT user_id, group_id, entity, pt
FROM merchant_rank.ekg_grey_trade_user_freq_res_7d_v3
WHERE pt >= '20260610' AND user_id IN ('1382333954','1755204970')
ORDER BY pt DESC, user_id
"""

# 6. 统一账号表 / 回扫明细表（买家众包识别结果）
q6 = """
SELECT buyer_id, zb_order_cnt, is_high_value, ue_365d, related_user_list
FROM merchant_rank.refund_risk_zhongbao_user_all_df
WHERE pt >= '20260617' AND buyer_id = '1382333954'
"""

if __name__ == '__main__':
    for name, q in [('rdm定位', q1), ('退仓富化', q2), ('行为分V2', q3),
                    ('高准团', q4), ('黑灰产', q5), ('统一账号', q6)]:
        print(f'===== {name} =====')
        try:
            cols, rows = run_sql(q)
            print('COLS:', cols)
            for row in rows:
                print(row)
        except Exception as e:
            print('FAIL:', repr(e)[:200])
        print()
