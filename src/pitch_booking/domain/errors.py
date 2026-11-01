class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class InvalidReservationError(DomainError):
    pass


class SlotUnavailableError(DomainError):
    pass


class InvalidStateTransitionError(DomainError):
    pass


class PaymentDeclinedError(DomainError):
    pass


class PermissionDeniedError(DomainError):
    pass
