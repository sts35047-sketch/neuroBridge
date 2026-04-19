from flask import Blueprint, request, redirect, url_for, session
from models import db, Recipient

# Create a "Blueprint" (a piece of the app)
recipient_bp = Blueprint('recipient_bp', __name__)

@recipient_bp.route('/add_recipient', methods=['POST'])
def add_recipient():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))

    new_recipient = Recipient(
        name=request.form['name'],
        age=request.form['age'],
        blood_group=request.form['blood_group'],
        organ=request.form['organ'],
        urgency=request.form['urgency'],
        phone=request.form['phone'],
        city=request.form['city'],
        hospital_id=session['hospital_id']
    )
    
    db.session.add(new_recipient)
    db.session.commit()
    
    return redirect(url_for('dashboard'))