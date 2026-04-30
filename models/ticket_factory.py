"""
models/ticket_factory.py
========================
TRUE FACTORY DESIGN PATTERN — No if/elif/else chains.

Classic Factory Pattern uses a REGISTRY (dictionary) that maps
type keys to concrete classes. This is the professional way:
  - Open/Closed Principle: add new ticket types without touching factory code
  - No conditionals — purely polymorphic dispatch
  - Each ticket class registers itself

Architecture:
  Ticket (Abstract Base)
    ├── BusTicket
    ├── TrainTicket
    └── PlaneTicket
  TicketFactory (Creator)
    └── uses _registry dict to instantiate correct class
"""

from abc import ABC, abstractmethod


# ── Abstract Product ──────────────────────────────────────────────────────────

class Ticket(ABC):
    """
    Abstract base class for all ticket types.
    Defines the interface every concrete ticket must implement.
    """

    def __init__(self, source: str, destination: str, price: int):
        self.source      = source
        self.destination = destination
        self.price       = price

    @property
    @abstractmethod
    def type(self) -> str:
        """Every subclass must declare its transport type."""
        ...

    @abstractmethod
    def get_info(self) -> str:
        """Human-readable description of this ticket."""
        ...

    def to_dict(self) -> dict:
        return {
            "type":        self.type,
            "source":      self.source,
            "destination": self.destination,
            "price":       self.price,
            "info":        self.get_info(),
        }

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.source}→{self.destination} ৳{self.price}>"


# ── Concrete Products ─────────────────────────────────────────────────────────

class BusTicket(Ticket):
    @property
    def type(self) -> str:
        return "Bus"

    def get_info(self) -> str:
        return f"Bus ticket from {self.source} to {self.destination}"


class TrainTicket(Ticket):
    @property
    def type(self) -> str:
        return "Train"

    def get_info(self) -> str:
        return f"Train ticket from {self.source} to {self.destination}"


class PlaneTicket(Ticket):
    @property
    def type(self) -> str:
        return "Plane"

    def get_info(self) -> str:
        return f"Air ticket from {self.source} to {self.destination}"


# ── Factory (Creator) ─────────────────────────────────────────────────────────

class TicketFactory:
    """
    Factory Pattern — Registry-based, NO if/else.

    The _registry maps string keys → concrete Ticket classes.
    create_ticket() looks up the registry and instantiates the
    correct class. To add a new transport type, just call
    TicketFactory.register() — zero changes to existing code.

    This satisfies the Open/Closed Principle.
    """

    _registry: dict[str, type[Ticket]] = {}

    @classmethod
    def register(cls, transport_type: str, ticket_class: type[Ticket]) -> None:
        """Register a new ticket class under a transport key."""
        cls._registry[transport_type.lower()] = ticket_class

    @classmethod
    def create_ticket(cls, transport_type: str, source: str,
                      destination: str, price: int) -> Ticket:
        """
        Factory method: look up the registry and create the ticket.
        Raises KeyError if the type is not registered.
        """
        key = transport_type.lower().strip()
        ticket_class = cls._registry.get(key)
        if ticket_class is None:
            available = list(cls._registry.keys())
            raise KeyError(
                f"Unknown ticket type '{transport_type}'. "
                f"Available: {available}"
            )
        return ticket_class(source, destination, price)

    @classmethod
    def available_types(cls) -> list[str]:
        """Return all registered transport types."""
        return list(cls._registry.keys())


# ── Self-registration (runs on import) ───────────────────────────────────────
# Each concrete class registers itself — factory code never needs to change.

TicketFactory.register("bus",   BusTicket)
TicketFactory.register("train", TrainTicket)
TicketFactory.register("plane", PlaneTicket)