/**
 * MetalsTerminal - Front-end Application Logic
 * (DOSSA Mobile-First Layout: Reports -> Integrated Market -> Freeboard -> Calculator)
 */

// 1. 초기 시드 데이터
const SEED_DATA = {
    reports: [
        {
            id: "r1",
            type: "[해설]",
            tagClass: "report",
            title: "왜 오늘 구리 런던 창고 재고가 1,400톤 빠졌을까? (3줄 요약)",
            author: "데이터데스크",
            date: "10-10",
            replies: 6,
            content: "1. 외국 대형 공장들이 런던 LME 창고에서 구리를 대량 출고해갔습니다.\n2. 창고에 남은 물건이 귀해지면서 오늘 LME 종가가 톤당 9,685달러로 반등했습니다.\n3. 국내 환율 감안 시 A동 스크랩은 kg당 80~120원 추가 상승 여력이 있습니다. 급한 자금 아니면 며칠 더 쥐고 계셔도 좋습니다."
        },
        {
            id: "r2",
            type: "[낱말풀이]",
            tagClass: "report",
            title: "'취소영수증(Cancelled Warrants)'이 늘면 왜 구리값이 뛸까?",
            author: "데이터데스크",
            date: "10-09",
            replies: 12,
            content: "고물상 마당에 구리가 10톤 쌓여 있어도, 어떤 사장님이 '내가 내일 트럭 보낼 테니 찜해둬' 하고 돈을 걸어둔 상태를 뜻합니다.\n이 물량이 전체의 20%를 넘어가면 실제 시장에서 살 수 있는 구리가 말라붙어 가격이 급등하게 됩니다."
        },
        {
            id: "r3",
            type: "[촉매분석]",
            tagClass: "report",
            title: "로듐(Rhodium) 1g당 20만 원 돌파: 폐촉매 매각 타이밍",
            author: "데이터데스크",
            date: "10-08",
            replies: 4,
            content: "남아공 광산 공급 지연으로 존슨매티 기준 로듐 가격이 1g당 206,000원에 안착했습니다.\n승용 디젤 폐촉매 1개당 유가금속 가치가 8~11만 원 선으로 상향 조정되고 있습니다."
        }
    ],
    market: [
        {
            id: "m1",
            type: "[팝니다]",
            tagClass: "sell",
            title: "피복 벗긴 굵은 전선 A동(밀베리) 2.5톤 일괄 매각",
            author: "화성야적장",
            date: "10-10",
            region: "경기 화성",
            contact: "010-8291-3841",
            replies: 5,
            content: "굵은 단선 피복 깨끗하게 벗긴 A동입니다. 이물질 전혀 없고 마당 상차 기준입니다. 당일 현금 결제 우대합니다."
        },
        {
            id: "m2",
            type: "[팝니다]",
            tagClass: "sell",
            title: "현대·기아 디젤 세라믹 삼원촉매 85개 일괄",
            author: "천안해체장",
            date: "10-10",
            region: "충남 천안",
            contact: "010-6632-4911",
            replies: 8,
            content: "파손 없는 정품 촉매입니다. 오늘 로듐 시세 반등 감안해서 개당 9만 5천 원 선에 정리 희망합니다. 직거래 우선."
        },
        {
            id: "m3",
            type: "[삽니다]",
            tagClass: "buy",
            title: "알루미늄 샷시(창틀) 및 프로파일 대량 고가 매입",
            author: "인천비철",
            date: "10-09",
            region: "인천 서구",
            contact: "010-4820-1923",
            replies: 2,
            content: "샷시 창틀 스크랩 5톤 이상 고정 납품처 모십니다. 계근 오차 없이 제련소 직납 단가로 맞춰드립니다."
        },
        {
            id: "m4",
            type: "[삽니다]",
            tagClass: "buy",
            title: "통신국사·서버실 불용 고품위 금도금 기판 최고가 수거",
            author: "도심광산랩",
            date: "10-09",
            region: "수도권 전역",
            contact: "010-7718-9923",
            replies: 3,
            content: "양면 에폭시, 골드핑거, 통신보드 매입합니다. XRF 현장 성분분석 후 즉시 현금 결제."
        },
        {
            id: "m5",
            type: "[팝니다]",
            tagClass: "sell",
            title: "공장 모터 분해 파쇄동(상동) 1.2톤 정리",
            author: "시흥정밀",
            date: "10-08",
            region: "경기 시흥",
            contact: "010-5512-8849",
            replies: 1,
            content: "모터 코일 분해한 파쇄동입니다. kg당 11,300원에 마당 상차로 뺍니다."
        }
    ],
    free: [
        {
            id: "f1",
            type: "[질문]",
            tagClass: "talk",
            title: "요즘 압연소 결제 며칠 정도 걸리나요?",
            author: "화성초보",
            date: "10-10",
            region: "경기 화성",
            contact: "",
            replies: 8,
            content: "A동 5톤 처음 납품해보려는데 보통 어음 끊어주나요 아니면 현금 당일 결제인가요? 선배님들 조언 부탁드립니다."
        },
        {
            id: "f2",
            type: "[정보]",
            tagClass: "talk",
            title: "청파워 vs 잡파워 보드 분별할 때 실수하기 쉬운 점",
            author: "기판10년차",
            date: "10-09",
            region: "전국",
            contact: "",
            replies: 14,
            content: "겉보기에 초록색이라고 다 청파워가 아닙니다. 단면 페놀수지 베이클라이트 재질은 잡파워로 들어가서 kg당 값이 절반도 안 나오니 방열판 틈새 밑면 꼭 확인하세요."
        },
        {
            id: "f3",
            type: "[주의]",
            tagClass: "talk",
            title: "[주의] 경기 북부 번호판 가린 무등록 수거 화물차 조심하세요",
            author: "포천자원",
            date: "10-08",
            region: "경기 포천",
            contact: "",
            replies: 6,
            content: "계근대 속이고 차액 떼먹으려는 외지 업자 돌아다닙니다. 반드시 마당 계근대 본인이 직접 확인하시기 바랍니다."
        },
        {
            id: "f4",
            type: "[이야기]",
            tagClass: "talk",
            title: "오늘 아침 비철 야적장 커피 한잔하며 시세 봅니다",
            author: "천안반장",
            date: "10-08",
            region: "충남 천안",
            contact: "",
            replies: 3,
            content: "환율 버텨주고 구리 올라가니 이번 주말은 야적장 분위기가 훈훈하네요. 다들 안전작업 하세요."
        }
    ]
};

