"""
models/base_ticket.py
Concrete Components - Like BasicSandwich and DeluxeSandwich
"""

from models.ticket_component import TicketComponent

class BaseTicket(TicketComponent):
    """Concrete Component - Basic ticket (like BasicSandwich)"""
    
    def __init__(self, ticket):
        self.ticket = ticket
        self.transport_type = ticket.type.lower()
        self.operator = getattr(ticket, 'operator', None)
    
    def get_cost(self) -> int:
        return self.ticket.price
    
    def get_description(self) -> str:
        return f"{self.ticket.type} ticket from {self.ticket.source} to {self.ticket.destination}"
    
    def get_features(self) -> list:
        return ["Base ticket"]


class PremiumTicket(TicketComponent):
    """Concrete Component - Premium ticket (like DeluxeSandwich)
    NOTE: Premium ticket has NO EXTRA COST and NO automatic features.
    Only selected add-ons add features and cost.
    """
    
    def __init__(self, ticket):
        self.ticket = ticket
        self.transport_type = ticket.type.lower()
        self.operator = getattr(ticket, 'operator', None)
    
    def get_cost(self) -> int:
        return self.ticket.price  # Same price as basic, no extra cost
    
    def get_description(self) -> str:
        return f"PREMIUM {self.ticket.type} ticket from {self.ticket.source} to {self.ticket.destination}"
    
    def get_features(self) -> list:
        # No automatic features - only add-ons will be added by decorators
        return ["Premium ticket (enables add-ons)"]