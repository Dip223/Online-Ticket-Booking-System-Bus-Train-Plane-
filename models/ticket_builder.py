from abc import ABC, abstractmethod
from datetime import datetime


class TicketView:
    """
    Product class.
    This is the final ticket object shown in the UI.
    """

    def __init__(self):
        self.ticket_id = ""
        self.title = ""
        self.subtitle = ""
        self.transport_type = ""
        self.theme = ""
        self.icon = ""
        self.route_line = ""
        self.status = "CONFIRMED"
        self.issue_time = ""
        self.footer_note = ""
        self.ticket_code = ""
        self.sections = []

    def add_section(self, title: str, rows: dict):
        self.sections.append({
            "title": title,
            "rows": rows
        })

    def to_dict(self):
        return {
            "ticket_id": self.ticket_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "transport_type": self.transport_type,
            "theme": self.theme,
            "icon": self.icon,
            "route_line": self.route_line,
            "status": self.status,
            "issue_time": self.issue_time,
            "footer_note": self.footer_note,
            "ticket_code": self.ticket_code,
            "sections": self.sections,
        }


class TicketBuilder(ABC):
    """
    Abstract Builder class.
    It defines the steps for building a complete ticket.
    """

    def __init__(self):
        self.product = TicketView()

    def reset(self):
        self.product = TicketView()

    @abstractmethod
    def add_header(self, booking_doc: dict, user_doc: dict):
        pass

    def add_passenger_info(self, booking_doc: dict, user_doc: dict):
        self.product.add_section("Passenger Information", {
            "Passenger Name": user_doc.get("name", "Passenger"),
            "Email": user_doc.get("email", "N/A"),
            "User ID": str(booking_doc.get("user_id", "N/A")),
        })

    def add_journey_info(self, booking_doc: dict, user_doc: dict):
        ticket = booking_doc.get("ticket", {})

        source = ticket.get("source", "N/A")
        destination = ticket.get("destination", "N/A")

        self.product.route_line = f"{source} → {destination}"

        self.product.add_section("Journey Information", {
            "From": source,
            "To": destination,
            "Journey Date": booking_doc.get("journey_date", "N/A"),
            "Departure Time": booking_doc.get("departure_time", "N/A"),
            "Operator": booking_doc.get("operator", "N/A"),
        })

    def add_seat_info(self, booking_doc: dict, user_doc: dict):
        self.product.add_section("Seat Information", {
            "Selected Seat": booking_doc.get("seat_no", "N/A"),
            "Seat Class": booking_doc.get("seat_class", "N/A"),
            "Layout": booking_doc.get("seat_layout", "N/A"),
        })

    def add_fare_info(self, booking_doc: dict, user_doc: dict):
        ticket = booking_doc.get("ticket", {})

        self.product.add_section("Fare Information", {
            "Ticket Fare": f"৳{ticket.get('price', 0)}",
            "Payment": "Not included in this module",
        })

    @abstractmethod
    def add_transport_specific_info(self, booking_doc: dict, user_doc: dict):
        pass

    @abstractmethod
    def add_ticket_style(self):
        pass

    def add_footer(self, booking_doc: dict, user_doc: dict):
        self.product.issue_time = datetime.now().strftime("%d %b %Y, %I:%M %p")
        self.product.ticket_code = self.product.ticket_id

    def return_product(self):
        final_ticket = self.product
        self.reset()
        return final_ticket


class BusTicketBuilder(TicketBuilder):
    """
    Concrete Builder for Bus ticket.
    """

    def add_header(self, booking_doc, user_doc):
        booking_id = str(booking_doc.get("_id", ""))[-8:].upper()

        self.product.ticket_id = f"BUS-{booking_id}"
        self.product.title = "BUS E-TICKET"
        self.product.subtitle = "36 Seat Bus Ticket Confirmation"
        self.product.transport_type = "Bus"
        self.product.icon = "fa-bus"

    def add_transport_specific_info(self, booking_doc, user_doc):
        self.product.add_section("Bus Details", {
            "Bus Operator": booking_doc.get("operator", "N/A"),
            "Seat Layout": "36 seats, 2 × 2 layout",
            "Boarding Point": booking_doc.get("boarding_point", "Main Counter"),
            "Reporting Time": "30 minutes before departure",
        })

    def add_ticket_style(self):
        self.product.theme = "bus"
        self.product.footer_note = "Please arrive at the bus counter at least 30 minutes before departure."


