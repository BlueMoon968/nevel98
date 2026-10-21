"""Build the NEVEL-98 website: index.html and docs/index.html.

usage: python3 build_site.py <nevel98 source folder> <site folder>

The manual comes from docs/MANUAL.md; the "Running and building"
appendix comes from the README. Run it again whenever they change.
"""
import html
import re
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1])
SITE = Path(sys.argv[2])

# ---------------------------------------------------------------- Lua colors

KEYWORDS = set("and break do else elseif end false for function goto if in local nil not or repeat return then true until while".split())


def api_names(manual: str) -> set:
    """Every function the manual documents, so the highlighter knows the API."""
    names = set()
    for row in re.findall(r"^\|\s*(`[^|]*`)[^|]*\|", manual, re.M):
        names.update(re.findall(r"`?([a-z_][a-z0-9_]*)\s*[({]", row))
        names.update(re.findall(r"`([a-z_][a-z0-9_]*)`", row))
    helpers = re.search(r"### Math helpers\s+(.+?)\n", manual)
    if helpers:
        names.update(re.findall(r"`([a-z_]+)", helpers.group(1)))
    names.update({"flag", "persist", "DITHER", "tr", "lang", "langs", "hastr"})
    return names - KEYWORDS


TOKEN = re.compile(
    r"(?P<com>--[^\n]*)"
    r"|(?P<str>\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*')"
    r"|(?P<num>\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)"
    r"|(?P<id>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<other>.)",
    re.S,
)


def highlight(code: str, api: set) -> str:
    out = []
    for m in TOKEN.finditer(code):
        kind, text = m.lastgroup, m.group()
        t = html.escape(text, quote=False)
        if kind == "com":
            out.append(f'<span class="tk-com">{t}</span>')
        elif kind == "str":
            out.append(f'<span class="tk-str">{t}</span>')
        elif kind == "num":
            out.append(f'<span class="tk-num">{t}</span>')
        elif kind == "id" and text in KEYWORDS:
            out.append(f'<span class="tk-kw">{t}</span>')
        elif kind == "id" and text in api:
            out.append(f'<span class="tk-api">{t}</span>')
        else:
            out.append(t)
    return "".join(out)


# ---------------------------------------------------------------- the manual

def load_manual() -> str:
    text = (SRC / "docs" / "MANUAL.md").read_text(encoding="utf-8")
    # MANUAL.md has two copies of "Framed layouts": keep the newer, second one
    first = text.find("### Framed layouts")
    second = text.find("### Framed layouts", first + 1)
    if first >= 0 and second > first:
        text = text[:first] + text[second:]
    return text


def readme_appendix() -> str:
    text = (SRC / "README.md").read_text(encoding="utf-8")
    start = text.find("## Playing in the browser")
    part = text[start:] if start >= 0 else ""
    part = re.sub(r"^### ", "#### ", part, flags=re.M)
    part = re.sub(r"^## ", "### ", part, flags=re.M)
    # links that point inside the repository make no sense on the website
    part = re.sub(r"\[([^\]]+)\]\((?!https?://)[^)]+\)", r"\1", part)
    return "\n---\n\n## 9. Running and building\n\n" + part


def build_docs(css: str, api: set) -> None:
    manual = load_manual()
    body_md = manual.split("\n", 1)[1]               # drop "# NEVEL-98 Manual", the template has it
    body_md += "\n" + readme_appendix()

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
        extension_configs={"toc": {"anchorlink": False, "permalink": "¶", "permalink_class": "anchor", "toc_depth": "2-3"}},
    )
    body = md.convert(body_md)

    def code_block(m):
        lang, inner = m.group(1), html.unescape(m.group(2))
        if lang == "lua":
            return "<pre><code>" + highlight(inner, api) + "</code></pre>"
        return '<pre class="plain"><code>' + html.escape(inner, quote=False) + "</code></pre>"

    body = re.sub(r'<pre><code(?: class="language-(\w+)")?>(.*?)</code></pre>', code_block, body, flags=re.S)
    body = body.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
    body = body.replace('<a class="anchor"', '<a class="anchor" aria-label="Link to this section"')

    def toc_html(tokens, depth=0):
        items = []
        for t in tokens:
            name = html.escape(t["name"].replace("&amp;", "&"))
            sub = toc_html(t["children"], depth + 1) if t["children"] else ""
            items.append(f'<li><a href="#{t["id"]}">{name}</a>{sub}</li>')
        return "<ol>" + "".join(items) + "</ol>"

    toc = toc_html(md.toc_tokens)
    page = (HERE / "tpl_docs.html").read_text(encoding="utf-8")
    page = page.replace("{{COMMON_CSS}}", css.replace("{{ROOT}}", "../"))
    page = page.replace("{{TOC}}", toc).replace("{{BODY}}", body)
    (SITE / "docs").mkdir(parents=True, exist_ok=True)
    (SITE / "docs" / "index.html").write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- landing

LANDING_LUA = '''scene("start", function()
  layout("game")
  bg("station", "dither")
  music(1)
  show("rei_smile", "right", "dither")
  say("Rei", "Ehehe! You missed it too?")
  if choice{ "Who are you?",
             "I didn't miss it. I let it go." } == 1 then
    flag.asked = true
  end
  jump("platform")
end)'''


def build_index(css: str, api: set) -> None:
    lines = LANDING_LUA.split("\n")
    gutter = "\n".join(str(i + 1) for i in range(len(lines)))
    snippet = ('<pre><span class="gut" aria-hidden="true">' + gutter + '</span>'
               '<code class="src">' + highlight(LANDING_LUA, api) + "</code></pre>")
    page = (HERE / "tpl_index.html").read_text(encoding="utf-8")
    page = page.replace("{{COMMON_CSS}}", css.replace("{{ROOT}}", ""))
    page = page.replace("{{LUA_SNIPPET}}", snippet)
    (SITE / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    css = (HERE / "common.css").read_text(encoding="utf-8")
    api = api_names(load_manual())
    build_index(css, api)
    build_docs(css, api)
    print(f"built {SITE}/index.html and {SITE}/docs/index.html ({len(api)} API names)")
