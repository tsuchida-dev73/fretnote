#!/usr/bin/env python3
"""フレットノート 静的サイトジェネレータ。
python3 tools/build.py で、リポジトリ直下に全ページを書き出す。
独自ドメインに移したら SITE を書き換えて再ビルドする。
"""
import json, os, html, datetime

SITE = "https://tsuchida-dev73.github.io/fretnote"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()
# アフィリエイトのタグ。ASP登録後に差し替える（空なら「準備中」表示）
AMAZON_TAG = ""

NOTES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
ALT = {"C#": "Db", "Eb": "D#", "F#": "Gb", "Ab": "G#", "Bb": "A#"}
SLUG = {"C": "c", "C#": "c-sharp", "D": "d", "Eb": "e-flat", "E": "e", "F": "f",
        "F#": "f-sharp", "G": "g", "Ab": "a-flat", "A": "a", "Bb": "b-flat", "B": "b"}
DO = ["ド", "ド#", "レ", "ミ♭", "ミ", "ファ", "ファ#", "ソ", "ラ♭", "ラ", "シ♭", "シ"]

QUAL = {
    "":     {"name": "メジャー", "iv": [0, 4, 7], "slug": "", "desc": "明るく安定した響き。曲の土台になる一番基本のコード。"},
    "m":    {"name": "マイナー", "iv": [0, 3, 7], "slug": "m", "desc": "切なく暗めの響き。メジャーの3度を半音下げた形。"},
    "7":    {"name": "セブンス", "iv": [0, 4, 7, 10], "slug": "7", "desc": "次のコードへ進みたくなる緊張感のある響き。ブルースやドミナントで多用。"},
    "m7":   {"name": "マイナーセブンス", "iv": [0, 3, 7, 10], "slug": "m7", "desc": "マイナーより柔らかくおしゃれな響き。J-POPやシティポップで頻出。"},
    "maj7": {"name": "メジャーセブンス", "iv": [0, 4, 7, 11], "slug": "maj7", "desc": "透明感のある浮遊した響き。バラードやおしゃれなコード進行の定番。"},
    "sus4": {"name": "サスフォー", "iv": [0, 5, 7], "slug": "sus4", "desc": "3度を4度に吊り上げた宙ぶらりんな響き。元のメジャーに戻すと解決感が出る。"},
    "add9": {"name": "アドナインス", "iv": [0, 4, 7, 2], "slug": "add9", "desc": "メジャーに9度を足したキラキラした響き。アコギのストロークで映える。"},
}
QORDER = ["", "m", "7", "m7", "maj7", "sus4", "add9"]

# 6弦→1弦、-1=ミュート
OPEN = {
    "C": [-1, 3, 2, 0, 1, 0], "D": [-1, -1, 0, 2, 3, 2], "E": [0, 2, 2, 1, 0, 0], "G": [3, 2, 0, 0, 0, 3], "A": [-1, 0, 2, 2, 2, 0],
    "Am": [-1, 0, 2, 2, 1, 0], "Em": [0, 2, 2, 0, 0, 0], "Dm": [-1, -1, 0, 2, 3, 1],
    "C7": [-1, 3, 2, 3, 1, 0], "D7": [-1, -1, 0, 2, 1, 2], "E7": [0, 2, 0, 1, 0, 0], "G7": [3, 2, 0, 0, 0, 1], "A7": [-1, 0, 2, 0, 2, 0], "B7": [-1, 2, 1, 2, 0, 2],
    "Am7": [-1, 0, 2, 0, 1, 0], "Em7": [0, 2, 2, 0, 3, 0], "Dm7": [-1, -1, 0, 2, 1, 1],
    "Cmaj7": [-1, 3, 2, 0, 0, 0], "Fmaj7": [-1, -1, 3, 2, 1, 0], "Gmaj7": [3, 2, 0, 0, 0, 2], "Amaj7": [-1, 0, 2, 1, 2, 0], "Dmaj7": [-1, -1, 0, 2, 2, 2], "Emaj7": [0, 2, 1, 1, 0, 0],
    "Asus4": [-1, 0, 2, 2, 3, 0], "Dsus4": [-1, -1, 0, 2, 3, 3], "Esus4": [0, 2, 2, 2, 0, 0], "Gsus4": [3, 3, 0, 0, 1, 3], "Csus4": [-1, 3, 3, 0, 1, 1],
    "Cadd9": [-1, 3, 2, 0, 3, 0], "Gadd9": [3, 0, 0, 2, 0, 3], "Dadd9": [-1, -1, 0, 2, 3, 0], "Aadd9": [-1, 0, 2, 4, 2, 0], "Eadd9": [0, 2, 2, 1, 0, 2],
}
ESHAPE = {"": [0, 2, 2, 1, 0, 0], "m": [0, 2, 2, 0, 0, 0], "7": [0, 2, 0, 1, 0, 0], "m7": [0, 2, 0, 0, 0, 0],
          "maj7": [0, -1, 1, 1, 0, -1], "sus4": [0, 2, 2, 2, 0, 0]}