class TrainTicketBuilder(TicketBuilder):
    """
    Concrete Builder for Train ticket.
    """

    def add_header(self, booking_doc, user_doc):
        booking_id = str(booking_doc.get("_id", ""))[-8:].upper()

        self.product.ticket_id = f"TRN-{booking_id}"
        self.product.title = "TRAIN E-TICKET"
        self.product.subtitle = "Six Bogie Train Ticket Confirmation"
        self.product.transport_type = "Train"
        self.product.icon = "fa-train"

    def add_transport_specific_info(self, booking_doc, user_doc):
        seat_no = booking_doc.get("seat_no", "N/A")

        bogie_name = "N/A"
        if isinstance(seat_no, str) and seat_no.startswith("B") and "-" in seat_no:
            bogie_code = seat_no.split("-")[0]   # Example: B3
            bogie_name = bogie_code.replace("B", "Bogie ")

        self.product.add_section("Train Details", {
            "Train Name": booking_doc.get("operator", "N/A"),
            "Selected Bogie": bogie_name,
            "Total Bogies": "6 Bogies",
            "Coach Type": booking_doc.get("seat_class", "N/A"),
            "ID Requirement": "Carry a valid ID card",
        })

    def add_ticket_style(self):
        self.product.theme = "train"
        self.product.footer_note = "Carry a valid ID card during the train journey."

class PlaneTicketBuilder(TicketBuilder):
    """
    Concrete Builder for Plane ticket.
    """

    def add_header(self, booking_doc, user_doc):
        booking_id = str(booking_doc.get("_id", ""))[-8:].upper()

        self.product.ticket_id = f"AIR-{booking_id}"
        self.product.title = "PLANE E-TICKET"
        self.product.subtitle = "Business / Economy Class Flight Ticket Confirmation"
        self.product.transport_type = "Plane"
        self.product.icon = "fa-plane"

    def add_transport_specific_info(self, booking_doc, user_doc):
        self.product.add_section("Flight Details", {
            "Airline": booking_doc.get("operator", "N/A"),
            "Selected Class": booking_doc.get("seat_class", "N/A"),
            "Available Classes": "Business and Economy",
            "Gate": booking_doc.get("gate_no", "Gate 1"),
            "Check-in": "Closes 45 minutes before departure",
        })

    def add_ticket_style(self):
        self.product.theme = "plane"
        self.product.footer_note = "Check-in closes 45 minutes before flight departure."

class TicketDirector:
    """
    Director class.
    It controls the order of ticket construction.
    """

    def __init__(self):
        self.builder = None

    def set_builder_type(self, builder):
        self.builder = builder

    def construct_ticket(self, booking_doc, user_doc):
        if self.builder is None:
            raise ValueError("Ticket builder is not selected.")

        self.builder.reset()
        self.builder.add_header(booking_doc, user_doc)
        self.builder.add_passenger_info(booking_doc, user_doc)
        self.builder.add_journey_info(booking_doc, user_doc)
        self.builder.add_seat_info(booking_doc, user_doc)
        self.builder.add_fare_info(booking_doc, user_doc)
        self.builder.add_transport_specific_info(booking_doc, user_doc)
        self.builder.add_ticket_style()
        self.builder.add_footer(booking_doc, user_doc)

        return self.builder.return_product()


def get_ticket_builder(transport_type: str):
    builders = {
        "bus": BusTicketBuilder,
        "train": TrainTicketBuilder,
        "plane": PlaneTicketBuilder,
    }

    builder_class = builders.get(str(transport_type).lower().strip())

    if builder_class is None:
        raise KeyError(f"No ticket builder found for type: {transport_type}")

    return builder_class()