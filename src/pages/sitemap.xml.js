// 검색엔진용 사이트맵: 모든 공개 페이지 주소를 알려 준다.
import { SITE, LEVELS, TRACKS } from "../data/site.js";
import { EPISODES, epUrl, epsOf } from "../data/episodes.js";

export function GET() {
  const latest = EPISODES.reduce((d, e) => (e.date > d ? e.date : d), "2026-11-11");
  const pages = [
    { path: "/", lastmod: latest },
    // /chatgpt/는 입문 목록과 같은 내용이라 대표 주소(/chatgpt/intro/)만 넣고, 아직 강의가 없는 단계는 뺀다
    ...TRACKS.flatMap((t) => LEVELS.filter((l) => epsOf(t.id, l.id).length).map((l) => ({ path: `/${t.id}/${l.id}/`, lastmod: latest }))),
    ...EPISODES.map((e) => ({ path: epUrl(e), lastmod: e.date })),
    { path: "/qna/" }, { path: "/resources/", lastmod: latest }, { path: "/about/" }, { path: "/privacy/" },
  ];
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map((p) => `  <url><loc>${SITE.url}${p.path}</loc>${p.lastmod ? `<lastmod>${p.lastmod}</lastmod>` : ""}</url>`).join("\n")}
</urlset>
`;
  return new Response(body, { headers: { "Content-Type": "application/xml; charset=utf-8" } });
}
