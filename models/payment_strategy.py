"""
models/payment_strategy.py
=========================
STRATEGY DESIGN PATTERN — Complete implementation matching lecture slides.

Based on the Strategy Pattern examples from Lecture 9:
- Example 1: Basic Strategy (Strategy1, Strategy2, Strategy3)
- Example 2: SortBehavior & SearchBehavior
- Example 3: RecordKeeper (different record strategies)

Architecture (Same as slide):
┌─────────────────┐
│ PaymentStrategy │ (Strategy Interface / Abstract Class)
│ (Abstract)      │
├─────────────────┤
│ + pay()         │
└────────┬────────┘
         │
    ┌────┴────────────────────────────┐
    │                                 │
┌───▼──────────┐  ┌───▼──────────┐  ┌───▼──────────┐
│ BkashPayment │  │ NagadPayment │  │ CardPayment  │
│   Strategy   │  │   Strategy   │  │   Strategy   │
│ (Concrete)   │  │ (Concrete)   │  │ (Concrete)   │
└──────────────┘  └──────────────┘  └──────────────┘
         │                                 │
         └────────────┬────────────────────┘
                      │
              ┌───────▼───────┐
              │PaymentContext │ (Context)
              │ (Context)     │
              ├───────────────┤
              │ + strategy    │
              │ + execute_    │
              │   payment()   │
              └───────────────┘
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import uuid
import re
from typing import Dict, Any, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: Strategy Interface (Same as Strategy, SortBehavior, SearchBehavior in slide)
# ═══════════════════════════════════════════════════════════════════════════════

class PaymentStrategy(ABC):
    """
    Abstract Strategy - Same as Strategy class in slide's Example 1.
    Defines the interface for the family of payment algorithms.
    
    In slide's Example 2: SortBehavior and SearchBehavior are also Strategy interfaces.
    """
    
    @abstractmethod
    def pay(self, amount: int, payer_info: dict) -> 'PaymentReceipt':
        """
        Execute payment - same as execute() in slide's Example 1,
        sort() in Example 2, and start_record()/store_field() in Example 3.
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of this strategy - for display purposes"""
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: Payment Receipt (Data class for payment result)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PaymentReceipt:
    """
    Payment receipt - holds the result of a payment transaction.
    This is like the output of the strategy execution.
    """
    method: str
    amount: int
    status: str
    transaction_id: str
    message: str
    paid_at: str
    payer_reference: str = ""

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "amount": self.amount,
            "status": self.status,
            "transaction_id": self.transaction_id,
            "message": self.message,
            "paid_at": self.paid_at,
            "payer_reference": self.payer_reference,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: Concrete Strategies (Same as Strategy1, Strategy2, Strategy3 in slide)
# ═══════════════════════════════════════════════════════════════════════════════
#
# In slide's Example 2: Merge, Quick, Heap are concrete strategies for SortBehavior
# In slide's Example 2: Sequential, BinaryTree, HashTable are concrete for SearchBehavior
# In slide's Example 3: DatabaseRecord and StreamRecord are concrete strategies for Record
# Here, BkashPaymentStrategy, NagadPaymentStrategy, CardPaymentStrategy are concrete strategies

class BkashPaymentStrategy(PaymentStrategy):
    """
    Concrete Strategy - Same as Strategy1, Merge, DatabaseRecord in slides.
    Implements bKash mobile payment.
    """
    
    def get_strategy_name(self) -> str:
        return "bKash"
    
    def pay(self, amount: int, payer_info: dict) -> PaymentReceipt:
        """
        Execute bKash payment - like sort() in slide's Example 2.
        """
        print(f"💰 Executing bKash payment strategy for amount: {amount}")
        
        phone = payer_info.get("phone", "").strip()
        pin = payer_info.get("pin", "").strip()

        if not self._is_valid_bd_phone(phone):
            raise ValueError("Invalid bKash phone number. Must be 01XXXXXXXXX")

        if len(pin) < 4:
            raise ValueError("Invalid bKash PIN. Minimum 4 digits")

        transaction_id = "BKS-" + uuid.uuid4().hex[:12].upper()

        print(f"✅ bKash payment processed. Transaction ID: {transaction_id}")

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
    """
    Concrete Strategy - Same as Strategy2, Quick in slides.
    Implements Nagad mobile payment.
    """
    
    def get_strategy_name(self) -> str:
        return "Nagad"
    
    def pay(self, amount: int, payer_info: dict) -> PaymentReceipt:
        """
        Execute Nagad payment
        """
        print(f"💰 Executing Nagad payment strategy for amount: {amount}")
        
        phone = payer_info.get("phone", "").strip()
        pin = payer_info.get("pin", "").strip()

        if not self._is_valid_bd_phone(phone):
            raise ValueError("Invalid Nagad phone number. Must be 01XXXXXXXXX")

        if len(pin) < 4:
            raise ValueError("Invalid Nagad PIN. Minimum 4 digits")

        transaction_id = "NGD-" + uuid.uuid4().hex[:12].upper()

        print(f"✅ Nagad payment processed. Transaction ID: {transaction_id}")

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
    """
    Concrete Strategy - Same as Strategy3, HashTable, StreamRecord in slides.
    Implements Credit/Debit Card payment with Luhn validation.
    """
    
    def get_strategy_name(self) -> str:
        return "Card"
    
    def pay(self, amount: int, payer_info: dict) -> PaymentReceipt:
        """
        Execute Card payment with full validation
        """
        print(f"💳 Executing Card payment strategy for amount: {amount}")
        
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

        print(f"✅ Card payment processed. Transaction ID: {transaction_id}")

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
        """
        Luhn algorithm for card validation
        """
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


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: Context (Same as Context class in slide's Example 1 and Example 2)
# ═══════════════════════════════════════════════════════════════════════════════
#
# In slide's Example 1: Context class holds a Strategy and calls execute()
# In slide's Example 2: Collection class holds SortBehavior and SearchBehavior
# In slide's Example 3: ContactRecorder class holds a Record strategy

class PaymentContext:
    """
    Context - Same as Context class in slide's Example 1, Collection in Example 2.
    
    This class:
    1. Maintains a reference to a Strategy object
    2. Delegates the algorithm's execution to the strategy
    3. Can switch between different strategies at runtime (set_strategy)
    """
    
    def __init__(self, strategy: Optional[PaymentStrategy] = None):
        """
        Initialize context with an optional strategy.
        Same as Collection class in slide's Example 2.
        """
        self._strategy = strategy
        print(f"📦 PaymentContext initialized with strategy: {strategy.get_strategy_name() if strategy else 'None'}")
    
    def set_strategy(self, strategy: PaymentStrategy) -> None:
        """
        Set/Change the strategy at runtime.
        Same as setStrategy() in slide's Example 1 and set_sort()/set_search() in Example 2.
        """
        old_name = self._strategy.get_strategy_name() if self._strategy else "None"
        self._strategy = strategy
        print(f"🔄 Strategy changed from {old_name} to {strategy.get_strategy_name()}")
    
    def execute_payment(self, amount: int, payer_info: dict) -> PaymentReceipt:
        """
        Execute the payment using the current strategy.
        Same as strategy() in slide's Example 1, sort()/search() in Example 2.
        """
        if self._strategy is None:
            raise ValueError("No payment strategy set. Call set_strategy() first.")
        
        print(f"🎯 Executing payment via context using {self._strategy.get_strategy_name()} strategy")
        return self._strategy.pay(amount, payer_info)
    
    def get_current_strategy_name(self) -> str:
        """Get the name of the currently set strategy"""
        return self._strategy.get_strategy_name() if self._strategy else "None"


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: Strategy Factory (For easy strategy selection)
# ═══════════════════════════════════════════════════════════════════════════════

class PaymentStrategyFactory:
    """
    Factory for selecting the correct payment strategy.
    This is like having multiple concrete strategies available for selection.
    """
    
    _strategies: Dict[str, type] = {
        "bkash": BkashPaymentStrategy,
        "nagad": NagadPaymentStrategy,
        "card": CardPaymentStrategy,
        "visa": CardPaymentStrategy,
        "mastercard": CardPaymentStrategy,
        "credit_card": CardPaymentStrategy,
        "debit_card": CardPaymentStrategy,
    }
    
    @classmethod
    def get_strategy(cls, payment_method: str) -> PaymentStrategy:
        """
        Get the appropriate strategy based on payment method.
        This creates a new instance of the requested strategy.
        """
        method = str(payment_method).lower().strip()
        
        strategy_class = cls._strategies.get(method)
        
        if strategy_class is None:
            available = list(cls._strategies.keys())
            raise ValueError(f"Unsupported payment method: {payment_method}. Available: {available[:3]}...")
        
        strategy = strategy_class()
        print(f"🏭 Factory created {strategy.get_strategy_name()} strategy")
        return strategy
    
    @classmethod
    def register_strategy(cls, method_name: str, strategy_class: type) -> None:
        """
        Register a new payment strategy dynamically.
        This follows Open/Closed Principle - add new strategies without modifying existing code.
        """
        cls._strategies[method_name.lower()] = strategy_class
        print(f"✅ Registered new strategy: {method_name}")


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY ALIASES
# ═══════════════════════════════════════════════════════════════════════════════

# For existing code that imports these names
PaymentStrategySelector = PaymentStrategyFactory

# Alias for backward compatibility
BkashPayment = BkashPaymentStrategy
NagadPayment = NagadPaymentStrategy
CardPayment = CardPaymentStrategy


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO (Same as slide's main() function)
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*70)
    print("STRATEGY PATTERN DEMO - Same as slide's examples")
    print("="*70)
    
    # ========== Example 1: Basic Strategy (Same as slide's Example 1) ==========
    print("\n📌 Example 1: Basic Strategy Switching (Like slide's Example 1)")
    print("-" * 50)
    
    context = PaymentContext()
    
    # Use bKash strategy
    context.set_strategy(BkashPaymentStrategy())
    receipt = context.execute_payment(500, {"phone": "01712345678", "pin": "1234"})
    print(f"   Result: {receipt.method} - {receipt.transaction_id}")
    
    # Switch to Card strategy at runtime (same as slide's dynamic switching)
    context.set_strategy(CardPaymentStrategy())
    receipt = context.execute_payment(1000, {
        "card_holder": "John Doe",
        "card_number": "4242424242424242",
        "expiry": "12/25",
        "cvv": "123"
    })
    print(f"   Result: {receipt.method} - {receipt.transaction_id}")
    
    # ========== Example 2: Using Factory (Like slide's registry pattern) ==========
    print("\n📌 Example 2: Using Strategy Factory (Like slide's FactoryRegistry)")
    print("-" * 50)
    
    strategy = PaymentStrategyFactory.get_strategy("nagad")
    receipt = strategy.pay(750, {"phone": "01912345678", "pin": "4321"})
    print(f"   Result: {receipt.method} payment of ৳{receipt.amount}")
    
    # ========== Example 3: Dynamic Strategy Selection (Like slide's Example 2) ==========
    print("\n📌 Example 3: Dynamic Strategy Selection (Like slide's Collection example)")
    print("-" * 50)
    
    payment_methods = ["bkash", "card", "nagad"]
    
    for method in payment_methods:
        strategy = PaymentStrategyFactory.get_strategy(method)
        print(f"   Selected: {strategy.get_strategy_name()} - Ready to process payment")
    
    print("\n" + "="*70)
    print("✅ Strategy Pattern Demo Complete!")
    print("="*70)