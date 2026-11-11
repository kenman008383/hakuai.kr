# hakuai.kr — 하쿠의 AI 첫걸음

유튜브 채널 "하쿠의 AI 첫걸음"의 강의 홈페이지. 영상마다 상세 설명, 따라 할 질문, 강의 슬라이드(PPTX·PDF)를 제공한다.
운영자(하쿠)는 유튜브에 영상을 올리고 **영상 주소만** 전달한다. 강의 페이지·자료 제작과 공개는 Claude가 맡는다.

- 사이트: https://hakuai.kr (GitHub Pages, `main`에 push하면 `.github/workflows/deploy.yml`이 자동 배포)
- 설계서: https://claude.ai/artifact/4rKaaW87NzkuY3M29VNxHL
- 디자인 시안: https://claude.ai/artifact/MwiJw83nHvTE28hMxT2JSD
- 유튜브 채널: https://www.youtube.com/@하쿠-b4r

## 구조
- `src/content/episodes/<과정>/<단계>/<번호>.json` — 강의 1편 = 파일 1개. 페이지·목록·자료실·슬라이드가 모두 여기서 만들어진다.
- `src/content/qna/*.json` — Q&A 1건 = 파일 1개 (하쿠가 승인한 것만).
- `src/data/tracks.json` — 과정과 단계(입문·초급·중급·고급) 정의. 사이트와 슬라이드 스크립트가 함께 읽는다.
- `src/data/site.js` — 사이트 이름, 채널 주소, Q&A 설문지 주소(`qnaFormUrl`).
- `public/files/<과정>/<단계>/<번호>/` — 강의 슬라이드 PPTX·PDF (스크립트가 생성, 저장소에 커밋).
- `tools/fetch_video.py` — 영상 주소 → 영상 정보·한국어 자막 (`tools/_work/`, 커밋하지 않음).
- `tools/make_slides.py` — 강의 JSON → PPTX·PDF.

## 결정된 규칙
- 지금 공개 과정은 ChatGPT 하나. 영상이 나오는 대로 차례로 공개하고, 전체 편수는 표시하지 않는다("공개 N편").
- 번호: 프롤로그 = `00`, 본편은 `01`부터 두 자리. 단계 id는 `intro` `basic` `mid` `adv`.
- 한 번 공개한 강의 주소(`/chatgpt/intro/01/`)는 바꾸지 않는다. 유튜브 설명란에 걸리는 주소다.
- 디자인: 밝은 단일 테마(청록 #146B63, 노랑 #F5C542, 크림 #FBF7EE), 다크 모드 없음. PC 내용 너비 1240px(강의 페이지 1320px), 1100px 이하 2단, 760px 이하 모바일 1단 + 하단 탭.
- 슬라이드: 16:9, 밝은 디자인, 11장 내외. PPTX 글꼴 '맑은 고딕', PDF는 나눔고딕 내장.
- 대상은 AI가 처음인 분들이다. 짧고 쉬운 존댓말("~해요"), 전문용어는 풀어서. 하쿠 영상의 말투를 따른다.
- 영상에 없는 사실(가격, 기능 이름, 날짜)을 지어내지 않는다. 따라 할 질문 예시는 영상 속 예시를 바탕으로 쓴다.
- 질문 예시와 연습에는 실제 개인정보를 넣지 않는다.

## 자주 하는 일
- 새 강의 올리기: `.claude/skills/new-episode/SKILL.md` 절차를 따른다 ("강의 올려 줘" + 유튜브 주소).
- Q&A 답변: `.claude/skills/answer-qna/SKILL.md` 절차를 따른다. 승인된 답변만 `src/content/qna/`에 추가한다. 답변 표시는 "AI 하쿠 도우미 답변 · 하쿠 확인". 개인정보는 지우고, 계정 해킹·결제·의료·법률 상담은 공식 창구로 안내한다.

## 작업 환경
- Node 22, `npm ci && npm run build` (Astro 7.4.2 고정).
- 슬라이드: `pip install python-pptx yt-dlp`, LibreOffice(`soffice`), `fonts-nanum`.
- 네트워크: www.youtube.com(영상 정보·자막), i.ytimg.com(썸네일) 허용 필요.
- 확인: `npm run build`가 통과해야 push한다. 큰 디자인 변경은 1920px과 390px 화면을 한 번씩 찍어 본다.
