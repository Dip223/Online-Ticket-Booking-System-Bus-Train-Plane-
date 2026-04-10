class Ticket:
    def __init__(self, type, source, destination, price):
        self.type = type
        self.source = source
        self.destination = destination
        self.price = price

    def to_dict(self):
        return self.__dict__


class BusTicket(Ticket):
    def __init__(self, source, destination, price):
        super().__init__("Bus", source, destination, price)


class TrainTicket(Ticket):
    def __init__(self, source, destination, price):
        super().__init__("Train", source, destination, price)


class PlaneTicket(Ticket):
    def __init__(self, source, destination, price):
        super().__init__("Plane", source, destination, price)


class TicketFactory:
    @staticmethod
    def create_ticket(type, source, destination, price):
        type = type.lower()  # ✅ FIX (very important)

        if type == "bus":
            return BusTicket(source, destination, price)
        elif type == "train":
            return TrainTicket(source, destination, price)
        elif type == "plane":
            return PlaneTicket(source, destination, price)
        else:
            raise ValueError("Invalid ticket type")