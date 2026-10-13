#!/usr/bin/env python3
"""Apply the 3urood (Creative Studio) branding on top of upstream DeckCraft.

Only user-visible text is rebranded; crate names, the file format and other internals keep their
upstream names so `git merge upstream/main` stays easy. The script is idempotent: after merging
upstream, resolve any conflicts in favour of upstream and run it again.

    python3 studio/rebrand.py
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = '3urood'
REPO = 'https://github.com/7mz410/CreativeStudio-3urood'
SITE = 'https://studio.creative.ps'
APP_SITE = 'https://3urood.studio.creative.ps'
# Persisted names and legal lines; renaming them would lose settings or misstate copyright.
KEEP = ('by the ArtCraft team', 'Application Support/DeckCraft', '/roaming/DeckCraft', 'the DeckCraft authors', 'DeckCraft contributors', 'DECKCRAFT_')

# (file, upstream text, our text[, marker meaning "already applied"]). The upstream text may also
# be found in its renamed form (after the general rename below).
RULES = [
    # Links: our site and repo. DISCORD stays defined (CLI, MCP) but nothing in the window shows it.
    ('crates/engine/src/links.rs', 'pub const WEBSITE: &str = "https://getartcraft.com/";', f'pub const WEBSITE: &str = "{SITE}/";'),
    ('crates/engine/src/links.rs', 'pub const APPS: &str = "https://getartcraft.com/apps";', f'pub const APPS: &str = "{SITE}";'),
    ('crates/engine/src/links.rs', 'pub const APP_PAGE: &str = "https://getartcraft.com/apps/deckcraft";', f'pub const APP_PAGE: &str = "{APP_SITE}";'),
    ('crates/engine/src/links.rs', 'pub const GITHUB: &str = "https://github.com/storytold/deckcraft";', f'pub const GITHUB: &str = "{REPO}";'),
    ('crates/engine/src/links.rs', 'pub const ISSUES: &str = "https://github.com/storytold/deckcraft/issues";', f'pub const ISSUES: &str = "{REPO}/issues";'),
    # The mark: the 3urood star (studio_mark.rs, generated from docs/studio/3urood.svg).
    ('crates/ui-egui/Cargo.toml', 'egui = { workspace = true }\n', 'egui = { workspace = true }\nvello_cpu = { workspace = true }\n', 'vello_cpu'),
    ('crates/ui-egui/src/lib.rs', 'pub mod canvas;\n', 'pub mod canvas;\npub mod studio_mark;\n', 'pub mod studio_mark;'),
    ('crates/ui-egui/src/dialogs.rs', """    let orange = Color32::from_rgb(0xF2, 0x6B, 0x1D);
    let deep = Color32::from_rgb(0xC2, 0x4E, 0x14);
    let card = r.shrink(r.width() * 0.08);
    p.rect_filled(card.translate(vec2(r.width() * 0.04, r.width() * 0.05)), CornerRadius::same((r.width() * 0.14) as u8), deep);
    p.rect_filled(card, CornerRadius::same((r.width() * 0.14) as u8), orange);
    let c = card.center();
    let s = card.width() * 0.22;
    p.add(egui::Shape::convex_polygon(
        vec![pos2(c.x - s * 0.7, c.y - s), pos2(c.x + s, c.y), pos2(c.x - s * 0.7, c.y + s)],
        Color32::WHITE,
        Stroke::NONE,
    ));
""", """    // Creative Studio: the 3urood star.
    crate::studio_mark::paint(p, r);
