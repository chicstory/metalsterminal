import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRICES_PATH = os.path.join(DATA_DIR, "prices.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")

YAHOO_SYMBOLS = {
    "copper": "HG=F",
    "aluminum": "ALI=F",
    "gold": "GC=F",
    "silver": "SI=F",
    "platinum": "PL=F",
    "palladium": "PA=F",
}


def _parse_usd(raw_usd):
    if raw_usd is None:
        return None
    m = re.search(r"[\d,]+(?:\.\d+)?", str(raw_usd))
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", ""))
    except ValueError:
        return None


def fetch_yahoo_closes(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        payload = res.json()
        result = payload.get("chart", {}).get("result", [])
        if not result:
            return []
        closes = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        return [float(c) for c in closes if c is not None]
    except Exception as e:
        print(f"    [WARN] Yahoo Finance fetch failed ({symbol}): {e}")
        return []


def _seed_history_from_git():
    history = {}
    try:
        out = subprocess.check_output(
            ["git", "-C", BASE_DIR, "log", "-n", "250", "--format=%H %cs", "--", "data/prices.json"],
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
    except Exception:
        return history

    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    for line in reversed(lines):
        parts = line.split()
        if len(parts) < 2:
            continue
        commit_hash, commit_date = parts[0], parts[1]
        try:
            raw_json = subprocess.check_output(
                ["git", "-C", BASE_DIR, "show", f"{commit_hash}:data/prices.json"],
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
            )
            pdata = json.loads(raw_json)
            date_key = str(pdata.get("updated_at", ""))[:10] or commit_date
            for sec in pdata.get("sections", []):
                for item in sec.get("items", []):
                    key = item.get("key")
                    val = _parse_usd(item.get("raw_usd"))
                    if key and val is not None:
                        history.setdefault(key, {})[date_key] = val
        except Exception:
            continue
    return history


def update_local_history(prices_data):
    history = {}
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = {}

    if not history:
        history = _seed_history_from_git()

    kst = timezone(timedelta(hours=9))
    today_key = str(prices_data.get("updated_at", ""))[:10]
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", today_key):
        today_key = datetime.now(kst).strftime("%Y-%m-%d")

    for sec in prices_data.get("sections", []):
        for item in sec.get("items", []):
            key = item.get("key")
            val = _parse_usd(item.get("raw_usd"))
            if key and val is not None:
                series = history.setdefault(key, {})
                series[today_key] = val
                # 최근 250거래일(약 1년) 유지
                sorted_dates = sorted(series.keys())[-250:]
                history[key] = {d: series[d] for d in sorted_dates}

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return history


def _tier_from_score(score):
    if score <= 24:
        return "극단적 침체", "extreme-fear"
    if score <= 44:
        return "약세·관망", "fear"
    if score <= 55:
        return "중립·보합", "neutral"
    if score <= 74:
        return "강세·모멘텀", "greed"
    return "과열·급등", "extreme-greed"


def compute_momentum(closes, basis):
    days_used = len(closes)
    if days_used < 3:
        return {
            "score": 50,
            "label": "중립·보합",
            "tier": "neutral",
            "rsi_14": None,
            "ma125_gap": None,
            "ma125_days": days_used,
            "range_pos": None,
            "days_used": days_used,
            "basis": f"{basis} (데이터 축적중)",
        }

    # 1. RSI (최대 14일)
    deltas = [closes[i] - closes[i - 1] for i in range(1, days_used)]
    rsi_window = deltas[-min(14, len(deltas)):]
    gains = [d for d in rsi_window if d > 0]
    losses = [-d for d in rsi_window if d < 0]
    avg_gain = sum(gains) / len(rsi_window)
    avg_loss = sum(losses) / len(rsi_window)
    if avg_loss == 0:
        rsi_14 = 100.0 if avg_gain > 0 else 50.0
    else:
        rs = avg_gain / avg_loss
        rsi_14 = 100.0 - (100.0 / (1.0 + rs))

    # 2. 125일 이동평균 이격도 (-20% ~ +20% -> 0 ~ 100, 실물 선적·중기 추세 반영)
    current = closes[-1]
    ma_window = closes[-min(125, days_used):]
    ma125_days = len(ma_window)
    ma125 = sum(ma_window) / ma125_days
    ma125_gap = ((current - ma125) / ma125) * 100.0 if ma125 else 0.0
    ma_score = max(0.0, min(100.0, (ma125_gap + 20.0) * 2.5))

    # 3. 125일(약 6개월) 가격 밴드 위치 (0 ~ 100)
    p_min = min(ma_window)
    p_max = max(ma_window)
    if p_max == p_min:
        range_pos = 50.0
    else:
        range_pos = ((current - p_min) / (p_max - p_min)) * 100.0

    raw_score = 0.4 * rsi_14 + 0.3 * ma_score + 0.3 * range_pos
    score = max(0, min(100, int(round(raw_score))))
    label, tier = _tier_from_score(score)

    return {
        "score": score,
        "label": label,
        "tier": tier,
        "rsi_14": round(rsi_14, 1),
        "ma125_gap": round(ma125_gap, 2),
        "ma125_days": ma125_days,
        "range_pos": round(range_pos, 1),
        "days_used": days_used,
        "basis": basis,
    }


def enrich_prices_with_momentum(prices_path=PRICES_PATH):
    if not os.path.exists(prices_path):
        raise FileNotFoundError(f"prices.json not found: {prices_path}")

    with open(prices_path, "r", encoding="utf-8") as f:
        prices_data = json.load(f)

    history = update_local_history(prices_data)

    for sec in prices_data.get("sections", []):
        for item in sec.get("items", []):
            key = item.get("key")
            if not key:
                continue

            closes = []
            basis = ""
            yahoo_sym = YAHOO_SYMBOLS.get(key)
            if yahoo_sym:
                closes = fetch_yahoo_closes(yahoo_sym)
                if len(closes) >= 5:
                    basis = f"Yahoo Finance ({yahoo_sym})"

            if len(closes) < 5:
                series = history.get(key, {})
                closes = [series[d] for d in sorted(series.keys())]
                basis = "자체 종가 히스토리"

            item["momentum"] = compute_momentum(closes, basis)

    with open(prices_path, "w", encoding="utf-8") as f:
        json.dump(prices_data, f, ensure_ascii=False, indent=2)

    return prices_data


if __name__ == "__main__":
    data = enrich_prices_with_momentum()
    for sec in data.get("sections", []):
        for item in sec.get("items", []):
            m = item.get("momentum", {})
            print(
                f"{item['key']:10s} | {m.get('score'):3d} ({m.get('label')}) "
                f"| RSI={m.get('rsi_14')} MA125={m.get('ma125_gap')}%({m.get('ma125_days')}d) POS={m.get('range_pos')}% "
                f"| {m.get('days_used')}d [{m.get('basis')}]"
            )
