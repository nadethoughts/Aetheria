from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parent
PORTRAITS = ROOT / "portraits"
PACKET = ROOT / "Session 08 - Temporary Player Characters - Complete Packet.pdf"

PAGE_W, PAGE_H = A4
INK = HexColor("#18212A")
MID = HexColor("#415364")
ICE = HexColor("#DCEAF2")
PALE = HexColor("#F3F7F9")
GOLD = HexColor("#D9A441")
GREEN = HexColor("#4D7B69")
BLUE = HexColor("#39749B")
RED = HexColor("#9B554C")
LINE = HexColor("#B7C4CC")


BODY = ParagraphStyle(
    "body",
    fontName="Helvetica",
    fontSize=10.2,
    leading=12.6,
    textColor=INK,
    alignment=TA_LEFT,
    allowWidows=0,
    allowOrphans=0,
)
SMALL_BODY = ParagraphStyle(
    "small-body",
    parent=BODY,
    fontSize=9.0,
    leading=11.0,
)
TAG = ParagraphStyle(
    "tag",
    parent=BODY,
    fontName="Helvetica-BoldOblique",
    fontSize=9.4,
    leading=11.2,
    textColor=MID,
    spaceAfter=4,
)
TITLE = ParagraphStyle(
    "title",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=11.6,
    leading=13.5,
    textColor=INK,
)
SHEET_BODY = ParagraphStyle(
    "sheet-body",
    parent=BODY,
    fontSize=8.7,
    leading=10.5,
)
SHEET_TAG = ParagraphStyle(
    "sheet-tag",
    parent=TAG,
    fontSize=8.2,
    leading=9.7,
)


COMMON_PAGE_2 = [
    {
        "title": "YOUR TURN",
        "tag": "3 ACTIONS · 1 FREE SIMPLE TASK OR SHORT PHRASE",
        "bullets": [
            "Spend 1 action to Move up to Speed, attack, Assess, or use an ability unless it says otherwise.",
            "Your second attack has disadvantage. Each later attack adds another disadvantage die.",
        ],
        "accent": BLUE,
    },
    {
        "title": "ATTACK ROLL",
        "tag": "PRIMARY DIE: 1 MISSES · MAXIMUM CRITS",
        "bullets": [
            "On a crit, roll the Primary Die again and add it. Repeat whenever that die rolls its maximum.",
            "A ranged attack has disadvantage while an enemy is adjacent.",
        ],
        "accent": RED,
    },
    {
        "title": "ASSESS",
        "tag": "1 ACTION · DC 10 · DO NOT REUSE A SKILL THIS ENCOUNTER",
        "bullets": [
            "Ask one honest question; or",
            "Create an Opening: +1 to the next Primary Die against the target this round; or",
            "Anticipate Danger: -1 to Primary Dice against you this round.",
        ],
        "accent": GOLD,
    },
    {
        "title": "REACTIONS",
        "tag": "COST 1 ACTION FROM YOUR NEXT TURN · EACH 1/ROUND",
        "bullets": [
            "Defend: reduce one attack's damage by Armor.",
            "Interpose: replace a nearby ally as the target.",
            "Opportunity Attack: melee attack with disadvantage when an adjacent enemy willingly leaves.",
            "Help: explain how; an ally rerolls. Only one Help per roll.",
        ],
        "accent": GREEN,
    },
    {
        "title": "MOVEMENT & TERRAIN",
        "tag": "MOVE UP TO SPEED · DIFFICULT TERRAIN HALVES MOVEMENT",
        "bullets": [
            "Reach effects are not ranged and do not suffer adjacent-enemy disadvantage.",
            "Use the map fiction: ropes, cover, ledges, and flight can change what is possible.",
        ],
        "accent": BLUE,
    },
    {
        "title": "REST & RECOVERY",
        "tag": "FIELD REST SPENDS HIT DICE · SAFE REST REFILLS RESOURCES",
        "bullets": [
            "Catch Breath (10 minutes): each Hit Die heals its roll + STR.",
            "Make Camp (8 hours, food and water): each Hit Die heals its maximum + STR.",
            "Safe Rest: recover HP and resources and heal 1 Wound when the GM says it is available.",
        ],
        "accent": GREEN,
    },
]


