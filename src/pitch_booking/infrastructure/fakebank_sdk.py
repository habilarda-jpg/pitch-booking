from itertools import count


class FakeBankClient:
    DECLINED_SUFFIX = "0002"

    def __init__(self) -> None:
        self._sequence = count(1000)
        self.transactions: list[dict] = []

    def make_transaction(self, card_no: str, amount_kurus: int, description: str) -> dict:
        if not (card_no.isdigit() and len(card_no) == 16):
            return {"result": "ERROR", "message": "INVALID_CARD"}
        if card_no.endswith(self.DECLINED_SUFFIX):
            return {"result": "DECLINED", "message": "INSUFFICIENT_FUNDS"}
        txn = {
            "result": "OK",
            "txn_id": f"FB-{next(self._sequence)}",
            "amount_kurus": amount_kurus,
            "description": description,
        }
        self.transactions.append(txn)
        return txn
