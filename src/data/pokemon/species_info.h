#include "constants/abilities.h"
#include "constants/teaching_types.h"
#include "species_info/shared_dex_text.h"
#include "species_info/shared_front_pic_anims.h"

// Macros for ease of use.

#define EVOLUTION(...) (const struct Evolution[]) { __VA_ARGS__, { EVOLUTIONS_END }, }
#define CONDITIONS(...) ((const struct EvolutionParam[]) { __VA_ARGS__, {CONDITIONS_END} })

#define ANIM_FRAMES(...) (const union AnimCmd *const[]) { sAnim_GeneralFrame0, (const union AnimCmd[]) { __VA_ARGS__ ANIMCMD_END, }, }

#if P_FOOTPRINTS
#define FOOTPRINT(sprite) .footprint = gMonFootprint_## sprite,
#else
#define FOOTPRINT(sprite)
#endif

#if B_ENEMY_MON_SHADOW_STYLE >= GEN_4 && P_GBA_STYLE_SPECIES_GFX == FALSE
#define SHADOW(x, y, size)  .enemyShadowXOffset = x, .enemyShadowYOffset = y, .enemyShadowSize = size,
#define NO_SHADOW           .suppressEnemyShadow = TRUE,
#else
#define SHADOW(x, y, size)  .enemyShadowXOffset = 0, .enemyShadowYOffset = 0, .enemyShadowSize = 0,
#define NO_SHADOW           .suppressEnemyShadow = FALSE,
#endif

#define SIZE_32x32 1
#define SIZE_64x64 0

// Set .compressed = OW_GFX_COMPRESS
#define COMP OW_GFX_COMPRESS

#if OW_POKEMON_OBJECT_EVENTS
#if OW_PKMN_OBJECTS_SHARE_PALETTES == FALSE
#define OVERWORLD_PAL(...)                                  \
    .overworldPalette = DEFAULT(NULL, __VA_ARGS__),         \
    .overworldShinyPalette = DEFAULT_2(NULL, __VA_ARGS__),
#if P_GENDER_DIFFERENCES
#define OVERWORLD_PAL_FEMALE(...)                                 \
    .overworldPaletteFemale = DEFAULT(NULL, __VA_ARGS__),         \
    .overworldShinyPaletteFemale = DEFAULT_2(NULL, __VA_ARGS__),
#else
#define OVERWORLD_PAL_FEMALE(...)
#endif //P_GENDER_DIFFERENCES
#else
#define OVERWORLD_PAL(...)
#define OVERWORLD_PAL_FEMALE(...)
#endif //OW_PKMN_OBJECTS_SHARE_PALETTES == FALSE

#define OVERWORLD_DATA(picTable, _size, shadow, _tracks, _anims)                                                                     \
{                                                                                                                                       \
    .tileTag = TAG_NONE,                                                                                                                \
    .paletteTag = OBJ_EVENT_PAL_TAG_DYNAMIC,                                                                                            \
    .reflectionPaletteTag = OBJ_EVENT_PAL_TAG_NONE,                                                                                     \
    .size = (_size == SIZE_32x32 ? 512 : 2048),                                                                                         \
    .width = (_size == SIZE_32x32 ? 32 : 64),                                                                                           \
    .height = (_size == SIZE_32x32 ? 32 : 64),                                                                                          \
    .paletteSlot = PALSLOT_NPC_1,                                                                                                       \
    .shadowSize = shadow,                                                                                                               \
    .inanimate = FALSE,                                                                                                                 \
    .compressed = COMP,                                                                                                                 \
    .tracks = _tracks,                                                                                                                  \
    .oam = (_size == SIZE_32x32 ? &gObjectEventBaseOam_32x32 : &gObjectEventBaseOam_64x64),                                             \
    .subspriteTables = (_size == SIZE_32x32 ? sOamTables_32x32 : sOamTables_64x64),                                                     \
    .anims = _anims,                                                                                                                    \
    .images = picTable,                                                                                                                 \
}

#define OVERWORLD(objEventPic, _size, shadow, _tracks, _anims, ...)                                 \
    .overworldData = OVERWORLD_DATA(objEventPic, _size, shadow, _tracks, _anims),                   \
    OVERWORLD_PAL(__VA_ARGS__)

