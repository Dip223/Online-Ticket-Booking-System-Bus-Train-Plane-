from flask import Blueprint, request, jsonify
from config import DB
from models.ticket_factory import TicketFactory

ticket = Blueprint("ticket", __name__)

@ticket.route('/add-ticket', methods=['POST'])
def add_ticket():
    data = request.json

    ticket_obj = TicketFactory.create_ticket(
        data['type'], data['source'], data['destination'], data['price']
    )

    db = DB.get_db()
    db.tickets.insert_one(ticket_obj.to_dict())

    return jsonify({"message": "Ticket added"})

@ticket.route('/tickets')
def get_tickets():
    db = DB.get_db()
    tickets = list(db.tickets.find())

    for t in tickets:
        t['_id'] = str(t['_id'])

    return jsonify(tickets)