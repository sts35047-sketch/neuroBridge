from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Hospital

settings_bp = Blueprint('settings_bp', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    hospital = Hospital.query.get(session['hospital_id'])

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            hospital.name = request.form['name']
            hospital.city = request.form['city']
            hospital.state = request.form['state']
            db.session.commit()
            session['hospital_name'] = hospital.name # Update session name
            flash("Profile Updated Successfully!", "success")
        
        elif action == 'change_password':
            current_pw = request.form['current_password']
            new_pw = request.form['new_password']
            
            if hospital.password == current_pw:
                hospital.password = new_pw
                db.session.commit()
                flash("Password Changed Successfully!", "success")
            else:
                flash("Incorrect Current Password!", "danger")

        return redirect(url_for('settings_bp.settings'))

    return render_template('settings.html', hospital=hospital)