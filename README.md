# hakuai.kr

**하쿠의 AI 첫걸음** 강의 홈페이지 — https://hakuai.kr

유튜브 강의마다 상세 설명, 따라 할 질문, 강의 슬라이드(PPTX·PDF)를 제공합니다. 강의 자료는 수업이나 가족 교육에 자유롭게 쓰셔도 됩니다.

## 만들고 확인하기

```bash
npm ci
npm run dev      # 미리보기
npm run build    # dist/ 에 사이트 생성
```

`main`에 push하면 GitHub Actions가 GitHub Pages로 자동 배포합니다.

## 새 강의 올리기

```bash
python3 tools/fetch_video.py <유튜브 주소>                                # 영상 정보·자막
# src/content/episodes/<과정>/<단계>/<번호>.json 작성
python3 tools/make_slides.py src/content/episodes/<과정>/<단계>/<번호>.json  # PPTX·PDF
```

자세한 절차는 `.claude/skills/new-episode/SKILL.md`, 운영 규칙은 `CLAUDE.md`에 있습니다.
