from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal


@dataclass
class Pitch:
    id: int
    name: str
    owner_id: int
    hourly_price: Decimal


@dataclass
class Reservation:
    id: int
    pitch_id: int
    customer_email: str
    start: datetime
    hours: int
    price: Decimal
    status: str = "PENDING"

    @property
    def end(self) -> datetime:
        return self.start + timedelta(hours=self.hours)
