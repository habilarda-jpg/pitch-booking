from datetime import datetime
from decimal import Decimal

import pytest

from conftest import MONDAY, SATURDAY, at
from pitch_booking.domain.pitch import Pitch
from pitch_booking.domain.pricing import (
    NormalPricing,
    PeakHourPricing,
    PriceCalculator,
    PricingStrategy,
    WeekendPricing,
)

PITCH = Pitch(id=1, name="Arena", owner_id=1, hourly_price=Decimal("1000"))


@pytest.fixture
def calculator() -> PriceCalculator:
    return PriceCalculator()


@pytest.mark.parametrize(
    ("start", "expected_strategy", "expected_price"),
    [
        (at(MONDAY, 10), "normal", Decimal("1000.00")),
        (at(MONDAY, 17), "normal", Decimal("1000.00")),
        (at(MONDAY, 18), "peak", Decimal("1300.00")),
        (at(MONDAY, 23), "peak", Decimal("1300.00")),
        (at(SATURDAY, 10), "weekend", Decimal("1500.00")),
        (at(SATURDAY, 20), "weekend", Decimal("1500.00")),
    ],
)
def test_hourly_price_uses_matching_strategy(calculator, start, expected_strategy, expected_price):
    assert calculator.strategy_for(start).name == expected_strategy
    assert calculator.hourly_price(PITCH, start) == expected_price


def test_total_sums_each_hour_with_its_own_strategy(calculator):
    assert calculator.total(PITCH, at(MONDAY, 17), 2) == Decimal("2300.00")


def test_individual_strategies():
    assert NormalPricing().price(Decimal("800")) == Decimal("800")
    assert PeakHourPricing(multiplier=Decimal("2")).price(Decimal("800")) == Decimal("1600")
    assert WeekendPricing().applies_to(at(SATURDAY, 9))
    assert not WeekendPricing().applies_to(at(MONDAY, 9))


def test_new_strategy_can_be_added_without_changing_calculator():
    class EarlyBirdPricing(PricingStrategy):
        name = "early-bird"

        def applies_to(self, hour_start: datetime) -> bool:
            return hour_start.hour < 11

        def price(self, base_price: Decimal) -> Decimal:
            return base_price * Decimal("0.8")

    calculator = PriceCalculator([EarlyBirdPricing(), NormalPricing()])
    assert calculator.hourly_price(PITCH, at(MONDAY, 9)) == Decimal("800.00")
    assert calculator.hourly_price(PITCH, at(MONDAY, 12)) == Decimal("1000.00")


def test_price_follows_owner_price_change(calculator):
    pitch = Pitch(id=2, name="B", owner_id=5, hourly_price=Decimal("1000"))
    pitch.change_price(5, Decimal("1200"))
    assert calculator.hourly_price(pitch, at(MONDAY, 10)) == Decimal("1200.00")
