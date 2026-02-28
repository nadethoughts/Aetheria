---
tags: [type/meta, meta]
---

# 📁 Obsidian Organization Guide — Aetheria Vault

Suggestions to keep your vault easy to navigate and consistent across campaigns.

---

## 1. Folder structure (current → suggested)

You already have a clear split: **World** (shared) vs **Campaigns** (Crown, Cracked Granite, Anchor's Secret, Warren's Want). No need to rename everything; small tweaks help.

| Area | Status |
|------|--------|
| **Root** | **Campaigns MOC.md**, **Adventure Progression & Brainstorm.md**, **Start Here.md** at root. |
| **World** | **World/World MOC.md** as the single entry point. |
| **Crown arcs** | Optional (manual): Rename to `1. The Light's Fall` and `2. Aftermath` when folders aren't locked; then update links in Campaigns MOC and AI Seeding Documents. |
| **Templates** | **Templates/** with Session Note, Adventure Outline, and NPC templates. |
---

## 2. Use MOCs as entry points

- **[[Campaigns MOC]]** — Open this when you’re planning or running any campaign.
- **[[World/World MOC]]** — Open when you need world lore (regions, gods, factions, species).
- **[[Adventure Progression & Brainstorm]]** — Open when planning future arcs or tying threads together.

Pin these in Obsidian’s sidebar or use a “Start here” note that links to all three.

---

## 3. Naming conventions

- **Locations:** `Region Name` or `Location Name` (e.g. `New Penmaris`, `Luakini o ka Manawa`).
- **Sessions:** Consistent pattern per campaign, e.g. `Session 01`, `Session 02` or `TCG - Session 01 - Transcription`.
- **Adventure docs:** One `Adventure.md` (or `Overview.md`) per arc so the MOC can point to a single “arc home” note.
- **Duplicates:** ✅ **Done.** **[[Flaming Retribution]]** is the canonical event note. **The-Flaming-Retribution.md** is a redirect that links to it so both link names resolve.

---

## 4. Tags

✅ **In use.** Frontmatter tags are on hub notes and key adventure/campaign notes. Add more as you go.

```yaml
---
tags: [campaign/crown, arc/ribbits-revenge, location, npc]
---
```

Suggested tag prefixes:

- `#campaign/crown` `#campaign/cracked-granite` `#campaign/anchor-secret`
- `#arc/aftermath` `#arc/ribbits-revenge`
- `#region/ironhold` `#region/verdant-strand`
- `#type/session` `#type/adventure` `#type/npc` `#type/location`
- `#thread/llano` `#thread/veilcant-guard` `#thread/giants`

Use **Tag pane** and **Search** (e.g. `tag:#campaign/crown`) to see everything for one campaign.

---

## 5. Templates

✅ **Implemented.** The **Templates/** folder contains:

- **Session Note.md** — Date, campaign, summary, NPCs, loot, hooks for next time. Uses `{{date}}` for Obsidian’s Templates plugin.
- **Adventure Outline.md** — Level band, location, themes, key NPCs, scenes (checkboxes), rewards.
- **NPC.md** — Name, role, location, faction, one-line, goals, relationships.

In Obsidian: **Settings → Core plugins → Templates** (enable), then **Settings → Templates** to set the template folder to `Templates`. Use **Insert template** (or your hotkey) when creating a new note.

---

## 6. Graph and backlinks

- **Local graph** from **World MOC** or **Campaigns MOC** to see how notes connect.
- **Backlinks** panel: see which sessions or adventures reference a given NPC, location, or faction.
- Exclude noisy folders (e.g. `Session Transcripts`) from the main graph if needed: **Settings → Graph → Filters**.

---

## 7. Quick summary (implemented)

1. ✅ **Enter the vault** → **Start Here** or **Campaigns MOC** or **World MOC**.
2. ✅ **Plan next adventures** → **Adventure Progression & Brainstorm**.
3. **Optional:** Manually rename Crown arc folders for consistent naming (see §1).
4. ✅ **Tags** on hub and key notes; use **Tag pane** and `tag:#campaign/crown` (etc.) to filter.
5. ✅ **One canonical note per concept** — Flaming Retribution: canonical + redirect in place.
6. ✅ **Templates** in `Templates/` for sessions, adventures, NPCs.