CHARACTERS = {
    "Skritch": {
        "file": "Skritch - Level 3 Temporary PC.pdf",
        "subtitle": "LEVEL 3 KOBOLD CHEAT · TOOLS OF THE SCOUNDREL",
        "stats": "HP 21   ·   ARMOR 6   ·   SPEED 6   ·   INIT +2   ·   SAVE +DEX / -WIL",
        "portrait": "Skritch.png",
        "roleplay": [
            "You were the kobold Rowan spared near Clackston. The Black Fang later used you as a guide, forced you across unstable ice, then left you beneath it.",
            "<b>You want:</b> protection, revenge, and a future where kobolds are not Razor's disposable miners.",
            "<b>You still believe:</b> kobolds deserve territory; the Erie are not entitled to rule the mountains.",
            "<b>Opening line:</b> “The giant who sat on me. This is either very good luck or very bad luck.”",
        ],
        "quick": [
            "<b>Travel:</b> lead with Stealth +4, Finesse +3, or Examination +3.",
            "<b>Combat:</b> stay beside an ally's target so it is Distracted.",
            "<b>Hit in melee:</b> use Vicious Opportunist to turn the Primary Die into a crit.",
            "<b>Crit:</b> add Sneak Attack +1d8.",
            "<b>Danger:</b> Hide or Move free; use Wily if a dangerous attack hits you.",
        ],
        "sheet_left": [
            ("CHEAT", "FREE · 1/ROUND", ["Move or Hide for free. Initiative results below 10 become 10."]),
            ("WILY", "TRIGGER: A NON-CRITICAL ATTACK HITS · 1/ENCOUNTER", ["Force the attacker to reroll."]),
            ("SWEET TALK", "WHEN YOU FIRST MEET AN NPC", ["Advantage on Influence until you fail or meet again."]),
            ("WILY UNDERDOG", "TRIGGER: FAILED STR-RELATED ROLL · 1/SAFE REST", ["Reroll it using another stat."]),
        ],
        "sheet_right": [
            ("WEAPONS", "RAPIER 2D4+2 · DAGGER 1D4+2 · SLING 1D4+2", ["Sling: Range 12, Vicious. Dagger: Thrown 4."]),
            ("VICIOUS OPPORTUNIST", "TRIGGER: MELEE HIT VS DISTRACTED · 1/TURN", ["Set the Primary Die to any result. Maximum becomes a crit."]),
            ("SNEAK ATTACK", "TRIGGER: YOU CRIT · 1/TURN", ["Add +1d8 damage; this is not another attack."]),
            ("LOW BLOW", "WITH SNEAK ATTACK · +2 ACTIONS", ["STR save DC 12 or Incapacitated next turn; Taunted until you drop to 0 HP."]),
        ],
        "abilities": [
            ("VICIOUS OPPORTUNIST", "TRIGGER: MELEE HIT AGAINST A DISTRACTED TARGET · 1/TURN", ["Change the Primary Die to any result you choose.", "Choosing its maximum makes the hit a crit."]),
            ("DISTRACTED", "CHECK THIS BEFORE YOU ATTACK", ["A target is Distracted if adjacent to or Taunted by your ally, or unable to see you."]),
            ("SNEAK ATTACK", "TRIGGER: YOU CRIT · 1/TURN", ["Deal +1d8 damage. It is added to the attack, not a separate attack."]),
            ("LOW BLOW", "WHEN YOU SNEAK ATTACK · COST: 2 EXTRA ACTIONS", ["Target makes a STR save, DC 12.", "Fail: Incapacitated next turn.", "Save or fail: Taunted by you until you drop to 0 HP."]),
            ("CHEAT", "FREE MOVE OR HIDE 1/ROUND · 1/Safe Rest SKILL TRICK", ["Set one skill check to 12.", "Initiative below 10 becomes 10.", "Advantage at games, competitions, and wagers—if you are not caught."]),
            ("WILY", "TRIGGER: NON-CRITICAL ATTACK AGAINST YOU · 1/ENCOUNTER", ["Force the attacker to reroll.", "+3 Influence with friendly characters; advantage on dragon-related checks."]),
            ("SWEET TALK", "WHEN YOU FIRST MEET AN NPC", ["Advantage on Influence until you fail or meet again.", "Then disadvantage with them until you repair the relationship."]),
            ("WILY UNDERDOG", "TRIGGER: FAILED STR ATTACK, SAVE, OR MIGHT CHECK · 1/SAFE REST", ["Reroll and use another stat instead."]),
            ("HIDING", "1 ACTION · STEALTH DC 10 · NEED COVER", ["Full cover succeeds automatically.", "Hiding is not invisibility: what enemies can see still matters."]),
            ("KOBOLD & LANGUAGES", "SMALL · COMMON, DRACONIC, ORCISH, DWARVISH", ["Thieves' Cant is your secret language of rogues and scoundrels."]),
        ],
    },
    "Da Long": {
        "file": "Da Long - Level 3 Temporary PC.pdf",
        "subtitle": "LEVEL 3 ORC HUNTER · BEASTMASTER (LARGE COMPANION)",
        "stats": "HP 28   ·   ARMOR 5   ·   SPEED 6   ·   INIT +2   ·   SAVE +DEX / -INT",
        "portrait": "Da Long.png",
        "roleplay": [
            "You are a Cloud Seer scout and Quickfeather's bonded rider. The Black Fang shot you down while you watched their diplomatic column; Lil Chang revived you.",
            "<b>You want:</b> Frostvein support against Razor.",
            "<b>You admit:</b> you were spying on the delegation.",
            "<b>You cannot promise:</b> that the Erie will honor every Frostvein demand.",
            "<b>Your proof:</b> you and Quickfeather act when Frostvein lives are in danger.",
        ],
        "quick": [
            "<b>Before combat:</b> mark the most important enemy.",
            "<b>At range:</b> choose advantage from Hunter's Mark until you crit.",
            "<b>On a melee hit or ranged crit:</b> gain 1 Thrill.",
            "<b>At 2 Thrill:</b> unleash Go for the Throat.",
            "<b>Avalanche:</b> spend an action to command Quickfeather to carry, Grapple, track, or Help.",
        ],
        "sheet_left": [
            ("HUNTER'S MARK", "1 ACTION · VISIBLE QUARRY · LASTS 1 DAY", ["It cannot hide from you. Before each attack choose advantage or +3 damage."]),
            ("GAIN THRILL", "QUARRY DIES · MELEE HIT · RANGED CRIT", ["Unspent charges vanish after combat."]),
            ("ROLL & STRIKE", "1 ACTION · ONLY AT 0 THRILL", ["Move Speed toward quarry; if adjacent, make a free melee attack."]),
            ("RELENTLESS", "TRIGGER: WOULD DROP TO 0 HP · 1/SAFE REST", ["Set HP to 3 instead."]),
        ],
        "sheet_right": [
            ("WEAPONS", "SHORTBOW 1D6+2 · DAGGER 1D4+2", ["Shortbow Range 12. Dagger Thrown 4."]),
            ("GO FOR THE THROAT!", "2 THRILL + 2 ACTIONS · 1/ENCOUNTER", ["Quickfeather deals 1d12+12 ignoring Armor."]),
            ("ALPHA PROTECTOR", "TRIGGER: FIRST ATTACK AGAINST YOU EACH ROUND", ["Halve that attack's damage."]),
            ("PROTECT ME!", "TRIGGER: YOU GAIN A WOUND · 1/ENCOUNTER", ["Quickfeather moves you up to 12 spaces to safety."]),
        ],
        "abilities": [
            ("HUNTER'S MARK", "1 ACTION · VISIBLE QUARRY · LASTS 1 DAY", ["The quarry cannot hide from you.", "Before each attack, choose advantage or +3 damage."]),
            ("GAIN THRILL", "WHEN QUARRY DIES, YOU HIT IT IN MELEE, OR CRIT IT AT RANGE", ["Gain 1 Thrill charge.", "An ability that spends Thrill cannot generate it.", "Unspent charges vanish after combat."]),
            ("GO FOR THE THROAT!", "2 ACTIONS + 2 THRILL · 1/ENCOUNTER", ["Quickfeather deals 1d12+12 damage ignoring Armor.", "If this kills, deal half that damage to another creature within Reach 4."]),
            ("ROLL & STRIKE", "1 ACTION · ONLY WHILE YOU HAVE 0 THRILL", ["Move up to Speed toward your quarry.", "If you end adjacent, make a free melee attack."]),
            ("ALPHA PROTECTOR", "TRIGGER: FIRST ATTACK AGAINST YOU EACH ROUND", ["Quickfeather halves that attack's damage."]),
            ("PROTECT ME!", "TRIGGER: YOU GAIN A WOUND · 1/ENCOUNTER", ["Quickfeather moves you up to 12 spaces to safety."]),
            ("QUICKFEATHER", "ABSTRACT LARGE COMPANION · NO SEPARATE HP OR ACTIONS", ["At GM discretion: fly, carry riders, track by scent, Grapple, or Help.", "Spend 1 action to command a complex task.", "Companion attacks count as yours for Thrill."]),
            ("TRACKER'S INTUITION", "WHEN YOU READ TRACKS", ["Learn creatures involved, direction, key actions, and elapsed time."]),
            ("FORAGER & SURVIVALIST", "ADVANTAGE FINDING FOOD/WATER · RATIONS DO NOT RUN OUT", ["Advantage on poison saves.", "+1 maximum Hit Die: 4d8 total."]),
            ("ORC — RELENTLESS", "TRIGGER: WOULD DROP TO 0 HP · 1/SAFE REST", ["Set HP to level (3) instead.", "Languages: Common, Orcish, Draconic."]),
        ],
    },
    "Feng Rui": {
        "file": "Feng Rui - Level 3 Temporary PC.pdf",
        "subtitle": "LEVEL 3 ORC COMMANDER · CHAMPION OF THE BULWARK",
        "stats": "HP 34   ·   ARMOR 14   ·   SPEED 6   ·   INIT -1   ·   SAVE +STR / -DEX",
        "portrait": "Feng Rui.png",
        "roleplay": [
            "You command Frostvein's northern pass wardens.",
            "<b>Starting position:</b> neutrality and closed borders.",
            "<b>You resent:</b> Erie patrols and Cloud Seer riders crossing without permission.",
            "<b>You fear:</b> either coalition using Frostvein as a road.",
            "<b>You can agree if:</b> Frostvein commands its passes and foreign troops require An Yue's permission.",
        ],
        "quick": [
            "<b>Stay near Cai Lin:</b> your maximum Wounds rises from 6 to 9.",
            "<b>Open combat:</b> Coordinated Strike with the strongest ally.",
            "<b>Protect:</b> use Shield Expert before spending a reaction on Defend.",
            "<b>Ally falls:</b> Hold the Line restores them to 9 HP.",
            "<b>Rescue:</b> Reposition allies; use Might +5 for lifting and ropes.",
        ],
        "sheet_left": [
            ("SHIELD EXPERT", "TRIGGER: AN ATTACK DEALS DAMAGE · 1/ROUND", ["Reduce damage by shield Armor 4; deal 4 to an enemy within Reach."]),
            ("REPOSITION!", "1 ACTION · OR REACTION ON ALLY'S TURN", ["One ally moves Speed free, or two allies move half Speed."]),
            ("FIELD MEDIC", "POTION OR 10-MINUTE EXAMINATION", ["Add a potion die; allies add Examination +4 to Hit Die healing."]),
            ("DEVOTED PROTECTOR", "WHILE CAI LIN IS NEARBY", ["Max Wounds 9. When she takes a Wound, you take one."]),
        ],
        "sheet_right": [
            ("WEAPONS", "HAND AXE 1D6+2 · JAVELIN 1D6+2", ["Axe Thrown 4. Javelin Range 8."]),
            ("COORDINATED STRIKE!", "FREE · 2/SAFE REST · 1/ROUND", ["You and an ally within 6 each make a free weapon attack or cantrip."]),
            ("HOLD THE LINE!", "REACTION: ALLY DROPS TO 0 HP · 1/ENCOUNTER", ["Set that ally to 9 HP."]),
            ("ARMOR MASTER", "PASSIVE", ["Plate proficiency. Armor 14 = rusty plate 10 + shield 4."]),
        ],
        "abilities": [
            ("COORDINATED STRIKE!", "FREE ACTION · 2/SAFE REST · 1/ROUND", ["You and one ally within 6 each make a free weapon attack or cantrip."]),
            ("REPOSITION!", "1 ACTION · OR REACTION ON AN ALLY'S TURN", ["One ally moves up to Speed for free; or", "Two allies each move up to half Speed for free.", "Orders require speech."]),
            ("SHIELD EXPERT", "TRIGGER: ATTACK DEALS DAMAGE · 1/ROUND", ["Reduce the damage by your shield's Armor (4) without Defending.", "Then deal 4 damage to an enemy within Reach."]),
            ("HOLD THE LINE!", "REACTION: AN ALLY DROPS TO 0 HP · 1/ENCOUNTER", ["Set that ally to 9 HP."]),
            ("FIELD MEDIC", "WHEN YOU ADMINISTER A POTION OR EXAMINE WOUNDS", ["Add one die to potions you administer.", "After a 10-minute examination, allies add Examination +4 to HP recovered from Hit Dice."]),
            ("DEVOTED PROTECTOR — CAI LIN", "PASSIVE WHILE CAI LIN IS NEARBY", ["Maximum Wounds becomes 9 instead of 6.", "Whenever Cai Lin takes a Wound, you also take 1 Wound."]),
            ("ARMOR MASTER", "PASSIVE", ["You are proficient with plate.", "Armor 14 = rusty plate 10 + iron shield 4."]),
            ("ORC — RELENTLESS", "TRIGGER: WOULD DROP TO 0 HP · 1/SAFE REST", ["Set HP to level (3) instead.", "Languages: Common, Orcish, Draconic, Dwarvish."]),
            ("DYING", "AT 0 HP", ["Normally you have only 1 action.", "If you attack, make a DC 10 STR save afterward or gain a Wound."]),
        ],
    },
    "Cai Lin": {
        "file": "Cai Lin - Level 3 Temporary PC.pdf",
        "subtitle": "LEVEL 3 ORC SHEPHERD · LUMINARY OF MERCY",
        "stats": "HP 34   ·   ARMOR 10   ·   SPEED 6   ·   INIT -1   ·   MANA 9   ·   SAVE +WIL / -DEX",
        "portrait": "Cai Lin.png",
        "roleplay": [
            "You tend Frostvein's hearths and injured climbers.",
            "<b>Starting position:</b> Razor must be resisted before war reaches the settlement.",
            "<b>You resent:</b> generations of Erie condescension.",
            "<b>You fear:</b> neutrality survives only while Razor permits it.",
            "<b>You can agree if:</b> Cloud Seers and Lil Chang put Frostvein lives ahead of winning the debate.",
        ],
        "quick": [
            "<b>First round:</b> summon Lifebinding Spirit.",
            "<b>Routine healing:</b> use Heal or your spirit.",
            "<b>Dying ally:</b> use Searing Light; Merciful Healing doubles it.",
            "<b>Control:</b> use Entice to pull or Shadow Trap to punish an approach.",
            "<b>Negotiation:</b> calm anger or fear with Bond of Peace.",
        ],
        "sheet_left": [
            ("LIFEBINDING SPIRIT", "1 MANA · SUMMON; THEN 1 ACTION PER USE", ["Within Reach 4: heal 1d6+2 or deal 1d6+2 radiant ignoring Armor."]),
            ("HEAL", "1 ACTION · 1 MANA · REACH 1", ["Heal 1d6+2 HP."]),
            ("MERCIFUL HEALING", "TRIGGER: HEAL A DYING CREATURE", ["Double your healing. While Dying, your spirit acts free 1/round."]),
            ("RELENTLESS", "TRIGGER: WOULD DROP TO 0 HP · 1/SAFE REST", ["Set HP to 3 instead."]),
        ],
        "sheet_right": [
            ("SEARING LIGHT", "1 ACTION · REACH 6 · 2/SAFE REST", ["Heal a Dying creature 2d8; doubled by Merciful Healing."]),
            ("SHADOW TRAP", "2 ACTIONS · 1 MANA · ADJACENT SPACE", ["Next creature takes 3d12; Small/Tiny is Restrained while you concentrate."]),
            ("CANTRIPS", "NO MANA", ["Rebuke · True Strike · Entice · Withering Touch."]),
            ("SPELLCASTING", "SPEAK + FREE HAND/FOCUS · SAVE DC 12", ["Range spells have disadvantage while an enemy is adjacent."]),
        ],
        "abilities": [
            ("SEARING LIGHT", "1 ACTION · REACH 6 · 2/SAFE REST", ["Dying creature: heal 2d8; Merciful Healing doubles it.", "Or deal 2d8 radiant to undead or a Bloodied enemy."]),
            ("LIFEBINDING SPIRIT", "1 MANA TO SUMMON · 1 ACTION TO COMMAND · REACH 4", ["Heal 1d6+2; or deal 1d6+2 radiant ignoring Armor.", "It can heal once before vanishing.", "Its attack counts separately for rushed attacks, but it shares your 3 actions."]),
            ("HEAL", "1 ACTION · 1 MANA · REACH 1", ["Heal 1d6+2 HP."]),
            ("MERCIFUL HEALING", "TRIGGER: YOUR HEALING TARGET IS DYING", ["Double the healing.", "While you are Dying, your spirit can act free once each round."]),
            ("SHADOW TRAP", "2 ACTIONS · 1 MANA · ADJACENT SPACE", ["The next creature entering takes 3d12 damage.", "Small or Tiny targets are Restrained while you concentrate."]),
            ("REBUKE", "CANTRIP · 1 ACTION · REACH 4", ["Deal 1d6 radiant ignoring Armor; cannot miss.", "Double damage against undead or cowardly targets."]),
            ("TRUE STRIKE / ENTICE", "CANTRIPS · 1 ACTION", ["True Strike (Reach 2): advantage on target's next attack by end of next turn.", "Entice (Range 8): 1d4 ignoring Armor; on hit pull 2 spaces."]),
            ("WITHERING TOUCH", "CANTRIP · 1 ACTION · REACH 1", ["Deal 1d12 damage.", "On damage, target counts as undead for 1 round."]),
            ("BOND OF PEACE / GRAVECRAFT", "UTILITY MAGIC", ["Bond: simple telepathic feelings with a friendly visible creature, or advantage to calm anger/fear.", "Gravecraft: soil a surface, or spend 1 minute shaping a body-sized plot of earth."]),
            ("HEALER / HERBALIST", "WHEN PROFESSION APPLIES", ["Advantage on checks related to healing or herbs."]),
            ("ORC — RELENTLESS", "TRIGGER: WOULD DROP TO 0 HP · 1/SAFE REST", ["Set HP to level (3) instead."]),
        ],
    },
    "Jian Bo": {
        "file": "Jian Bo - Level 3 Temporary PC.pdf",
        "subtitle": "LEVEL 3 ORC BERSERKER · PATH OF THE MOUNTAINHEART",
        "stats": "HP 42   ·   ARMOR 1   ·   SPEED 6   ·   INIT +3   ·   SAVE +STR / -INT",
        "portrait": "Jian Bo.png",
        "roleplay": [
            "You keep Frostvein fed, equipped, and moving.",
            "<b>Starting position:</b> hear the Black Fang offer before choosing.",
            "<b>You resent:</b> Erie demands unsupported by food, metal, or labor.",
            "<b>You fear:</b> a long war that empties Frostvein stores.",
            "<b>You can agree if:</b> Lil Chang offers routes, supplies, and mutual defense—not honor alone.",
        ],
        "quick": [
            "<b>Rescue:</b> Might +6 makes you the rope anchor and heavy lifter.",
            "<b>First turn:</b> Rage, move, attack.",
            "<b>Later turns:</b> gain a Fury Die free; use actions to attack.",
            "<b>Defense:</b> save Fury Dice to reduce a major hit by 5–8 each.",
            "<b>Negotiation:</b> ask exactly what each side will deliver before winter.",
        ],
        "sheet_left": [
            ("RAGE", "1 ACTION · 1/TURN", ["Roll and set aside a d4 Fury Die. Add all Fury Dice to every STR attack. Max 2."]),
            ("INTENSIFYING FURY", "AT TURN START WHILE ALREADY RAGING", ["Gain 1 Fury Die for free."]),
            ("BLOODLUST", "ON YOUR TURN · EXPEND FURY", ["Move 2 spaces free per Fury Die spent."]),
            ("FEARLESS", "PASSIVE", ["Immune to Frightened; +1 Initiative; -1 Armor."]),
        ],
        "sheet_right": [
            ("WEAPONS", "GREATMAUL 1D12+2 · JAVELIN 1D6+2", ["Javelin Range 8. Add Fury Dice to STR attacks."]),
            ("THAT ALL YOU GOT?!", "TRIGGER: YOU ARE ATTACKED · EXPEND FURY", ["Reduce damage by 4 + the rolled value of each die spent."]),
            ("MOUNTAINOUS TENACITY", "WHEN SPENDING HIT DICE", ["For each 10 HP you would recover, you may heal 1 Wound instead."]),
            ("ONE WITH THE ANCIENTS", "1/SAFE REST", ["Ask which path is most dangerous or challenging."]),
        ],
        "abilities": [
            ("RAGE", "1 ACTION · 1/TURN", ["Roll a d4 Fury Die and set it aside.", "Add every Fury Die to every STR attack.", "Maximum 2 Fury Dice."]),
            ("INTENSIFYING FURY", "AT THE START OF YOUR TURN WHILE ALREADY RAGING", ["Gain 1 Fury Die for free."]),
            ("RAGE ENDS", "CHECK AT THE END OF EACH ROUND", ["It ends if you leave combat, drop to 0 HP, or spend a round without attacking or Raging."]),
            ("BLOODLUST", "ON YOUR TURN · EXPEND ONE OR MORE FURY DICE", ["Move 2 spaces for free per die spent."]),
            ("THAT ALL YOU GOT?!", "TRIGGER: YOU ARE ATTACKED · EXPEND FURY DICE", ["Each spent die reduces damage by 4 + that die's rolled value.", "Each d4 therefore prevents 5–8 damage."]),
            ("FURY & ARMOR", "WHEN YOU DAMAGE A FOE", ["Fury Dice remain dice when checking monster Armor.", "If replacing a maxed Fury Die, choose which die to keep."]),
            ("MOUNTAINOUS TENACITY", "WHEN YOU SPEND HIT DICE", ["For every 10 HP you would recover, you may heal 1 Wound instead."]),
            ("ONE WITH THE ANCIENTS", "1/SAFE REST", ["Ask which path is most dangerous or challenging."]),
            ("FEARLESS", "PASSIVE", ["Immune to Frightened.", "+1 Initiative and -1 Armor are already on the sheet."]),
            ("ORC — RELENTLESS", "TRIGGER: WOULD DROP TO 0 HP · 1/SAFE REST", ["Set HP to level (3) instead."]),
            ("DYING", "AT 0 HP", ["Normally only 1 action.", "If you attack, make a DC 10 STR save afterward or gain a Wound."]),
        ],
    },
    "Mei Rong": {
        "file": "Mei Rong - Level 3 Temporary PC.pdf",
        "subtitle": "LEVEL 3 ORC SONGWEAVER · HERALD OF COURAGE",
        "stats": "HP 26   ·   ARMOR 5   ·   SPEED 6   ·   INIT +1   ·   MANA 6   ·   INSPIRATION 4",
        "portrait": "Mei Rong.png",
        "roleplay": [
            "You preserve Frostvein's oral histories.",
            "<b>Starting position:</b> Razor is dangerous, but resisting him must not restore Erie rule.",
            "<b>You resent:</b> anyone dismissing real Erie wrongdoing because Razor is worse.",
            "<b>You can agree if:</b> Frostvein independence is recognized and its grievances receive a formal hearing.",
        ],
        "quick": [
            "<b>Negotiation:</b> lead with Influence +4, Insight +3, or Lore +3.",
            "<b>Important failure:</b> spend Inspiration so an ally rerolls.",
            "<b>Protect the group:</b> Inspiration also grants nearby allies 2 temp HP.",
            "<b>Control:</b> Ice Lance Slows; Mockery Taunts; Gale pushes.",
            "<b>Rescue:</b> Feather Fall stops a fall; Ice Disk carries injured people or supplies.",
        ],
        "sheet_left": [
            ("INSPIRATION", "FREE REACTION · 4/SAFE REST", ["Ally rerolls one attack/save die and keeps either result."]),
            ("INSPIRING PRESENCE", "WHEN YOU INSPIRE", ["Allies within 12 who hear you gain 2 temp HP."]),
            ("QUICK WIT", "ON INITIATIVE", ["Regain 2 spent Inspiration; unused regained uses expire after combat."]),
            ("BREATH OF LIFE", "CANTRIP · RANGE 6 · DYING ALLY", ["Heal 1d4; on a 4, also restore 1 action."]),
        ],
        "sheet_right": [
            ("VICIOUS MOCKERY", "1 ACTION · RANGE 12", ["1d4+1 psychic ignoring Armor; on hit Taunted next turn."]),
            ("RAZOR WIND", "1 ACTION · RANGE 12", ["1d4 slashing, Vicious. Choose advantage or damage an adjacent target too."]),
            ("ICE LANCE / SNOWBLIND", "1 ACTION", ["Ice Lance: Range 12, 1d6, Slowed. Snowblind: Reach 1, 1d6, Blinded."]),
            ("TIER 1 SPELLS", "1 MANA EACH", ["Blustery Gale · Frost Shield. Utilities: Feather Fall · Ice Disk."]),
        ],
        "abilities": [
            ("SONGWEAVER'S INSPIRATION", "FREE REACTION · ALLY ATTACK OR SAVE · 4/SAFE REST", ["The ally rerolls one die and keeps either result."]),
            ("INSPIRING PRESENCE", "TRIGGER: YOU INSPIRE", ["Allies within 12 who can hear you gain 2 temporary HP."]),
            ("QUICK WIT", "ON INITIATIVE", ["Regain 2 spent Inspiration.", "Unused regained uses expire after combat."]),
            ("VICIOUS MOCKERY", "CANTRIP · 1 ACTION · RANGE 12", ["1d4+1 psychic damage ignoring Armor.", "On hit, target is Taunted next turn."]),
            ("RAZOR WIND", "CANTRIP · 1 ACTION · RANGE 12", ["1d4 slashing, Vicious.", "Choose advantage or also damage one target adjacent to the first."]),
            ("ICE LANCE / SNOWBLIND", "CANTRIPS · 1 ACTION", ["Ice Lance (Range 12): 1d6 cold/piercing; on hit Slowed.", "Snowblind (Reach 1): 1d6; on hit Blinded through target's next turn."]),
            ("BREATH OF LIFE", "CANTRIP · 1 ACTION · RANGE 6 · DYING ALLY", ["Heal 1d4 HP.", "If the die shows 4, the ally also regains 1 action."]),
            ("BLUSTERY GALE", "2 ACTIONS · 1 MANA · RANGE 12", ["3d4 bludgeoning; advantage vs flying, Small, or Tiny.", "On hit push: Medium 2, Small/Tiny 4, Large 1."]),
            ("FROST SHIELD", "1 ACTION · 1 MANA; THEN REACTION WHEN ATTACKED", ["Gain 4 temp HP and Defend for free.", "Temp HP vanish at the start of your next turn."]),
            ("FEATHER FALL / ICE DISK", "UTILITY MAGIC", ["Feather Fall: reaction, Reach 6; falling target lands safely.", "Ice Disk: 1 minute; carries 250 lb for 1 hour."]),
            ("HISTORY BUFF / SONG OF REST", "PASSIVE · SONG 1/SAFE REST", ["Advantage on Lore about events or items over 100 years old.", "During a Field Rest, creatures spending Hit Dice heal +2 HP."]),
            ("ORC — RELENTLESS", "TRIGGER: WOULD DROP TO 0 HP · 1/SAFE REST", ["Set HP to level (3) instead."]),
        ],
    },
}


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("–", "&#8211;")
        .replace("—", "&#8212;")
    )


