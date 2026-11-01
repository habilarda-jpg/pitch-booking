from decimal import Decimal

from pitch_booking.application.ports import PaymentGateway
from pitch_booking.domain.errors import PaymentDeclinedError
from pitch_booking.infrastructure.fakebank_sdk import FakeBankClient


class FakeBankPaymentAdapter(PaymentGateway):
    def __init__(self, client: FakeBankClient) -> None:
        self._client = client

    def charge(self, amount: Decimal, card_number: str, reference: str) -> str:
        response = self._client.make_transaction(
            card_no=card_number.replace(" ", ""),
            amount_kurus=int(amount * 100),
            description=reference,
        )
        if response["result"] != "OK":
            raise PaymentDeclinedError(f"Payment declined: {response['message']}")
        return response["txn_id"]
