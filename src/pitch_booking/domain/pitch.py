from dataclasses import dataclass
from decimal import Decimal

from pitch_booking.domain.errors import InvalidReservationError, PermissionDeniedError


@dataclass
class Pitch:
    id: int
    name: str
    owner_id: int
    hourly_price: Decimal

    def change_price(self, owner_id: int, new_price: Decimal) -> None:
        if owner_id != self.owner_id:
            raise PermissionDeniedError("Only the pitch owner can change its price")
        if new_price <= 0:
            raise InvalidReservationError("Hourly price must be positive")
        self.hourly_price = new_price