ASHAPE = {"": [-1, 0, 2, 2, 2, 0], "m": [-1, 0, 2, 2, 1, 0], "7": [-1, 0, 2, 0, 2, 0], "m7": [-1, 0, 2, 0, 1, 0],
          "maj7": [-1, 0, 2, 1, 2, 0], "sus4": [-1, 0, 2, 2, 3, 0], "add9": [-1, 0, 2, 4, 2, 0]}

LETTERS = ["C", "D", "E", "F", "G", "A", "B"]; LP = [0, 2, 4, 5, 7, 9, 11]
JA = {"C": "ド", "D": "レ", "E": "ミ", "F": "ファ", "G": "ソ", "A": "ラ", "B": "シ"}
DEG = {0: 0, 2: 1, 3: 2, 4: 2, 5: 3, 7: 4, 10: 6, 11: 6}
def spell(root_name, semis, deg):
    """root_name を基準に、degree（文字の進み）とsemitoneから正しい音名を返す"""
    L = LETTERS.index(root_name[0]); acc = {"#": 1, "b": -1}.get(root_name[1:2], 0)
    rp = (LP[L] + acc) % 12
    nl = (L + deg) % 7; need = (rp + semis) % 12
    d = ((need - LP[nl] + 6) % 12) - 6
    return LETTERS[nl] + {0: "", 1: "#", -1: "b", 2: "##", -2: "bb"}[d]
def ja(n): return JA[n[0]] + n[1:].replace("#", "♯").replace("b", "♭")
def name(r, q): return NOTES[r % 12] + q
def alt_name(r, q):
    n = NOTES[r % 12]
    return ALT[n] + q if n in ALT else None
def chord_slug(r, q):
    return SLUG[NOTES[r % 12]] + (("-" + QUAL[q]["slug"]) if q else "")
def esc(s): return html.escape(str(s), quote=True)

def shapes(r, q):
    """押さえ方の候補（ラベル, フレット配列, バレーか）"""
    out = []
    o = OPEN.get(name(r, q)) or (OPEN.get(alt_name(r, q)) if alt_name(r, q) else None)
    if o: out.append(("ローコード（開放弦あり）", o, False))
    for label, tbl, open_root in (("6弦ルートのバレー", ESHAPE, 4), ("5弦ルートのバレー", ASHAPE, 9)):
        if q in tbl:
            fr = (r - open_root) % 12
            if fr == 0: continue  # 開放形はOPENで扱う
            f = [(-1 if v < 0 else v + fr) for v in tbl[q]]
            out.append((f"{label}（{fr}フレット）", f, True))
    # ローコードを先頭に、バレーは低いフレット順
    out = [x for x in out if not x[2]] + sorted([x for x in out if x[2]], key=lambda x: min(v for v in x[1] if v > 0))
    # 重複除去
    seen, res = set(), []
    for s in out:
        k = tuple(s[1])
        if k not in seen: seen.add(k); res.append(s)
    return res

def tab(f): return "".join("x" if v < 0 else (str(v) if v < 10 else f"({v})") for v in f)

