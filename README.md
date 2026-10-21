# nevel98.bluemoon.moe

The website of **NEVEL-98**, a fantasy computer for making visual novels in the style of the NEC PC-9801 era.

| Path | What it is |
|---|---|
| `/` | landing page (`index.html`) |
| `/docs/` | the manual, generated from `docs/MANUAL.md` of NEVEL-98 |
| `/play/` | the demo cart *Last Train Home* (copy of `web/dist/demo.html`) |
| `/app/` | the whole machine in the browser (copy of `web/dist/index.html`) |
| `/carts/` | the demo as `.n98` and as a floppy `.n98.png` |

The site is static and needs no build to be served. GitHub Pages serves it from the root of `main`, with the custom domain in `CNAME`.

## Updating

**The manual and the landing page.** After changing `docs/MANUAL.md` or the README of NEVEL-98, rebuild both pages:

```sh
pip install markdown
python3 tools/build_site.py /path/to/nevel98 .
```

The generator reads the manual (keeping only the newer copy of any duplicated section), appends the "Running and building" part of the README, and colors Lua code like the machine's code editor. The page designs live in `tools/tpl_index.html`, `tools/tpl_docs.html` and `tools/common.css`.

**The web player.** After a new web build of NEVEL-98, copy the two files:

```sh
cp /path/to/nevel98/web/dist/demo.html  play/index.html
cp /path/to/nevel98/web/dist/index.html app/index.html
```

**The screenshots** in `assets/screens/` are real frames of the machine (640×400, 16 colors). Replace them with frames of the same size and name.

## Credits

NEVEL-98 is released under the MIT license. The site uses the fonts Spleen (BSD 2-Clause), DotGothic16 and M PLUS 1p (SIL Open Font License 1.1), served from `assets/fonts/` together with their licenses.
