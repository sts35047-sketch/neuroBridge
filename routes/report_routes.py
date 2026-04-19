from flask import Blueprint, render_template, session, redirect, url_for
from models import Donor, Recipient
from datetime import datetime

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/generate_report/<int:donor_id>/<int:recipient_id>')
def generate_report(donor_id, recipient_id):
    if 'hospital_id' not in session:
        return redirect(url_for('login'))

    # Fetch the specific pair
    donor = Donor.query.get_or_404(donor_id)
    recipient = Recipient.query.get_or_404(recipient_id)

    # Re-calculate the Score for the Report
    score = 0
    # Base Match (Blood & Organ must match to even get here)
    score += 50
    
    if recipient.urgency == 'High':
        score += 30
    elif recipient.urgency == 'Medium':
        score += 15
        
    if donor.city.lower() == recipient.city.lower():
        score += 20
        
    # Get current date
    date_generated = datetime.now().strftime("%d %B, %Y - %H:%M")

    return render_template('match_report.html', 
                         donor=donor, 
                         recipient=recipient, 
                         score=score,
                         date=date_generated,
                         hospital_name=session['hospital_name'])