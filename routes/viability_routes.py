from flask import Blueprint, render_template, session, redirect, url_for
from models import Donor, ActivityLog
from datetime import datetime, timedelta

viability_bp = Blueprint('viability_bp', __name__)

@viability_bp.route('/viability')
def view_viability():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    donors = Donor.query.filter_by(hospital_id=session['hospital_id']).all()
    viability_data = []
    
    # Standard Shelf Life in Hours
    shelf_life = {
        'kidney': 24, 'liver': 12, 'heart': 4, 
        'lung': 6, 'pancreas': 12, 'cornea': 24, 'eye': 24
    }
    
    now = datetime.now()
    
    for d in donors:
        # Find when this donor was added by checking Activity Logs
        # We look for "Added Donor" action for this hospital containing the donor's name
        log = ActivityLog.query.filter_by(hospital_id=session['hospital_id'], action="Added Donor")\
            .filter(ActivityLog.details.contains(d.name))\
            .order_by(ActivityLog.timestamp.desc()).first()
            
        # If log exists, use its time. If not (old data), assume added NOW (fresh).
        added_time = log.timestamp if log else now
        
        # Get Max Hours for this specific organ
        organ_key = d.organ.lower()
        # Default to 24h if organ not in list
        max_hours = next((val for key, val in shelf_life.items() if key in organ_key), 24)
        
        expires_at = added_time + timedelta(hours=max_hours)
        remaining = expires_at - now
        
        # Calculate breakdown
        total_seconds = remaining.total_seconds()
        hours_left = int(total_seconds / 3600)
        minutes_left = int((total_seconds % 3600) / 60)
        
        # Status Logic
        if total_seconds < 0:
            status = "EXPIRED"
            css = "danger"
            percent = 0
        elif hours_left < 2:
            status = "CRITICAL"
            css = "warning"
            percent = (total_seconds / (max_hours * 3600)) * 100
        else:
            status = "VIABLE"
            css = "success"
            percent = (total_seconds / (max_hours * 3600)) * 100
            
        viability_data.append({
            'name': d.name,
            'organ': d.organ,
            'added': added_time.strftime("%d %b %H:%M"),
            'expires': expires_at.strftime("%d %b %H:%M"),
            'h_left': hours_left,
            'm_left': minutes_left,
            'status': status,
            'css': css,
            'percent': int(percent)
        })
        
    return render_template('viability.html', data=viability_data)