const STORAGE_KEY = "metalsterminal_v2_data";

let appData = { ...SEED_DATA };
let currentViewItem = null;
let pricesData = null;
let currentCategoryFilter = "all";

// 리포트 목록 렌더링 (data/reports.json 연동)
async function renderReports() {
    const ul = document.getElementById("list-reports");
    if (!ul) return;

    let reports = appData.reports || [];
    try {
        const res = await fetch("data/reports.json");
        if (res.ok) {
            reports = await res.json();
        }
    } catch (e) {
        console.warn("로컬 환경 fallback reports 사용:", e);
    }

    ul.innerHTML = "";
    if (reports.length === 0) {
        ul.innerHTML = `<li class="dossa-board-item" style="color:#94a3b8; justify-content:center;">발행된 리포트가 없습니다.</li>`;
        return;
    }

    reports.slice(0, 5).forEach(rep => {
        const li = document.createElement("li");
        li.className = "dossa-board-item";
        li.onclick = () => {
            if (rep.article_url) {
                window.location.href = rep.article_url;
            } else {
                openViewModal(rep, "reports");
            }
        };

        li.innerHTML = `
            <div class="dbi-title-wrap">
                <span class="dbi-tag report">${rep.type || '[리포트]'}</span>
                <span class="dbi-title">${escapeHtml(rep.title)}</span>
            </div>
            <span class="dbi-comment-count">${rep.replies || 0}</span>
        `;
        ul.appendChild(li);
    });
}

// 초기 로딩 수정
document.addEventListener("DOMContentLoaded", () => {
    loadLocalData();
    loadPricesData();
    renderReports();
    renderBoard("market", "list-market");
    renderBoard("free", "list-free");
});

