from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Message, Hospital

message_bp = Blueprint('message_bp', __name__)

@message_bp.route('/messages', methods=['GET', 'POST'])
def inbox():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    my_id = session['hospital_id']
    
    # Send Message
    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        msg = Message(sender_id=my_id, receiver_id=receiver_id, subject=subject, body=body)
        db.session.add(msg)
        db.session.commit()
        flash("Message Sent!", "success")
        return redirect(url_for('message_bp.inbox'))

    # Get Messages
    # Received
    received = db.session.query(Message, Hospital).join(Hospital, Message.sender_id == Hospital.id)\
        .filter(Message.receiver_id == my_id).order_by(Message.timestamp.desc()).all()
    
    # Sent
    sent = db.session.query(Message, Hospital).join(Hospital, Message.receiver_id == Hospital.id)\
        .filter(Message.sender_id == my_id).order_by(Message.timestamp.desc()).all()
    
    # List of other hospitals for dropdown
    hospitals = Hospital.query.filter(Hospital.id != my_id).all()

    return render_template('messages.html', received=received, sent=sent, hospitals=hospitals)