def rich(text: str) -> str:
    """Escape prose while preserving the small, trusted emphasis tags in our data."""
    return (
        esc(text)
        .replace("&lt;b&gt;", "<b>")
        .replace("&lt;/b&gt;", "</b>")
        .replace("&lt;i&gt;", "<i>")
        .replace("&lt;/i&gt;", "</i>")
    )


def draw_paragraph(c, text, style, x, y_top, width):
    p = Paragraph(text, style)
    _, height = p.wrap(width, PAGE_H)
    p.drawOn(c, x, y_top - height)
    return height


def card_height(title, tag, bullets, width, compact=False):
    pad = 9 if compact else 11
    title_style = TITLE if not compact else ParagraphStyle("sheet-title", parent=TITLE, fontSize=9.5, leading=11)
    tag_style = TAG if not compact else SHEET_TAG
    body_style = BODY if not compact else SHEET_BODY
    h = pad
    for text, style in [(esc(title), title_style), (f"<b><i>{esc(tag)}</i></b>", tag_style)]:
        p = Paragraph(text, style)
        _, ph = p.wrap(width - 2 * pad, PAGE_H)
        h += ph + 2
    bullet_html = "<br/>".join(f"&#8226;&nbsp; {rich(b)}" for b in bullets)
    p = Paragraph(bullet_html, body_style)
    _, ph = p.wrap(width - 2 * pad, PAGE_H)
    return h + ph + pad


