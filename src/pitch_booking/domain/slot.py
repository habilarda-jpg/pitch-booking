from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal


@dataclass(frozen=True)
class OpeningHours:
    open_hour: int = 9
    close_hour: int = 24

    def contains(self, start: datetime, hours: int) -> bool:
        midnight = start.replace(hour=0, minute=0, second=0, microsecond=0)
        opens = midnight + timedelta(hours=self.open_hour)
        closes = midnight + timedelta(hours=self.close_hour)
        return opens <= start and start + timedelta(hours=hours) <= closes


@dataclass(frozen=True)
class Slot:
    pitch_id: int
    start: datetime
    price: Decimal
    available: bool = True

    @property
    def end(self) -> datetime:
        return self.start + timedelta(hours=1)