#if P_GENDER_DIFFERENCES
#define OVERWORLD_FEMALE(objEventPic, _size, shadow, _tracks, _anims, ...)                          \
    .overworldDataFemale = OVERWORLD_DATA(objEventPic, _size, shadow, _tracks, _anims),             \
    OVERWORLD_PAL_FEMALE(__VA_ARGS__)
#else
#define OVERWORLD_FEMALE(...)
#endif //P_GENDER_DIFFERENCES

#else
#define OVERWORLD(...)
#define OVERWORLD_FEMALE(...)
#define OVERWORLD_PAL(...)
#define OVERWORLD_PAL_FEMALE(...)
#endif //OW_POKEMON_OBJECT_EVENTS

// Maximum value for a female Pokémon is 254 (MON_FEMALE) which is 100% female.
// 255 (MON_GENDERLESS) is reserved for genderless Pokémon.
#define PERCENT_FEMALE(percent) min(254, ((percent * 255) / 100))

#define MON_TYPES(type1, ...) { type1, DEFAULT(type1, __VA_ARGS__) }
#define MON_EGG_GROUPS(group1, ...) { group1, DEFAULT(group1, __VA_ARGS__) }

#define FLIP    0
#define NO_FLIP 1

const struct SpeciesInfo gSpeciesInfo[] =
{
    [SPECIES_NONE] =
    {
        .speciesName = _("??????????"),
        .cryId = CRY_PORYGON,
        .natDexNum = NATIONAL_DEX_NONE,
        .categoryName = _("Unknown"),
        .height = 0,
        .weight = 0,
        .description = gFallbackPokedexText,
        .pokemonScale = 256,
        .pokemonOffset = 0,
        .trainerScale = 256,
        .trainerOffset = 0,
        .frontPic = gMonFrontPic_CircledQuestionMark,
        .frontPicSize = MON_COORDS_SIZE(40, 40),
        .frontPicYOffset = 12,
        .frontAnimFrames = sAnims_TwoFramePlaceHolder,
        .frontAnimId = ANIM_V_SQUISH_AND_BOUNCE,
        .backPic = gMonBackPic_CircledQuestionMark,
        .backPicSize = MON_COORDS_SIZE(40, 40),
        .backPicYOffset = 12,
        .backAnimId = BACK_ANIM_NONE,
        .palette = gMonPalette_CircledQuestionMark,
        .shinyPalette = gMonShinyPalette_CircledQuestionMark,
        .iconSprite = gMonIcon_QuestionMark,
        .iconPalIndex = 0,
        .pokemonJumpType = PKMN_JUMP_TYPE_NONE,
        FOOTPRINT(QuestionMark)
        SHADOW(-1, 0, SHADOW_SIZE_M)
    #if OW_POKEMON_OBJECT_EVENTS
        .overworldData = {
            .tileTag = TAG_NONE,
            .paletteTag = OBJ_EVENT_PAL_TAG_SUBSTITUTE,
            .reflectionPaletteTag = OBJ_EVENT_PAL_TAG_NONE,
            .size = 512,
            .width = 32,
            .height = 32,
            .paletteSlot = PALSLOT_NPC_1,
            .shadowSize = SHADOW_SIZE_M,
            .inanimate = FALSE,
            .compressed = COMP,
            .tracks = TRACKS_FOOT,
            .oam = &gObjectEventBaseOam_32x32,
            .subspriteTables = sOamTables_32x32,
            .anims = sAnimTable_Following,
            .images = sPicTable_Substitute,
        },
    #endif
        .levelUpLearnset = sNoneLevelUpLearnset,
        .teachableLearnset = sNoneTeachableLearnset,
        .eggMoveLearnset = sNoneEggMoveLearnset,
    },

    #include "species_info/gen_1_families.h"
    #include "species_info/gen_2_families.h"
    #include "species_info/gen_3_families.h"
    #include "species_info/gen_4_families.h"
    #include "species_info/gen_5_families.h"
    #include "species_info/gen_6_families.h"
    #include "species_info/gen_7_families.h"
    #include "species_info/gen_8_families.h"
    #include "species_info/gen_9_families.h"

    [SPECIES_EGG] =
    {
        .frontPic = gMonFrontPic_Egg,
        .frontPicSize = MON_COORDS_SIZE(24, 24),
        .frontPicYOffset = 20,
        .backPic = gMonFrontPic_Egg,
        .backPicSize = MON_COORDS_SIZE(24, 24),
        .backPicYOffset = 20,
        .palette = gMonPalette_Egg,
        .shinyPalette = gMonPalette_Egg,
        .iconSprite = gMonIcon_Egg,
        .iconPalIndex = 1,
    },

    /* You may add any custom species below this point based on the following structure: */

    /*
    [SPECIES_NONE] =
    {
        .baseHP        = 1,
        .baseAttack    = 1,
        .baseDefense   = 1,
        .baseSpeed     = 1,
        .baseSpAttack  = 1,
        .baseSpDefense = 1,
        .types = MON_TYPES(TYPE_MYSTERY),
        .catchRate = 255,
        .expYield = 67,
        .evYield_HP = 1,
        .evYield_Defense = 1,
        .evYield_SpDefense = 1,
        .genderRatio = PERCENT_FEMALE(50),
        .eggCycles = 20,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_FAST,
        .eggGroups = MON_EGG_GROUPS(EGG_GROUP_NO_EGGS_DISCOVERED),
        .abilities = { ABILITY_NONE, ABILITY_CURSED_BODY, ABILITY_DAMP },
        .bodyColor = BODY_COLOR_BLACK,
        .speciesName = _("??????????"),
        .cryId = CRY_NONE,
        .natDexNum = NATIONAL_DEX_NONE,
        .categoryName = _("Unknown"),
        .height = 0,
        .weight = 0,
        .description = COMPOUND_STRING(
            "This is a newly discovered Pokémon.\n"
            "It is currently under investigation.\n"
            "No detailed information is available\n"
            "at this time."),
        .pokemonScale = 256,
        .pokemonOffset = 0,
        .trainerScale = 256,
        .trainerOffset = 0,
        .frontPic = gMonFrontPic_CircledQuestionMark,
        .frontPicSize = MON_COORDS_SIZE(64, 64),
        .frontPicYOffset = 0,
        .frontAnimFrames = sAnims_None,
        //.frontAnimId = ANIM_V_SQUISH_AND_BOUNCE,
        .backPic = gMonBackPic_CircledQuestionMark,
        .backPicSize = MON_COORDS_SIZE(64, 64),
        .backPicYOffset = 7,
#if P_GENDER_DIFFERENCES
        .frontPicFemale = gMonFrontPic_CircledQuestionMark,
        .frontPicSizeFemale = MON_COORDS_SIZE(64, 64),
        .backPicFemale = gMonBackPic_CircledQuestionMarkF,
        .backPicSizeFemale = MON_COORDS_SIZE(64, 64),
        .paletteFemale = gMonPalette_CircledQuestionMarkF,
        .shinyPaletteFemale = gMonShinyPalette_CircledQuestionMarkF,
        .iconSpriteFemale = gMonIcon_QuestionMarkF,
        .iconPalIndexFemale = 1,
#endif //P_GENDER_DIFFERENCES
        .backAnimId = BACK_ANIM_NONE,
        .palette = gMonPalette_CircledQuestionMark,
        .shinyPalette = gMonShinyPalette_CircledQuestionMark,
        .iconSprite = gMonIcon_QuestionMark,
        .iconPalIndex = 0,
        FOOTPRINT(QuestionMark)
        .levelUpLearnset = sNoneLevelUpLearnset,
        .teachableLearnset = sNoneTeachableLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 100, SPECIES_NONE},
                                {EVO_ITEM, ITEM_MOOMOO_MILK, SPECIES_NONE}),
        //.formSpeciesIdTable = sNoneFormSpeciesIdTable,
        //.formChangeTable = sNoneFormChangeTable,
        //.perfectIVCount = NUM_STATS,
    },
    */

#if P_FAMILY_ASTRALIT
    [SPECIES_ASTRALIT] =
    {
        .baseHP        = 44,
        .baseAttack    = 52,
        .baseDefense   = 48,
        .baseSpeed     = 60,
        .baseSpAttack  = 70,
        .baseSpDefense = 65,
        .types = MON_TYPES(TYPE_PSYCHIC),
        .catchRate = 45,
        .expYield = 64,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_SLOW,
        .abilities = { ABILITY_ASTRAL_GLOW, ABILITY_NONE, ABILITY_ASTRAL_GLOW },
        .bodyColor = BODY_COLOR_PURPLE,
        .speciesName = _("Astralit"),
        .natDexNum = NATIONAL_DEX_ASTRALIT,
        .categoryName = _("Dawn Star"),
        .height = 6,
        .weight = 58,
        .description = COMPOUND_STRING(
            "A small cosmic spark that coaxes the\n"
            "night sky awake with a gentle glow."),
        .levelUpLearnset = sAstralitLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 18, SPECIES_ASTRALIT_AURORA}),
    },
    [SPECIES_ASTRALIT_AURORA] =
    {
        .baseHP        = 59,
        .baseAttack    = 65,
        .baseDefense   = 58,
        .baseSpeed     = 72,
        .baseSpAttack  = 88,
        .baseSpDefense = 82,
        .types = MON_TYPES(TYPE_PSYCHIC, TYPE_FAIRY),
        .catchRate = 45,
        .expYield = 126,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_SLOW,
        .abilities = { ABILITY_ASTRAL_GLOW, ABILITY_NONE, ABILITY_ASTRAL_GLOW },
        .bodyColor = BODY_COLOR_PINK,
        .speciesName = _("Astralit Aurora"),
        .natDexNum = NATIONAL_DEX_ASTRALIT_AURORA,
        .categoryName = _("Aurora Bloom"),
        .height = 12,
        .weight = 160,
        .description = COMPOUND_STRING(
            "It rides the first light of dawn,\n"
            "painting the horizon with warm stardust."),
        .levelUpLearnset = sAstralitAuroraLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 31, SPECIES_ASTRALIT_TIDE}),
    },
    [SPECIES_ASTRALIT_TIDE] =
    {
        .baseHP        = 74,
        .baseAttack    = 78,
        .baseDefense   = 69,
        .baseSpeed     = 80,
        .baseSpAttack  = 104,
        .baseSpDefense = 96,
        .types = MON_TYPES(TYPE_PSYCHIC, TYPE_WATER),
        .catchRate = 45,
        .expYield = 182,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_SLOW,
        .abilities = { ABILITY_ASTRAL_GLOW, ABILITY_NONE, ABILITY_ASTRAL_GLOW },
        .bodyColor = BODY_COLOR_BLUE,
        .speciesName = _("Astralit Tide"),
        .natDexNum = NATIONAL_DEX_ASTRALIT_TIDE,
        .categoryName = _("Wave Finder"),
        .height = 23,
        .weight = 560,
        .description = COMPOUND_STRING(
            "Its body mirrors the sea, trailing ribbons\n"
            "of reflected moonlight across the surf."),
        .levelUpLearnset = sAstralitTideLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 45, SPECIES_ASTRALIT_STORM}),
    },
    [SPECIES_ASTRALIT_STORM] =
    {
        .baseHP        = 90,
        .baseAttack    = 92,
        .baseDefense   = 82,
        .baseSpeed     = 94,
        .baseSpAttack  = 118,
        .baseSpDefense = 108,
        .types = MON_TYPES(TYPE_PSYCHIC, TYPE_ELECTRIC),
        .catchRate = 45,
        .expYield = 260,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_SLOW,
        .abilities = { ABILITY_ASTRAL_GLOW, ABILITY_NONE, ABILITY_ASTRAL_GLOW },
        .bodyColor = BODY_COLOR_YELLOW,
        .speciesName = _("Astralit Storm"),
        .natDexNum = NATIONAL_DEX_ASTRALIT_STORM,
        .categoryName = _("Skybreaker"),
        .height = 34,
        .weight = 920,
        .description = COMPOUND_STRING(
            "It gathers thunderheads into its body,\n"
            "turning every charge into a stormfront."),
        .levelUpLearnset = sAstralitStormLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 60, SPECIES_ASTRALIT_FINAL}),
    },
    [SPECIES_ASTRALIT_FINAL] =
    {
        .baseHP        = 104,
        .baseAttack    = 110,
        .baseDefense   = 96,
        .baseSpeed     = 110,
        .baseSpAttack  = 138,
        .baseSpDefense = 124,
        .types = MON_TYPES(TYPE_PSYCHIC, TYPE_DRAGON),
        .catchRate = 45,
        .expYield = 340,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_SLOW,
        .abilities = { ABILITY_ASTRAL_GLOW, ABILITY_NONE, ABILITY_ASTRAL_GLOW },
        .bodyColor = BODY_COLOR_PURPLE,
        .speciesName = _("Astralit Final"),
        .natDexNum = NATIONAL_DEX_ASTRALIT_FINAL,
        .categoryName = _("Celestial"),
        .height = 48,
        .weight = 1420,
        .description = COMPOUND_STRING(
            "The heavens answer its call, and every\n"
            "lightning bolt becomes a shining constellation."),
        .levelUpLearnset = sAstralitFinalLevelUpLearnset,
    },
