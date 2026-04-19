from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Hospital, Donor, Recipient, Notification, ActivityLog
from sqlalchemy import func

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin123':
            session['is_admin'] = True
            return redirect(url_for('admin_bp.dashboard'))
        else:
            return "Invalid Admin Credentials! <a href='/admin/login'>Try Again</a>"
            
    return render_template('admin_login.html')

@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_bp.login'))
        
    hospitals = Hospital.query.all()
    donors = Donor.query.all()
    recipients = Recipient.query.all()
    
    stats = {
        'h_count': len(hospitals),
        'd_count': len(donors),
        'r_count': len(recipients)
    }
    
    return render_template('admin_dashboard.html', 
                         hospitals=hospitals, 
                         donors=donors, 
                         recipients=recipients,
                         stats=stats)

@admin_bp.route('/global_matches')
def global_matches():
    if not session.get('is_admin'):
        return redirect(url_for('admin_bp.login'))

    donors = Donor.query.all()
    recipients = Recipient.query.all()
    hospitals = Hospital.query.all()
    hosp_map = {h.id: h for h in hospitals}

    matches = []
    blood_compatibility = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+']
    }

    for r in recipients:
        for d in donors:
            score = 0
            reasons = []

            if d.organ.lower() != r.organ.lower(): continue
            if r.blood_group not in blood_compatibility.get(d.blood_group, []): continue

            score += 50
            if r.urgency == 'High': score += 30; reasons.append("High Urgency")
            elif r.urgency == 'Medium': score += 15
            
            donor_hosp = hosp_map.get(d.hospital_id)
            recipient_hosp = hosp_map.get(r.hospital_id)
            
            if d.hospital_id == r.hospital_id:
                score += 10; reasons.append("Same Hospital")
            else:
                reasons.append(f"Cross-Hospital Match")

            if d.city.lower() == r.city.lower():
                score += 10; reasons.append("Same City")

            matches.append({
                'donor': d,
                'recipient': r,
                'donor_hospital': donor_hosp,
                'recipient_hospital': recipient_hosp,
                'score': score,
                'reasons': ", ".join(reasons)
            })

    matches.sort(key=lambda x: x['score'], reverse=True)
    return render_template('admin_matches.html', matches=matches)

# --- NEW: SEND NOTIFICATION ---
@admin_bp.route('/notify/<int:hospital_id>/<path:message>')
def notify_hospital(hospital_id, message):
    if not session.get('is_admin'):
        return redirect(url_for('admin_bp.login'))
        
    # Create Notification
    notif = Notification(hospital_id=hospital_id, message=message)
    db.session.add(notif)
    db.session.commit()
    
    return "Notification Sent!" # In a real app, use AJAX to avoid page reload

@admin_bp.route('/manage')
def manage():
    if not session.get('is_admin'):
        return redirect(url_for('admin_bp.login'))
    
    # System-wide statistics
    hospitals = Hospital.query.all()
    donors = Donor.query.all()
    recipients = Recipient.query.all()
    activity_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(50).all()
    
    stats = {
        'h_count': len(hospitals),
        'd_count': len(donors),
        'r_count': len(recipients),
        'total_matches': len([d for d in donors if d.hospital_id]),  # Count active donors
        'total_activity_logs': len(activity_logs)
    }
    
    return render_template('admin_manage.html', 
                         hospitals=hospitals, 
                         donors=donors, 
                         recipients=recipients,
                         activity_logs=activity_logs,
                         stats=stats)

@admin_bp.route('/analytics')
def admin_analytics():
    if not session.get('is_admin'):
        return redirect(url_for('admin_bp.login'))
    
    # Global analytics data
    donors = Donor.query.all()
    recipients = Recipient.query.all()
    
    # Blood group distribution for ALL donors
    blood_counts = db.session.query(Donor.blood_group, func.count(Donor.id)).group_by(Donor.blood_group).all()
    d_labels = [x[0] for x in blood_counts]
    d_values = [x[1] for x in blood_counts]
    
    # Urgency matrix for ALL recipients
    urgency_counts = db.session.query(Recipient.urgency, func.count(Recipient.id)).group_by(Recipient.urgency).all()
    r_labels = [x[0] for x in urgency_counts]
    r_values = [x[1] for x in urgency_counts]
    
    # Supply vs demand trend (last 6 months mock data)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    supply = [45, 52, 48, 61, 55, 58]
    demand = [60, 65, 72, 68, 75, 82]
    
    return render_template('admin_analytics.html',
                         d_labels=d_labels, d_values=d_values,
                         r_labels=r_labels, r_values=r_values,
                         months=months, supply=supply, demand=demand)

@admin_bp.route('/logistics')
def admin_logistics():
    if not session.get('is_admin'):
        return redirect(url_for('admin_bp.login'))
    
    # Global logistics view (all transports)
    return render_template('admin_logistics.html')

@admin_bp.route('/waitlist')
def admin_waitlist():
    if not session.get('is_admin'):
        return redirect(url_for('admin_bp.login'))
    
    # Global waitlist (all recipients)
    recipients = Recipient.query.order_by(Recipient.urgency.desc()).all()
    
    return render_template('admin_waitlist.html', recipients=recipients)

@admin_bp.route('/hospital_details', methods=['GET', 'POST'])
def hospital_details():
    if not session.get('is_admin'):
        return redirect(url_for('admin_bp.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':
            hospitals = Hospital.query.all()
            return render_template('admin_hospital_details.html', hospitals=hospitals)
        else:
            flash('Incorrect admin password. Access denied.')
            return redirect(url_for('admin_bp.hospital_details'))
    
    return render_template('admin_hospital_details_form.html')

@admin_bp.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))