from typing import Any, Union, ForwardRef

from cogs.Cog_Utils.osspy.Enums import Status, GameMode, Nomination, Failtimes, Covers
from cogs.Cog_Utils.osspy.Utils import Datetime

from pydantic import BaseModel

from cogs.Cog_Utils.osspy.models.mod import Mod

BeatmapRef = ForwardRef('Beatmap')
BeatmapExtendedRef = ForwardRef('BeatmapExtended')
BeatmapsetRef = ForwardRef('Beatmapset')
BeatmapsetExtendedRef = ForwardRef('BeatmapsetExtended')


class Beatmap(BaseModel):
    # Required fields
    beatmapset_id: int
    difficulty_rating: float
    id: int
    mode: GameMode
    status: Status
    total_length: int
    user_id: int
    version: str

    # Optional fields
    beatmapset: Union[BeatmapsetRef, BeatmapsetExtendedRef] | None = None
    checksum: str | None = None
    failtimes: Failtimes | None = None
    max_combo: int | None = None

    def get_beatmapset(self):
        return self.data


class BeatmapExtended(Beatmap):
    accuracy: float
    ar: float
    bpm: float | None = None
    convert: bool
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: float
    deleted_at: Datetime | None = None
    drain: float
    hit_length: int
    is_scoreable: bool
    last_updated: Datetime
    mode_int: int
    passcount: int
    playcount: int
    ranked: Status
    url: str


class Beatmapset(BaseModel):
    # Required fields
    artist: str
    artist_unicode: str
    covers: Covers
    creator: str
    favourite_count: int
    id: int
    nsfw: bool
    offset: int
    play_count: int
    preview_url: str
    source: str
    status: Status
    spotlight: bool
    title: str
    title_unicode: str
    user_id: int
    video: bool

    # Optional fields
    beatmaps: list[Union[Beatmap, BeatmapExtended]] | None = None
    converts: Any | None = None
    current_nomitations: Nomination | None = None
    current_user_attributes: Any | None = None
    description: Any | None = None
    discussion: Any | None = None
    events: Any | None = None
    genre: Any | None = None
    has_favourited: bool | None = None
    language: Any | None = None
    nominations: Any | None = None
    pack_tags: list[str] | None = None
    ratings: Any | None = None
    recent_favourites: Any | None = None
    related_users: Any | None = None
    user: Any | None = None
    track_id: int | None = None

class BeatmapsetExtended(Beatmapset):
    pass


Beatmap.model_rebuild()
BeatmapExtended.model_rebuild()
Beatmapset.model_rebuild()
BeatmapsetExtended.model_rebuild()


class BeatmapDifficultyAttributes(BaseModel):
    max_combo: int
    star_rating: float

    # osu fields
    aim_difficulty: float
    approach_rate: float
    flashlight_difficulty: float
    overall_difficulty: float
    slider_factor: float
    speed_difficulty: float

    # taiko fields
    stamina_difficulty: float
    rhythm_difficulty: float
    colour_difficulty: float
    approach_rate: float
    great_hit_window: float

    # ctb (fruits) fields
    approach_rate: float

    # mania fields
    great_hit_window: float
    score_multiplier: float


class BeatmapPack(BaseModel):
    # Required fields
    author: str
    date: Datetime
    name: str
    no_diff_reduction: bool
    ruleset_id: int
    tag: str
    url: str

    # Optional fields
    beatmapsets: list[Union[Beatmapset, BeatmapsetExtended]] | None = None

    # TODO: beatmapasets_ids: list[int], compeleted: bool
    # user_completion_data


class BeatmapPlaycount(BaseModel):
    beatmap_id: int
    beatmap: Union[Beatmap, BeatmapExtended] | None = None
    beatmapset: Union[Beatmapset, BeatmapsetExtended] | None = None
    count: int


class ScoreStatistics(BaseModel):
    combo_break: int | None = None
    good: int | None = None
    great: int | None = None
    ignore_hit: int | None = None
    ignore_miss: int | None = None
    large_bonus: int | None = None
    large_tick_hit: int | None = None
    large_tick_miss: int | None = None
    legacy_combo_increase: int | None = None
    meh: int | None = None
    miss: int | None = None
    ok: int | None = None
    perfect: int | None = None
    slider_tail_hit: int | None = None
    small_bonus: int | None = None
    small_tick_hit: int | None = None
    small_tick_miss: int | None = None

class Score(BaseModel):
    accuracy: float
    beatmap_id: int
    best_id: int | None = None
    build_id: int | None = None
    classic_total_score: int
    ended_at: Datetime
    has_replay: bool
    id: int
    is_perfect_combo: bool
    legacy_perfect: bool
    legacy_score_id: int | None = None
    legacy_total_score: int
    max_combo: int
    maximum_statistics: Any     # TODO: Not specified in docs yet (dict)
    mods: list[Mod]
    passed: bool
    playlist_item_id: int | None = None
    pp: float | None = None
    preserve: bool
    processed: bool
    rank: str
    ranked: bool
    room_id: int | None = None  # Probably multi only
    ruleset_id: int
    started_at: Datetime | None = None
    statistics: ScoreStatistics     # TODO: Make class Statistics(great, meh, miss, ok)
    total_score: int
    total_score_without_mods: int
    type: str
    user_id: int

class BeatmapUserScore(BaseModel):
    position: int
    score: Score

class BeatmapScores(BaseModel):
    scores: list[Score]
    userScore: BeatmapUserScore | None