#endif //P_FAMILY_ASTRALIT

#if P_FAMILY_FERROVALE
    [SPECIES_FERROVALE] =
    {
        .baseHP        = 46,
        .baseAttack    = 59,
        .baseDefense   = 62,
        .baseSpeed     = 48,
        .baseSpAttack  = 45,
        .baseSpDefense = 55,
        .types = MON_TYPES(TYPE_STEEL),
        .catchRate = 45,
        .expYield = 64,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_SLOW,
        .abilities = { ABILITY_FERRO_MIGHT, ABILITY_NONE, ABILITY_FERRO_MIGHT },
        .bodyColor = BODY_COLOR_GRAY,
        .speciesName = _("Ferrovale"),
        .natDexNum = NATIONAL_DEX_FERROVALE,
        .categoryName = _("Forge Pup"),
        .height = 7,
        .weight = 90,
        .description = COMPOUND_STRING(
            "It digs into volcanic soil and stores\n"
            "heat in its body before the sunrise."),
        .levelUpLearnset = sFerrovaleLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 18, SPECIES_FERROVALE_CINDER}),
    },
    [SPECIES_FERROVALE_CINDER] =
    {
        .baseHP        = 63,
        .baseAttack    = 76,
        .baseDefense   = 78,
        .baseSpeed     = 56,
        .baseSpAttack  = 62,
        .baseSpDefense = 70,
        .types = MON_TYPES(TYPE_STEEL, TYPE_FIRE),
        .catchRate = 45,
        .expYield = 126,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_SLOW,
        .abilities = { ABILITY_FERRO_MIGHT, ABILITY_NONE, ABILITY_FERRO_MIGHT },
        .bodyColor = BODY_COLOR_RED,
        .speciesName = _("Ferrovale Cinder"),
        .natDexNum = NATIONAL_DEX_FERROVALE_CINDER,
        .categoryName = _("Ember Brute"),
        .height = 15,
        .weight = 260,
        .description = COMPOUND_STRING(
            "Its shoulders radiate enough heat to\n"
            "soften stone with a single charge."),
        .levelUpLearnset = sFerrovaleCinderLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 31, SPECIES_FERROVALE_MARROW}),
    },
    [SPECIES_FERROVALE_MARROW] =
    {
        .baseHP        = 80,
        .baseAttack    = 92,
        .baseDefense   = 94,
        .baseSpeed     = 64,
        .baseSpAttack  = 82,
        .baseSpDefense = 88,
        .types = MON_TYPES(TYPE_STEEL, TYPE_GROUND),
        .catchRate = 45,
        .expYield = 182,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_SLOW,
        .abilities = { ABILITY_FERRO_MIGHT, ABILITY_NONE, ABILITY_FERRO_MIGHT },
        .bodyColor = BODY_COLOR_BROWN,
        .speciesName = _("Ferrovale Marrow"),
        .natDexNum = NATIONAL_DEX_FERROVALE_MARROW,
        .categoryName = _("Core Guard"),
        .height = 28,
        .weight = 760,
        .description = COMPOUND_STRING(
            "A heavy mantle of iron hardens around its\n"
            "body as it guards mountain passes."),
        .levelUpLearnset = sFerrovaleMarrowLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 46, SPECIES_FERROVALE_TITAN}),
    },
    [SPECIES_FERROVALE_TITAN] =
    {
        .baseHP        = 98,
        .baseAttack    = 112,
        .baseDefense   = 116,
        .baseSpeed     = 72,
        .baseSpAttack  = 98,
        .baseSpDefense = 104,
        .types = MON_TYPES(TYPE_STEEL, TYPE_ROCK),
        .catchRate = 45,
        .expYield = 260,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_SLOW,
        .abilities = { ABILITY_FERRO_MIGHT, ABILITY_NONE, ABILITY_FERRO_MIGHT },
        .bodyColor = BODY_COLOR_BLACK,
        .speciesName = _("Ferrovale Titan"),
        .natDexNum = NATIONAL_DEX_FERROVALE_TITAN,
        .categoryName = _("Mountain Breaker"),
        .height = 42,
        .weight = 1260,
        .description = COMPOUND_STRING(
            "Tremors follow it wherever it walks,\n"
            "lashing cracks through the bedrock below."),
        .levelUpLearnset = sFerrovaleTitanLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 60, SPECIES_FERROVALE_FINAL}),
    },
    [SPECIES_FERROVALE_FINAL] =
    {
        .baseHP        = 118,
        .baseAttack    = 136,
        .baseDefense   = 142,
        .baseSpeed     = 84,
        .baseSpAttack  = 116,
        .baseSpDefense = 126,
        .types = MON_TYPES(TYPE_STEEL, TYPE_FIRE),
        .catchRate = 45,
        .expYield = 340,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_SLOW,
        .abilities = { ABILITY_FERRO_MIGHT, ABILITY_NONE, ABILITY_FERRO_MIGHT },
        .bodyColor = BODY_COLOR_RED,
        .speciesName = _("Ferrovale Final"),
        .natDexNum = NATIONAL_DEX_FERROVALE_FINAL,
        .categoryName = _("Sunforge"),
        .height = 58,
        .weight = 1950,
        .description = COMPOUND_STRING(
            "Its body shines like a forgefire,\n"
            "and every strike can split a mountain in two."),
        .levelUpLearnset = sFerrovaleFinalLevelUpLearnset,
    },
