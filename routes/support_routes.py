from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Notification, Hospital

support_bp = Blueprint('support_bp', __name__)

@support_bp.route('/support', methods=['GET', 'POST'])
def support_center():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))

    hospital_id = session['hospital_id']
    hospital = Hospital.query.get(hospital_id)

    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Create a "Support Ticket" using the Notification model
        # We prefix the message with "SUPPORT:" to distinguish it
        full_message = f"SUPPORT TICKET from {hospital.name}: [{subject}] {message}"
        
        # In a real app, this might go to an Admin user's ID (e.g., 1)
        # For this demo, we'll save it to the current user's notifications so they can see their history
        # And we'll also save a copy for the "Admin" (assuming admin is a special hospital or just logging it)
        
        # 1. Save for User (History)
        user_ticket = Notification(
            hospital_id=hospital_id,
            message=f"Ticket Submitted: {subject}",
            is_read=True 
        )
        db.session.add(user_ticket)
        
        # 2. Save for Admin (We'll simulate this by adding a log or a specific admin notification if an admin user existed)
        # For now, let's just log it to the console for the "Admin"
        print(f"--- NEW SUPPORT TICKET ---\nFrom: {hospital.name}\nSubject: {subject}\nMessage: {message}\n--------------------------")

        db.session.commit()
        flash("Support ticket submitted successfully!", "success")
        return redirect(url_for('support_bp.support_center'))

    # Fetch past tickets (Notifications starting with "Ticket Submitted:")
    tickets = Notification.query.filter_by(hospital_id=hospital_id).filter(Notification.message.like('Ticket Submitted:%')).order_by(Notification.date.desc()).all()

    return render_template('support.html', tickets=tickets)     