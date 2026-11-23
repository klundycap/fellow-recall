# Fellow Recall

Pain medicine flashcards for fellowship. Every fact has two faces:

- **Recall**: a bare question and answer.
- **Clinic**: the same fact inside a short patient scenario, so it comes back the way you'll need it in clinic.

Spaced repetition alternates the two faces. Cards are grouped into pain board topic areas.

## Features

- **Study** with spaced repetition (Again / Hard / Good / Easy), filtered by topic area.
- **Ask**: ask a clinical question and get an evidence summary plus card pairs.
- **Distill**: paste an OpenEvidence answer and keep the 1–2 facts that change practice.
- **Import** from Anki (File › Export › Notes in Plain Text, with HTML) or from a backup.
- **Write clinic faces** for imported cards with Claude, 8 at a time.
- Works offline for studying. Installable from Chrome as its own app.

## Setup on your phone

1. Open the GitHub Pages link in Chrome and tap **Install app**.
2. In the Deck tab, paste your Claude API key from console.anthropic.com under **Claude API key**. It is stored only on the device and sent only to Anthropic.

Cards are stored on the device (IndexedDB). Use **Download backup** regularly.

## How it's built

A single static page with no server.

- `index.html`: the app.
- `shim.js`: device storage (IndexedDB), the Claude API calls (model `claude-opus-5-5`), and downloads.
- `anthropic-sdk.js`: the official `@anthropic-ai/sdk` 1.6.0, bundled for the browser with esbuild.
- `sw.js`, `manifest.webmanifest`, `icon-*.png`: make it installable and usable offline.
- `tools/build.py`: regenerates the app from `tools/claude-artifact.html` (the claude.ai version). Bump the version argument so phones pick up the update.