def svg(f, label, w=150, barre=None):
    frets = [v for v in f if v > 0]
    mx = max([4] + frets)
    base = min(frets) if mx > 4 else 1
    sx, sy, gw, gh = 14, 22, 100, 110
    cols, rows = gw / 5, gh / 4
    h = round(w * 150 / 140)
    if barre is None: barre = min(frets or [0]) > 0 and sum(1 for v in f if v == min(frets)) >= 2 and min(frets) == min(v for v in f if v >= 0)
    s = [f'<svg class="dg" width="{w}" height="{h}" viewBox="0 0 140 150" role="img" aria-label="{esc(label)}">']
    for i in range(6):
        s.append(f'<line x1="{sx+i*cols:.1f}" y1="{sy}" x2="{sx+i*cols:.1f}" y2="{sy+gh}" stroke="var(--muted)" stroke-width="1"/>')
    for j in range(5):
        sw = 4 if (j == 0 and base == 1) else 1
        s.append(f'<line x1="{sx}" y1="{sy+j*rows:.1f}" x2="{sx+gw}" y2="{sy+j*rows:.1f}" stroke="var(--muted)" stroke-width="{sw}"/>')
    if base > 1:
        s.append(f'<text x="{sx+gw+5}" y="{sy+rows*0.65:.1f}" font-size="13" fill="var(--muted)" font-family="JetBrains Mono,monospace">{base}f</text>')
    lo = min(frets) if frets else 0
    on_base = [i for i, v in enumerate(f) if v == lo]
    if barre and lo and len(on_base) >= 2:
        a, b = on_base[0], on_base[-1]
        s.append(f'<rect x="{sx+a*cols-7:.1f}" y="{sy+(lo-base+0.5)*rows-7:.1f}" width="{(b-a)*cols+14:.1f}" height="14" rx="7" fill="var(--chord)"/>')
    for i, v in enumerate(f):
        x = sx + i * cols
        if v < 0:
            s.append(f'<text x="{x:.1f}" y="{sy-7}" text-anchor="middle" font-size="13" fill="var(--muted)">×</text>')
        elif v == 0:
            s.append(f'<circle cx="{x:.1f}" cy="{sy-11}" r="4.5" fill="none" stroke="var(--muted)" stroke-width="1.4"/>')
        else:
            y = sy + (v - base + 0.5) * rows
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="var(--chord)"/>')
    s.append('</svg>')
    return "".join(s)

def is_easy(r, q):
    return bool(OPEN.get(name(r, q)) or (alt_name(r, q) and OPEN.get(alt_name(r, q))))

# ---------- 共通レイアウト ----------
def page(path, title, desc, body, crumbs=None, jsonld=None, depth=None):
    """path: '' or 'chords/c/' のようなディレクトリ"""
    if depth is None: depth = path.count("/")
    rel = "../" * depth
    url = f"{SITE}/{path}"
    ld = []
    if crumbs:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE}/{p}"} for i, (n, p) in enumerate(crumbs)]})
    if jsonld: ld.extend(jsonld)
    crumb_html = ""
    if crumbs and len(crumbs) > 1:
        crumb_html = '<nav class="crumbs" aria-label="パンくず">' + " / ".join(
            (f'<a href="{rel}{p}">{esc(n)}</a>' if i < len(crumbs) - 1 else f'<span>{esc(n)}</span>') for i, (n, p) in enumerate(crumbs)) + "</nav>"
    doc = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="フレットノート">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Dela+Gothic+One&family=JetBrains+Mono:wght@500;700&display=swap">