// 시세 데이터 비동기 로딩 (data/prices.json)
async function loadPricesData() {
    try {
        const response = await fetch("data/prices.json");
        if (!response.ok) throw new Error("Network response was not ok");
        pricesData = await response.json();
    } catch (e) {
        console.warn("로컬 환경 또는 Fetch 실패로 기본 시세 데이터를 사용합니다:", e);
        pricesData = {
            display_date: "2026.10.10(금) 09:00 고시",
            usd_rate: 1356.2,
            metals: [
                { key: "copper", name: "구리", scrap_name: "A동 (밀베리 전선)", badge: "cu", category: "nonferrous", unit: "원/kg", raw_usd: "$9,685/t", raw_krw: 19590, floor_price: "12,300", diff_krw: 120, diff_pct: 0.61, trend: "up" },
                { key: "aluminum", name: "알루미늄", scrap_name: "창틀 샷시 (프로파일)", badge: "al", category: "nonferrous", unit: "원/kg", raw_usd: "$2,540/t", raw_krw: 4390, floor_price: "2,500", diff_krw: -35, diff_pct: -0.80, trend: "down" },
                { key: "iron_scrap", name: "고철·철스크랩", scrap_name: "생철 · 중량A", badge: "fe", category: "nonferrous", unit: "원/kg", raw_usd: "$372/t", raw_krw: 548, floor_price: "400", diff_krw: 0, diff_pct: 0.00, trend: "same" },
                { key: "rhodium", name: "로듐 (Rhodium)", scrap_name: "승용 삼원촉매 (로듐)", badge: "rh", category: "pgm", unit: "원/g", raw_usd: "$4,750/oz", raw_krw: 206000, floor_price: "7만 ~ 11만", floor_unit: "원/개", diff_krw: 1500, diff_pct: 0.73, trend: "up" },
                { key: "zinc", name: "아연", scrap_name: "다이캐스팅 (자막)", badge: "zn", category: "nonferrous", unit: "원/kg", raw_usd: "$3,085/t", raw_krw: 5231, floor_price: "3,650", diff_krw: 40, diff_pct: 0.77, trend: "up" },
                { key: "lead", name: "납 (Lead)", scrap_name: "폐배터리 (폐축전지)", badge: "pb", category: "nonferrous", unit: "원/kg", raw_usd: "$2,050/t", raw_krw: 2594, floor_price: "1,450", diff_krw: -24, diff_pct: -0.92, trend: "down" },
                { key: "nickel", name: "니켈", scrap_name: "스테인리스 (STS 304)", badge: "ni", category: "nonferrous", unit: "원/kg", raw_usd: "$16,250/t", raw_krw: 22030, floor_price: "1,850", diff_krw: 110, diff_pct: 0.50, trend: "up" },
                { key: "gold", name: "순금 (Gold)", scrap_name: "구형 PC 메인보드", badge: "au", category: "pgm", unit: "원/g", raw_usd: "$2,650/oz", raw_krw: 115200, floor_price: "14,000", floor_unit: "원/kg", diff_krw: 600, diff_pct: 0.52, trend: "up" },
                { key: "silver", name: "은 (Silver)", scrap_name: "전자폐기물 은접점", badge: "ag", category: "pgm", unit: "원/g", raw_usd: "$31.8/oz", raw_krw: 1380, floor_price: "950", floor_unit: "원/g", diff_krw: 12, diff_pct: 0.88, trend: "up" }
            ]
        };
    }

    // 헤더 상태 갱신
    if (pricesData.display_date) {
        document.getElementById("display-date").innerText = pricesData.display_date;
    }
    if (pricesData.usd_rate) {
        document.getElementById("display-rate").innerText = `${pricesData.usd_rate.toLocaleString()}원`;
    }

    renderMetalsCards();
}

