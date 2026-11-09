# Third-party notices

## Screen Vision (MIT)

The desktop front end of GeoLens started from **Screen Vision**
(<https://screen.vision/>, source <https://github.com/r-muresan/screen.vision>),
an open-source web application in which a vision-language model reads the
screen the user shares and a language model displays step-by-step
instructions. GeoLens keeps Screen Vision's screen-sharing hook, pixel-diff
change detection, picture-in-picture instruction panel, SSE stream reader and
the `step` / `check` / `help` / `coordinates` request structure, and adds the
manual-derived knowledge store, graph routing, context assembly and the
benchmark harness described in the accompanying manuscript.

Files that started from Screen Vision (all modified since):

- `hooks/screenshare.tsx`, `hooks/pip.tsx`
- `components/task-screen/*`, `components/multimodal-input.tsx`,
  `components/screenshare-button.tsx`, `components/screenshare-modal.tsx`,
  `components/markdown.tsx`, `components/icons.tsx`, `components/ui/*`
- `app/layout.tsx`, `app/globals.css`, `app/task/page.tsx`,
  `app/providers/TaskProvider.tsx`, `app/providers/SettingsProvider.tsx`
- `lib/ai.ts`, `lib/utils.ts`, `lib/prompts/{action,check,coordinate,help,index}.ts`
- `api/index.py` (FastAPI skeleton, rate limiter) and the `step` / `check` /
  `help` / `coordinates` routes now in `api/routers/task.py`
- build configuration: `package.json` (dependency base), `next.config.js`,
  `tailwind.config.js`, `postcss.config.js`, `tsconfig.json`, `.eslintrc.json`,
  `.python-version`, `Procfile`, `vercel.json`

Screen Vision licence text:

```
MIT License

Copyright (c) 2026 bullmeza

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Manuals used to build the knowledge stores (not redistributed)

- *Introduction to OpendTect and OpendTect Pro Training Manual 7.0* — dGB Earth
  Sciences. The PDF is not included; short excerpts appear inside the released
  run logs as retrieved context.
- *QGIS Training Manual 3.44* — QGIS project,
  <https://docs.qgis.org/3.44/en/docs/training_manual/>, provided under the
  GNU Free Documentation License 1.3 or later. The PDF is not included;
  obtain it from the QGIS documentation site.

## Models and libraries

Model names (Gemini, Claude, GPT-4o, bge-m3, open-clip ViT-B/32) are
trademarks of their respective owners. Python and JavaScript dependencies are
listed with their pinned versions in `requirements.txt` and `package.json`
and keep their own licences. `pymupdf` (AGPL-3.0) is an optional dependency
used only to build the manual-figure cache; see `requirements.txt`.
