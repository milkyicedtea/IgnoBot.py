from enum import IntEnum, Enum
from cogs.Cog_Utils.osspy.Utils import Field
from pydantic import BaseModel

class Status(IntEnum):
    GRAVEYARD = -2
    WIP = -1
    PENDING = 0
    RANKED = 1
    APPROVED = 2
    QUALIFIED = 3
    LOVED = 4

    @classmethod
    def _missing_(cls, value):
        # Api returns `RankStatus` as int or string
        if value == "graveyard":
            return cls(-2)
        elif value == "wip":
            return cls(-1)
        elif value == "pending":
            return cls(0)
        elif value == "ranked":
            return cls(1)
        elif value == "approved":
            return cls(2)
        elif value == "qualified":
            return cls(3)
        elif value == "loved":
            return cls(4)


class GameMode(str, Enum):
    OSU = 'osu'
    TAIKO = 'taiko'
    CATCH = 'fruits'
    MANIA = 'mania'


class Covers(BaseModel):
    cover: str
    cover_2x: str = Field(name = 'cover@2x')
    card: str
    card_2x: str = Field(name = 'card@2x')
    list: str
    list_2x: str = Field(name = 'list@2x')
    slimcover: str
    slimcover_2x: str = Field(name = 'slimcover@2x')

    class Config:
        populate_by_name = True


class PlayStyles(IntEnum):
    MOUSE = 1
    KEYBOARD = 2
    TABLET = 4
    TOUCH = 8

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, list):
            value = iter(value)
            new_val = cls(next(value))
            for val in value:
                new_val |= cls(val)
            return new_val


class Hype(BaseModel):
    current: int
    required: int

    def to_dict(self):
        return {
            'current': self.current,
            'required': self.required
        }

class Nomination(BaseModel):
    beatmapset_id: int
    rulesets: list[GameMode]
    reset: bool
    user_id: int

class Failtimes(BaseModel):
    exit: list[int] | None
    fail: list[int] | None

class BeatmapPackType(str, Enum):
    STANDARD = 'standard'
    FEATURED = 'featured'
    TOURNAMENT = 'tournament'
    LOVED = 'loved'
    CHARD = 'chart'
    THEME = 'theme'
    ARTIST = 'artist'

