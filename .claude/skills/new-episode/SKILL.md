---
name: new-episode
description: 하쿠가 준 유튜브 영상 주소로 새 강의를 hakuai.kr에 올린다. 영상 정보·자막 읽기 → 강의 JSON 작성 → PPTX·PDF 생성 → 빌드 확인 → main에 push. "강의 올려 줘", 유튜브 주소만 보낸 경우에 사용.
---

# 새 강의 올리기

하쿠는 유튜브 주소만 준다(여러 개일 수 있음). 대본·자막 파일을 같이 주면 그걸 자막보다 우선한다.

## 1. 영상 정보와 자막 가져오기
```bash
python3 tools/fetch_video.py <주소> [<주소> ...]
```
- `tools/_work/<ID>/meta.json`, `transcript.txt`가 생긴다.
- 자막이 아직 없으면(업로드 직후) 하쿠에게 알리고, 대본이 있으면 받는다. 둘 다 없으면 제목·설명만으로 쓰지 말고, 몇 시간 뒤 다시 시도하겠다고 말한다.

## 2. 과정·단계·번호 정하기
- 제목, 설명, 썸네일 문구의 "입문 01" 같은 표기를 우선한다(썸네일: `https://i.ytimg.com/vi/<ID>/maxresdefault.jpg`를 받아서 직접 본다).
- 표기가 없으면 같은 단계의 마지막 번호 + 1. 애매하면 하쿠에게 한 번 묻는다.
- 이미 있는 번호면 덮어쓰지 말고 하쿠에게 확인한다.

## 3. 강의 JSON 쓰기
`src/content/episodes/chatgpt/intro/00.json`과 같은 형식으로 `src/content/episodes/<과정>/<단계>/<번호>.json`을 만든다.

| 항목 | 쓰는 법 |
| --- | --- |
| `video`, `date`, `duration`, `ytTitle` | meta.json 그대로 |
| `tag` | 짧은 주제어 (예: "첫 질문") |
| `title` | 시청자에게 말 걸듯 한 줄. 썸네일 큰 글씨가 있으면 그 문구 |
| `coverLines` | 표지 2줄 이내, 강조할 말은 `**` |
| `subtitle`, `oneLine` | 한 줄 |
| `summary` | 2~4문장. 무엇을 배우고 왜 쓸모 있는지 |
| `goals` | `[제목, 설명]` 3개 |
| `timeline` | `[초, 소제목, 설명]` 6~8개. 자막 시간 기준, 영상 길이를 넘지 않게 |
| `prompts` | 영상 속 예시를 따라 할 질문 2~4개 `{label, text, after}` |
| `cautions` | `[제목, 설명]` 2~3개, 영상에서 강조한 주의점 |
| `practice` | "~했어요" 체크리스트 3~4개 |
| `next` | 영상 끝 예고 `{no, title}`. 예고가 없으면 빼기 |
| `slides` | 본문 슬라이드 3~6장 (`bullets` / `prompt` / `statement`, 형식은 `tools/make_slides.py` 위쪽 설명) |

- 자동 자막의 오타는 고쳐서 쓴다(예: "su 있는" → "수 있는"). 영상에 없는 사실은 넣지 않는다.
- 앞 편의 `next`가 이번 편을 가리키면 그대로 두어도 된다(사이트가 실제 강의 링크로 바꿔 보여 줌).

## 4. 슬라이드 만들기
```bash
python3 tools/make_slides.py src/content/episodes/<과정>/<단계>/<번호>.json
```
- PDF를 PNG로 몇 장 렌더링해서(`pdftoppm -r 40`) 글자가 상자를 넘거나 겹치는지 본다. 넘치면 JSON 문장을 줄인다.

## 5. 빌드하고 올리기
```bash
npm run build
git add src/content public/files && git commit -m "Add <과정> <단계> <번호>: <제목>" && git push origin main
```
- push 후 GitHub Actions 배포가 끝나면(1~3분) `https://hakuai.kr/<과정>/<단계>/<번호>/`가 열리는지 확인한다.

## 6. 하쿠에게 보고
- 공개된 주소, 각 편 제목 한 줄, 자막 오타나 확인이 필요한 부분.
- 유튜브 설명란에 넣을 문구: `강의 자료와 따라 하기: https://hakuai.kr/<과정>/<단계>/<번호>/`
