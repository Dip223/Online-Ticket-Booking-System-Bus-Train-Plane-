"""
models/ticket_factory.py
========================
FACTORY DESIGN PATTERN — Complete implementation matching lecture slides.

Based on the Battleship/Carrier/Destroyer example from Lecture 12.

Architecture (Same as slide):
┌─────────────────┐     ┌─────────────────┐
│   Ticket        │     │  TicketCreator  │ (Abstract Creator)
│ (Abstract       │     │  - factory_     │
│  Product)       │     │    method()     │
├─────────────────┤     └────────┬────────┘
│ +type           │              │
│ +get_info()     │       ┌──────┴──────┐
└────────┬────────┘       │             │
         │         ┌──────▼──────┐ ┌────▼───────────┐
    ┌────┴────┐    │BusTicket    │ │TrainTicket    │
    │         │    │Creator      │ │Creator        │
┌───▼───┐ ┌───▼───┐│(Concrete    │ │(Concrete      │
│ Bus   │ │ Train ││ Creator)    │ │ Creator)      │
│Ticket │ │Ticket │└─────────────┘ └───────────────┘
└───────┘ └───────┘
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: Abstract Product (Same as Battleship class in slide)
# ═══════════════════════════════════════════════════════════════════════════════

class Ticket(ABC):
    """
    Abstract Product - Same as Battleship class in slide.
    Defines the interface all concrete products must implement.
    """
    
    def __init__(self, source: str, destination: str, price: int):
        print(f"🎫 Ticket base created")  # Like "Battleship Created" in slide
        self.source = source
        self.destination = destination
        self.price = price
    
    @property
    @abstractmethod
    def type(self) -> str:
        """Every subclass must declare its transport type."""
        pass
    
    @abstractmethod
    def fire(self) -> None:
        """
        Corresponds to Fire() method in slide's Battleship class.
        Each ticket type has its own behavior.
        """
        pass
    
    @abstractmethod
    def steer(self) -> None:
        """
        Corresponds to Steer() method in slide's Battleship class.
        """
        pass
    
    @abstractmethod
    def get_info(self) -> str:
        """Human-readable description of this ticket."""
        pass
    
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "source": self.source,
            "destination": self.destination,
            "price": self.price,
            "info": self.get_info(),
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.source}→{self.destination} ৳{self.price}>"


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: Concrete Products (Same as Destroyer and Carrier in slide)
# ═══════════════════════════════════════════════════════════════════════════════

class BusTicket(Ticket):
    """Concrete Product - Same as Destroyer in slide"""
    
    def __init__(self, source: str, destination: str, price: int):
        super().__init__(source, destination, price)
        print(f"🚌 Bus Ticket Created")  # Like "Destroyer Created" in slide
    
    @property
    def type(self) -> str:
        return "Bus"
    
    def fire(self) -> None:
        """Bus-specific behavior"""
        print(f"🚌 Bus ticket booked from {self.source} to {self.destination}")
    
    def steer(self) -> None:
        print(f"🚌 Bus route: {self.source} → {self.destination}")
    
    def get_info(self) -> str:
        return f"Bus ticket from {self.source} to {self.destination}"


class TrainTicket(Ticket):
    """Concrete Product - Same as another ship type in slide"""
    
    def __init__(self, source: str, destination: str, price: int):
        super().__init__(source, destination, price)
        print(f"🚆 Train Ticket Created")
    
    @property
    def type(self) -> str:
        return "Train"
    
    def fire(self) -> None:
        print(f"🚆 Train ticket booked from {self.source} to {self.destination}")
    
    def steer(self) -> None:
        print(f"🚆 Train route: {self.source} → {self.destination}")
    
    def get_info(self) -> str:
        return f"Train ticket from {self.source} to {self.destination}"


class PlaneTicket(Ticket):
    """Concrete Product - Same as Carrier in slide"""
    
    def __init__(self, source: str, destination: str, price: int):
        super().__init__(source, destination, price)
        print(f"✈️ Plane Ticket Created")  # Like "Carrier Created" in slide
    
    @property
    def type(self) -> str:
        return "Plane"
    
    def fire(self) -> None:
        print(f"✈️ Plane ticket booked from {self.source} to {self.destination}")
    
    def steer(self) -> None:
        print(f"✈️ Flight route: {self.source} → {self.destination}")
    
    def get_info(self) -> str:
        return f"Air ticket from {self.source} to {self.destination}"


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: Abstract Creator (Same as ShipCreator class in slide)
# ═══════════════════════════════════════════════════════════════════════════════

class TicketCreator(ABC):
    """
    Abstract Creator - Same as ShipCreator class in slide.
    Declares the factory method that returns product objects.
    """
    
    @abstractmethod
    def factory_method(self, source: str, destination: str, price: int) -> Ticket:
        """
        Factory Method - Same as FactoryMethod() in slide.
        Returns a Ticket object (Product).
        """
        pass
    
    def create_ticket(self, source: str, destination: str, price: int) -> Ticket:
        """
        Template method - Same as CreateShip() in slide.
        This method uses the factory method to create a product.
        """
        print(f"\n🏭 Creating ticket via Creator...")
        ticket = self.factory_method(source, destination, price)
        return ticket


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: Concrete Creators (Same as CarrierCreator and DestroyerCreator in slide)
# ═══════════════════════════════════════════════════════════════════════════════

class BusTicketCreator(TicketCreator):
    """
    Concrete Creator - Same as DestroyerCreator in slide.
    Creates BusTicket objects.
    """
    
    def factory_method(self, source: str, destination: str, price: int) -> BusTicket:
        print(f"🏭 BusTicketCreator: Creating Bus ticket")
        return BusTicket(source, destination, price)


class TrainTicketCreator(TicketCreator):
    """
    Concrete Creator - Creates TrainTicket objects.
    """
    
    def factory_method(self, source: str, destination: str, price: int) -> TrainTicket:
        print(f"🏭 TrainTicketCreator: Creating Train ticket")
        return TrainTicket(source, destination, price)


class PlaneTicketCreator(TicketCreator):
    """
    Concrete Creator - Same as CarrierCreator in slide.
    Creates PlaneTicket objects.
    """
    
    def factory_method(self, source: str, destination: str, price: int) -> PlaneTicket:
        print(f"🏭 PlaneTicketCreator: Creating Plane ticket")
        return PlaneTicket(source, destination, price)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: Factory Registry (Singleton) - Same as PizzaFactoryRegistry in slide
# ═══════════════════════════════════════════════════════════════════════════════

class TicketFactoryRegistry:
    """
    Singleton Factory Registry - Same as PizzaFactoryRegistry in slide.
    Manages all registered creators.
    """
    
    _instance = None
    _creators: Dict[str, TicketCreator] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            print("🏭 TicketFactoryRegistry Created (Singleton)")
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance - same as slide's getInstance()"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_creator(self, ticket_type: str, creator: TicketCreator) -> None:
        """Register a creator - same as slide's registerFactory()"""
        self._creators[ticket_type.lower()] = creator
        print(f"✅ Registered creator for: {ticket_type}")
    
    def get_creator(self, ticket_type: str) -> Optional[TicketCreator]:
        """Get creator - same as slide's getFactory()"""
        return self._creators.get(ticket_type.lower())
    
    def get_available_types(self) -> list:
        """Get all registered ticket types"""
        return list(self._creators.keys())


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6: Ticket Store (Client) - Same as PizzaStore in slide
# ═══════════════════════════════════════════════════════════════════════════════

