from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import uuid
import re


@dataclass
class PaymentReceipt:
    method: str
    amount: int
    status: str
    transaction_id: str
    message: str
    paid_at: str
    payer_reference: str = ""

    def to_dict(self):
        return {
            "method": self.method,
            "amount": self.amount,
            "status": self.status,
            "transaction_id": self.transaction_id,
            "message": self.message,
            "paid_at": self.paid_at,
            "payer_reference": self.payer_reference,
        }


class PaymentStrategy(ABC):
    """
    Abstract Strategy.
    All payment methods must implement pay().
    """

    @abstractmethod
    def pay(self, amount: int, payer_info: dict) -> PaymentReceipt:
        pass


class BkashPaymentStrategy(PaymentStrategy):
    def pay(self, amount: int, payer_info: dict) -> PaymentReceipt:
        phone = payer_info.get("phone", "").strip()
        pin = payer_info.get("pin", "").strip()

        if not self._is_valid_bd_phone(phone):
            raise ValueError("Invalid bKash phone number.")

        if len(pin) < 4:
            raise ValueError("Invalid bKash PIN.")

        transaction_id = "BKS-" + uuid.uuid4().hex[:12].upper()

        return PaymentReceipt(
            method="bKash",
            amount=amount,
            status="PAID",
            transaction_id=transaction_id,
            message="bKash payment completed successfully.",
            paid_at=datetime.utcnow().isoformat(),
            payer_reference=self._mask_phone(phone)
        )

    def _is_valid_bd_phone(self, phone: str) -> bool:
        return bool(re.match(r"^01[0-9]{9}$", phone))

    def _mask_phone(self, phone: str) -> str:
        return phone[:3] + "***" + phone[-3:]


class NagadPaymentStrategy(PaymentStrategy):
    def pay(self, amount: int, payer_info: dict) -> PaymentReceipt:
        phone = payer_info.get("phone", "").strip()
        pin = payer_info.get("pin", "").strip()

        if not self._is_valid_bd_phone(phone):
            raise ValueError("Invalid Nagad phone number.")

        if len(pin) < 4:
            raise ValueError("Invalid Nagad PIN.")

        transaction_id = "NGD-" + uuid.uuid4().hex[:12].upper()

        return PaymentReceipt(
            method="Nagad",
            amount=amount,
            status="PAID",
            transaction_id=transaction_id,
            message="Nagad payment completed successfully.",
            paid_at=datetime.utcnow().isoformat(),
            payer_reference=self._mask_phone(phone)
        )

    def _is_valid_bd_phone(self, phone: str) -> bool:
        return bool(re.match(r"^01[0-9]{9}$", phone))

    def _mask_phone(self, phone: str) -> str:
        return phone[:3] + "***" + phone[-3:]


class CardPaymentStrategy(PaymentStrategy):
    def pay(self, amount: int, payer_info: dict) -> PaymentReceipt:
        card_number = payer_info.get("card_number", "").replace(" ", "").strip()
        card_holder = payer_info.get("card_holder", "").strip()
        expiry = payer_info.get("expiry", "").strip()
        cvv = payer_info.get("cvv", "").strip()

        if not card_holder:
            raise ValueError("Card holder name is required.")

        if not self._is_valid_card_number(card_number):
            raise ValueError("Invalid card number.")

        if not self._is_valid_expiry(expiry):
            raise ValueError("Invalid card expiry. Use MM/YY format.")

        if not self._is_valid_cvv(cvv):
            raise ValueError("Invalid CVV.")

        transaction_id = "CRD-" + uuid.uuid4().hex[:12].upper()

        return PaymentReceipt(
            method="Card",
            amount=amount,
            status="PAID",
            transaction_id=transaction_id,
            message="Card payment completed successfully.",
            paid_at=datetime.utcnow().isoformat(),
            payer_reference=self._mask_card(card_number)
        )

    def _is_valid_card_number(self, card_number: str) -> bool:
        if not card_number.isdigit():
            return False

        if len(card_number) < 13 or len(card_number) > 19:
            return False

        return self._luhn_check(card_number)

    def _luhn_check(self, card_number: str) -> bool:
        digits = [int(digit) for digit in card_number]
        checksum = 0
        parity = len(digits) % 2

        for index, digit in enumerate(digits):
            if index % 2 == parity:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit

        return checksum % 10 == 0

    def _is_valid_expiry(self, expiry: str) -> bool:
        if not re.match(r"^(0[1-9]|1[0-2])\/[0-9]{2}$", expiry):
            return False

        month, year = expiry.split("/")
        expiry_year = int("20" + year)
        expiry_month = int(month)

        now = datetime.utcnow()

        if expiry_year < now.year:
            return False

        if expiry_year == now.year and expiry_month < now.month:
            return False

        return True

    def _is_valid_cvv(self, cvv: str) -> bool:
        return bool(re.match(r"^[0-9]{3,4}$", cvv))

    def _mask_card(self, card_number: str) -> str:
        return "****-****-****-" + card_number[-4:]


class PaymentContext:
    """
    Context class.
    Receives a strategy and executes payment.
    """

    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def execute_payment(self, amount: int, payer_info: dict) -> PaymentReceipt:
        return self.strategy.pay(amount, payer_info)


class PaymentStrategyFactory:
    """
    Selects the correct payment strategy based on payment method string.
    """

    @staticmethod
    def get_strategy(payment_method: str) -> PaymentStrategy:
        method = str(payment_method).lower().strip()

        if method == "bkash":
            return BkashPaymentStrategy()

        if method == "nagad":
            return NagadPaymentStrategy()

        if method in ["card", "visa", "mastercard", "credit_card", "debit_card"]:
            return CardPaymentStrategy()

        raise ValueError(f"Unsupported payment method: {payment_method}")


# Optional alias — prevents errors if any route imports PaymentStrategySelector.
class PaymentStrategySelector:
    @staticmethod
    def get_strategy(payment_method: str) -> PaymentStrategy:
        return PaymentStrategyFactory.get_strategy(payment_method)

    @staticmethod
    def select(payment_method: str) -> PaymentStrategy:
        return PaymentStrategyFactory.get_strategy(payment_method)