# a11y-audit

Crawl a site with **axe-core** and get an aggregated WCAG violation report — JSON
and readable HTML. Free, MIT.

```bash
npm i axe-core            # or point --axe-path at an existing copy
python3 audit/crawl.py --url https://example.com \
    --axe-path node_modules/axe-core/axe.min.js --out report
```

```
Audited 5 page(s); 1 page(s) not audited.
Violations: 21 rule instance(s) across 27 element(s); worst impact: critical
JSON: report.json
HTML: report.html
```

Try it against the bundled deliberately-bad demo site:

```bash
python3 examples/serve_demo.py &          # serves examples/demo-site on :8765
python3 audit/crawl.py --url http://127.0.0.1:8765/ \
    --axe-path node_modules/axe-core/axe.min.js --out report
```

## What it does

- crawls same-origin links to a configurable depth and page cap
- runs axe-core on every page, including JS-rendered content after a settle delay
- records for each violation the axe rule id, impact, the WCAG success criteria
  axe maps it to, the affected selector, the HTML snippet, and axe's own
  remediation text with its guidance link
- **reports pages it could not audit** rather than silently skipping them, so a
  gap in coverage stays visible
- handles timeouts, redirects, non-HTML responses and load failures without crashing

Options: `--max-pages`, `--depth`, `--include` / `--exclude`, `--settle-ms`, `--json-only`.

## The line worth reading

Every run prints:

```
Full conformance can be asserted from this audit: no
```

**No automated tool can certify WCAG conformance, and any that claims to is
wrong.** axe-core finds a subset of issues. It cannot tell you whether alt text
is *meaningful* rather than merely present, whether focus order is logical,
whether content makes sense when read aloud, whether instructions rely on colour
alone, or whether captions are accurate. Those need a person.

This tool tells you where the mechanical problems are, so you can spend human
effort on the parts a machine cannot see.

## Requirements

Python 3.9+, Playwright with Chromium, and axe-core (`npm i axe-core`, MPL-2.0 —
not bundled here). Set `AXE_CORE_PATH` instead of passing `--axe-path` each time.

## The full pack

The paid kit adds the **accessibility statement generator**, which refuses to
claim full conformance when the audit found violations (it exits 4 and writes
nothing); a **remediation library** with wrong-and-correct markup per axe rule
and why each matters to a screen-reader user; a **CI gate** with baselines so
accessibility does not regress; and the EAA/WCAG and manual-checks guides.

→ More developer tooling like this: **[duke5am.gumroad.com](https://duke5am.gumroad.com)** <!-- GUMROAD-LINK -->