def draw_card(c, x, y_top, width, title, tag, bullets, accent=BLUE, compact=False):
    height = card_height(title, tag, bullets, width, compact)
    radius = 7 if not compact else 5
    c.setFillColor(white)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.roundRect(x, y_top - height, width, height, radius, fill=1, stroke=1)
    c.setFillColor(accent)
    c.roundRect(x, y_top - height, 5, height, radius, fill=1, stroke=0)
    pad = 9 if compact else 11
    yy = y_top - pad
    title_style = TITLE if not compact else ParagraphStyle("sheet-title", parent=TITLE, fontSize=9.5, leading=11)
    tag_style = TAG if not compact else SHEET_TAG
    body_style = BODY if not compact else SHEET_BODY
    yy -= draw_paragraph(c, esc(title), title_style, x + pad, yy, width - 2 * pad) + 2
    yy -= draw_paragraph(c, f"<b><i>{esc(tag)}</i></b>", tag_style, x + pad, yy, width - 2 * pad) + 3
    bullet_html = "<br/>".join(f"&#8226;&nbsp; {rich(b)}" for b in bullets)
    draw_paragraph(c, bullet_html, body_style, x + pad, yy, width - 2 * pad)
    return height


def draw_page_header(c, name, subtitle, stats, page_label):
    c.setFillColor(INK)
    c.rect(0, PAGE_H - 64, PAGE_W, 64, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(34, PAGE_H - 29, name.upper())
    c.setFont("Helvetica-Bold", 10)
    c.drawString(34, PAGE_H - 47, subtitle)
    c.setFillColor(ICE)
    c.setFont("Helvetica-Bold", 8.7)
    c.drawRightString(PAGE_W - 34, PAGE_H - 27, page_label)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10.3)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 82, stats)
    c.setStrokeColor(LINE)
    c.line(34, PAGE_H - 90, PAGE_W - 34, PAGE_H - 90)


