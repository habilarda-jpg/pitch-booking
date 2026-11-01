from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal

from pitch_booking.domain.pitch import Pitch


class PricingStrategy(ABC):
    name: str

    @abstractmethod
    def applies_to(self, hour_start: datetime) -> bool: ...

    @abstractmethod
    def price(self, base_price: Decimal) -> Decimal: ...


class NormalPricing(PricingStrategy):
    name = "normal"

    def applies_to(self, hour_start: datetime) -> bool:
        return True

    def price(self, base_price: Decimal) -> Decimal:
        return base_price


class PeakHourPricing(PricingStrategy):
    name = "peak"

    def __init__(
        self, first_hour: int = 18, last_hour: int = 23, multiplier: Decimal = Decimal("1.3")
    ) -> None:
        self._first_hour = first_hour
        self._last_hour = last_hour
        self._multiplier = multiplier

    def applies_to(self, hour_start: datetime) -> bool:
        return self._first_hour <= hour_start.hour <= self._last_hour

    def price(self, base_price: Decimal) -> Decimal:
        return base_price * self._multiplier


class WeekendPricing(PricingStrategy):
    name = "weekend"

    def __init__(self, multiplier: Decimal = Decimal("1.5")) -> None:
        self._multiplier = multiplier

    def applies_to(self, hour_start: datetime) -> bool:
        return hour_start.weekday() >= 5

    def price(self, base_price: Decimal) -> Decimal:
        return base_price * self._multiplier


def default_strategies() -> list[PricingStrategy]:
    return [WeekendPricing(), PeakHourPricing(), NormalPricing()]


class PriceCalculator:
    def __init__(self, strategies: list[PricingStrategy] | None = None) -> None:
        self._strategies = strategies if strategies is not None else default_strategies()

    def strategy_for(self, hour_start: datetime) -> PricingStrategy:
        for strategy in self._strategies:
            if strategy.applies_to(hour_start):
                return strategy
        raise LookupError(f"No pricing strategy applies to {hour_start}")

    def hourly_price(self, pitch: Pitch, hour_start: datetime) -> Decimal:
        price = self.strategy_for(hour_start).price(pitch.hourly_price)
        return price.quantize(Decimal("0.01"))

    def total(self, pitch: Pitch, start: datetime, hours: int) -> Decimal:
        return sum(
            (self.hourly_price(pitch, start + timedelta(hours=h)) for h in range(hours)),
            Decimal("0.00"),
        )
