"""강의 파일(JSON) 하나로 강의 슬라이드 PPTX와 PDF를 만든다.

사용법:
    python3 tools/make_slides.py src/content/episodes/chatgpt/intro/00.json

결과:
    public/files/<과정>/<단계>/<번호>/hakuai-<과정>-<단계>-<번호>.pptx / .pdf

필요한 것: python-pptx, LibreOffice(soffice), 한글 글꼴(fonts-nanum), 썸네일을 받기 위한 i.ytimg.com 접속.
PPTX는 '맑은 고딕'으로, PDF는 글꼴이 내장되도록 나눔고딕으로 따로 만든다.

슬라이드 순서: 표지 → 오늘의 목표 → (강의 파일의 slides 항목) → 꼭 확인할 것 → 오늘의 연습 → 과정 로드맵 → 다음 편
slides 항목 형식:
    {"type": "bullets", "kicker", "title", "bullets": [...], "card": [제목, 내용]?}
    {"type": "prompt", "promptIndex": n, "kicker", "title", "intro"}   # prompts[n]의 질문과 확인할 점을 씀
    {"type": "statement", "kicker", "lines": [...], "body"}
문장 안의 **굵게** 표시는 청록색 굵은 글씨가 된다.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "src/data/tracks.json").read_text(encoding="utf-8"))

TEAL = RGBColor(0x14, 0x6B, 0x63)
TEAL_SOFT = RGBColor(0xDC, 0xEE, 0xEA)
MIST = RGBColor(0xE9, 0xF4, 0xF1)
YELLOW = RGBColor(0xF5, 0xC5, 0x42)
CREAM = RGBColor(0xFB, 0xF7, 0xEE)
INK = RGBColor(0x1C, 0x29, 0x2E)
MUTED = RGBColor(0x5B, 0x6B, 0x70)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
IN = 914400


def i(x):
    return Emu(int(x * IN))


def runs_of(s, base):
    """'**굵게**' 표시를 (글자, 덮어쓸 속성) 조각으로 나눈다."""
    out = []
    for n, part in enumerate(re.split(r"\*\*(.+?)\*\*", s)):
        if part:
            out.append((part, {"bold": True, "color": TEAL} if n % 2 else dict(base)))
    return out


class Deck:
    def __init__(self, ep, font):
        self.ep, self.font = ep, font
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Emu(12192000), Emu(6858000)
        self.page = 0
        track = next(t for t in DATA["tracks"] if t["id"] == ep["track"])
        self.track = track
        self.level_name = next(l["name"] for l in DATA["levels"] if l["id"] == ep["level"])
        self.footer = f"하쿠의 AI 첫걸음 · {track['name']} {self.level_name} {ep['no']} {ep['tag']}"

    # ---- primitives ----
    def new(self, color=CREAM):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        f = s.background.fill
        f.solid()
        f.fore_color.rgb = color
        self.page += 1
        return s

    def rect(self, s, x, y, w, h, color, shape=MSO_SHAPE.RECTANGLE, line=None, radius=None):
        r = s.shapes.add_shape(shape, i(x), i(y), i(w), i(h))
        r.fill.solid()
        r.fill.fore_color.rgb = color
        if line:
            r.line.color.rgb = line
            r.line.width = Pt(1.5)
        else:
            r.line.fill.background()
        r.shadow.inherit = False
        if radius is not None:
            r.adjustments[0] = radius
        return r

    def text(self, s, x, y, w, h, paras, size=20, color=INK, bold=False, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, spacing=1.25, shape=None, space_after=0):
        tb = shape or s.shapes.add_textbox(i(x), i(y), i(w), i(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = i(0.08)
        tf.margin_top = tf.margin_bottom = i(0.05)
        paras = paras if isinstance(paras, list) else [paras]
        for n, para in enumerate(paras):
            p = tf.paragraphs[0] if n == 0 else tf.add_paragraph()
            p.alignment = align
            p.line_spacing = spacing
            if space_after:
                p.space_after = Pt(space_after)
            segs = runs_of(para, {}) if isinstance(para, str) else para
            for seg, ov in segs:
                r = p.add_run()
                r.text = seg
                r.font.name = self.font
                r.font.size = Pt(ov.get("size", size))
                r.font.bold = ov.get("bold", bold)
                r.font.color.rgb = ov.get("color", color)
        return tb

    def header(self, s, kicker, title):
        self.rect(s, 0, 0, 13.333, 0.12, TEAL)
        self.text(s, 0.7, 0.45, 11, 0.4, kicker, size=14, color=TEAL, bold=True)
        self.text(s, 0.7, 0.8, 11.9, 0.9, title, size=34, bold=True)
        self.rect(s, 0.78, 1.72, 0.9, 0.08, YELLOW)
        self.foot(s)

    def foot(self, s):
        self.text(s, 0.7, 7.0, 9, 0.35, self.footer, size=11, color=MUTED)
        self.text(s, 11.6, 7.0, 1.0, 0.35, str(self.page), size=11, color=MUTED, align=PP_ALIGN.RIGHT)

    # ---- slide types ----
    def cover(self, thumb):
        ep, s = self.ep, self.new(MIST)
        self.rect(s, 0.7, 0.75, 0.08, 0.42, YELLOW)
        self.text(s, 0.9, 0.72, 6, 0.5, "하쿠와 함께 AI", size=18, bold=True)
        self.rect(s, 0.7, 1.55, 3.6, 0.55, WHITE, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
        self.text(s, 0.7, 1.55, 3.6, 0.55, f"{self.level_name} {ep['no']} · {ep['tag']}", size=17, color=TEAL,
                  bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        lines = ep.get("coverLines") or [ep["title"]]
        size = 54 if max(len(l) for l in lines) <= 12 else 40
        paras = [[(t, {**ov, "size": size, "bold": True}) for t, ov in runs_of(l, {})] for l in lines]
        self.text(s, 0.7, 2.45, 6.6, 2.5, paras, spacing=1.05)
        if ep.get("subtitle"):
            self.text(s, 0.7, 5.05, 6.4, 0.5, ep["subtitle"], size=20)
        self.text(s, 0.7, 6.55, 6.4, 0.4, "강의 자료 · 자유롭게 내려받아 쓰세요 · hakuai.kr", size=12, color=MUTED)
        if thumb:
            s.shapes.add_picture(str(thumb), i(7.55), i(1.75), width=i(5.2))

    def goals(self):
        if not self.ep.get("goals"):
            return
        s = self.new()
        self.header(s, "오늘의 목표", f"이 시간에 알아볼 {len(self.ep['goals'])}가지")
        for n, (t, d) in enumerate(self.ep["goals"][:4]):
            y = 2.25 + n * 1.5
            self.rect(s, 0.8, y, 0.8, 0.8, TEAL, MSO_SHAPE.OVAL)
            self.text(s, 0.8, y, 0.8, 0.8, str(n + 1), size=26, color=WHITE, bold=True, align=PP_ALIGN.CENTER,
                      anchor=MSO_ANCHOR.MIDDLE)
            self.text(s, 1.9, y - 0.05, 10.5, 0.5, t, size=24, bold=True)
            self.text(s, 1.9, y + 0.5, 10.5, 0.5, d, size=18, color=MUTED)

    def bullets(self, sp):
        s = self.new()
        self.header(s, sp["kicker"], sp["title"])
        card = sp.get("card")
        w = 6.3 if card else 11.8
        self.text(s, 0.8, 2.2, w, 4.2, sp["bullets"], size=21, spacing=1.35, space_after=14)
        if card:
            self.rect(s, 7.6, 2.2, 5.0, 3.7, TEAL_SOFT, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
            self.text(s, 7.95, 2.45, 4.4, 0.5, card[0], size=15, color=TEAL, bold=True)
            self.text(s, 7.95, 3.0, 4.4, 2.7, card[1], size=24, bold=True, spacing=1.4)

    def prompt(self, sp):
        p = self.ep["prompts"][sp["promptIndex"]]
        s = self.new()
        self.header(s, sp["kicker"], sp["title"])
        self.text(s, 0.8, 2.15, 11.8, 1.0, sp.get("intro", ""), size=19, color=MUTED, spacing=1.35)
        lines = p["text"].count("\n") + 1
        h = 0.95 + 0.42 * lines
        y = 3.35 if lines <= 2 else 2.9
        self.rect(s, 0.8, y, 11.8, h, WHITE, MSO_SHAPE.ROUNDED_RECTANGLE, line=TEAL, radius=0.06)
        self.text(s, 1.05, y + 0.18, 11.3, 0.4, "이렇게 물어보세요", size=13, color=TEAL, bold=True)
        self.text(s, 1.05, y + 0.6, 11.3, h - 0.7, p["text"].split("\n"), size=18, spacing=1.3)
        self.text(s, 0.8, max(5.45, y + h + 0.25), 11.8, 0.9, p["after"], size=19)

    def statement(self, sp):
        s = self.new(MIST)
        self.rect(s, 0, 0, 0.18, 7.5, YELLOW)
        self.text(s, 0.9, 0.9, 11.5, 0.5, sp["kicker"], size=16, color=TEAL, bold=True)
        paras = [[(t, {**ov, "size": 40, "bold": True}) for t, ov in runs_of(l, {})] for l in sp["lines"]]
        self.text(s, 0.9, 1.7, 11.5, 2.4, paras, spacing=1.2)
        if sp.get("body"):
            self.text(s, 0.9, 4.3, 11.0, 1.8, sp["body"], size=20, color=MUTED, spacing=1.45)

    def cautions(self):
        if not self.ep.get("cautions"):
            return
        s = self.new()
        self.header(s, "안전하게 쓰기", "도움을 받아도, 확인은 내가 해요")
        for n, (t, d) in enumerate(self.ep["cautions"][:4]):
            y = 2.2 + n * 1.5
            self.rect(s, 0.8, y + 0.05, 0.12, 1.05, YELLOW)
            self.text(s, 1.15, y, 11.3, 0.5, t, size=23, bold=True)
            self.text(s, 1.15, y + 0.55, 11.3, 0.5, d, size=18, color=MUTED)

    def practice(self):
        if not self.ep.get("practice"):
            return
        s = self.new()
        self.header(s, "오늘의 연습", "작은 일 하나로 직접 해 보기")
        for n, st in enumerate(self.ep["practice"][:5]):
            y = 2.2 + n * 1.0
            self.rect(s, 0.85, y + 0.08, 0.45, 0.45, WHITE, MSO_SHAPE.ROUNDED_RECTANGLE, line=TEAL, radius=0.15)
            self.text(s, 1.55, y, 11.0, 0.7, st, size=20)

    def roadmap(self):
        s = self.new()
        self.header(s, "앞으로의 과정", f"{self.track['name']} 입문부터 고급까지")
        rows = [(l["name"], self.track["levels"][l["id"]]["goal"], self.track["levels"][l["id"]]["topics"])
                for l in DATA["levels"]]
        tbl = s.shapes.add_table(len(rows) + 1, 3, i(0.8), i(2.15), i(11.8), i(4.3)).table
        for c, wdt in enumerate([1.6, 4.0, 6.2]):
            tbl.columns[c].width = i(wdt)
        for c, h in enumerate(["과정", "목표", "다룰 내용"]):
            cell = tbl.cell(0, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = TEAL
            self.text(None, 0, 0, 0, 0, h, size=16, color=WHITE, bold=True, shape=cell)
        for r, row in enumerate(rows, start=1):
            current = DATA["levels"][r - 1]["id"] == self.ep["level"]
            for c, v in enumerate(row):
                cell = tbl.cell(r, c)
                cell.fill.solid()
                cell.fill.fore_color.rgb = TEAL_SOFT if current else WHITE
                self.text(None, 0, 0, 0, 0, v, size=16, bold=(c == 0), shape=cell)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    def ending(self):
        ep, s = self.ep, self.new(MIST)
        self.rect(s, 0, 0, 0.18, 7.5, YELLOW)
        nxt = ep.get("next")
        self.text(s, 0.9, 1.1, 11.5, 0.5, "다음 편 예고" if nxt else "수고하셨어요", size=16, color=TEAL, bold=True)
        title = nxt["title"] if nxt else "오늘 배운 것을 작은 일 하나에 써 보세요"
        self.text(s, 0.9, 1.9, 11.5, 1.8, title, size=40, bold=True, spacing=1.2)
        self.text(s, 0.9, 4.4, 11.5, 0.6, "서두르지 말고, 하쿠와 함께 차근차근 시작해요.", size=22, color=MUTED)
        url = f"hakuai.kr/{ep['track']}/{ep['level']}/{ep['no']}"
        self.text(s, 0.9, 5.6, 11.5, 0.9, [
            [("강의 자료  ", {"size": 15, "color": TEAL, "bold": True}), (url, {"size": 15})],
            [("영상 보기  ", {"size": 15, "color": TEAL, "bold": True}), (f"youtube.com/watch?v={ep['video']}", {"size": 15})],
        ], spacing=1.5)

    def build(self, thumb):
        self.cover(thumb)
        self.goals()
        for sp in self.ep.get("slides", []):
            getattr(self, sp["type"])(sp)
        self.cautions()
        self.practice()
        self.roadmap()
        self.ending()
        return self.prs


def fetch_thumb(video, dest):
    for name in ("maxresdefault", "hqdefault"):
        try:
            with urllib.request.urlopen(f"https://i.ytimg.com/vi/{video}/{name}.jpg", timeout=20) as r:
                dest.write_bytes(r.read())
                return dest
        except Exception:
            continue
    print("  ! 썸네일을 받지 못해 표지에 넣지 않았어요")
    return None


def main(path):
    ep = json.loads(Path(path).read_text(encoding="utf-8"))
    out_dir = ROOT / "public/files" / ep["track"] / ep["level"] / ep["no"]
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"hakuai-{ep['track']}-{ep['level']}-{ep['no']}"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        thumb = fetch_thumb(ep["video"], tmp / "thumb.jpg")
        pptx = out_dir / f"{base}.pptx"
        deck = Deck(ep, "맑은 고딕").build(thumb)
        deck.save(pptx)
        # PDF: 나눔고딕으로 만든 사본을 변환해 글꼴이 PDF에 들어가게 한다
        pdf_src = tmp / f"{base}.pptx"
        Deck(ep, "NanumGothic").build(thumb).save(pdf_src)
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(pdf_src)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.copy(tmp / f"{base}.pdf", out_dir / f"{base}.pdf")
    print(f"  ✓ {pptx.relative_to(ROOT)} ({len(deck.slides)}장)")
    print(f"  ✓ {(out_dir / (base + '.pdf')).relative_to(ROOT)}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
