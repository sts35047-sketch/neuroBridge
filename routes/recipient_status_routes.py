from flask import Blueprint, render_template, request, jsonify, session
from models import Recipient, Donor, db
from datetime import datetime

recipient_status_bp = Blueprint('recipient_status_bp', __name__)

@recipient_status_bp.route('/recipient/track/<phone>')
def track_recipient(phone):
    """Track recipient status by phone number"""
    recipient = Recipient.query.filter_by(phone=phone).first()
    
    if not recipient:
        return render_template('recipient_track.html', error="Recipient not found")
    
    # Get matching opportunities
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
    
    available_donors = Donor.query.filter(
        Donor.organ.ilike(recipient.organ),
        Donor.blood_group.in_(blood_compatibility.get(recipient.blood_group, []))
    ).all()
    
    # Calculate compatibility score
    matches = []
    for donor in available_donors:
        score = 0
        reasons = []
        
        if donor.blood_group == recipient.blood_group:
            score += 50
            reasons.append("Exact blood match")
        
        if donor.age and recipient.age:
            age_diff = abs(donor.age - recipient.age)
            if age_diff <= 10:
                score += 40
                reasons.append(f"Close age match (±{age_diff} years)")
            elif age_diff <= 20:
                score += 20
                reasons.append(f"Reasonable age difference")
        
        if donor.city and recipient.city and donor.city.lower() == recipient.city.lower():
            score += 30
            reasons.append("Same location")
        
        matches.append({
            'donor': donor,
            'score': score,
            'reasons': reasons
        })
    
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    return render_template('recipient_track.html', 
                         recipient=recipient,
                         matches=matches[:5],  # Top 5 matches
                         total_matches=len(available_donors))

@recipient_status_bp.route('/donor/track/<phone>')
def track_donor(phone):
    """Track donor status by phone number"""
    donor = Donor.query.filter_by(phone=phone).first()
    
    if not donor:
        return render_template('donor_track.html', error="Donor not found")
    
    # Find potential recipients
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
    
    compatible_recipients = Recipient.query.filter(
        Recipient.organ.ilike(donor.organ),
        Recipient.blood_group.in_(blood_compatibility.get(donor.blood_group, []))
    ).all()
    
    # Sort by urgency
    compatible_recipients.sort(key=lambda x: {'High': 3, 'Medium': 2, 'Low': 1}.get(x.urgency, 0), reverse=True)
    
    return render_template('donor_track.html',
                         donor=donor,
                         potential_recipients=compatible_recipients[:5],
                         total_recipients=len(compatible_recipients))

@recipient_status_bp.route('/api/recipient/notification', methods=['POST'])
def recipient_notification():
    """Send notification to recipient"""
    data = request.json
    phone = data.get('phone')
    
    recipient = Recipient.query.filter_by(phone=phone).first()
    if recipient:
        # Here you would integrate with SMS/Email service
        return jsonify({
            'success': True,
            'message': f'Notification sent to {recipient.name}'
        })
    
    return jsonify({'success': False, 'message': 'Recipient not found'})
