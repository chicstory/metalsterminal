# 📜 MetalsTerminal Task History

## [2026-10-10] 독립 리포트 전문관(report.html) 구축 및 5대 메뉴 일원화
- **1. 요청사항**: 
  - `report.html` 독립 페이지 생성 (국제시세, 스크랩시세와 대등한 리포트 전용관 구축).
  - 전체 페이지 상단 메뉴 탭의 리포트 링크를 `report.html`로 100% 일원화.
- **2. 솔루션 & 구현**:
  - `report.html`: 카테고리 칩 필터(`[전체] [제강사 고철] [LME 구리] [폐촉매·PGM]`)와 각 발행 아티클의 3줄 핵심 요약 프리뷰 피드 탑재.
  - `index.html`, `price.html`, `scrap.html`, `report.html`: 5대 메뉴(`price.html`, `scrap.html`, `report.html`, `index.html#section-free`, `index.html#section-market`) 상호 링크 완벽 일원화.
  - `run_terminal.bat`: 배치 실행 시 `report.html`까지 자동 추적·커밋되도록 파이프라인 연동.
- **3. 결과 & 검증**:
  - `run_terminal.bat` 자동 실행 시 0.8초 만에 전체 데이터 갱신 및 Git 자동 커밋 완료 (`commit 5a86b06`).

## [2026-10-10] AI 기반 심층 리포트 자동 작성 엔진 탑재 & metals 매일 무인 파이프라인 자동 연동
- **1. 요청사항**: 
  - 뉴스는 간략 링크만 걸고, metals처럼 Gemini 및 로컬 AI를 활용하여 심층 분석 기사를 자동 작성하여 report에 발행.
  - 현대제철·동국제강 등 국내 제강사 고철 구매단가 인상 이슈 및 비철·스크랩, 차종별 폐촉매 이슈까지 리포트에 포함.
  - 수동 원클릭에 그치지 않고 metals 무인 파이프라인(`auto_daily_briefing.bat`)과 자동 연동되어 매일 아침 정기 발행되도록 구현.
- **2. 솔루션 & 구현**:
  - `pipeline.py` AI 분석 기사 생성기(`call_ai_article_generator`) 구축:
    - 1순위: Google Gemini Flash API (`GEMINI_API_KEY`)
    - 2순위: 로컬 GPU Ollama (`gemma4:12b-it-qat`, 무과금 0원 로컬 AI)
    - 3순위: 실시간 환율·시세 결합형 고품질 팩트 템플릿 Graceful Fallback
    - 기사 표준 구조: `[💡 3줄 핵심 요약]`, `[1. 현재 상황]`, `[2. 재고 상황]`, `[3. 거시경제]`, `[4. 향후 예측 및 현장 가이드]`, `[⚠️ 가격 예측 면책 고지]`, `[🔗 실시간 원문 뉴스 링크]`
  - 3대 정적 아티클 자동 동시 발행:
    - `articles/2026-10-10-steel-scrap.html`: 현대제철·동국제강 인천·당진공장 철스크랩 kg당 +10원 인상 단행 이슈
    - `articles/2026-10-10-copper.html`: LME 구리 창고 1,425톤 급감 및 국내 A동(밀베리) 스크랩 가격 전망
    - `articles/2026-10-10-catalyst.html`: 존슨매티 로듐 20만 원 돌파 및 가솔린/디젤 폐촉매 실무 매각 가이드
  - `thepathlab/auto_daily_briefing.bat` 자동 연동:
    - metals의 매일 새벽/아침 9시 무인 브리핑 배치 스크립트에 `metalsterminal` 자동 연동 스텝 추가.
    - metals 시세 수집 ➔ metalsterminal 시세·스크랩·AI 리포트 발행 ➔ 자동 Git 커밋까지 원스톱 연속 실행.
- **3. 결과 & 검증**:
  - `pipeline.py` 실행 시 네이버 금융 실시간 환율(1,342.7원) 기준 12종 시세 + 스크랩 5등급 + 폐촉매 6종 + AI 리포트 3편이 1초 만에 정상 생성됨.
  - `report.html`에서 카테고리 칩 필터링(`[제강사 고철] [LME 구리] [폐촉매·PGM]`) 및 상세 기사 페이지 이동 정상 동작 확인.

## [2026-10-10] GitHub Actions 매일 09:00 완전 무인 스케줄러, 실시간 뉴스 크롤러 & GitHub Pages 배포
- **1. 요청사항**: 
  - 로컬 PC(Ollama) 의존성을 배제하고, `metals`처럼 GitHub Actions 클라우드 스케줄러를 통해 매일 오전 9시 완전 무인 자동 발행.
  - 과거 자료가 아닌 최근 실제로 스크랩된 최신 뉴스 위주로 수집하여 Gemini API로 분석하고, 리포트에 발행 일시를 명확히 기재.
  - GitHub 원격 레포지토리 연결 및 GitHub Pages 웹 배포 활성화.
- **2. 솔루션 & 구현**:
  - **실시간 뉴스 크롤러 탑재 (`pipeline.py`)**:
    - Google News RSS(최근 7일 윈도우) 연동: 제강사 고철, LME 구리, 폐촉매/PGM 3대 분야별 실시간 기사 수집.
    - 실제 기사 발행일자(`YYYY-MM-DD`), 언론사명, 제목, 원문 링크 정밀 파싱.
  - **Gemini Flash 듀얼 SDK 연동 (`call_gemini_api`)**:
    - `metals`에서 검증된 `google-genai` 공식 SDK 및 REST API 다중 폴백망 구축.
    - GitHub Secrets의 `GEMINI_API_KEY` 기반으로 클라우드에서 무인 기사 작성 완결.
  - **발행 일시 및 뉴스 출처 투명 박제**:
    - 리포트 피드 및 3대 정적 아티클 상단에 `📅 YYYY년 MM월 DD일(요일) 09:00 KST 정기 고시` 대문짝 표기.
    - 하단 원문 출처 섹션에 각 언론사별 실제 보도일(`보도일: YYYY-MM-DD`) 배지 노출.
  - **GitHub Actions 완전 무인 스케줄러 (`.github/workflows/daily_terminal.yml`)**:
    - 매일 UTC 00:00 (한국 시간 KST 오전 09:00 정각) Cron 자동 실행 및 `workflow_dispatch` 수동 즉시 실행 지원.
    - `python pipeline.py` ➔ 시세, 스크랩, 리포트, 정적 아티클 일괄 갱신 ➔ `github-actions[bot]` 자동 git push.
  - **GitHub 원격 저장소 및 Pages 배포**:
    - `git remote add origin https://github.com/chicstory/metalsterminal.git` 연결 및 `main` 브랜치 푸시 완료.
- **3. 결과 & 검증**:
  - `pipeline.py` 실행 시 실제 철강금속신문(`동국제강 인천·포항 7차 인하 동참`), 스트레이트뉴스 등 최신 기사가 1초 만에 스크랩되어 리포트와 아티클에 즉시 반영됨.
  - GitHub `chicstory/metalsterminal` 메인 브랜치에 100% 푸시 완료.
- **4. 주요 합의 사항**:
  - 리포트는 반드시 당일 실시간 환율/시세와 최신 뉴스 보도일을 기준으로 생성되며, 과거 데이터로 작성되는 현상을 원천 차단함.