def draw_roleplay_card(c, x, y_top, width, roleplay):
    return draw_card(
        c,
        x,
        y_top,
        width,
        "ROLEPLAY CARD",
        "WHAT YOU BELIEVE · WHAT CAN CHANGE YOUR MIND",
        roleplay,
        accent=GOLD,
    )


def draw_quick_card(c, x, y_top, width, quick):
    return draw_card(
        c,
        x,
        y_top,
        width,
        "QUICK START",
        "FOLLOW THESE IN ORDER WHEN YOU ARE UNSURE",
        quick,
        accent=GREEN,
    )


def draw_readable_pages(character):
    out = io.BytesIO()
    c = canvas.Canvas(out, pagesize=A4, pageCompression=1)
    margin = 34
    gutter = 12
    col_w = (PAGE_W - 2 * margin - gutter) / 2

    draw_page_header(c, character["name"], character["subtitle"], character["stats"], "PLAY GUIDE")
    top = PAGE_H - 106
    left_y = top
    right_y = top
    left_y -= draw_roleplay_card(c, margin, left_y, col_w, character["roleplay"]) + 10
    right_y -= draw_quick_card(c, margin + col_w + gutter, right_y, col_w, character["quick"]) + 10
    columns = [[margin, left_y], [margin + col_w + gutter, right_y]]
    for item in COMMON_PAGE_2:
        idx = 0 if columns[0][1] >= columns[1][1] else 1
        x, y = columns[idx]
        h = draw_card(c, x, y, col_w, item["title"], item["tag"], item["bullets"], item["accent"])
        columns[idx][1] -= h + 10
    c.setFillColor(MID)
    c.setFont("Helvetica-Oblique", 7.6)
    c.drawString(margin, 18, "Short cards preserve the controlling Nimble rule while keeping each decision visually separate.")
    c.drawRightString(PAGE_W - margin, 18, "Rules: local Nimble-Rules + later controlling errata")
    c.showPage()

    draw_page_header(c, character["name"], character["subtitle"], character["stats"], "ABILITY CARDS")
    columns = [[margin, PAGE_H - 106], [margin + col_w + gutter, PAGE_H - 106]]
    for title, tag, bullets in character["abilities"]:
        idx = 0 if columns[0][1] >= columns[1][1] else 1
        x, y = columns[idx]
        accent = GREEN if any(word in title for word in ("HEAL", "PROTECT", "SHIELD", "RELENTLESS")) else BLUE
        h = draw_card(c, x, y, col_w, title, tag, bullets, accent)
        columns[idx][1] -= h + 9
    c.setFillColor(MID)
    c.setFont("Helvetica-Oblique", 7.6)
    c.drawString(margin, 18, "Bold titles name the choice. Bold italics show the trigger, cost, range, or limit.")
    c.drawRightString(PAGE_W - margin, 18, "Ask the GM only when the fiction changes what is possible.")
    c.save()
    out.seek(0)
    return PdfReader(out)


