from datetime import datetime
from decimal import Decimal

import pytest

from pitch_booking.bootstrap import Container, build_container
from pitch_booking.domain.pitch import Pitch

MONDAY = datetime(2026, 11, 2)
SATURDAY = datetime(2026, 11, 7)


def at(day: datetime, hour: int) -> datetime:
    return day.replace(hour=hour)


@pytest.fixture
def container() -> Container:
    return build_container()


@pytest.fixture
def pitch(container: Container) -> Pitch:
    return container.pitch_service.register_pitch("Arena 1", owner_id=10, hourly_price=Decimal("1000"))
