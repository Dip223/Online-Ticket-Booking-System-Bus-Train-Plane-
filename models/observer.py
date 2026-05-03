from abc import ABC, abstractmethod
from datetime import datetime
from config import DB


# ============= OBSERVER INTERFACE =============
class Observer(ABC):
    @abstractmethod
    def update(self, booking_data):
        pass


# ============= WEBSITE NOTIFICATION OBSERVER ONLY (NO EMAIL) =============
class WebsiteNotificationObserver(Observer):
    def update(self, booking_data):
        """Store notification in database for website display"""
        try:
            db = DB.get_db()
            
            ticket = booking_data.get('ticket', {})
            
            # Create a clear notification message
            message = f"🎫 {ticket.get('type', 'Ticket')} booked from {ticket.get('source', 'N/A')} → {ticket.get('destination', 'N/A')}"
            
            # Create notification document with ALL details
            notification = {
                "user_id": booking_data.get('user_id'),
                "user_name": booking_data.get('user_name'),
                "booking_id": booking_data.get('booking_id'),
                "message": message,
                "ticket_type": ticket.get('type', 'N/A'),
                "source": ticket.get('source', 'N/A'),
                "destination": ticket.get('destination', 'N/A'),
                "price": ticket.get('price', 'N/A'),
                "payment": booking_data.get('payment', 'N/A'),
                "operator": booking_data.get('operator', 'N/A'),
                "seat_no": booking_data.get('seat_no', 'N/A'),
                "journey_date": booking_data.get('journey_date', 'N/A'),
                "departure_time": booking_data.get('departure_time', 'N/A'),
                "read": False,
                "created_at": datetime.utcnow().isoformat(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p")
            }
            
            # Insert into notifications collection
            result = db.notifications.insert_one(notification)
            print(f"✅ Notification stored for {booking_data.get('user_name')} (ID: {result.inserted_id})")
            
        except Exception as e:
            print(f"❌ Notification failed: {e}")


# ============= SUBJECT (OBSERVABLE) =============
class BookingSubject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"📌 Attached: {observer.__class__.__name__}")
    
    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"❌ Detached: {observer.__class__.__name__}")
    
    def notify(self, booking_data):
        print(f"\n📢 Notifying {len(self._observers)} observer(s)...")
        for observer in self._observers:
            observer.update(booking_data)


# Create singleton instance and attach website observer only
booking_subject = BookingSubject()
booking_subject.attach(WebsiteNotificationObserver())