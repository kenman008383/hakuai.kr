// 사이트 전체 설정. 과정(트랙)과 단계는 여기서만 정의한다.
export const SITE = {
  name: "하쿠의 AI 첫걸음",
  domain: "hakuai.kr",
  url: "https://hakuai.kr",
  channel: "https://www.youtube.com/@%ED%95%98%EC%BF%A0-b4r",
  description: "AI가 처음인 분을 위한 하쿠의 ChatGPT 강의. 짧은 영상으로 보고, 다시 읽고, 강의 자료를 내려받아 따라 해 보세요.",
  // Q&A 질문 접수용 Google 설문지 주소. 비어 있으면 "곧 열려요"로 표시된다.
  qnaFormUrl: "",
};

// 과정·단계 정의는 tracks.json 한 곳에서 관리한다 (슬라이드 생성 스크립트도 같은 파일을 읽음).
// 새 과정(예: codex, claude)은 tracks.json에 추가하고 src/pages 아래에 같은 구조를 만든다.
import DATA from "./tracks.json";
export const LEVELS = DATA.levels;
export const TRACKS = DATA.tracks;

export const levelName = (id) => LEVELS.find((l) => l.id === id)?.name ?? id;
export const trackOf = (id) => TRACKS.find((t) => t.id === id);
