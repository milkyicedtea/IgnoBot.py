from datetime import datetime, timezone
from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class Field:
    def __init__(self, name: str = None, field_type = None):
        self.name = name
        self.type = field_type

class Datetime(datetime):
    """Custom datetime handler that supports multiple timestamp formats"""

    FORMATS: ClassVar[list[str]] = [
        "%Y-%m-%dT%H:%M:%S.%fZ",    # 2025-01-01T12:34:56.789Z
        "%Y-%m-%dT%H:%M:%S%z",      # 2025-01-01T12:34:56+00:00
        "%Y-%m-%d",                 # 2025-01-01
        "%Y-%m-%d %H:%M:%S"         # 2025-01-01 12:34:56
    ]

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.union_schema([
            core_schema.datetime_schema(),
            core_schema.int_schema(),
            core_schema.str_schema()
        ])

    @classmethod
    def validate(cls, value: Any) -> datetime:
        if value is None:
            raise ValueError("Timestamp can't be None")

        if isinstance(value, datetime):
            return value

        # unix timestamp (milliseconds)
        if isinstance(value, (int, str)) and str(value).isdigit():
            timestamp = int(value) / 1000  # convert to seconds
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)

        if not isinstance(value, str):
            raise ValueError(f"Unsupported timestamp type: {type(value)}")

        # try each format
        for format_str in cls.FORMATS:
            try:
                dt = datetime.strptime(value, format_str)
                # add utc timezone
                return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
            except ValueError:
                continue
        raise ValueError(f"Could not parse timestamp: {value}")
