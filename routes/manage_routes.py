from flask import Blueprint, redirect, url_for, session, request, render_template
from models import db, Donor, Recipient, ActivityLog

manage_bp = Blueprint('manage_bp', __name__)

@manage_bp.route('/delete/donor/<int:id>')
def delete_donor(id):
    if 'hospital_id' not in session: return redirect(url_for('login'))
        
    donor = Donor.query.get_or_404(id)
    if donor.hospital_id != session['hospital_id']: return "Unauthorized", 403
        
    name = donor.name
    db.session.delete(donor)
    
    # Log Action
    log = ActivityLog(hospital_id=session['hospital_id'], action="Deleted Donor", details=f"Name: {name}")
    db.session.add(log)
    
    db.session.commit()
    return redirect(url_for('dashboard'))

@manage_bp.route('/delete/recipient/<int:id>')
def delete_recipient(id):
    if 'hospital_id' not in session: return redirect(url_for('login'))
        
    recipient = Recipient.query.get_or_404(id)
    if recipient.hospital_id != session['hospital_id']: return "Unauthorized", 403
        
    name = recipient.name
    db.session.delete(recipient)

    # Log Action
    log = ActivityLog(hospital_id=session['hospital_id'], action="Deleted Recipient", details=f"Name: {name}")
    db.session.add(log)

    db.session.commit()
    return redirect(url_for('dashboard'))

@manage_bp.route('/edit/donor/<int:id>', methods=['GET', 'POST'])
def edit_donor(id):
    if 'hospital_id' not in session: return redirect(url_for('login'))
    
    donor = Donor.query.get_or_404(id)
    if donor.hospital_id != session['hospital_id']: return "Unauthorized", 403

    if request.method == 'POST':
        donor.name = request.form['name']
        donor.age = request.form['age']
        donor.blood_group = request.form['blood_group']
        donor.organ = request.form['organ']
        donor.phone = request.form['phone']
        donor.city = request.form['city']
        
        # Log Action
        log = ActivityLog(hospital_id=session['hospital_id'], action="Updated Donor", details=f"Name: {donor.name}")
        db.session.add(log)
        
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_donor.html', donor=donor)

@manage_bp.route('/edit/recipient/<int:id>', methods=['GET', 'POST'])
def edit_recipient(id):
    if 'hospital_id' not in session: return redirect(url_for('login'))
    
    recipient = Recipient.query.get_or_404(id)
    if recipient.hospital_id != session['hospital_id']: return "Unauthorized", 403

    if request.method == 'POST':
        recipient.name = request.form['name']
        recipient.age = request.form['age']
        recipient.blood_group = request.form['blood_group']
        recipient.organ = request.form['organ']
        recipient.urgency = request.form['urgency']
        recipient.phone = request.form['phone']
        recipient.city = request.form['city']
        
        # Log Action
        log = ActivityLog(hospital_id=session['hospital_id'], action="Updated Recipient", details=f"Name: {recipient.name}")
        db.session.add(log)

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_recipient.html', recipient=recipient)