#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetalsTerminal Data Collector & Synchronizer
- Reads daily TE and exchange rate data from workspace (thepathlab/latest.json)
- Formats structured price & scrap data for MetalsTerminal mobile portal
- Outputs directly to metalsterminal/data/prices.json
"""

import os
import sys
import json
from datetime import datetime

# Windows 콘솔 cp949 출력 인코딩 방어
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 상대 경로 기준 베이스 디렉토리 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TERMINAL_DATA_DIR = os.path.join(SCRIPT_DIR, "data")
OUTPUT_JSON_PATH = os.path.join(TERMINAL_DATA_DIR, "prices.json")

# thepathlab의 latest.json 경로
WORKSPACE_ROOT = os.path.dirname(SCRIPT_DIR)
THEPATHLAB_LATEST_PATH = os.path.join(WORKSPACE_ROOT, "thepathlab", "latest.json")

# 금속별 현장 스크랩 대표 품목 및 매핑 메타데이터
SCRAP_META = {
    "copper": {
        "scrap_name": "A동 (밀베리 전선)",
        "badge": "cu",
        "category": "nonferrous",
        "unit": "원/kg",
        "raw_unit": "$/t",
        "calc_floor": lambda krw, raw: f"{int(round(krw * 0.63, -1)):,}"  # A동 통상 수율 62~65%
    },
    "aluminum": {
        "scrap_name": "창틀 샷시 (프로파일)",
        "badge": "al",
        "category": "nonferrous",
        "unit": "원/kg",
        "raw_unit": "$/t",
        "calc_floor": lambda krw, raw: f"{int(round(krw * 0.57, -1)):,}"
    },
    "iron_scrap": {
        "scrap_name": "생철 · 중량A",
        "badge": "fe",
        "category": "nonferrous",
        "unit": "원/kg",
        "raw_unit": "$/t",
        "calc_floor": lambda krw, raw: f"{int(round(krw * 0.73, -1)):,}"
    },
    "rhodium": {
        "scrap_name": "승용 삼원촉매 (로듐)",
        "badge": "rh",
        "category": "pgm",
        "unit": "원/g",
        "raw_unit": "$/oz",
        "calc_floor": lambda krw, raw: "7만 ~ 11만",
        "floor_unit": "원/개"
    },
    "zinc": {
        "scrap_name": "다이캐스팅 (자막)",
        "badge": "zn",
        "category": "nonferrous",
        "unit": "원/kg",
        "raw_unit": "$/t",
        "calc_floor": lambda krw, raw: f"{int(round(krw * 0.70, -1)):,}"
    },
    "lead": {
        "scrap_name": "폐배터리 (폐축전지)",
        "badge": "pb",
        "category": "nonferrous",
        "unit": "원/kg",
        "raw_unit": "$/t",
        "calc_floor": lambda krw, raw: f"{int(round(krw * 0.56, -1)):,}"
    },
    "tin": {
        "scrap_name": "솔더 크림·폐납·주석재",
        "badge": "sn",
        "category": "nonferrous",
        "unit": "원/kg",
        "raw_unit": "$/t",
        "calc_floor": lambda krw, raw: f"{int(round(krw * 0.75, -1)):,}"
    },
    "nickel": {
        "scrap_name": "스테인리스 (STS 304)",
        "badge": "ni",
        "category": "nonferrous",
        "unit": "원/kg",
        "raw_unit": "$/t",
        "calc_floor": lambda krw, raw: f"{int(round(krw * 0.084, -1)):,}" # STS304 니켈 함량 8%
    },
    "gold": {
        "scrap_name": "구형 PC 메인보드",
        "badge": "au",
        "category": "pgm",
        "unit": "원/g",
        "raw_unit": "$/oz",
        "calc_floor": lambda krw, raw: "14,000",
        "floor_unit": "원/kg"
    },
    "silver": {
        "scrap_name": "전자폐기물 은접점",
        "badge": "ag",
        "category": "pgm",
        "unit": "원/g",
        "raw_unit": "$/oz",
        "calc_floor": lambda krw, raw: "950",
        "floor_unit": "원/g"
    }
}

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

    # 요일 문자열 생성
    dt = datetime.strptime(latest_date, "%Y-%m-%d")
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][dt.weekday()]
    display_date = f"{dt.strftime('%Y.%m.%d')}({weekday_kr}) 09:00 고시"

    out_metals = []
    for item in latest.get("metals", []):
        key = item.get("key")
        name = item.get("name")
        krw_price = item.get("krw_price", 0)
        diff_krw = item.get("diff_krw", 0)
        diff_pct = item.get("diff_pct", 0.0)

        meta = SCRAP_META.get(key, {})
        scrap_name = meta.get("scrap_name", name)
        badge = meta.get("badge", "etc")
        category = meta.get("category", "nonferrous")
        unit = meta.get("unit", item.get("unit", "원/kg"))

        # 추정 단가 계산
        calc_fn = meta.get("calc_floor")
        floor_price = calc_fn(krw_price, 0) if calc_fn else f"{int(round(krw_price * 0.7, -1)):,}"
        floor_unit = meta.get("floor_unit", unit)

        trend = "same"
        if diff_krw > 0:
            trend = "up"
        elif diff_krw < 0:
            trend = "down"

        out_metals.append({
            "key": key,
            "name": name,
            "scrap_name": scrap_name,
            "badge": badge,
            "category": category,
            "unit": unit,
            "raw_usd": f"기준원가 {krw_price:,}원",
            "raw_krw": krw_price,
            "floor_price": floor_price,
            "floor_unit": floor_unit,
            "diff_krw": diff_krw,
            "diff_pct": diff_pct,
            "trend": trend
        })

    # 로듐(Rhodium) 데이터 보충 (thepathlab에 없는 경우 보강)
    has_rhodium = any(m["key"] == "rhodium" for m in out_metals)
    if not has_rhodium:
        out_metals.insert(3, {
            "key": "rhodium",
            "name": "로듐 (Rhodium)",
            "scrap_name": "승용 삼원촉매 (로듐)",
            "badge": "rh",
            "category": "pgm",
            "unit": "원/g",
            "raw_usd": "$4,750/oz",
            "raw_krw": 206000,
            "floor_price": "7만 ~ 11만",
            "floor_unit": "원/개",
            "diff_krw": 1500,
            "diff_pct": 0.73,
            "trend": "up"
        })

    payload = {
        "updated_at": f"{latest_date} 09:00 KST",
        "display_date": display_date,
        "usd_rate": usd_rate,
        "rate_source": rate_source,
        "metals": out_metals
    }

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ MetalsTerminal 시세 동기화 완료: {OUTPUT_JSON_PATH}")
    print(f"   - 일자: {display_date} | 환율: {usd_rate}원 | {len(out_metals)}개 품목 적재")
    return True

if __name__ == "__main__":
    sync_prices()