def draw_portrait(c, image_path):
    cx, cy, radius = 81.5, 754.5, 65.0
    c.saveState()
    path = c.beginPath()
    path.circle(cx, cy, radius)
    c.clipPath(path, stroke=0, fill=0)
    c.drawImage(ImageReader(str(image_path)), cx - radius, cy - radius, 2 * radius, 2 * radius, mask="auto")
    c.restoreState()
    c.setStrokeColor(INK)
    c.setLineWidth(2.0)
    c.circle(cx, cy, radius, fill=0, stroke=1)


def draw_sheet_overlay(character):
    out = io.BytesIO()
    c = canvas.Canvas(out, pagesize=A4, pageCompression=1)
    draw_portrait(c, PORTRAITS / character["portrait"])

    panels = [
        (158, 35, 204, "REACTIONS & UTILITY", character["sheet_left"], GREEN),
        (374, 35, 204, "ACTIONS & ATTACKS", character["sheet_right"], BLUE),
    ]
    for x, bottom, width, heading, items, accent in panels:
        c.setFillColor(white)
        c.rect(x, bottom, width, 594, fill=1, stroke=0)
        c.setFillColor(INK)
        c.roundRect(x, 607, width, 20, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8.7)
        c.drawString(x + 9, 613, heading)
        y = 599
        for title, tag, bullets in items:
            h = draw_card(c, x, y, width, title, tag, bullets, accent=accent, compact=True)
            y -= h + 7
    c.setFillColor(MID)
    c.setFont("Helvetica-Oblique", 6.2)
    c.drawRightString(578, 12, "Large-print rules continue on the Play Guide and Ability Cards.")
    c.save()
    out.seek(0)
    return PdfReader(out).pages[0]


