from flask import Blueprint, render_template, session, redirect, url_for
from models import Donor, Recipient
import datetime

card_bp = Blueprint('card_bp', __name__)

@card_bp.route('/generate_card/<type>/<int:id>')
def generate_card(type, id):
    if 'hospital_id' not in session:
        return redirect(url_for('login'))

    person = None
    role = ""
    color_theme = ""

    if type == 'donor':
        person = Donor.query.get_or_404(id)
        role = "OFFICIAL DONOR"
        color_theme = "success" # Green
    elif type == 'recipient':
        person = Recipient.query.get_or_404(id)
        role = "RECIPIENT WAITING"
        color_theme = "primary" # Blue

    # Generate a fake QR code string (just for visuals)
    qr_data = f"NB-{type.upper()}-{id}-{person.blood_group}"
    
    date_issued = datetime.datetime.now().strftime("%d %b %Y")

    return render_template('id_card.html', 
                         person=person, 
                         role=role, 
                         color=color_theme,
                         hospital_name=session['hospital_name'],
                         date=date_issued,
                         qr_data=qr_data)