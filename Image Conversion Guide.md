---
tags: [meta, type/guide]
---

# Image Conversion Guide — WEBP

Use this list to **convert non-WEBP images to .webp** (e.g. with [Squoosh](https://squoosh.app), ImageMagick, or a batch script). After converting, save each file with the **Suggested .webp name** in the same folder as the original (or update the note’s path). All markdown references in the vault have been updated to use the .webp filename so links will work once the file exists.

---

## Already WEBP (no change)

These are already referenced as .webp: no conversion needed.

- `flaming-retrobution.webp`
- `Raythelion-logo-2.webp`, `Erabose-Logo.webp`, `Justicar-logo.webp`, `Cadens-Logo-1.webp`, deity symbols (Uhlvara, Zhurak, Dholgrym, Aelra, etc.)
- `Order-of-the-Blessed-realm.webp`, `order-of-the-dawnguard.webp`, `sentinels-of-equilibrium.webp`
- Character portraits under World/Characters (e.g. Gorvok, Hargrin, Kael, Bramli, etc.) — many already .webp
- Crown PC avatars: `alwor_thistlegift.Avatar.webp`, `Cahir.Avatar.webp`, `karsten.Avatar.webp`, `simear.Avatar.webp`
- Relics: `Beacon's Blade.webp`, `Heart of the Flame.webp`, `Infernal Breeze Gauntlets.webp`, `Mirror of Ashes.webp`

---

## Convert to WEBP (reference updated in vault)

| Original file (or path) | Suggested .webp name | Notes / file |
|--------------------------|----------------------|--------------|
| Hurgan Portrait.jpg | Hurgan Portrait.webp | World + Cracked Granite PCs |
| Demlor Portrait.jpg | Demlor Portrait.webp | World + Cracked Granite |
| Demlor Action.jpg | Demlor Action.webp | Cracked Granite |
| Hurgan Action.jpg | Hurgan Action.webp | Cracked Granite |
| Orc.png | Orc.webp | World/Species |
| Fredrick Wainshore.png | Fredrick Wainshore.webp | World + Anchor's Secret |
| Firewalker Goblin.png | Firewalker Goblin.webp | World/Species (path: img/Crown of the immortals/) |
| Gurlunk.png | Gurlunk.webp | World/Characters |
| Zibini.png | Zibini.png → Zibini.webp | World/Characters |
| Beastkin.png, Dwarf.png, Elf.png, Human.png, Kobold.png, Orc.png, Syderean.png, Smallfolk.png | Same base name .webp | World/Species/ToV Lineage Cards |
| Plate_Armor.png, +1_Warhammer.png, Dockbreaker's_Chain.png, etc. | Same base name .webp | Anchor's Secret Session Notes (item art) |
| Otyugh.png, Otyugh stat block.png | Otyugh.webp, Otyugh stat block.webp | Anchor's Secret/Enemies |
| Skirk.png, Arthur.png, Mistral.png, Xander.png, Lil John.jpeg | Same base name .webp | Anchor's Secret/Player Characters |
| Moon Knight Image.png, Moon Knight Stat block.png | Moon Knight Image.webp, Moon Knight Stat block.webp | Knight of Miraine |
| Animated Objects.png | Animated Objects.webp | Anchor's Secret/Enemies |
| Stormcaller cultist 1–3.png | Stormcaller cultist 1.webp, etc. | World + Anchor's Secret |
| Thrain Emberhelm.png | Thrain Emberhelm.webp | World/Characters |
| Ogre-Werewolf.jpg, Dwarven Watchtower.png, Ironhold.png, Ironhold Throne Room.jpg | Same base name .webp | Cracked Granite Session Notes |
| Vessan's Holy Symbol.png | Vessan's Holy Symbol.webp | World/Religion |
| Eldran's holy symbol.png | Eldran's holy symbol.webp | World/Religion |
| Serelle's holy symbol.png | Serelle's holy symbol.webp | World/Religion |
| Miraine Symbol.png | Miraine Symbol.webp | World/Religion |
| Thalyth.png, Veryic Thorne.png (typo: Veyric) | Thalyth.webp, Veyric Thorne.webp | World/Characters/New Penmaris |
| Iron Tide Regiment.png | Iron Tide Regiment.webp | World/Factions |
| Coral Bound 1.png, Coral Bound 2.png | Coral Bound 1.webp, Coral Bound 2.webp | World/Factions Pearlbound |
| solaris-sentinels.jpg | solaris-sentinels.webp | World/Factions (SS) |
| Acolyte.png, Cultist Fanatic.png, Knight.png | Same base name .webp | Anchor's Secret/Enemies |
| Zombie Statblocks.png | Zombie Statblocks.webp | Pearlbound |
| Giant Rat.png, Rat Swarm.png | Same base name .webp | Beasts of the Tidewatch Ward |
| sporeborn.png | sporeborn.webp | Miridine |
| Fog Monster.png, ToV-Invisible-Stalker.png, Steam Mephit Image.png, Steam Mephit Stat block.png | Same base name .webp | Fog Monster |
| Mimic Stat Block.png | Mimic Stat Block.webp | Anchor's Secret/Enemies |
| Jesrek.webp | (already webp; note: filename typo vs Jezrek) | Anchor's Secret |

---

## Batch conversion (optional)

From the vault root, if you have ImageMagick:

```bash
# Example: convert all .png in a folder to .webp (backup originals first)
magick mogrify -format webp -path ./output *.png
```

Or use Obsidian’s attachment folder and a tool like [Squoosh](https://squoosh.app) for bulk conversion, then rename to match the table above.

---

*After converting, delete or archive the old .png/.jpg/.jpeg files to avoid duplicate assets.*

---

## Manual link updates (if needed)

If a note still shows a .png/.jpg link, replace the extension with `.webp` to match the converted file (e.g. `Fredrick Wainshore.png` → `Fredrick Wainshore.webp` in **The Anchor's Secret/Player Primers/Session 01 - Enter the Ward.md**). Most World and campaign notes have already been updated to .webp references.