<link rel="stylesheet" href="{rel}assets/site.css">
{''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)}
</head>
<body>
<header class="top"><div class="in">
<a class="logo" href="{rel}"><svg width="24" height="24" viewBox="0 0 26 26" aria-hidden="true"><rect x="3" y="2" width="20" height="22" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><g stroke="currentColor" stroke-width="1.2"><line x1="8" y1="2" x2="8" y2="24"/><line x1="13" y1="2" x2="13" y2="24"/><line x1="18" y1="2" x2="18" y2="24"/></g><line x1="3" y1="9" x2="23" y2="9" stroke="currentColor" stroke-width="2"/><circle cx="13" cy="14" r="2.6" fill="var(--accent)"/></svg>フレットノート</a>
<nav class="gnav"><a href="{rel}chords/">コード辞典</a><a href="{rel}capo/">カポ計算</a><a href="{rel}progressions/">コード進行</a><a href="{rel}player/">曲を弾く</a></nav>
</div></header>
<main class="page">{crumb_html}{body}</main>
<footer class="foot"><div class="in">
<p><a href="{rel}chords/">コード辞典</a> · <a href="{rel}capo/">カポ計算</a> · <a href="{rel}progressions/">コード進行</a> · <a href="{rel}player/">曲を弾く</a> · <a href="{rel}about/">このサイトについて</a></p>
<p class="small">フレットノートは一部のリンクでアフィリエイトプログラムを利用しています。</p>
</div></footer>
</body>
</html>
"""
    out = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(doc)
    PAGES.append(path)

PAGES = []

def gear(items):
    """商品導線。AMAZON_TAG未設定なら検索リンク（収益なし）で出しておく"""
    li = []
    for label, query, why in items:
        href = f"https://www.amazon.co.jp/s?k={html.escape(query)}" + (f"&tag={AMAZON_TAG}" if AMAZON_TAG else "")
        li.append(f'<li><a href="{href}" rel="sponsored nofollow noopener" target="_blank">{esc(label)}</a><span>{esc(why)}</span></li>')
    return f'<aside class="gear"><h2>このページで役立つ道具</h2><ul>{"".join(li)}</ul></aside>'

def faq(qas):
    h = '<section class="faq"><h2>よくある質問</h2>' + "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in qas) + "</section>"
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qas]}
    return h, ld

# ---------- コード辞典 ----------
MAJOR_STEPS = [(0, ""), (2, "m"), (4, "m"), (5, ""), (7, ""), (9, "m")]
def keys_containing(r, q):
    base = {"": "", "m": "m", "7": None, "m7": "m", "maj7": "", "sus4": None, "add9": ""}[q]
    if base is None and q == "7":
        return [(r - 7) % 12]  # V7 になるキー
    res = []
    for k in range(12):
        for st, qq in MAJOR_STEPS:
            if (k + st) % 12 == r % 12 and qq == base:
                if q == "maj7" and st not in (0, 5): continue
                if q == "m7" and st not in (2, 4, 9): continue
                if q == "add9" and st not in (0, 5, 7): continue
                res.append(k)
    return res

def capo_alt(r, q):
    """カポで簡単な形にできる提案"""
    res = []
    for c in range(1, 8):
        rr = (r - c) % 12
        if is_easy(rr, q):
            res.append((c, name(rr, q)))
    return res[:3]

def build_chords():
    cards = []
    for r in range(12):
        row = []
        for q in QORDER:
            n = name(r, q); a = alt_name(r, q)
            sh = shapes(r, q)
            if not sh: continue
            slug = chord_slug(r, q)
            path = f"chords/{slug}/"
            letters = [spell(NOTES[r], i, DEG[i]) for i in QUAL[q]["iv"]]
            notes = [ja(x) for x in letters]
            first = sh[0]
            title = f"{n}{'（'+a+'）' if a else ''}コードの押さえ方｜ギター初心者向け図解"
            desc = f"ギターの{n}コード（{QUAL[q]['name']}）の押さえ方を図で解説。構成音は{'・'.join(notes)}。{'バレーなしで押さえられます。' if not first[2] else 'バレーが難しい人向けにカポを使った代替も紹介。'}"
            # 本文
            intro = (f"<p class='lead'><strong>{esc(n)}</strong>は{esc(ja(NOTES[r]))}を根音とする{QUAL[q]['name']}コード。"
                     f"構成音は<strong>{'・'.join(notes)}</strong>（{' '.join(letters)}）。"
                     f"一番押さえやすいのは<strong>{esc(first[0].split('（')[0])}</strong>で、TAB表記だと<code>{tab(first[1])}</code>。</p>")
            shape_html = "".join(
                f'<figure class="shape">{svg(f, f"{n} {lab}", barre=b)}<figcaption><b>{esc(lab)}</b><code>{tab(f)}</code></figcaption></figure>'
                for lab, f, b in sh)
            tips = []
            if first[2]:
                ca = capo_alt(r, q)
                if ca:
                    lis = "".join(f"<li>カポ<b>{c}</b>を付けて<b>{esc(x)}</b>の形で押さえると、同じ{esc(n)}の音になる</li>" for c, x in ca)
                    tips.append(f"<h2>バレーがつらいときはカポで</h2><ul class='plain'>{lis}</ul><p class='small'>曲全体のキーで考えるなら<a href='../../capo/'>カポ計算ツール</a>が便利。</p>")
            else:
                tips.append(f"<h2>押さえるコツ</h2><ul class='plain'><li>×の弦は鳴らさないか、指の腹で軽く触れてミュートする</li><li>指はフレットのすぐ手前（ボディ側）を押さえると少ない力で鳴る</li><li>1本ずつ弦を弾いて、こもる弦がないか確認する</li></ul>")
            ks = keys_containing(r, q)
            key_html = ""
            if ks:
                key_html = "<h2>このコードがよく出てくるキー</h2><p>" + "、".join(f"キー<b>{NOTES[k]}</b>" for k in ks) + f"の曲。{esc(QUAL[q]['desc'])}</p>"
            # 同じルートの他コード
            sib = "".join(f'<a class="chip{" on" if qq==q else ""}" href="../{chord_slug(r, qq)}/">{esc(name(r, qq))}</a>' for qq in QORDER if shapes(r, qq))
            qas = [
                (f"{n}コードの構成音は？", f"{n}の構成音は{'・'.join(notes)}（{' '.join(letters)}）です。"),
                (f"{n}コードの一番簡単な押さえ方は？", f"{first[0]}で、6弦から順に{tab(first[1])}と押さえます（xは鳴らさない弦）。"),
            ]
            if first[2] and capo_alt(r, q):
                c, x = capo_alt(r, q)[0]
                qas.append((f"{n}のバレーコードが押さえられないときは？", f"カポを{c}フレットに付けて{x}の形で押さえると、バレーなしで同じ響きになります。"))
            fh, fld = faq(qas)
            g = gear([("弾きやすいアコギ弦（ライトゲージ）", "アコギ 弦 ライト", "押さえる力が少なく済む"),
                      ("カポタスト", "カポタスト ギター", "バレーを避けて同じキーで弾ける")])
            body = (f"<article><h1>{esc(n)}{('<small>（'+esc(a)+'）</small>') if a else ''} コードの押さえ方</h1>{intro}"
                    f"<div class='shapes'>{shape_html}</div><p class='small'>○=開放弦、×=鳴らさない弦、数字=フレット。TABは6弦→1弦の順。</p>"
                    f"<nav class='chips'>{sib}</nav>{''.join(tips)}{key_html}{g}{fh}</article>")
            page(path, title, desc, body,
                 crumbs=[("フレットノート", ""), ("コード辞典", "chords/"), (n, path)], jsonld=[fld])
            row.append(f'<a class="cc" href="{slug}/"><span>{esc(n)}</span>{svg(first[1], n, 64)}</a>')
        cards.append(f"<section class='root'><h2 id='{SLUG[NOTES[r]]}'>{esc(NOTES[r])}{('（'+ALT[NOTES[r]]+'）') if NOTES[r] in ALT else ''}</h2><div class='grid'>{''.join(row)}</div></section>")
    jump = "".join(f'<a class="chip" href="#{SLUG[n]}">{esc(n)}</a>' for n in NOTES)
    body = ("<h1>ギターコード辞典</h1><p class='lead'>12のルート音×7種類、全84コードの押さえ方を図解。"
            "各コードのページで、ローコードとバレーの両方の形、構成音、カポを使った簡単な代替を確認できます。</p>"
            f"<nav class='chips'>{jump}</nav>{''.join(cards)}")
    page("chords/", "ギターコード辞典｜全84コードの押さえ方を図解", "ギターコードの押さえ方を12キー×7種類（メジャー・マイナー・セブンス・m7・maj7・sus4・add9）で図解。バレーが苦手な人向けのカポ代替つき。",
         body, crumbs=[("フレットノート", ""), ("コード辞典", "chords/")])

# ---------- コード進行 ----------
PROGS = [
    ("oudou", "王道進行", [(5, "maj7"), (7, "7"), (4, "m7"), (9, "m")], "IVmaj7 → V7 → IIIm7 → VIm",
     "J-POPで最も多く使われる進行のひとつ。切なさと高揚感が同居し、サビの定番。"),
    ("canon", "カノン進行", [(0, ""), (7, ""), (9, "m"), (4, "m"), (5, ""), (0, ""), (5, ""), (7, "")], "I → V → VIm → IIIm → IV → I → IV → V",
     "パッヘルベルのカノン由来。ベースが順に下がっていく安心感があり、卒業ソングやバラードで多用される。"),
    ("komuro", "小室進行", [(9, "m"), (5, ""), (7, ""), (0, "")], "VIm → IV → V → I",
     "マイナーから始まる疾走感のある進行。90年代のヒット曲で多用され、今も定番。"),
    ("marusa", "丸サ進行", [(5, "maj7"), (4, "7"), (9, "m7"), (0, "m7")], "IVmaj7 → III7 → VIm7 → Vm7(→I7)",
     "おしゃれでシティポップ的な響き。最後のVm7は本来I7につなぐことが多い。"),
    ("1645", "1-6-4-5進行（50年代進行）", [(0, ""), (9, "m"), (5, ""), (7, "")], "I → VIm → IV → V",
     "オールディーズの定番。初心者でもローコードだけで弾きやすい。"),
    ("1564", "1-5-6-4進行", [(0, ""), (7, ""), (9, "m"), (5, "")], "I → V → VIm → IV",
     "洋楽ポップスで非常に多い進行。ループさせるだけで曲の雰囲気が出る。"),
]
KEYN = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
SDEG = {0: 0, 2: 1, 4: 2, 5: 3, 7: 4, 9: 5, 11: 6}
def pname(k, st, q): return spell(KEYN[k], st % 12, SDEG[st % 12]) + q
def build_progs():
    cards = []
    for slug, title, steps, roman, desc in PROGS:
        rows = []
        for k in range(12):
            cells = "".join(f"<td><a href='../../chords/{chord_slug(k+st, q)}/'>{esc(pname(k, st, q))}</a></td>" for st, q in steps)
            rows.append(f"<tr><th>{KEYN[k]}</th>{cells}</tr>")
        # 弾きやすいキー（ローコード率が高い順）
        score = sorted(range(12), key=lambda k: -sum(is_easy(k + st, q) for st, q in steps))[:3]
        easy = "、".join(f"キー<b>{KEYN[k]}</b>（{' → '.join(pname(k,st,q) for st,q in steps)}）" for k in score)
        ex = score[0]
        dgs = "".join(f'<figure class="shape sm">{svg(shapes(ex+st,q)[0][1], name(ex+st,q), 96)}<figcaption><b>{esc(name(ex+st,q))}</b></figcaption></figure>' for st, q in steps[:4])
        qas = [(f"{title}とは？", f"{roman}と進むコード進行。{desc}"),
               (f"{title}を一番簡単に弾けるキーは？", f"ローコードだけで弾きやすいのは{KEYN[score[0]]}です。")]
        fh, fld = faq(qas)
        body = (f"<article><h1>{esc(title)}</h1><p class='lead'><code>{esc(roman)}</code><br>{esc(desc)}</p>"
                f"<h2>弾きやすいキー</h2><p>{easy}</p><div class='shapes'>{dgs}</div>"
                f"<h2>全12キーのコード表</h2><div class='tw'><table class='prog'><thead><tr><th>キー</th>{''.join(f'<th>{i+1}</th>' for i in range(len(steps)))}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
                f"<p class='small'>コード名をタップすると押さえ方を表示。自分の声に合うキーが分からないときは<a href='../../capo/'>カポ計算</a>へ。</p>"
                f"{gear([('初心者向けギター教本', 'ギター 弾き語り 教本 初心者', 'コード進行の使い方が体系的にわかる')])}{fh}</article>")
        path = f"progressions/{slug}/"
        page(path, f"{title}のコード一覧（全12キー）｜ギター", f"{title}（{roman}）を全12キーのコード表で紹介。ギターで弾きやすいキーと押さえ方つき。", body,
             crumbs=[("フレットノート", ""), ("コード進行", "progressions/"), (title, path)], jsonld=[fld])
        cards.append(f"<li><a href='{slug}/'><b>{esc(title)}</b><code>{esc(roman)}</code><span>{esc(desc)}</span></a></li>")
    body = ("<h1>定番コード進行</h1><p class='lead'>J-POPやバラードでよく使われるコード進行を、全12キーのコード表と押さえ方つきでまとめています。</p>"
            f"<ul class='list'>{''.join(cards)}</ul>")
    page("progressions/", "定番コード進行一覧｜王道進行・カノン進行など全12キー", "王道進行、カノン進行、小室進行、丸サ進行など定番コード進行をギター向けに全12キーで掲載。", body,
         crumbs=[("フレットノート", ""), ("コード進行", "progressions/")])

# ---------- カポ計算 ----------
def build_capo():
    # 静的な対応表（検索用）
    rows = []
    for k in range(12):
        cells = "".join(f"<td>{NOTES[(k - c) % 12]}</td>" for c in range(0, 8))
        rows.append(f"<tr><th>{NOTES[k]}</th>{cells}</tr>")
    qas = [("カポを付けるとキーはどう変わる？", "カポを1フレット付けるごとに、同じ形で押さえたときの音が半音ずつ上がります。例えばカポ2でGの形を弾くと、実際の音はAになります。"),
           ("原曲キーがBbのときはカポ何番？", "カポ1でAの形、カポ3でGの形、カポ6でEの形で弾けます。ローコードが多いGの形（カポ3）が弾きやすい定番です。"),
           ("カポは何フレットまで使える？", "7フレット程度までが一般的です。それ以上は弦長が短くなり、響きが軽くなります。")]
    fh, fld = faq(qas)
    tool = """
