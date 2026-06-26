# PixelDraft — Phase 4b: Frontend (Next.js)

The product surface. Upload a screenshot, watch the detected layout draw itself
over the image (the signature view), then read the generated React or see it
rendered live.

## Design

A "blueprint" aesthetic — the product's job is revealing structure hidden in
pixels, so the UI is a draughting surface: ink-blue gridded paper, a single amber
"detection" accent, monospace for data. The amber detection overlay is the
signature element.

## Setup & run

```bash
cd frontend
npm install
cp .env.local.example .env.local      # set NEXT_PUBLIC_API if backend isn't on :8000
npm run dev                           # http://localhost:3000
```

The backend (Phase 4a) must be running for generation to work.

## How it works

- `app/page.js` — upload, detection overlay, code/preview tabs, copy/reset.
- `components/preview.js` — wraps the generated component in a self-contained HTML
  doc (CDN React + Babel + Tailwind) and renders it in a **sandboxed iframe**, so
  generated code can never touch the host page. (Live preview needs internet for
  the CDNs.)

## Demo tips (for your portfolio)

- Record a GIF: drop a real login/dashboard screenshot → overlay appears → flip to
  Preview. That overlay-drawing moment is the shot that sells the project.
- Keep a few clean sample screenshots on hand that show the pipeline at its best,
  plus one honest "harder" case for your failure gallery.
