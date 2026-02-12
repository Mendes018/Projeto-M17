from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from Permissions import IsAdmin

reports_route = Blueprint('reports', __name__)

@reports_route.route('/', methods=['GET'])
@IsAdmin
def sales_per_user():
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('''SELECT d.name, c.Title, sum(a.paid_price) FROM tickets a LEFT JOIN sessions b On a.id_session=b.id LEFT JOIN events c on b.id_event=c.id LEFT JOIN users d on a.id_user=d.id GROUP BY d.name, c.Title''')
    sales_per_user = cursor.fetchall()
    cursor.execute('''SELECT c.title, b.session_date, sum(a.paid_price) FROM tickets a JOIN sessions b on a.id_session=b.id JOIN events c on b.id_event=c.id GROUP BY c.title, b.session_date''')
    sales_per_event = cursor.fetchall()
    dbconnection.close()
    return render_template('reports/dashboard.html', sales_per_user=sales_per_user, sales_per_event=sales_per_event)
