"""
models/payment_strategy.py
===========================
TRUE STRATEGY DESIGN PATTERN

Strategy Pattern defines a FAMILY of algorithms (payment methods),
encapsulates each one, and makes them interchangeable. The context
(PaymentContext) can switch strategy at runtime without changing itself.

Components:
  PaymentStrategy  — Abstract interface (Strategy)
  BkashPayment     — Concrete Strategy A
  NagadPayment     — Concrete Strategy B
  VisaCardPayment  — Concrete Strategy C
  PaymentContext   — Context (uses a strategy, delegates to it)

This means: adding MasterCard tomorrow = one new class, zero other changes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import random
import string


# ── Payment Result (Value Object) ────────────────────────────────────────────

@dataclass
class PaymentReceipt:
    """
    Immutable payment result returned by every strategy.
    Stored in the database as proof of payment.
    """
    method:        str
    amount:        int
    transaction_id: str
    status:        str
    timestamp:     str
    gateway_msg:   str

    def to_dict(self) -> dict:
        return {
            "method":         self.method,
            "amount":         self.amount,
            "transaction_id": self.transaction_id,
            "status":         self.status,
            "timestamp":      self.timestamp,
            "gateway_msg":    self.gateway_msg,
        }

    def display(self) -> str:
        return (f"Paid ৳{self.amount} via {self.method} "
                f"[TXN: {self.transaction_id}]")


def _generate_txn(prefix: str) -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"{prefix}-{suffix}"


# ── Abstract Strategy ─────────────────────────────────────────────────────────

class PaymentStrategy(ABC):
    """
    Abstract base for all payment strategies.
    Every concrete strategy MUST implement process_payment().
    """

    @abstractmethod
    def process_payment(self, amount: int, payer_info: dict) -> PaymentReceipt:
        """
        Simulate processing a payment.
        Returns a PaymentReceipt regardless of the underlying method.
        """
        ...

    @property
    @abstractmethod
    def method_name(self) -> str:
        """Human-readable payment method name."""
        ...

    @property
    @abstractmethod
    def method_key(self) -> str:
        """Short key used in API requests (e.g. 'bkash')."""
        ...


# ── Concrete Strategies ───────────────────────────────────────────────────────

class BkashPayment(PaymentStrategy):
    """
    bKash Mobile Banking strategy.
    Simulates bKash gateway: generates a TXN ID, validates wallet.
    """

    @property
    def method_name(self) -> str:
        return "bKash"

    @property
    def method_key(self) -> str:
        return "bkash"

    def process_payment(self, amount: int, payer_info: dict) -> PaymentReceipt:
        # Simulate bKash gateway processing
        txn_id = _generate_txn("BKS")
        phone  = payer_info.get("phone", "01XXXXXXXXX")

        return PaymentReceipt(
            method         = self.method_name,
            amount         = amount,
            transaction_id = txn_id,
            status         = "SUCCESS",
            timestamp      = datetime.utcnow().isoformat(),
            gateway_msg    = (
                f"bKash payment of ৳{amount} received from {phone}. "
                f"Transaction ID: {txn_id}. Your bKash account has been debited."
            ),
        )


class NagadPayment(PaymentStrategy):
    """
    Nagad Mobile Banking strategy.
    Simulates Nagad gateway processing.
    """

    @property
    def method_name(self) -> str:
        return "Nagad"

    @property
    def method_key(self) -> str:
        return "nagad"

    def process_payment(self, amount: int, payer_info: dict) -> PaymentReceipt:
        txn_id = _generate_txn("NGD")
        phone  = payer_info.get("phone", "01XXXXXXXXX")

        return PaymentReceipt(
            method         = self.method_name,
            amount         = amount,
            transaction_id = txn_id,
            status         = "SUCCESS",
            timestamp      = datetime.utcnow().isoformat(),
            gateway_msg    = (
                f"Nagad payment of ৳{amount} confirmed from {phone}. "
                f"Reference: {txn_id}. Nagad balance updated."
            ),
        )


class VisaCardPayment(PaymentStrategy):
    """
    Visa Card (Debit/Credit) strategy.
    Simulates card gateway: masks card number, runs authorization.
    """

    @property
    def method_name(self) -> str:
        return "Visa Card"

    @property
    def method_key(self) -> str:
        return "visa"

    def process_payment(self, amount: int, payer_info: dict) -> PaymentReceipt:
        txn_id   = _generate_txn("VIS")
        card_num = payer_info.get("card_number", "4XXX XXXX XXXX XXXX")
        masked   = "**** **** **** " + str(card_num)[-4:]

        return PaymentReceipt(
            method         = self.method_name,
            amount         = amount,
            transaction_id = txn_id,
            status         = "AUTHORISED",
            timestamp      = datetime.utcnow().isoformat(),
            gateway_msg    = (
                f"Visa card {masked} charged ৳{amount}. "
                f"Authorization code: {txn_id}. Bank approved."
            ),
        )


class MasterCardPayment(PaymentStrategy):
    """MasterCard strategy — shows how easy it is to add a new method."""

    @property
    def method_name(self) -> str:
        return "MasterCard"

    @property
    def method_key(self) -> str:
        return "mastercard"

    def process_payment(self, amount: int, payer_info: dict) -> PaymentReceipt:
        txn_id = _generate_txn("MCD")
        masked = "**** **** **** " + str(payer_info.get("card_number", "0000"))[-4:]

        return PaymentReceipt(
            method         = self.method_name,
            amount         = amount,
            transaction_id = txn_id,
            status         = "AUTHORISED",
            timestamp      = datetime.utcnow().isoformat(),
            gateway_msg    = (
                f"MasterCard {masked} charged ৳{amount}. "
                f"Auth code: {txn_id}."
            ),
        )


# ── Context ───────────────────────────────────────────────────────────────────

class PaymentContext:
    """
    Strategy Pattern Context.

    Holds a reference to a PaymentStrategy and delegates
    payment processing entirely to it. The context does NOT
    know or care which concrete strategy is used.

    The strategy can be swapped at runtime via set_strategy().
    """

    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: PaymentStrategy) -> None:
        """Swap strategy at runtime — the hallmark of Strategy Pattern."""
        self._strategy = strategy

    def execute_payment(self, amount: int, payer_info: dict = None) -> PaymentReceipt:
        """Delegate to whichever strategy is currently set."""
        if payer_info is None:
            payer_info = {}
        return self._strategy.process_payment(amount, payer_info)

    @property
    def current_method(self) -> str:
        return self._strategy.method_name


# ── Strategy Registry (no if/else needed in routes) ──────────────────────────

class PaymentStrategyFactory:
    """
    Registry of all available payment strategies.
    Routes call get_strategy(key) — zero if/else needed.
    """

    _registry: dict[str, type[PaymentStrategy]] = {}

    @classmethod
    def register(cls, strategy_class: type[PaymentStrategy]) -> None:
        instance = strategy_class()
        cls._registry[instance.method_key] = strategy_class

    @classmethod
    def get_strategy(cls, key: str) -> PaymentStrategy:
        strategy_class = cls._registry.get(key.lower())
        if strategy_class is None:
            raise KeyError(
                f"Unknown payment method '{key}'. "
                f"Available: {list(cls._registry.keys())}"
            )
        return strategy_class()

    @classmethod
    def available_methods(cls) -> list[str]:
        return list(cls._registry.keys())


# Auto-register all strategies on import
PaymentStrategyFactory.register(BkashPayment)
PaymentStrategyFactory.register(NagadPayment)
PaymentStrategyFactory.register(VisaCardPayment)
PaymentStrategyFactory.register(MasterCardPayment)