def build_one(name, character):
    character = dict(character)
    character["name"] = name
    target = ROOT / character["file"]
    original_bytes = target.read_bytes()
    base = PdfReader(io.BytesIO(original_bytes))
    first_page = base.pages[0]
    first_page.merge_page(draw_sheet_overlay(character))
    readable = draw_readable_pages(character)

    writer = PdfWriter()
    writer.add_page(first_page)
    writer.add_page(readable.pages[0])
    writer.add_page(readable.pages[1])
    writer.add_metadata(
        {
            "/Title": f"{name} - Level 3 Temporary PC",
            "/Subject": "Accessible three-page Nimble player handoff",
            "/Creator": "Codex using the local Nimble-Rules project",
        }
    )
    with target.open("wb") as handle:
        writer.write(handle)


def build_packet():
    writer = PdfWriter()
    for character in CHARACTERS.values():
        reader = PdfReader(str(ROOT / character["file"]))
        for page in reader.pages:
            writer.add_page(page)
    writer.add_metadata(
        {
            "/Title": "Session 08 - Temporary Player Characters - Complete Packet",
            "/Subject": "Six accessible level 3 Nimble character handoffs",
        }
    )
    with PACKET.open("wb") as handle:
        writer.write(handle)


if __name__ == "__main__":
    for character_name, character_data in CHARACTERS.items():
        build_one(character_name, character_data)
    build_packet()
    print(f"Built {len(CHARACTERS)} accessible three-page character PDFs and {PACKET.name}.")