<div class="tool" id="capo">
  <div class="field"><label for="k">原曲キー（聞こえる音）</label><select id="k"></select></div>
  <div class="field"><label for="m">メジャー／マイナー</label><select id="m"><option value="">メジャー</option><option value="m">マイナー</option></select></div>
  <div id="res" class="res" aria-live="polite"></div>
</div>
<script>
const N=["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"];
const EASY_M=["C","D","E","G","A"], EASY_m=["Am","Em","Dm"];
const k=document.getElementById("k"),m=document.getElementById("m"),res=document.getElementById("res");
k.innerHTML=N.map((n,i)=>`<option value="${i}" ${i===10?"selected":""}>${n}</option>`).join("");
function run(){const key=+k.value,q=m.value;let h="";
 for(let c=0;c<=7;c++){const sh=N[(key-c+12)%12]+q;const easy=(q?EASY_m:EASY_M).includes(sh);
  h+=`<div class="r${easy?" ok":""}"><span class="c">カポ${c}</span><span class="s">${sh} の形</span>${easy?'<span class="tag">弾きやすい</span>':""}</div>`}
 res.innerHTML=h}
k.onchange=m.onchange=run;run();
</script>"""
    body = ("<article><h1>カポ計算ツール</h1><p class='lead'>原曲キーを選ぶと、カポ何フレットでどのコードの形を弾けばいいかが一覧で出ます。"
            "ローコード中心で弾ける組み合わせには「弾きやすい」が付きます。</p>"
            f"{tool}<h2>カポ早見表</h2><p class='small'>行＝原曲キー、列＝カポ位置。マスの中が押さえる形のキー。</p>"
            f"<div class='tw'><table class='prog'><thead><tr><th>原曲</th>{''.join(f'<th>{c}</th>' for c in range(8))}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
            f"{gear([('カポタスト（ワンタッチ式）', 'カポタスト ワンタッチ', '曲の途中でも素早く付け替えられる'), ('クリップチューナー', 'クリップチューナー ギター', 'カポを付けた後のチューニング確認に')])}{fh}</article>")
    page("capo/", "カポ計算ツール｜原曲キーから弾きやすいカポ位置を一発で", "原曲キーを選ぶだけで、カポ何フレットでどのコードの形を弾けばいいかがわかる無料ツール。全キーのカポ早見表つき。",
         body, crumbs=[("フレットノート", ""), ("カポ計算", "capo/")], jsonld=[fld, {"@context": "https://schema.org", "@type": "WebApplication", "name": "カポ計算ツール", "applicationCategory": "MusicApplication", "operatingSystem": "Web", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}}])

# ---------- トップ・about ----------
def build_top():
    popular = ["F", "Bm", "C", "G", "Am", "D", "Em", "Fmaj7", "Bb", "C#m"]
    def link(n):
        for r in range(12):
            for q in QORDER:
                if name(r, q) == n: return f'<a class="chip" href="chords/{chord_slug(r, q)}/">{esc(n)}</a>'
        return ""
    body = ("<section class='hero'><h1>弾きたいときに、<br>すぐ弾けるコード帳。</h1>"
            "<p class='lead'>フレットノートは、ギターのコードの押さえ方、カポ計算、定番コード進行をまとめた無料サイト。登録なしですぐ使えます。</p></section>"
            "<section class='hub'>"
            "<a href='chords/'><b>コード辞典</b><span>全84コードの押さえ方を図解。バレーが苦手ならカポ代替も。</span></a>"
            "<a href='capo/'><b>カポ計算</b><span>原曲キーから、弾きやすいカポ位置と形を一発で。</span></a>"
            "<a href='progressions/'><b>コード進行</b><span>王道進行・カノン進行などを全12キーで。</span></a>"
            "<a href='player/'><b>曲を弾く</b><span>キー変更・自動スクロール・自作コード譜エディタ。</span></a>"
            "</section>"
            f"<h2>よく使うコード</h2><nav class='chips'>{''.join(link(n) for n in popular)}</nav>")
    page("", "フレットノート｜ギターコードの押さえ方・カポ計算・コード進行", "ギターコードの押さえ方図解、カポ計算ツール、定番コード進行を無料でまとめたサイト。初心者でもすぐ弾ける。",
         body, crumbs=[("フレットノート", "")], jsonld=[{"@context": "https://schema.org", "@type": "WebSite", "name": "フレットノート", "url": SITE + "/", "inLanguage": "ja"}])
    about = ("<article><h1>このサイトについて</h1><p>フレットノートは、アコースティックギターを弾く人が「このコードどう押さえるんだっけ」「カポ何番だっけ」をすぐ解決できるように作った無料サイトです。</p>"
             "<h2>掲載ルール</h2><ul class='plain'><li>歌詞を掲載する曲は、著作権の保護期間が終了した唱歌・童謡と、オリジナル曲に限っています</li><li>コード表記は一般的な押さえ方を基準にしています</li></ul>"
             "<h2>広告・アフィリエイトについて</h2><p>運営費のため、一部のリンクでアフィリエイトプログラムを利用しています。紹介する道具は、ページの内容に関係するものに限っています。</p></article>")
    page("about/", "このサイトについて｜フレットノート", "フレットノートの運営方針、掲載ルール、広告について。", about,
         crumbs=[("フレットノート", ""), ("このサイトについて", "about/")])

def build_meta():
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    urls = "".join(f"<url><loc>{SITE}/{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES + ["player/"])
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    llms = ["# フレットノート", "", "> ギターコードの押さえ方図解、カポ計算、定番コード進行の無料サイト（日本語）。", "",
            "## 主なページ", f"- [コード辞典]({SITE}/chords/): 全84コードの押さえ方（TAB表記・構成音・カポ代替）",
            f"- [カポ計算]({SITE}/capo/): 原曲キーとカポ位置から押さえる形を算出", f"- [コード進行]({SITE}/progressions/): 王道進行など6種を全12キーで",
            f"- [曲を弾く]({SITE}/player/): パブリックドメイン曲とオリジナル曲のコード譜", ""]
    open(os.path.join(ROOT, "llms.txt"), "w").write("\n".join(llms))

if __name__ == "__main__":
    build_top(); build_chords(); build_progs(); build_capo(); build_meta()
    print(len(PAGES), "pages")
