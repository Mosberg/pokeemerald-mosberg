#include "global.h"
#include "constants/trainers.h"

static enum TrainerPicID sSelectedPlayerTrainerPic = TRAINER_PIC_NONE;

static enum TrainerPicID GetEmeraldTrainerPic(enum Gender gender)
{
    return gender == MALE ? TRAINER_PIC_BRENDAN : TRAINER_PIC_MAY;
}
static enum TrainerPicID GetRSTrainerPic(enum Gender gender)
{
    return gender == MALE ? TRAINER_PIC_RS_BRENDAN : TRAINER_PIC_RS_MAY;
}

static enum TrainerPicID GetKantoTrainerPic(enum Gender gender)
{
    return gender == MALE ? TRAINER_PIC_RED : TRAINER_PIC_LEAF;
}

void SetSelectedPlayerTrainerPic(enum TrainerPicID trainerPicId)
{
    sSelectedPlayerTrainerPic = trainerPicId;
}

void ClearSelectedPlayerTrainerPic(void)
{
    sSelectedPlayerTrainerPic = TRAINER_PIC_NONE;
}

enum TrainerPicID GetSelectedPlayerTrainerPic(void)
{
    return sSelectedPlayerTrainerPic;
}

enum TrainerPicID GetPlayerTrainerPic(enum Gender gender, enum GameVersion version)
{
    if (sSelectedPlayerTrainerPic != TRAINER_PIC_NONE)
        return sSelectedPlayerTrainerPic;

    switch (version)
    {
        case VERSION_SAPPHIRE:
        case VERSION_RUBY:
            return GetRSTrainerPic(gender);
        case VERSION_LEAF_GREEN:
        case VERSION_FIRE_RED:
            return GetKantoTrainerPic(gender);
        case VERSION_EMERALD:
        default:
            return GetEmeraldTrainerPic(gender);
    }
}
