// RSS: 새 강의 목록. 네이버 서치어드바이저에 제출하면 새 강의를 더 빨리 수집해 간다.
import { SITE, levelName, trackOf } from "../data/site.js";
import { EPISODES, epUrl } from "../data/episodes.js";

const esc = (s) => String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
const rfc822 = (d) => new Date(`${d}T09:00:00+09:00`).toUTCString();

export function GET() {
  const items = [...EPISODES].sort((a, b) => b.date.localeCompare(a.date) || b.level.localeCompare(a.level) || b.no.localeCompare(a.no)).slice(0, 50);
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>${esc(SITE.name)}</title>
  <link>${SITE.url}/</link>
  <description>${esc(SITE.description)}</description>
  <language>ko</language>
  <atom:link href="${SITE.url}/rss.xml" rel="self" type="application/rss+xml"/>
  <lastBuildDate>${rfc822(items[0]?.date ?? "2026-11-11")}</lastBuildDate>
${items.map((e) => {
    const url = `${SITE.url}${epUrl(e)}`;
    const name = `${trackOf(e.track).name} ${levelName(e.level)} ${e.no}`;
    return `  <item>
    <title>${esc(`${e.title} — ${name}`)}</title>
    <link>${url}</link>
    <guid isPermaLink="true">${url}</guid>
    <pubDate>${rfc822(e.date)}</pubDate>
    <category>${esc(name)}</category>
    <description>${esc(e.summary || e.oneLine)}</description>
  </item>`;
  }).join("\n")}
</channel>
</rss>
`;
  return new Response(body, { headers: { "Content-Type": "application/rss+xml; charset=utf-8" } });
}