#endif //P_FAMILY_FERROVALE

#if P_FAMILY_NIMBARA
    [SPECIES_NIMBARA] =
    {
        .baseHP        = 48,
        .baseAttack    = 52,
        .baseDefense   = 53,
        .baseSpeed     = 55,
        .baseSpAttack  = 66,
        .baseSpDefense = 62,
        .types = MON_TYPES(TYPE_GRASS),
        .catchRate = 45,
        .expYield = 64,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_FAST,
        .abilities = { ABILITY_NIMBARA_HUSH, ABILITY_NONE, ABILITY_NIMBARA_HUSH },
        .bodyColor = BODY_COLOR_GREEN,
        .speciesName = _("Nimbara"),
        .natDexNum = NATIONAL_DEX_NIMBARA,
        .categoryName = _("Canopy Seed"),
        .height = 6,
        .weight = 52,
        .description = COMPOUND_STRING(
            "It listens to the rustle of the leaves\n"
            "before opening its petals each morning."),
        .levelUpLearnset = sNimbaraLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 18, SPECIES_NIMBARA_LEAF}),
    },
    [SPECIES_NIMBARA_LEAF] =
    {
        .baseHP        = 69,
        .baseAttack    = 70,
        .baseDefense   = 72,
        .baseSpeed     = 68,
        .baseSpAttack  = 88,
        .baseSpDefense = 82,
        .types = MON_TYPES(TYPE_GRASS, TYPE_POISON),
        .catchRate = 45,
        .expYield = 126,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_FAST,
        .abilities = { ABILITY_NIMBARA_HUSH, ABILITY_NONE, ABILITY_NIMBARA_HUSH },
        .bodyColor = BODY_COLOR_GREEN,
        .speciesName = _("Nimbara Leaf"),
        .natDexNum = NATIONAL_DEX_NIMBARA_LEAF,
        .categoryName = _("Blooming Vine"),
        .height = 14,
        .weight = 162,
        .description = COMPOUND_STRING(
            "Its fragrance lures bugs in close,\n"
            "then softens their escape with thorny leaves."),
        .levelUpLearnset = sNimbaraLeafLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 31, SPECIES_NIMBARA_BLOOM}),
    },
    [SPECIES_NIMBARA_BLOOM] =
    {
        .baseHP        = 86,
        .baseAttack    = 89,
        .baseDefense   = 86,
        .baseSpeed     = 78,
        .baseSpAttack  = 110,
        .baseSpDefense = 98,
        .types = MON_TYPES(TYPE_GRASS, TYPE_FAIRY),
        .catchRate = 45,
        .expYield = 182,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_FAST,
        .abilities = { ABILITY_NIMBARA_HUSH, ABILITY_NONE, ABILITY_NIMBARA_HUSH },
        .bodyColor = BODY_COLOR_PINK,
        .speciesName = _("Nimbara Bloom"),
        .natDexNum = NATIONAL_DEX_NIMBARA_BLOOM,
        .categoryName = _("Mist Petal"),
        .height = 25,
        .weight = 520,
        .description = COMPOUND_STRING(
            "Every bloom smells like rain on warm stone,\n"
            "and the air fogs with pollen at dusk."),
        .levelUpLearnset = sNimbaraBloomLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 46, SPECIES_NIMBARA_GALE}),
    },
    [SPECIES_NIMBARA_GALE] =
    {
        .baseHP        = 102,
        .baseAttack    = 104,
        .baseDefense   = 100,
        .baseSpeed     = 92,
        .baseSpAttack  = 126,
        .baseSpDefense = 116,
        .types = MON_TYPES(TYPE_GRASS, TYPE_FLYING),
        .catchRate = 45,
        .expYield = 260,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_FAST,
        .abilities = { ABILITY_NIMBARA_HUSH, ABILITY_NONE, ABILITY_NIMBARA_HUSH },
        .bodyColor = BODY_COLOR_YELLOW,
        .speciesName = _("Nimbara Gale"),
        .natDexNum = NATIONAL_DEX_NIMBARA_GALE,
        .categoryName = _("Wind Weaver"),
        .height = 38,
        .weight = 980,
        .description = COMPOUND_STRING(
            "Its curling seed-wings turn warm winds into\n"
            "whirlpools that carry pollen to every grove."),
        .levelUpLearnset = sNimbaraGaleLevelUpLearnset,
        .evolutions = EVOLUTION({EVO_LEVEL, 60, SPECIES_NIMBARA_FINAL}),
    },
    [SPECIES_NIMBARA_FINAL] =
    {
        .baseHP        = 120,
        .baseAttack    = 118,
        .baseDefense   = 110,
        .baseSpeed     = 102,
        .baseSpAttack  = 148,
        .baseSpDefense = 132,
        .types = MON_TYPES(TYPE_GRASS, TYPE_DRAGON),
        .catchRate = 45,
        .expYield = 340,
        .friendship = STANDARD_FRIENDSHIP,
        .growthRate = GROWTH_MEDIUM_FAST,
        .abilities = { ABILITY_NIMBARA_HUSH, ABILITY_NONE, ABILITY_NIMBARA_HUSH },
        .bodyColor = BODY_COLOR_GREEN,
        .speciesName = _("Nimbara Final"),
        .natDexNum = NATIONAL_DEX_NIMBARA_FINAL,
        .categoryName = _("Verdant Song"),
        .height = 54,
        .weight = 1620,
        .description = COMPOUND_STRING(
            "The forest follows its song, and every leaf\n"
            "turns into a banner of living light."),
        .levelUpLearnset = sNimbaraFinalLevelUpLearnset,
    },
#endif //P_FAMILY_NIMBARA
};

const struct EggData gEggDatas[EGG_ID_COUNT] =
{
#include "egg_data.h"
};