"""),
    ('crates/ui-egui/src/dialogs.rs', 'use egui::{Align2, Color32, CornerRadius, Rect, Sense, Stroke, Ui, pos2, vec2};', 'use egui::{Align2, CornerRadius, Rect, Sense, Stroke, Ui, pos2, vec2};'),
    # About and start screen: our links, no Discord.
    ('crates/ui-egui/src/dialogs.rs', '        ui.hyperlink_to("Join our community on Discord", deckcraft_engine::links::DISCORD);\n', ''),
    ('crates/ui-egui/src/dialogs.rs', 'ui.hyperlink_to("getartcraft.com/apps/deckcraft", deckcraft_engine::links::APP_PAGE);', 'ui.hyperlink_to("3urood.studio.creative.ps", deckcraft_engine::links::APP_PAGE);'),
    ('crates/ui-egui/src/dialogs.rs', '"Presentations and slide shows, rebuilt from scratch in pure Rust."', '"Presentations and slide shows, part of the Creative Studio suite. Built on DeckCraft by the ArtCraft team."'),
    ('crates/ui-egui/src/dialogs.rs', 'ui.hyperlink_to("Join the ArtCraft community on Discord", deckcraft_engine::links::DISCORD);', 'ui.hyperlink_to("Creative Studio", deckcraft_engine::links::WEBSITE);'),
    # Web page and packages.
    ('apps/deckcraft-web/index.html', '<title>DeckCraft</title>', f'<title>{NAME}</title>'),
    ('apps/deckcraft-web/index.html', 'Loading DeckCraft&hellip;', f'Loading {NAME}&hellip;', 'ss-scene'),  # or the splash
    ('packaging/macos/Info.plist.in', '<string>ai.storyteller.deckcraft</string>', '<string>ps.creative.studio.3urood</string>'),
    ('packaging/windows/deckcraft.wxs', '<Property Id="ARPURLINFOABOUT" Value="https://getartcraft.com/apps/deckcraft" />', f'<Property Id="ARPURLINFOABOUT" Value="{APP_SITE}" />'),
    ('packaging/windows/deckcraft.wxs', '<Property Id="ARPURLUPDATEINFO" Value="https://getartcraft.com/apps/deckcraft" />', f'<Property Id="ARPURLUPDATEINFO" Value="{REPO}/releases" />'),
    ('packaging/windows/deckcraft.wxs', '<Property Id="ARPHELPLINK" Value="https://discord.gg/artcraft" />', f'<Property Id="ARPHELPLINK" Value="{REPO}/issues" />'),
    ('packaging/linux/nfpm.yaml', 'homepage: https://getartcraft.com/apps/deckcraft', f'homepage: {APP_SITE}'),
]
# Text in string literals and catalogs, before the general rename.
LITERALS = []
STRING = re.compile(r'"(?:[^"\\\n]|\\.)*"')


def rename(lit: str) -> str:
    for a, b in LITERALS:
        lit = lit.replace(a, b)
    if any(k in lit for k in KEEP):
        return lit
    return lit.replace('DeckCraft', NAME)


def renamed_code(text: str) -> str:
    return STRING.sub(lambda m: rename(m.group(0)), text)


def apply_rules() -> list:
    changed = []
    for rel, a, b, *marker in RULES:
        p = ROOT / rel
        s = p.read_text(encoding='utf-8')
        if marker and marker[0] in s:
            continue
        if a not in s and renamed_code(a) in s:
            a = renamed_code(a)  # the general rename got there first
        if a not in s or (b and a in b and b in s):
            if not b or b in s or renamed_code(b) in s:
                continue  # already applied
            print(f'warning: {rel}: upstream text not found (did upstream change it?): {a[:70]!r}')
            continue
        p.write_text(s.replace(a, b), encoding='utf-8')
        changed.append(rel)
    return changed


def rename_sources() -> list:
    changed = []
    for p in sorted((ROOT / 'crates/ui-egui').rglob('*.rs')) + [q for q in sorted((ROOT / 'crates/engine').rglob('*.rs')) if not q.name.startswith('tests')] + sorted((ROOT / 'apps').rglob('*.rs')):
        s = p.read_text(encoding='utf-8')
        o = renamed_code(s)
        if o != s:
            p.write_text(o, encoding='utf-8')
            changed.append(p.relative_to(ROOT).as_posix())
    # Catalog rows are `context<TAB>English<TAB>translation`: rename both text columns alike.
    for p in sorted((ROOT / 'crates/ui-egui/src/i18n').glob('*.tsv')):
        s = p.read_text(encoding='utf-8')
        rows = []
        for line in s.split('\n'):
            cells = line.split('\t')
            if len(cells) >= 3 and not line.startswith('#'):
                line = '\t'.join([cells[0], *(rename(c) for c in cells[1:])])
            rows.append(line)
        o = '\n'.join(rows)
        if o != s:
            p.write_text(o, encoding='utf-8')
            changed.append(p.relative_to(ROOT).as_posix())
    plist = ROOT / 'packaging/macos/Info.plist.in'
    s = plist.read_text(encoding='utf-8')
    o = re.sub(r'(<key>CFBundle(?:Display|Executable)?Name</key>\s*<string>)DeckCraft(</string>)', rf'\g<1>{NAME}\2', s)
    if o != s:
        plist.write_text(o, encoding='utf-8')
        changed.append('packaging/macos/Info.plist.in')
    return changed


def write_mark() -> bool:
    svg = (ROOT / f'docs/studio/{NAME}.svg').read_text(encoding='utf-8')
    _, _, w, h = (float(x) for x in re.search(r'viewBox="([^"]+)"', svg).group(1).split())
    fills = dict(re.findall(r'\.(cls-\d+)\s*\{\s*fill:\s*#([0-9a-fA-F]{6})', svg))
    rows = []
    for attrs in re.findall(r'<path\b([^>]*)>', svg):
        cls = re.search(r'class="(cls-\d+)"', attrs)
        c = fills.get(cls.group(1), 'eb1b3c') if cls else 'eb1b3c'
        d = re.search(r'\bd="([^"]+)"', attrs).group(1)
        rgb = ', '.join(str(int(c[i:i + 2], 16)) for i in (0, 2, 4))
        rows.append(f'    ("{d}", [{rgb}]),')
    out = f"""//! Creative Studio: the {NAME} star (docs/studio/{NAME}.svg), generated by studio/rebrand.py.

