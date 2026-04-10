class PaymentStrategy:
    def pay(self, amount):
        pass


class BkashPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid {amount} using bKash"


class CardPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid {amount} using Card"


class PaymentContext:
    def __init__(self, strategy):
        self.strategy = strategy

    def execute(self, amount):
        return self.strategy.pay(amount)