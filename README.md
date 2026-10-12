<p align="center">
  <img alt="shoof" src="docs/studio/shoof.svg" width="140">
</p>

<h1 align="center">shoof</h1>

<p align="center">
  <b>Free, open-source presentations — part of the Creative Studio creative suite.</b><br>
  <b>العروض التقديمية، مجاني ومفتوح المصدر — جزء من حزمة Creative Studio.</b>
</p>

<p align="center">
  <a href="https://shoof.studio.creative.ps/">shoof.studio.creative.ps</a> ·
  <a href="https://studio.creative.ps/">studio.creative.ps</a>
</p>

<p align="center">
  <img alt="License: MIT OR Apache-2.0" src="https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-555555">
  <img alt="Based on DeckCraft" src="https://img.shields.io/badge/based%20on-DeckCraft-0d2d3f">
</p>

## Built on DeckCraft

shoof is a fork of **[DeckCraft](https://github.com/storytold/deckcraft)**, the open-source, clean-room
application written in Rust by the **[ArtCraft](https://getartcraft.com/)** team and the DeckCraft
contributors. Almost everything that makes this app work is their work. Thank you. If you like
shoof, please star and support the upstream project as well.

What we add: the Creative Studio identity, the Arabic interface laid out right to left, and Arabic
features to come. Our changes are listed in [`studio/CHANGES.md`](studio/CHANGES.md).
Upstream's own README, with the full feature list and build instructions, is in
[`docs/UPSTREAM-README.md`](docs/UPSTREAM-README.md).

## The Creative Studio suite

| App | What it's for | Based on |
|---|---|---|
| [rsm](https://github.com/7mz410/CreativeStudio-rsm) | Vector illustration | VectorCraft |
| [ttshat](https://github.com/7mz410/CreativeStudio-ttshat) | Photo library and raw development | LightCraft |
| [tlween](https://github.com/7mz410/CreativeStudio-tlween) | Image editing | PhotoCraft |
| [tsweer](https://github.com/7mz410/CreativeStudio-tsweer) | Video editing | FilmCraft |
| [effectat](https://github.com/7mz410/CreativeStudio-effectat) | Motion graphics and effects | EffectCraft |
| [sf7aat](https://github.com/7mz410/CreativeStudio-sf7aat) | PDF documents | PdfCraft |
| [trteeb](https://github.com/7mz410/CreativeStudio-trteeb) | Page layout | DesignCraft |
| [klmat](https://github.com/7mz410/CreativeStudio-klmat) | Word processing | WordCraft |
| [arqam](https://github.com/7mz410/CreativeStudio-arqam) | Spreadsheets | GridCraft |
| **shoof** | Presentations | DeckCraft |
| [muhandes](https://github.com/7mz410/CreativeStudio-muhandes) | Computer-aided design | CADCraft |

## Building

```sh
cargo run --release -p deckcraft
# after merging upstream:
git fetch upstream && git merge upstream/main && python3 studio/rebrand.py
```

## Licence

Code: MIT OR Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE`, `NOTICE`), like upstream. The Creative Studio
name and logos in `docs/studio/` belong to the Creative Studio project.
