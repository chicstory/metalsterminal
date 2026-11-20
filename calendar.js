/* ===========================================================
   📅 MetalsTerminal 일별 아카이브 캘린더 컨트롤러
   =========================================================== */
window.MetalsCalendar = (function () {
    let dates = [];
    let latestDate = "";
    let currentIdx = 0;
    let onSelectCb = null;

    function getQueryDate() {
        const params = new URLSearchParams(window.location.search);
        return params.get("date") || "";
    }

    function formatKoreanDate(d) {
        if (!d) return "";
        const parts = d.split("-");
        if (parts.length !== 3) return d;
        const dt = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
        const wk = ["일", "월", "화", "수", "목", "금", "토"][dt.getDay()] || "";
        return `${parts[0]}.${parts[1]}.${parts[2]}(${wk})`;
    }

    function notify() {
        const selected = dates[currentIdx] || null;
        const prev = currentIdx + 1 < dates.length ? dates[currentIdx + 1] : null;
        const isLatest = currentIdx === 0;
        if (typeof onSelectCb === "function") {
            onSelectCb(selected, prev, isLatest);
        }
        renderBar();
    }

    function renderBar() {
        const bar = document.getElementById("archive-calendar-bar");
        if (!bar) return;

        if (!dates.length) {
            bar.style.display = "none";
            return;
        }
        bar.style.display = "flex";

        const optionsHtml = dates
            .map((d, idx) => {
                const label = `${formatKoreanDate(d)}${idx === 0 ? " (최신)" : ""}`;
                return `<option value="${idx}" ${idx === currentIdx ? "selected" : ""}>${label}</option>`;
            })
            .join("");

        const isLatest = currentIdx === 0;
        const hasPrev = currentIdx < dates.length - 1;
        const hasNext = currentIdx > 0;

        bar.innerHTML = `
            <div class="cal-left">
                <span class="cal-icon">📅</span>
                <span class="cal-title">누적 아카이브</span>
                <span class="cal-count">${dates.length}일치</span>
            </div>
            <div class="cal-controls">
                <button type="button" class="cal-btn" id="cal-prev-btn" ${hasPrev ? "" : "disabled"} title="이전 날짜">◀</button>
                <select id="cal-date-select" class="cal-select" aria-label="아카이브 날짜 선택">
                    ${optionsHtml}
                </select>
                <button type="button" class="cal-btn" id="cal-next-btn" ${hasNext ? "" : "disabled"} title="다음 날짜">▶</button>
                <button type="button" class="cal-btn cal-btn-latest ${isLatest ? "active" : ""}" id="cal-latest-btn" ${isLatest ? "disabled" : ""}>최신</button>
            </div>
        `;

        const sel = document.getElementById("cal-date-select");
        const prevBtn = document.getElementById("cal-prev-btn");
        const nextBtn = document.getElementById("cal-next-btn");
        const latestBtn = document.getElementById("cal-latest-btn");

        if (sel) {
            sel.addEventListener("change", (e) => {
                currentIdx = Number(e.target.value) || 0;
                notify();
            });
        }
        if (prevBtn) {
            prevBtn.addEventListener("click", () => {
                if (currentIdx < dates.length - 1) {
                    currentIdx += 1;
                    notify();
                }
            });
        }
        if (nextBtn) {
            nextBtn.addEventListener("click", () => {
                if (currentIdx > 0) {
                    currentIdx -= 1;
                    notify();
                }
            });
        }
        if (latestBtn) {
            latestBtn.addEventListener("click", () => {
                if (currentIdx !== 0) {
                    currentIdx = 0;
                    notify();
                }
            });
        }
    }

    async function init(options) {
        onSelectCb = options && options.onSelect;
        try {
            const res = await fetch("data/archive/index.json");
            if (res.ok) {
                const idxData = await res.json();
                dates = Array.isArray(idxData.dates) ? idxData.dates : [];
                latestDate = idxData.latest || dates[0] || "";
            }
        } catch (e) {
            console.warn("아카이브 인덱스 로드 스킵:", e);
        }

        const qDate = getQueryDate();
        if (qDate && dates.includes(qDate)) {
            currentIdx = dates.indexOf(qDate);
        } else {
            currentIdx = 0;
        }

        notify();
    }

    function getFileUrl(fileName, dateStr, isLatest) {
        if (isLatest || !dateStr) {
            return `data/${fileName}`;
        }
        return `data/archive/${dateStr}/${fileName}`;
    }

    return {
        init,
        getFileUrl,
    };
})();
