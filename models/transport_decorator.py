"""
models/transport_decorator.py
Concrete Decorators - Like CondimentDecorator and SideDecorator
"""

from models.ticket_decorator import TicketDecorator


# ============= COMMON DECORATORS (All Transports) =============

class ExtraLuggageDecorator(TicketDecorator):
    """Extra luggage - same for all transports (like adding mayo)"""
    
    def __init__(self, component: TicketComponent):
        super().__init__(component)
        self.cost = 200
    
    def get_cost(self) -> int:
        return self.cost + self.component.get_cost()
    
    def get_description(self) -> str:
        return self.component.get_description() + " + Extra Luggage"
    
    def get_features(self) -> list:
        features = self.component.get_features()
        features.append("Extra 10kg luggage (+200 BDT)")
        return features


class MealDecorator(TicketDecorator):
    """Meal - same for all transports (like adding mustard)"""
    
    def __init__(self, component: TicketComponent):
        super().__init__(component)
        self.cost = 150
    
    def get_cost(self) -> int:
        return self.cost + self.component.get_cost()
    
    def get_description(self) -> str:
        return self.component.get_description() + " + Meal"
    
    def get_features(self) -> list:
        features = self.component.get_features()
        features.append("Complimentary Meal (+150 BDT)")
        return features


# ============= INSURANCE DECORATOR (Different for each transport) =============

class InsuranceDecorator(TicketDecorator):
    """
    Insurance - DIFFERENT PRICE PER TRANSPORT (like pickle with different prices)
    - Plane: 300 BDT
    - Train: 50 BDT
    - Bus: 50 BDT
    """
    
    def __init__(self, component: TicketComponent):
        super().__init__(component)
        
        # Get transport type from the component
        transport = getattr(component, 'transport_type', 'bus')
        
        insurance_prices = {
            "bus": 50,
            "train": 50,
            "plane": 300
        }
        self.cost = insurance_prices.get(transport, 50)
        self.transport = transport
    
    def get_cost(self) -> int:
        return self.cost + self.component.get_cost()
    
    def get_description(self) -> str:
        return self.component.get_description() + " + Travel Insurance"
    
    def get_features(self) -> list:
        features = self.component.get_features()
        
        if self.transport == "plane":
            features.append(f"Flight Insurance (+{self.cost} BDT) - Cancellation + Medical")
        elif self.transport == "train":
            features.append(f"Rail Insurance (+{self.cost} BDT) - Journey protection")
        else:
            features.append(f"Bus Insurance (+{self.cost} BDT) - Trip protection")
        
        return features


# ============= PLANE-ONLY DECORATORS =============

class PriorityBoardingDecorator(TicketDecorator):
    """Priority Boarding - ONLY FOR PLANE (like adding special topping)"""
    
    def __init__(self, component: TicketComponent):
        super().__init__(component)
        
        # Check if transport supports priority boarding
        transport = getattr(component, 'transport_type', 'bus')
        
        if transport != "plane":
            raise ValueError(f"Priority boarding is only available for PLANE, not for {transport.upper()}")
        
        self.cost = 300
    
    def get_cost(self) -> int:
        return self.cost + self.component.get_cost()
    
    def get_description(self) -> str:
        return self.component.get_description() + " + Priority Boarding"
    
    def get_features(self) -> list:
        features = self.component.get_features()
        features.append("Priority Boarding (+300 BDT) - Skip the queue")
        return features


class LoungeAccessDecorator(TicketDecorator):
    """VIP Lounge Access - ONLY FOR PLANE"""
    
    def __init__(self, component: TicketComponent):
        super().__init__(component)
        
        transport = getattr(component, 'transport_type', 'bus')
        
        if transport != "plane":
            raise ValueError(f"VIP Lounge is only available for PLANE, not for {transport.upper()}")
        
        self.cost = 400
    
    def get_cost(self) -> int:
        return self.cost + self.component.get_cost()
    
    def get_description(self) -> str:
        return self.component.get_description() + " + VIP Lounge Access"
    
    def get_features(self) -> list:
        features = self.component.get_features()
        features.append("VIP Lounge (+400 BDT) - Airport lounge access")
        return features


# ============= BUS-ONLY DECORATOR: VOUCHER FOR HANIF =============

class HanifVoucherDecorator(TicketDecorator):
    """
    Voucher for Hanif Bus - 10% discount
    ONLY FOR BUS with operator = Hanif (like a special coupon)
    """
    
    def __init__(self, component: TicketComponent, voucher_code: str = "HANIF10"):
        super().__init__(component)
        self.voucher_code = voucher_code
        
        # Check if this voucher can be applied
        transport = getattr(component, 'transport_type', 'bus')
        operator = getattr(component, 'operator', None)
        
        if transport != "bus":
            raise ValueError(f"Hanif voucher is only available for BUS, not for {transport.upper()}")
        
        if operator != "Hanif" and operator != "Hanif Transport":
            raise ValueError(f"Hanif voucher is only valid for Hanif Transport. Current operator: {operator}")
        
        # Calculate 10% discount
        current_cost = component.get_cost()
        self.discount = int(current_cost * 0.10)  # 10% off
        self.discount = min(self.discount, 500)  # Max discount 500 BDT
    
    def get_cost(self) -> int:
        current_cost = self.component.get_cost()
        final_cost = current_cost - self.discount
        return max(final_cost, 0)  # Don't go below 0
    
    def get_description(self) -> str:
        return self.component.get_description() + f" + Voucher ({self.voucher_code}: 10% off, -{self.discount} BDT)"
    
    def get_features(self) -> list:
        features = self.component.get_features()
        features.append(f"💸 Hanif Voucher {self.voucher_code} applied (10% off, -{self.discount} BDT)")
        return features