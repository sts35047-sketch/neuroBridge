from flask import Blueprint, render_template, session, redirect, url_for
from models import Donor, Recipient

match_bp = Blueprint('match_bp', __name__)

@match_bp.route('/matches')
def view_matches():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))

    # Fetch all data for this hospital
    donors = Donor.query.filter_by(hospital_id=session['hospital_id']).all()
    recipients = Recipient.query.filter_by(hospital_id=session['hospital_id']).all()

    matches = []

    # Medical Logic: Key is Donor, Value is list of compatible Recipients
    # O- is Universal Donor, AB+ is Universal Recipient
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

    # The AI Loop
    for recipient in recipients:
        for donor in donors:
            score = 0
            reasons = []

            # Rule 1: Organ must match exactly
            if donor.organ.lower() != recipient.organ.lower():
                continue 

            # Rule 2: Blood Type must be compatible
            if recipient.blood_group not in blood_compatibility.get(donor.blood_group, []):
                continue

            # If we survive the first two rules, it's a Valid Match! Base Score: 50
            score += 50

            # Rule 3: Urgency Weight
            if recipient.urgency == 'High':
                score += 30
                reasons.append("High Urgency")
            elif recipient.urgency == 'Medium':
                score += 15
            
            # Rule 4: Location Weight (Logistics)
            if donor.city.lower() == recipient.city.lower():
                score += 20
                reasons.append("Same City")
            
            matches.append({
                'donor': donor,
                'recipient': recipient,
                'score': score,
                'reasons': ", ".join(reasons)
            })

    # Sort results so the best matches appear first
    matches.sort(key=lambda x: x['score'], reverse=True)

    return render_template('matches.html', matches=matches)
    