from flask import Blueprint, render_template, session, redirect, url_for
from models import db, Donor, Recipient
from sqlalchemy import func

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/analytics')
def view_analytics():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    h_id = session['hospital_id']
    
    # 1. Total Counts
    total_donors = Donor.query.filter_by(hospital_id=h_id).count()
    total_recipients = Recipient.query.filter_by(hospital_id=h_id).count()
    
    # 2. Blood Group Distribution (Donors vs Recipients)
    donor_blood = db.session.query(Donor.blood_group, func.count(Donor.id)).filter_by(hospital_id=h_id).group_by(Donor.blood_group).all()
    recipient_blood = db.session.query(Recipient.blood_group, func.count(Recipient.id)).filter_by(hospital_id=h_id).group_by(Recipient.blood_group).all()
    
    # Format for Chart.js
    all_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    d_data = {g: 0 for g in all_groups}
    r_data = {g: 0 for g in all_groups}
    
    for bg, count in donor_blood: d_data[bg] = count
    for bg, count in recipient_blood: r_data[bg] = count
    
    # 3. Urgency Breakdown
    urgency_stats = db.session.query(Recipient.urgency, func.count(Recipient.id)).filter_by(hospital_id=h_id).group_by(Recipient.urgency).all()
    u_labels = [x[0] for x in urgency_stats]
    u_values = [x[1] for x in urgency_stats]
    
    # 4. Organ Demand
    organ_stats = db.session.query(Recipient.organ, func.count(Recipient.id)).filter_by(hospital_id=h_id).group_by(Recipient.organ).all()
    o_labels = [x[0] for x in organ_stats]
    o_values = [x[1] for x in organ_stats]

    # 5. Supply vs Demand Trend (Mock data for 6 months)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    supply = [total_donors] * 6  # Mock: show current donors for each month
    demand = [total_recipients] * 6  # Mock: show current recipients for each month

    return render_template('analytics.html', 
                         total_d=total_donors, total_r=total_recipients,
                         bg_labels=all_groups, 
                         bg_d_values=list(d_data.values()), 
                         bg_r_values=list(r_data.values()),
                         u_labels=u_labels, u_values=u_values,
                         o_labels=o_labels, o_values=o_values,
                         months=months, supply=supply, demand=demand,
                         b_labels=all_groups, b_values=list(d_data.values()))