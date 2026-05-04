"""
models/ticket_decorator.py
Decorator Abstract Class - Like Decorator class
"""

from models.ticket_component import TicketComponent

class TicketDecorator(TicketComponent):
    """Abstract Decorator - wraps the component"""
    
    def __init__(self, component: TicketComponent):
        self.component = component
    
    def get_cost(self) -> int:
        return self.component.get_cost()
    
    def get_description(self) -> str:
        return self.component.get_description()
    
    def get_features(self) -> list:
        return self.component.get_features()