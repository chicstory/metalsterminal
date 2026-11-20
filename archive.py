import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive")
INDEX_PATH = os.path.join(ARCHIVE_DIR, "index.json")
TARGET_FILES = ("prices.json", "scrap.json", "reports.json")


def _extract_date_from_prices(prices_path, fallback_date=None):
    try:
        with open(prices_path, "r", encoding="utf-8") as f:
            pdata = json.load(f)
        m = re.match(r"^(\d{4}-\d{2}-\d{2})", str(pdata.get("updated_at", "")))
        if m:
            return m.group(1)
    except Exception:
        pass
    if fallback_date:
        return fallback_date
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y-%m-%d")


def rebuild_archive_index():
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    dates = []
    for name in os.listdir(ARCHIVE_DIR):
        full = os.path.join(ARCHIVE_DIR, name)
        if os.path.isdir(full) and re.match(r"^\d{4}-\d{2}-\d{2}$", name):
            if any(os.path.exists(os.path.join(full, fn)) for fn in TARGET_FILES):
                dates.append(name)
    dates.sort(reverse=True)
    payload = {
        "latest": dates[0] if dates else "",
        "count": len(dates),
        "dates": dates,
    }
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload


def save_daily_archive(date_str=None):
    if not date_str:
        date_str = _extract_date_from_prices(os.path.join(DATA_DIR, "prices.json"))
    day_dir = os.path.join(ARCHIVE_DIR, date_str)
    os.makedirs(day_dir, exist_ok=True)

    saved = []
    for fn in TARGET_FILES:
        src = os.path.join(DATA_DIR, fn)
        dst = os.path.join(day_dir, fn)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            saved.append(fn)

    idx = rebuild_archive_index()
    print(f"    -> [아카이브 완료] data/archive/{date_str}/ ({', '.join(saved)}) | 총 {idx['count']}일 누적")
    return idx


def backfill_from_git(limit=120):
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    try:
        out = subprocess.check_output(
            ["git", "-C", BASE_DIR, "log", "-n", str(limit), "--format=%H %cs", "--", "data/prices.json"],
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
    except Exception as e:
        print(f"    [WARN] git log 조회 실패: {e}")
        return rebuild_archive_index()

    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    for line in reversed(lines):
        parts = line.split()
        if len(parts) < 2:
            continue
        commit_hash, commit_date = parts[0], parts[1]

        # 날짜 결정 (prices.json의 updated_at 우선)
        date_str = commit_date
        try:
            raw_p = subprocess.check_output(
                ["git", "-C", BASE_DIR, "show", f"{commit_hash}:data/prices.json"],
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
            )
            pdata = json.loads(raw_p)
            m = re.match(r"^(\d{4}-\d{2}-\d{2})", str(pdata.get("updated_at", "")))
            if m:
                date_str = m.group(1)
        except Exception:
            continue

        day_dir = os.path.join(ARCHIVE_DIR, date_str)
        os.makedirs(day_dir, exist_ok=True)

        for fn in TARGET_FILES:
            dst = os.path.join(day_dir, fn)
            try:
                raw_fn = subprocess.check_output(
                    ["git", "-C", BASE_DIR, "show", f"{commit_hash}:data/{fn}"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                    encoding="utf-8",
                )
                # 유효 JSON 검증
                json.loads(raw_fn)
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(raw_fn)
            except Exception:
                continue

    # 최신 작업 디렉터리 데이터도 오늘 날짜로 반영
    return save_daily_archive()


if __name__ == "__main__":
    idx = backfill_from_git()
    print(f"아카이브 인덱스 갱신 완료: 최신={idx['latest']}, 누적={idx['count']}일")
