"""
models/ticket_component.py
Component Interface - Like SandwichOrder class
"""

from abc import ABC, abstractmethod

class TicketComponent(ABC):
    """Abstract Component - defines the base interface"""
    
    @abstractmethod
    def get_cost(self) -> int:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    def get_features(self) -> list:
        pass