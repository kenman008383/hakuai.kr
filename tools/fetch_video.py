"""유튜브 영상 주소에서 강의 작성에 필요한 정보(제목, 길이, 날짜, 설명, 한국어 자막)를 가져온다.

사용법:
    python3 tools/fetch_video.py https://www.youtube.com/watch?v=XXXXXXXXXXX [주소 ...]

결과: tools/_work/<영상ID>/
    meta.json       제목·채널·공개일·길이·설명·자막 언어
    transcript.txt  [분:초] 자막 한 줄씩 (자동 자막은 오타가 있을 수 있음)

필요한 것: yt-dlp (pip install yt-dlp), www.youtube.com 접속.
자동 자막은 업로드 후 몇 시간 뒤에 생긴다. 자막이 없으면 meta.json만 만들고 알려 준다.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "tools/_work"


def video_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|live/)([\w-]{11})", url)
    if not m:
        raise SystemExit(f"영상 주소를 알아볼 수 없어요: {url}")
    return m.group(1)


def clean_vtt(path):
    out, last, ts = [], None, "00:00"
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        m = re.match(r"(\d+):(\d+):(\d+)\.\d+ -->", line)
        if m:
            h, mi, s = map(int, m.groups())
            ts = f"{h * 60 + mi}:{s:02d}"
            continue
        if not line or line.startswith(("WEBVTT", "Kind:", "Language:")) or re.match(r"^\d+$", line):
            continue
        t = re.sub(r"<[^>]+>", "", line).replace("&gt;&gt;", "").replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").strip()
        if t and t != last:
            out.append(f"[{ts}] {t}")
            last = t
    return "\n".join(out)


def main(url):
    vid = video_id(url)
    d = WORK / vid
    d.mkdir(parents=True, exist_ok=True)
    full = f"https://www.youtube.com/watch?v={vid}"
    raw = subprocess.run(["yt-dlp", "--skip-download", "--dump-json", full], capture_output=True, text=True)
    if raw.returncode != 0:
        raise SystemExit(f"영상 정보를 가져오지 못했어요 ({vid}):\n{raw.stderr[-800:]}")
    info = json.loads(raw.stdout)
    auto = info.get("automatic_captions") or {}
    manual = info.get("subtitles") or {}
    lang = next((l for l in ("ko", "ko-KR") if l in manual), None) or next((l for l in ("ko-orig", "ko") if l in auto), None)
    meta = {
        "video": vid,
        "title": info.get("title"),
        "channel": info.get("channel"),
        "date": f"{info['upload_date'][:4]}-{info['upload_date'][4:6]}-{info['upload_date'][6:]}" if info.get("upload_date") else None,
        "duration": f"{info['duration'] // 60}:{info['duration'] % 60:02d}" if info.get("duration") else None,
        "description": info.get("description"),
        "captions": lang,
        "captionsKind": "manual" if lang in manual else ("auto" if lang else None),
    }
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    if lang:
        kind = "--write-subs" if lang in manual else "--write-auto-subs"
        subprocess.run(["yt-dlp", "--skip-download", kind, "--sub-langs", lang, "--sub-format", "vtt",
                        "-o", str(d / "sub"), full], capture_output=True, text=True)
        vtt = next(d.glob("sub*.vtt"), None)
        if vtt:
            (d / "transcript.txt").write_text(clean_vtt(vtt), encoding="utf-8")
            vtt.unlink()
    print(f"✓ {vid} · {meta['title']} · {meta['duration']} · {meta['date']}")
    print(f"  자막: {meta['captionsKind'] or '없음 (업로드 직후면 몇 시간 뒤 다시 시도)'} → {d.relative_to(ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for u in sys.argv[1:]:
        main(u)
