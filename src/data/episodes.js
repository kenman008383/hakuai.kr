// 강의 데이터: src/content/episodes/<과정>/<단계>/<번호>.json 파일 하나가 강의 1편이다.
import { LEVELS } from "./site.js";

const files = import.meta.glob("../content/episodes/*/*/*.json", { eager: true });

export const EPISODES = Object.values(files)
  .map((m) => m.default ?? m)
  .sort((a, b) =>
    a.track.localeCompare(b.track) ||
    LEVELS.findIndex((l) => l.id === a.level) - LEVELS.findIndex((l) => l.id === b.level) ||
    a.no.localeCompare(b.no));

export const epUrl = (e) => `/${e.track}/${e.level}/${e.no}/`;
export const epsOf = (track, level) => EPISODES.filter((e) => e.track === track && (!level || e.level === level));
export const latestEpisode = () => [...EPISODES].sort((a, b) => b.date.localeCompare(a.date) || b.no.localeCompare(a.no))[0];
export const thumbOf = (e) => `https://i.ytimg.com/vi/${e.video}/maxresdefault.jpg`;
export const ytUrl = (e, t) => `https://www.youtube.com/watch?v=${e.video}${t ? `&t=${t}s` : ""}`;
export const mmss = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
export const fmtDate = (d) => d.replaceAll("-", ".");
export const fileUrl = (e, ext) => `/files/${e.track}/${e.level}/${e.no}/hakuai-${e.track}-${e.level}-${e.no}.${ext}`;

// 자료 내려받을 때 보이는 파일 이름
export const fileName = (e, ext, levelName) => `하쿠의AI첫걸음_ChatGPT_${levelName}${e.no}_${e.tag}.${ext}`;

// 다음 편: 실제로 공개된 다음 번호가 있으면 그 강의, 없으면 예고(next)만
export function nextOf(e) {
  const same = epsOf(e.track, e.level);
  const i = same.findIndex((x) => x.no === e.no);
  return same[i + 1] ?? null;
}
export function prevOf(e) {
  const same = epsOf(e.track, e.level);
  const i = same.findIndex((x) => x.no === e.no);
  return i > 0 ? same[i - 1] : null;
}