use vello_cpu::{{kurbo, peniko}};

/// The artwork size (its viewBox).
pub const SIZE: (f64, f64) = ({w}, {h});

/// SVG path data and fill colour, painted in order.
pub const PATHS: &[(&str, [u8; 3])] = &[
""" + '\n'.join(rows) + """
];

/// Paint the star into `r` (centred, square), rasterised once per size and cached.
pub fn paint(p: &egui::Painter, r: egui::Rect) {
    let ctx = p.ctx();
    let px = ((r.width().min(r.height()) * ctx.pixels_per_point()).round() as u32).clamp(8, 1024);
    let key = egui::Id::new(("studio_mark", px));
    let tex: Option<egui::TextureHandle> = ctx.data(|d| d.get_temp(key));
    let tex = tex.unwrap_or_else(|| {
        let mut rc = vello_cpu::RenderContext::new(px as u16, px as u16);
        let (w, h) = SIZE;
        let k = px as f64 / w.max(h);
        rc.set_transform(kurbo::Affine::scale(k) * kurbo::Affine::translate(((h - w).max(0.0) / 2.0, (w - h).max(0.0) / 2.0)));
        for (d, [cr, cg, cb]) in PATHS {
            rc.set_paint(peniko::Color::from_rgba8(*cr, *cg, *cb, 255));
            if let Ok(path) = kurbo::BezPath::from_svg(d) {
                rc.fill_path(&path);
            }
        }
        rc.flush();
        let mut pm = vello_cpu::Pixmap::new(px as u16, px as u16);
        let mut res = vello_cpu::Resources::new();\n        rc.render(&mut pm, &mut res);
        let img = egui::ColorImage::from_rgba_premultiplied([px as usize, px as usize], pm.data_as_u8_slice());
        let t = ctx.load_texture("studio_mark", img, egui::TextureOptions::LINEAR);
        ctx.data_mut(|d| d.insert_temp(key, t.clone()));
        t
    });
    let side = r.width().min(r.height());
    let r = egui::Rect::from_center_size(r.center(), egui::vec2(side, side));
    p.image(tex.id(), r, egui::Rect::from_min_max(egui::pos2(0.0, 0.0), egui::pos2(1.0, 1.0)), egui::Color32::WHITE);
}
"""
    f = ROOT / 'crates/ui-egui/src/studio_mark.rs'
    out = subprocess.run(['rustfmt', '--edition', '2024', '--emit', 'stdout', '--config-path', str(ROOT)], input=out, capture_output=True, text=True).stdout or out
    if f.exists() and f.read_text(encoding='utf-8') == out:
        return False
    f.write_text(out, encoding='utf-8')
    return True


def main():
    changed = apply_rules() + rename_sources()
    if write_mark():
        changed.append('crates/ui-egui/src/studio_mark.rs')
    for c in sorted(set(changed)):
        print('rebranded', c)


# Creative Studio: the macOS app folder in the .dmg and the volume name carry our name
# (packaging/macos/package.sh). Bundle and binary names inside the package stay as upstream has them.
PACKAGING_NAMES = {
    'packaging/macos/package.sh': [
        ('DeckCraft.app', '3urood.app'),
        ('-volname "DeckCraft"', '-volname "3urood"'),
        ('-hfs-volume-name "DeckCraft"', '-hfs-volume-name "3urood"'),
    ],
}


def apply_packaging_names() -> list:
    changed = []
    for rel, pairs in PACKAGING_NAMES.items():
        path = ROOT / rel
        src = path.read_text(encoding='utf-8')
        out = src
        for a, b in pairs:
            out = out.replace(a, b)
        if out != src:
            path.write_text(out, encoding='utf-8')
            changed.append(path)
    return changed


if __name__ == '__main__':
    main()
    for _p in apply_packaging_names():
        print('rebranded', _p.relative_to(ROOT))
