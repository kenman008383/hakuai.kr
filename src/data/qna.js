// Q&A: src/content/qna/<날짜>-<번호>.json 파일 하나가 질문 1개다.
// { "id", "track", "level", "ep", "date", "status": "done" | "pending", "q", "a", "nick"? }
// 공개 사이트에는 하쿠가 확인한(저장소에 합쳐진) 질문만 들어온다.
const files = import.meta.glob("../content/qna/*.json", { eager: true });

export const QNA = Object.values(files)
  .map((m) => m.default ?? m)
  .sort((a, b) => b.date.localeCompare(a.date) || String(b.id).localeCompare(String(a.id)));
