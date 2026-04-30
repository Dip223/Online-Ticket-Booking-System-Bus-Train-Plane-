from abc import ABC, abstractmethod
from models.email_sender import send_email
from datetime import datetime
from config import DB


# ============= OBSERVER INTERFACE =============
class Observer(ABC):
    @abstractmethod
    def update(self, booking_data):
        pass


# ============= EMAIL OBSERVER =============
class EmailNotificationObserver(Observer):
    def update(self, booking_data):
        """Send email notification to user after booking"""
        try:
            user_email = booking_data.get('user_email')
            ticket = booking_data.get('ticket', {})
            
            if user_email:
                subject = "🎉 Booking Confirmation - Online Ticket System"
                body = f"""
Hello {booking_data.get('user_name', 'User')},

🎫 Your booking has been confirmed successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 BOOKING DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Booking ID: {booking_data.get('booking_id', 'N/A')}
Ticket Type: {ticket.get('type', 'N/A')}
From: {ticket.get('source', 'N/A')}
To: {ticket.get('destination', 'N/A')}
Price: {ticket.get('price', 'N/A')} BDT
Payment Method: {booking_data.get('payment', 'N/A')}
Operator: {booking_data.get('operator', 'N/A')}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for choosing Online Ticket System!

Best regards,
Online Ticket System Team
"""
                send_email(user_email, subject, body)
                print(f"✅ Email notification sent to {user_email}")
                
        except Exception as e:
            print(f"❌ Email notification failed: {e}")


# ============= WEBSITE OBSERVER =============
class WebsiteNotificationObserver(Observer):
    def update(self, booking_data):
        """Store notification in database for website display"""
        try:
            db = DB.get_db()
            
            # Create notification document
            notification = {
                "user_id": booking_data.get('user_id'),
                "user_name": booking_data.get('user_name'),
                "booking_id": booking_data.get('booking_id'),
                "message": f"✅ Booking confirmed! {booking_data.get('ticket', {}).get('type', 'Ticket')} booked from {booking_data.get('ticket', {}).get('source', 'N/A')} → {booking_data.get('ticket', {}).get('destination', 'N/A')}",
                "ticket_details": booking_data.get('ticket', {}),
                "payment": booking_data.get('payment'),
                "operator": booking_data.get('operator'),
                "read": False,
                "created_at": datetime.now(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Insert into notifications collection
            result = db.notifications.insert_one(notification)
            print(f"✅ Website notification stored for {booking_data.get('user_name')} (ID: {result.inserted_id})")
            
        except Exception as e:
            print(f"❌ Website notification failed: {e}")


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
        print(f"\n📢 Notifying {len(self._observers)} observers...")
        for observer in self._observers:
            observer.update(booking_data)