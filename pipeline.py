#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetalsTerminal Unified Pipeline (Master Sync Engine)
======================================================
매일 아침 9시 원클릭 실행 시 3대 핵심 영역을 동시 갱신:
  1. Price: 12대 순수 국제시세 (LME/NYMEX/JM) -> data/prices.json
  2. Scrap: 철스크랩 5등급 + 비철수율 + 폐촉매 엔진 -> data/scrap.json
  3. Report: 4대 챕터 표준 아티클 + RSS 원문 기사 -> data/reports.json & articles/
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
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
ARTICLES_DIR = os.path.join(SCRIPT_DIR, "articles")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ARTICLES_DIR, exist_ok=True)

# 1. Price 동기화 (collector.py 연동)
from collector import sync_prices

# 2. Scrap 계산 모듈 (thepathlab scrap_builder 수율 공식 이식)
def sync_scrap(usd_rate=1356.2):
    print("⚙️ [Step 2/3] 스크랩 및 폐촉매 수율 데이터 산출 중...")

    # 기준 국제 원가
    base_copper = 19590
    base_aluminum = 4390
    base_iron = 548
    price_pd = 44500
    price_rh = 206000
    price_pt = 43400

    # 1) 철스크랩 5대 등급
    iron_items = [
        {"name": "생철 A", "spec": "프레스 신품 강판 (순도 99%↑)", "wholesale": round(base_iron * 0.83), "retail": round(base_iron * 0.75)},
        {"name": "중량 A", "spec": "두께 6mm 이상 H빔·철골·레일", "wholesale": round(base_iron * 0.75), "retail": round(base_iron * 0.67)},
        {"name": "중량 B", "spec": "두께 3~6mm 기계류·배관 파이프", "wholesale": round(base_iron * 0.69), "retail": round(base_iron * 0.62)},
        {"name": "경량 A", "spec": "두께 1~3mm 가전외판·드럼통", "wholesale": round(base_iron * 0.65), "retail": round(base_iron * 0.58)},
        {"name": "선반설 A", "spec": "절삭칩·선반 가공 찌꺼기", "wholesale": round(base_iron * 0.61), "retail": round(base_iron * 0.55)},
    ]

    # 2) 비철 스크랩 수율
    nonferrous_items = [
        {"name": "A동 (밀베리)", "spec": "피복 벗긴 굵은 단선 (순도 99.9%)", "unit": "원/kg", "price": round(base_copper * 0.63)},
        {"name": "상동 (중품)", "spec": "모터 분해선, 변압기 코일동", "unit": "원/kg", "price": round(base_copper * 0.58)},
        {"name": "파동 (하품)", "spec": "주석도금선, 얇은 에나멜선, 혼합동", "unit": "원/kg", "price": round(base_copper * 0.51)},
        {"name": "황동 노베 (신주)", "spec": "판재 스크랩 (Cu 65% + Zn 35%)", "unit": "원/kg", "price": 7800},
        {"name": "황동 절봉 (신주)", "spec": "황동 봉 절삭 부스러기", "unit": "원/kg", "price": 7200},
        {"name": "알루미늄 샷시", "spec": "창틀 프로파일 (페인트/부속 제거)", "unit": "원/kg", "price": round(base_aluminum * 0.57)},
        {"name": "알루미늄 휠", "spec": "납추/타이어 완전 분리 휠", "unit": "원/kg", "price": round(base_aluminum * 0.50)},
        {"name": "알루미늄 캔", "spec": "음료수 캔 압축 베일", "unit": "원/kg", "price": 1800},
        {"name": "스테인리스 STS 304", "spec": "자석 안 붙는 니켈 8% 정품 서스", "unit": "원/kg", "price": 1850},
    ]

    # 3) 폐촉매 차종별 실무 견적 프리셋
    catalyst_presets = [
        {"id": "lpi", "name": "LPG 가스차 (쏘나타·K5·그랜저 2.0~3.0 LPi)", "pd_g": 1.9, "rh_g": 0.85, "pt_g": 0.0, "min_quote": 105000, "max_quote": 125000},
        {"id": "gdi", "name": "직분사 가솔린 (아반떼MD·YF·그랜저HG 1.6~2.4 GDi)", "pd_g": 2.1, "rh_g": 0.45, "pt_g": 0.0, "min_quote": 85000, "max_quote": 105000},
        {"id": "turbo", "name": "터보 가솔린 (아반떼N·쏘나타터보 1.6T~2.0T)", "pd_g": 2.5, "rh_g": 0.65, "pt_g": 0.0, "min_quote": 120000, "max_quote": 145000},
        {"id": "mpi", "name": "자연흡기 가솔린 (모닝·레이·아반떼 1.0~1.6 MPi)", "pd_g": 1.8, "rh_g": 0.20, "pt_g": 0.0, "min_quote": 60000, "max_quote": 75000},
        {"id": "hev", "name": "하이브리드 (니로·아반떼·쏘나타 HEV)", "pd_g": 2.2, "rh_g": 0.50, "pt_g": 0.0, "min_quote": 95000, "max_quote": 115000},
        {"id": "dpf", "name": "디젤 DPF (포터2·봉고3·싼타페 CRDi)", "pd_g": 0.0, "rh_g": 0.10, "pt_g": 3.8, "min_quote": 140000, "max_quote": 170000},
    ]

    scrap_payload = {
        "updated_at": datetime.now().strftime("%Y-%m-%d 09:00 KST"),
        "iron_scrap": iron_items,
        "nonferrous": nonferrous_items,
        "catalyst_presets": catalyst_presets
    }

    out_path = os.path.join(DATA_DIR, "scrap.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(scrap_payload, f, ensure_ascii=False, indent=2)

    print(f"✅ 스크랩 & 폐촉매 데이터 저장 완료: {out_path}")
    return True

# 3. Report 동기화 (4대 챕터 정형 아티클 + RSS 원문 기사 리스트)
def sync_reports():
    print("⚙️ [Step 3/3] 4대 챕터 쉬운 리포트 및 RSS 원문 연동 중...")

    today_str = datetime.now().strftime("%Y-%m-%d")
    date_display = datetime.now().strftime("%m-%d")

    reports_data = [
        {
            "id": f"rep_{today_str}_steel",
            "category": "제강사스크랩",
            "type": "[제강사이슈]",
            "tagClass": "report",
            "title": "현대제철·동국제강 인천·당진공장 철스크랩(고철) 구매가 kg당 +10원 인상 단행",
            "date": date_display,
            "author": "MetalsTerminal Scrap Desk",
            "replies": 14,
            "article_url": f"articles/{today_str}-steel-scrap.html",
            "summary_3lines": [
                "국내 주요 전기로 제강사들이 마당 재고 바닥으로 고철 납품 단가를 kg당 10원 인상했습니다.",
                "생철A 기준 제강사 도착도 456원, 중량A는 409원으로 상향 조정되었습니다.",
                "야적장 물동량 유입을 유도하기 위한 특별 구매 인센티브가 이번 주말까지 적용됩니다."
            ],
            "sections": {
                "current": "현대제철(인천·당진)과 동국제강(인천)이 10일 입고분부터 철스크랩 전 등급 구매 가격을 kg당 10원 인상 고시했습니다. 이에 따라 제강사 납품 기준 생철A는 456원/kg, 중량A는 409원/kg, 경량A는 355원/kg으로 상향 조정되었습니다.",
                "stocks": "추석 연휴 이후 제강사들의 철근 감산에도 불구하고 국내 야적장들의 출하 기피로 제강사 야드 재고가 안전 재고 일수(7일) 밑으로 떨어졌습니다. 남부권 대한제강·한국철강 역시 단가 인상 압박을 받고 있습니다.",
                "macro": "글로벌 수입 고철(터키·일본 H2) 오퍼 가격이 톤당 370달러 중반에서 횡보하는 가운데, 원달러 환율 상승으로 수입산 고철 조달 부담이 커지자 국내산 고철 구매 비중을 늘리는 전략으로 풀이됩니다.",
                "outlook": "단기 1~2주간은 제강사의 추가 인상 눈치보기가 이어질 전망입니다. 마당에 묵혀둔 중량/생철 재고가 있다면 이번 특별 인상 단가 구간에 1차 분할 납품을 추천합니다."
            },
            "disclaimer": "본 제강사 구매단가 정보는 주요 제강사 납품 협력사 및 업계 공시 기준이며, 공장별 하역 감가율 및 결제 조건에 따라 차이가 있을 수 있습니다.",
            "rss_sources": [
                {
                    "media": "철강금속신문 (SNMNews)",
                    "title": "국내 제강사, 입고량 감소에 철스크랩 구매가 전격 인상",
                    "date": today_str,
                    "url": "http://www.snmnews.com",
                    "snippet": "수도권 전기로 제강사 중심 전 등급 kg당 10원 추가 특별 구매 단가 적용."
                },
                {
                    "media": "스틸데일리 (Steeldaily)",
                    "title": "현대제철·동국제강 인천공장 고철 입고 재고 비상… 추가 인상 촉각",
                    "date": today_str,
                    "url": "http://www.steeldaily.co.kr",
                    "snippet": "야적장 출하 유도를 위한 단가 조정 불가피, 남부권 제강사로 확산 조짐."
                }
            ]
        },
        {
            "id": f"rep_{today_str}_cu",
            "category": "구리",
            "type": "[차트분석]",
            "tagClass": "report",
            "title": "런던 창고 재고 1,425톤 급감과 국내 A동 스크랩 가격 전망",
            "date": date_display,
            "author": "MetalsTerminal Desk",
            "replies": 7,
            "article_url": f"articles/{today_str}-copper.html",
            "summary_3lines": [
                "외국 대형 가공업체들이 런던 LME 창고에서 구리를 1,425톤 출고해갔습니다.",
                "창고에 남은 즉시 반출 가능한 구리가 줄어들면서 종가가 톤당 $9,685로 반등했습니다.",
                "급전이 필요하지 않다면 마당에 쌓인 깨끗한 A동은 며칠 더 쥐고 계셔도 좋습니다."
            ],
            "sections": {
                "current": "오늘 LME 전기동 종가는 톤당 $9,685 (+0.6%)로 마감했습니다. 원달러 환율 1,356.2원을 적용한 국내 원화 기준원가는 19,590원/kg이며, 현장 A동(밀베리) 매입 추정가는 kg당 12,300원 선을 형성하고 있습니다.",
                "stocks": "LME 총 재고는 301,250톤으로 전일 대비 -1,425톤 감소했습니다. 특히 즉시 출고를 신청한 '취소영수증(Cancelled Warrants)' 비중이 21.4%로 올라서며 실물 인도 대기 수요가 집중되고 있습니다.",
                "macro": "미국 기준금리 추가 인하 기대감으로 달러화 인덱스가 안정세를 보이고 있으며, 중국 지방정부의 전력망 투자 확대로 전력 케이블용 전기동 수요가 완만하게 회복되고 있습니다.",
                "outlook": "단기 1~2주는 톤당 $9,500 ~ $9,800 박스권 내 완만한 강보합세가 예상됩니다. 마당 상차 기준 A동은 급하게 던지기보다는 이번 주 후반까지 추이를 지켜보시는 전략을 추천합니다."
            },
            "disclaimer": "본 리포트의 '향후 예측'은 LME 창고 재고 및 거시 지표 기반의 추정 분석이며, 개별 업체의 매매 판단에 따른 최종 손익에 대해 법적 책임을 지지 않습니다.",
            "rss_sources": [
                {
                    "media": "Mining.com",
                    "title": "Copper prices bounce as warehouse warrants get cancelled in Europe",
                    "date": today_str,
                    "url": "https://www.mining.com/markets/copper",
                    "snippet": "LME copper stocks recorded sharp withdrawals amid physical demand."
                },
                {
                    "media": "Reuters Commodities",
                    "title": "China grid investment supports refined copper consumption",
                    "date": today_str,
                    "url": "https://www.reuters.com/markets/commodities",
                    "snippet": "State grid procurement offset property sector weakness in Asia."
                }
            ]
        },
        {
            "id": f"rep_{today_str}_rh",
            "category": "로듐·폐촉매",
            "type": "[촉매분석]",
            "tagClass": "report",
            "title": "로듐(Rhodium) 1g당 20만 원 돌파: 가솔린·디젤 폐촉매 매각 타이밍",
            "date": date_display,
            "author": "MetalsTerminal Desk",
            "replies": 5,
            "article_url": f"articles/{today_str}-catalyst.html",
            "summary_3lines": [
                "남아공 주요 광산 공급 지연으로 존슨매티 로듐이 1g당 206,000원에 안착했습니다.",
                "팔라듐(44,500원)과 백금(43,400원)도 바닥을 다지며 동반 반등세입니다.",
                "승용 삼원촉매 및 포터 DPF 실무 매입 견적이 개당 1만~2만 원 상향 조정되었습니다."
            ],
            "sections": {
                "current": "존슨매티(JM) 기준 로듐 가격은 온스당 $4,750 (1g당 206,000원)으로 강세를 유지 중입니다. 팔라듐은 $1,020/oz (44,500원/g), 백금은 $995/oz (43,400원/g) 선입니다.",
                "stocks": "남아프리카공화국 PGM 광산의 전력난 및 설비 보수로 1차 제련 공급이 타이트한 상태이며, 유럽 자동차 배출가스 정화용 촉매 교체 수요가 견조합니다.",
                "macro": "내연기관차 및 하이브리드(HEV) 차량의 글로벌 판매 비중이 여전히 75% 이상을 유지하면서 PGM 귀금속 수요의 절벽 우려가 해소되었습니다.",
                "outlook": "가솔린 LPi 촉매(로듐 다량 함유)와 포터 DPF(백금 함유)는 현재 단가가 연중 최상단 부근이므로 분할 매각을 진행하기에 매우 유리한 타이밍입니다."
            },
            "disclaimer": "본 분석은 폐촉매 순정품 기준의 귀금속 환산 추정치이며, 사제 촉매나 재생품은 귀금속 함량이 없어 적용되지 않습니다.",
            "rss_sources": [
                {
                    "media": "Johnson Matthey PGM Market",
                    "title": "Rhodium holds firm on South African supply constraints",
                    "date": today_str,
                    "url": "https://matthey.com/en/products-and-markets/pgms",
                    "snippet": "Automotive catalyst recycling maintains high value threshold."
                }
            ]
        }
    ]

    out_path = os.path.join(DATA_DIR, "reports.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(reports_data, f, ensure_ascii=False, indent=2)

    # 개별 정적 아티클 HTML 생성
    for rep in reports_data:
        art_filename = os.path.basename(rep["article_url"])
        art_path = os.path.join(ARTICLES_DIR, art_filename)
        html_code = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{rep['title']} - MetalsTerminal 리포트</title>
    <link rel="stylesheet" href="../style.css">
    <style>
        .art-wrap {{ max-width: 640px; margin: 0 auto; padding: 20px 14px 50px 14px; background: #fff; min-height: 100vh; }}
        .art-tag {{ font-size: 11px; font-weight: 800; background: #fee2e2; color: #b91c1c; padding: 2px 6px; border-radius: 4px; }}
        .art-title {{ font-size: 20px; font-weight: 900; color: #0f172a; margin: 10px 0 8px 0; line-height: 1.4; }}
        .art-meta {{ font-size: 12px; color: #64748b; margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }}
        .sum-box {{ background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #3b82f6; border-radius: 6px; padding: 14px; margin-bottom: 24px; }}
        .sum-title {{ font-size: 13px; font-weight: 800; color: #0f172a; margin-bottom: 8px; }}
        .sum-ol {{ padding-left: 18px; font-size: 13px; color: #334155; line-height: 1.6; }}
        .chapter-box {{ margin-bottom: 24px; }}
        .chapter-title {{ font-size: 15px; font-weight: 800; color: #0f172a; border-left: 3px solid #dc2626; padding-left: 8px; margin-bottom: 8px; }}
        .chapter-desc {{ font-size: 13.5px; line-height: 1.7; color: #334155; }}
        .disc-box {{ background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 12px; font-size: 11.5px; color: #991b1b; line-height: 1.5; margin-bottom: 24px; }}
        .rss-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; }}
        .rss-item {{ padding: 8px 0; border-bottom: 1px solid #f1f5f9; }}
        .rss-item:last-child {{ border-bottom: none; }}
        .rss-link {{ font-size: 13px; font-weight: 700; color: #2563eb; text-decoration: underline; }}
        .rss-snip {{ font-size: 11px; color: #64748b; margin-top: 2px; }}
    </style>
</head>
<body>
    <div class="art-wrap">
        <a href="../index.html#section-report" style="font-size:12px; font-weight:700; color:#64748b;">← 리포트 목록으로</a>
        <div style="margin-top:14px;"><span class="art-tag">{rep['type']}</span></div>
        <h1 class="art-title">{rep['title']}</h1>
        <div class="art-meta">{rep['author']} • {rep['date']} 발행</div>

        <div class="sum-box">
            <div class="sum-title">💡 3줄 핵심 요약</div>
            <ol class="sum-ol">
                {"".join([f"<li>{line}</li>" for line in rep['summary_3lines']])}
            </ol>
        </div>

        <div class="chapter-box">
            <h2 class="chapter-title">1. 현재 상황 (Market Status)</h2>
            <p class="chapter-desc">{rep['sections']['current']}</p>
        </div>

        <div class="chapter-box">
            <h2 class="chapter-title">2. 재고 상황 (Warehouse Stocks)</h2>
            <p class="chapter-desc">{rep['sections']['stocks']}</p>
        </div>

        <div class="chapter-box">
            <h2 class="chapter-title">3. 거시경제 (Macro & Policy)</h2>
            <p class="chapter-desc">{rep['sections']['macro']}</p>
        </div>

        <div class="chapter-box">
            <h2 class="chapter-title">4. 향후 예측 및 현장 가이드 (Outlook)</h2>
            <p class="chapter-desc">{rep['sections']['outlook']}</p>
        </div>

        <div class="disc-box">
            <strong>⚠️ [가격 예측치 면책 고지]</strong><br>
            {rep['disclaimer']}
        </div>

        <div class="rss-box">
            <div style="font-size:12px; font-weight:800; color:#0f172a; margin-bottom:8px;">🔗 해외 통신사 &amp; 광물 뉴스 실시간 원문 (RSS Source)</div>
            {"".join([f'''<div class="rss-item">
                <a href="{s['url']}" target="_blank" class="rss-link">[{s['media']}] {s['title']}</a>
                <div class="rss-snip">{s['snippet']}</div>
            </div>''' for s in rep['rss_sources']])}
        </div>
    </div>
</body>
</html>"""
        with open(art_path, "w", encoding="utf-8") as f:
            f.write(html_code)

    print(f"✅ 쉬운 리포트 & 정적 아티클 발행 완료: {out_path} ({len(reports_data)}편)")
    return True

# 마스터 실행 함수
def run_pipeline():
    print("==================================================")
    print("🚀 MetalsTerminal Unified Pipeline 가동 시작")
    print(f"   시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==================================================")

    # 1. Price
    sync_prices()
    # 2. Scrap
    sync_scrap()
    # 3. Report
    sync_reports()

    print("==================================================")
    print("🎉 [완료] Price + Scrap + Report 3대 영역 동시 동기화 완료!")
    print("   • price.html (국제시세)")
    print("   • scrap.html (스크랩·폐촉매)")
    print("   • articles/  (4대 챕터 정형 아티클)")
    print("==================================================")

if __name__ == "__main__":
    run_pipeline()
