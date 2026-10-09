#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetalsTerminal Global Price Collector & Synchronizer
- Pure Global Benchmark Prices: [Ferrous -> Non-ferrous -> Precious/PGM]
- 12 Core Metals including Platinum(Pt), Palladium(Pd), Rhodium(Rh) for auto catalyst calculation
- Outputs to metalsterminal/data/prices.json
"""

import os
import sys
import json
from datetime import datetime

# Windows 콘솔 cp949 인코딩 방어
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TERMINAL_DATA_DIR = os.path.join(SCRIPT_DIR, "data")
OUTPUT_JSON_PATH = os.path.join(TERMINAL_DATA_DIR, "prices.json")

WORKSPACE_ROOT = os.path.dirname(SCRIPT_DIR)
THEPATHLAB_LATEST_PATH = os.path.join(WORKSPACE_ROOT, "thepathlab", "latest.json")

def sync_prices():
    os.makedirs(TERMINAL_DATA_DIR, exist_ok=True)

    if not os.path.exists(THEPATHLAB_LATEST_PATH):
        print(f"[경고] thepathlab/latest.json 파일을 찾을 수 없습니다: {THEPATHLAB_LATEST_PATH}")
        return False

    with open(THEPATHLAB_LATEST_PATH, "r", encoding="utf-8") as f:
        latest = json.load(f)

    latest_date = latest.get("latest_date", datetime.now().strftime("%Y-%m-%d"))
    usd_rate = latest.get("usd_rate", 1356.2)
    rate_source = latest.get("rate_source", "하나은행 고시환율")

    dt = datetime.strptime(latest_date, "%Y-%m-%d")
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][dt.weekday()]
    display_date = f"{dt.strftime('%Y.%m.%d')}({weekday_kr}) 09:00 고시"

    # 기존 metals를 딕셔너리로 맵핑
    existing_map = {m["key"]: m for m in latest.get("metals", [])}

    def get_metal_item(key, name_kr, name_en, source, unit, default_usd, default_krw, diff_krw=0, diff_pct=0.0):
        if key in existing_map:
            em = existing_map[key]
            krw = em.get("krw_price", default_krw)
            dk = em.get("diff_krw", diff_krw)
            dp = em.get("diff_pct", diff_pct)
        else:
            krw = default_krw
            dk = diff_krw
            dp = diff_pct

        trend = "same"
        if dk > 0: trend = "up"
        elif dk < 0: trend = "down"

        return {
            "key": key,
            "name_kr": name_kr,
            "name_en": name_en,
            "source": source,
            "unit": unit,
            "raw_usd": default_usd,
            "krw_price": krw,
            "diff_krw": dk,
            "diff_pct": dp,
            "trend": trend
        }

    # 1. 철 (Ferrous)
    ferrous_items = [
        get_metal_item("iron_scrap", "철스크랩", "Steel Scrap", "Global Index", "원/kg", "$372/t", 548, 0, 0.0)
    ]

    # 2. 비철 (Non-ferrous - LME)
    nonferrous_items = [
        get_metal_item("copper", "구리", "Copper", "LME", "원/kg", "$9,685/t", 19590, 120, 0.61),
        get_metal_item("aluminum", "알루미늄", "Aluminum", "LME", "원/kg", "$2,540/t", 4390, -35, -0.80),
        get_metal_item("zinc", "아연", "Zinc", "LME", "원/kg", "$3,085/t", 5231, 40, 0.77),
        get_metal_item("lead", "납", "Lead", "LME", "원/kg", "$2,050/t", 2594, -24, -0.92),
        get_metal_item("nickel", "니켈", "Nickel", "LME", "원/kg", "$16,250/t", 22030, 110, 0.50),
        get_metal_item("tin", "주석", "Tin", "LME", "원/kg", "$32,800/t", 72945, -519, -0.71)
    ]

    # 3. 귀금속 & PGM (백금, 팔라듐, 로듐, 금, 은)
    precious_items = [
        get_metal_item("platinum", "백금", "Platinum", "NYMEX", "원/g", "$995/oz", 43400, 350, 0.81),
        get_metal_item("palladium", "팔라듐", "Palladium", "NYMEX", "원/g", "$1,020/oz", 44500, -210, -0.47),
        get_metal_item("rhodium", "로듐", "Rhodium", "Johnson Matthey", "원/g", "$4,750/oz", 206000, 1500, 0.73),
        get_metal_item("gold", "금", "Gold", "COMEX", "원/g", "$2,650/oz", 115200, 600, 0.52),
        get_metal_item("silver", "은", "Silver", "COMEX", "원/g", "$31.8/oz", 1380, 12, 0.88)
    ]

    sections = [
        {"section_key": "ferrous", "section_name": "철 (Ferrous)", "badge_color": "fe", "items": ferrous_items},
        {"section_key": "nonferrous", "section_name": "비철 (Non-ferrous)", "badge_color": "cu", "items": nonferrous_items},
        {"section_key": "precious", "section_name": "귀금속 & PGM (폐촉매·도시광산)", "badge_color": "au", "items": precious_items}
    ]

    payload = {
        "updated_at": f"{latest_date} 09:00 KST",
        "display_date": display_date,
        "usd_rate": usd_rate,
        "rate_source": rate_source,
        "sections": sections
    }

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    total_count = len(ferrous_items) + len(nonferrous_items) + len(precious_items)
    print(f"✅ 12종 국제 시세 데이터 동기화 완료: {OUTPUT_JSON_PATH}")
    print(f"   - 일자: {display_date} | 환율: {usd_rate}원 | 철 1종 / 비철 6종 / 귀금속(Pt/Pd/Rh/Au/Ag) 5종 적재")
    return True

if __name__ == "__main__":
    sync_prices()
