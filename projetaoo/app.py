from flask import Flask, render_template, request, redirect, url_for, flash
from eventos_bilhetes import init_db
from routes.events import event_route
from routes.home import home_route
from routes.organizers import organizer_route
from routes.event_types import event_type_route
from routes.places import place_route
from routes.sessions import session_route
from routes.seats import seat_route
from routes.tickets import ticket_route
from routes.users import user_route
from routes.reports import reports_route




app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

init_db()
app.register_blueprint(home_route)
app.register_blueprint(event_route, url_prefix='/events')
app.register_blueprint(organizer_route, url_prefix='/organizers')
app.register_blueprint(event_type_route, url_prefix='/event_types')
app.register_blueprint(place_route, url_prefix='/places')
app.register_blueprint(session_route, url_prefix='/sessions')
app.register_blueprint(seat_route, url_prefix='/seats')
app.register_blueprint(ticket_route, url_prefix='/tickets')
app.register_blueprint(user_route, url_prefix='/users')
app.register_blueprint(reports_route, url_prefix='/reports')
if __name__ == '__main__':
    app.run()
