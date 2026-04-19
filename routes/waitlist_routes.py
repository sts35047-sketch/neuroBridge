from flask import Blueprint, render_template, session, redirect, url_for
from models import Recipient

waitlist_bp = Blueprint('waitlist_bp', __name__)

@waitlist_bp.route('/waitlist')
def view_waitlist():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))

    recipients = Recipient.query.filter_by(hospital_id=session['hospital_id']).all()
    
    waitlist_data = []
    
    for r in recipients:
        score = 0
        reasons = []
        
        # 1. Medical Urgency (Primary Factor)
        if r.urgency == 'High':
            score += 100
            reasons.append("Critical Urgency (+100)")
        elif r.urgency == 'Medium':
            score += 50
            reasons.append("Stable Urgency (+50)")
        else:
            score += 10
            reasons.append("Routine (+10)")
            
        # 2. Pediatric Priority (Children < 18 get priority)
        if r.age < 18:
            score += 30
            reasons.append("Pediatric Priority (+30)")
            
        # 3. Geriatric Consideration (Age > 75)
        elif r.age > 75:
            score += 10
            reasons.append("Geriatric Vulernability (+10)")
            
        waitlist_data.append({
            'recipient': r,
            'score': score,
            'breakdown': ", ".join(reasons)
        })
        
    # Sort by Score (Highest First)
    waitlist_data.sort(key=lambda x: x['score'], reverse=True)
    
    return render_template('waitlist.html', waitlist=waitlist_data)