class TicketStore:
    """
    Ticket Store - Same as PizzaStore in slide.
    Uses the registry to get creators and order tickets.
    """
    
    def __init__(self):
        self.registry = TicketFactoryRegistry.get_instance()
    
    def order_ticket(self, ticket_type: str, source: str, destination: str, price: int) -> Ticket:
        """
        Order a ticket - Same as orderPizza() in slide.
        Uses registry to find the right creator.
        """
        print(f"\n📞 Customer ordered: {ticket_type}")
        
        creator = self.registry.get_creator(ticket_type)
        
        if creator is None:
            available = self.registry.get_available_types()
            raise ValueError(f"Unknown ticket type: {ticket_type}. Available: {available}")
        
        ticket = creator.create_ticket(source, destination, price)
        
        # Call the product methods (like Fire() and Steer() in slide)
        ticket.fire()
        ticket.steer()
        
        return ticket


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 7: Simple Factory (For backward compatibility with existing code)
# ═══════════════════════════════════════════════════════════════════════════════

class SimpleTicketFactory:
    """
    Simple Factory - For backward compatibility with existing booking code.
    This provides the same interface as your original TicketFactory.
    """
    
    @staticmethod
    def create_ticket(transport_type: str, source: str, destination: str, price: int) -> Ticket:
        """Simple factory method - compatible with existing code"""
        registry = TicketFactoryRegistry.get_instance()
        creator = registry.get_creator(transport_type)
        
        if creator is None:
            raise ValueError(f"Unknown ticket type: {transport_type}")
        
        return creator.factory_method(source, destination, price)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 8: Auto-registration (Runs on import) - Same as slide's registration
# ═══════════════════════════════════════════════════════════════════════════════

def _register_all_creators():
    """Register all concrete creators - happens automatically on import"""
    registry = TicketFactoryRegistry.get_instance()
    registry.register_creator("bus", BusTicketCreator())
    registry.register_creator("train", TrainTicketCreator())
    registry.register_creator("plane", PlaneTicketCreator())
    print("🎉 All ticket creators registered successfully!")


# Run registration on module import
_register_all_creators()


# ═══════════════════════════════════════════════════════════════════════════════
# Backward Compatibility
# ═══════════════════════════════════════════════════════════════════════════════

# For existing code that imports TicketFactory
TicketFactory = SimpleTicketFactory


# ═══════════════════════════════════════════════════════════════════════════════
# Demo (Same as slide's main() function)
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("FACTORY PATTERN DEMO - Same as slide's Battleship example")
    print("="*60)
    
    # Method 1: Using Ticket Store (Same as slide's PizzaStore)
    print("\n📦 Using TicketStore (like PizzaStore in slide):")
    store = TicketStore()
    
    # Order Bus Ticket
    bus_ticket = store.order_ticket("bus", "Dhaka", "Chittagong", 800)
    print(f"   Result: {bus_ticket.get_info()}")
    
    # Order Train Ticket
    train_ticket = store.order_ticket("train", "Dhaka", "Sylhet", 700)
    print(f"   Result: {train_ticket.get_info()}")
    
    # Order Plane Ticket
    plane_ticket = store.order_ticket("plane", "Dhaka", "Cox's Bazar", 5000)
    print(f"   Result: {plane_ticket.get_info()}")
    
    # Method 2: Using Simple Factory (Compatible with existing code)
    print("\n📦 Using SimpleTicketFactory (compatible with old code):")
    ticket = SimpleTicketFactory.create_ticket("bus", "Dhaka", "Rajshahi", 650)
    print(f"   Result: {ticket.get_info()}")
    
    # Method 3: Direct Creator usage (Same as slide's CarrierCreator/DestroyerCreator)
    print("\n📦 Using Direct Creator (like CarrierCreator in slide):")
    creator = BusTicketCreator()
    ticket = creator.create_ticket("Dhaka", "Barishal", 600)
    ticket.fire()
    ticket.steer()
    
    print("\n" + "="*60)
    print("✅ Factory Pattern Demo Complete!")
    print("="*60)