// 시세 카드 렌더링 (철 -> 비철 -> 귀금속 3대 섹션)
function renderMetalsCards() {
    const container = document.getElementById("metals-container");
    if (!container || !pricesData) return;

    container.innerHTML = "";

    const sections = pricesData.sections || [];

    sections.forEach(sec => {
        const groupBlock = document.createElement("div");
        groupBlock.className = "market-group-block";

        const headerLabel = document.createElement("div");
        headerLabel.className = "group-header-label";
        headerLabel.innerHTML = `<span>●</span> ${sec.section_name}`;
        groupBlock.appendChild(headerLabel);

        sec.items.forEach(m => {
            const row = document.createElement("div");
            row.className = "metal-row";

            let diffClass = "same";
            let diffText = "─ 보합 (0.0%)";

            if (m.diff_krw > 0) {
                diffClass = "up";
                diffText = `▲ +${m.diff_krw.toLocaleString()} (+${m.diff_pct.toFixed(1)}%)`;
            } else if (m.diff_krw < 0) {
                diffClass = "down";
                diffText = `▼ ${m.diff_krw.toLocaleString()} (${m.diff_pct.toFixed(1)}%)`;
            }

            row.innerHTML = `
                <div class="mr-info">
                    <div class="mr-name-line">
                        <strong>${m.name_kr}</strong>
                        <span class="mr-en-name">${m.name_en}</span>
                    </div>
                    <div class="mr-benchmark">
                        <span class="mr-source-tag">${m.source}</span>
                        <span>${m.raw_usd}</span>
                    </div>
                </div>
                <div class="mr-price-block">
                    <div class="mr-krw-wrap">
                        <strong class="mr-krw-val">${m.krw_price.toLocaleString()}</strong>
                        <span class="mr-krw-unit">${m.unit}</span>
                    </div>
                    <div class="mr-diff ${diffClass}">${diffText}</div>
                </div>
            `;
            groupBlock.appendChild(row);
        });

        container.appendChild(groupBlock);
    });
}

// 필터링 버튼 클릭 이벤트
function filterMetals(category, btnEl) {
    currentCategoryFilter = category;
    document.querySelectorAll(".sh-filter .filter-chip").forEach(el => el.classList.remove("active"));
    if (btnEl) btnEl.classList.add("active");
    renderMetalsCards();
}

function toggleNav() {
    alert("⚡ MetalsTerminal\n\n• 시세·스크랩\n• 쉬운리포트\n• 직거래장터\n• 자유게시판\n• 스크랩 계산기(calc.html)");
}

function loadLocalData() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        try {
            appData = JSON.parse(saved);
        } catch (e) {
            appData = { ...SEED_DATA };
        }
    } else {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(appData));
    }
}

function saveData() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(appData));
}

// 도싸 스타일 리스트 렌더링 (초록색 댓글수)
function renderBoard(category, elementId) {
    const ul = document.getElementById(elementId);
    if (!ul) return;

    const list = appData[category] || [];
    ul.innerHTML = "";

    if (list.length === 0) {
        ul.innerHTML = `<li class="dossa-board-item" style="color:#94a3b8; justify-content:center;">등록된 글이 없습니다.</li>`;
        return;
    }

    list.slice(0, 5).forEach(item => {
        const li = document.createElement("li");
        li.className = "dossa-board-item";
        li.onclick = () => openViewModal(item, category);

        li.innerHTML = `
            <div class="dbi-title-wrap">
                <span class="dbi-tag ${item.tagClass || 'talk'}">${item.type}</span>
                <span class="dbi-title">${escapeHtml(item.title)}</span>
            </div>
            <span class="dbi-comment-count">${item.replies || 0}</span>
        `;
        ul.appendChild(li);
    });
}

// 익명 글쓰기 처리
function handleFormSubmit(event) {
    event.preventDefault();

    const quizInput = document.getElementById("post-quiz").value.trim().toLowerCase();
    if (quizInput !== "cu" && quizInput !== "씨유") {
        alert("스팸 방지 퀴즈가 틀렸습니다. 구리의 화학 기호 'Cu'를 입력해주세요.");
        return;
    }

    const board = document.getElementById("post-board").value; // market or free
    const type = document.getElementById("post-type").value;
    const author = document.getElementById("post-author").value.trim();
    const pass = document.getElementById("post-pass").value.trim();
    const region = document.getElementById("post-region").value.trim();
    const contact = document.getElementById("post-contact").value.trim();
    const title = document.getElementById("post-title").value.trim();
    const content = document.getElementById("post-content").value.trim();

    let tagClass = "talk";
    if (type === "[팝니다]") tagClass = "sell";
    else if (type === "[삽니다]") tagClass = "buy";
    else if (type === "[홍보]") tagClass = "report";

    const now = new Date();
    const dateStr = `${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

    const newItem = {
        id: "p_" + Date.now(),
        type: type,
        tagClass: tagClass,
        title: title,
        author: author,
        password: pass,
        date: dateStr,
        region: region || "전국",
        contact: contact,
        replies: 0,
        content: content
    };

    if (!appData[board]) appData[board] = [];
    appData[board].unshift(newItem);

    saveData();
    renderBoard(board, board === "market" ? "list-market" : "list-free");

    closeModal("write-modal");
    document.getElementById("write-form").reset();
    alert("🎉 글이 성공적으로 등록되었습니다!");
}

// 상세 글 보기
function openViewModal(item, category) {
    currentViewItem = { item, category };

    document.getElementById("view-tag").innerText = item.type;
    document.getElementById("view-title").innerText = item.title;
    document.getElementById("view-author").innerText = item.author;
    document.getElementById("view-date").innerText = item.date;
    document.getElementById("view-region").innerText = item.region || "지역 무관";

    const contactBox = document.getElementById("view-contact-box");
    const telBtn = document.getElementById("view-tel-btn");
    if (item.contact) {
        contactBox.style.display = "flex";
        document.getElementById("view-contact").innerText = item.contact;
        telBtn.href = `tel:${item.contact.replace(/[^0-9]/g, '')}`;
    } else {
        contactBox.style.display = "none";
    }

    document.getElementById("view-content").innerText = item.content;
    document.getElementById("view-modal").classList.add("active");
}

function deleteCurrentPost() {
    if (!currentViewItem) return;

    const inputPass = prompt("등록 시 입력한 비밀번호 4자리를 입력해주세요:");
    if (!inputPass) return;

    const { item, category } = currentViewItem;
    if (item.password && item.password !== inputPass) {
        alert("비밀번호가 일치하지 않습니다.");
        return;
    }

    const list = appData[category];
    const idx = list.findIndex(p => p.id === item.id);
    if (idx !== -1) {
        list.splice(idx, 1);
        saveData();
        renderBoard(category, category === "market" ? "list-market" : (category === "reports" ? "list-reports" : "list-free"));
        closeModal("view-modal");
        alert("삭제되었습니다.");
    }
}

// 계산기 로직
function runModalCalculation() {
    const select = document.getElementById("calc-select");
    const amountInput = document.getElementById("calc-amount");
    const finalVal = document.getElementById("calc-final-val");
    const unitDisplay = document.getElementById("calc-unit-display");
    const amountLabel = document.getElementById("calc-amount-label");

    if (!select || !amountInput || !finalVal) return;

    const selectedOption = select.options[select.selectedIndex];
    const unitPrice = parseFloat(selectedOption.value) || 0;
    const unit = selectedOption.getAttribute("data-unit") || "kg";
    const amount = parseFloat(amountInput.value) || 0;

    unitDisplay.innerText = unit;
    amountLabel.innerText = unit === "개" ? "수량 (개수 입력)" : "무게 (kg 입력)";

    const total = Math.round(unitPrice * amount);
    finalVal.innerText = total.toLocaleString("ko-KR");
}

// 모달 제어
function openWriteModal(defaultBoard) {
    if (defaultBoard) {
        const boardSelect = document.getElementById("post-board");
        if (boardSelect) boardSelect.value = defaultBoard;
    }
    document.getElementById("write-modal").classList.add("active");
}

function openCalcModal(e) {
    if (e) e.preventDefault();
    document.getElementById("calc-modal").classList.add("active");
}

function openSubscribeModal(e) {
    if (e) e.preventDefault();
    document.getElementById("sub-modal").classList.add("active");
}

function closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.remove("active");
}

function closeModalOnBackdrop(event, modalId) {
    if (event.target.id === modalId) {
        closeModal(modalId);
    }
}

function openNavDrawer() {
    alert("⚡ MetalsTerminal\n\n• 시세·단가\n• 쉬운리포트\n• 직거래장터\n• 자유게시판\n• 스크랩 계산기");
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
