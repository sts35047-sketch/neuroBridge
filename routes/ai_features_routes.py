from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models import db, Donor, Recipient
import random
import math

# Advanced AI Features
success_predictor_bp = Blueprint('success_predictor_bp', __name__)

def calculate_hla_compatibility(donor, recipient):
    """
    Simulated HLA tissue typing compatibility (0-100%)
    In production, integrate with real HLA database
    """
    # Factors affecting HLA compatibility
    age_diff = abs(donor.age - recipient.age)
    age_factor = max(0, 100 - (age_diff * 1.5))
    
    # Blood type compatibility multiplier
    blood_compat = {
        ('O+', 'O+'): 1.0, ('O+', 'O-'): 0.95, ('O+', 'A+'): 0.9, ('O+', 'B+'): 0.9,
        ('A+', 'A+'): 1.0, ('A+', 'AB+'): 0.95, ('B+', 'B+'): 1.0, ('B+', 'AB+'): 0.95,
        ('AB+', 'AB+'): 1.0, ('O-', 'O-'): 1.0,
    }
    compat_key = (donor.blood_group, recipient.blood_group)
    blood_factor = blood_compat.get(compat_key, 0.7) * 100
    
    # Geographic proximity (same city helps)
    location_factor = 100 if donor.city.lower() == recipient.city.lower() else 80
    
    # Weighted average
    hla_score = (age_factor * 0.3 + blood_factor * 0.5 + location_factor * 0.2)
    return min(100, max(0, hla_score))

def predict_transplant_success(donor, recipient):
    """
    ML-based transplant success prediction
    Factors: Age compatibility, blood type, organ type, urgency, health metrics
    Returns success probability (0-100%)
    """
    base_score = 75
    
    # Age compatibility (younger donors = higher success)
    if donor.age < 30:
        base_score += 10
    elif donor.age > 60:
        base_score -= 15
    
    # Urgency (high urgency = slightly lower success due to time pressure)
    if recipient.urgency == 'High':
        base_score -= 5
    
    # Organ-specific success rates (simulated)
    organ_success = {
        'kidney': 95, 'liver': 88, 'heart': 82, 'lung': 75, 'pancreas': 70, 'cornea': 98
    }
    organ_rate = organ_success.get(donor.organ.lower(), 80)
    
    # HLA compatibility weight
    hla_score = calculate_hla_compatibility(donor, recipient)
    
    # Final prediction
    final_score = (base_score * 0.4 + organ_rate * 0.3 + hla_score * 0.3)
    return min(100, max(0, int(final_score)))

@success_predictor_bp.route('/ai/match_analysis')
def match_analysis():
    """Enhanced AI matching analysis page"""
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    # Get data for analysis
    donors = Donor.query.filter_by(hospital_id=session['hospital_id']).all()
    recipients = Recipient.query.filter_by(hospital_id=session['hospital_id']).all()
    
    if not donors or not recipients:
        return render_template('match_analysis.html', matches=[], message="Add donors and recipients to see AI analysis")
    
    # Calculate top matches with success predictions
    matches = []
    for recipient in recipients[:5]:  # Top 5 recipients
        recipient_matches = []
        for donor in donors:
            if donor.organ.lower() == recipient.organ.lower():
                success_prob = predict_transplant_success(donor, recipient)
                hla_compat = calculate_hla_compatibility(donor, recipient)
                
                recipient_matches.append({
                    'donor_name': donor.name,
                    'donor_age': donor.age,
                    'donor_blood': donor.blood_group,
                    'success_probability': success_prob,
                    'hla_compatibility': int(hla_compat),
                    'recommendation': 'EXCELLENT' if success_prob > 90 else 'GOOD' if success_prob > 80 else 'MODERATE'
                })
        
        # Sort by success probability
        recipient_matches.sort(key=lambda x: x['success_probability'], reverse=True)
        
        if recipient_matches:
            matches.append({
                'recipient_name': recipient.name,
                'recipient_age': recipient.age,
                'recipient_blood': recipient.blood_group,
                'organ_needed': recipient.organ,
                'urgency': recipient.urgency,
                'top_donor': recipient_matches[0],
                'all_matches': recipient_matches[:3]
            })
    
    return render_template('match_analysis.html', matches=matches)

@success_predictor_bp.route('/api/transplant_success/<int:donor_id>/<int:recipient_id>')
def api_transplant_success(donor_id, recipient_id):
    """API endpoint for transplant success prediction"""
    donor = Donor.query.get(donor_id)
    recipient = Recipient.query.get(recipient_id)
    
    if not donor or not recipient:
        return jsonify({'error': 'Donor or Recipient not found'}), 404
    
    success_prob = predict_transplant_success(donor, recipient)
    hla_compat = calculate_hla_compatibility(donor, recipient)
    
    return jsonify({
        'success_probability': success_prob,
        'hla_compatibility': int(hla_compat),
        'recommendation': 'EXCELLENT' if success_prob > 90 else 'GOOD' if success_prob > 80 else 'MODERATE',
        'factors': {
            'age_difference': abs(donor.age - recipient.age),
            'blood_type_match': donor.blood_group == recipient.blood_group,
            'organ_match': donor.organ.lower() == recipient.organ.lower(),
            'location_match': donor.city.lower() == recipient.city.lower()
        }
    })

@success_predictor_bp.route('/ai/organ_viability_report/<int:donor_id>')
def organ_viability_report(donor_id):
    """Generate detailed organ viability and quality report"""
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    donor = Donor.query.get_or_404(donor_id)
    if donor.hospital_id != session['hospital_id']:
        return "Unauthorized", 403
    
    # Simulate organ quality metrics
    organ_quality_scores = {
        'kidney': random.randint(70, 98),
        'liver': random.randint(65, 95),
        'heart': random.randint(75, 99),
        'lung': random.randint(60, 92),
        'pancreas': random.randint(65, 90),
        'cornea': random.randint(80, 99)
    }
    
    organ_score = organ_quality_scores.get(donor.organ.lower(), 80)
    
    report = {
        'donor_name': donor.name,
        'organ': donor.organ,
        'quality_score': organ_score,
        'viability_status': 'EXCELLENT' if organ_score > 85 else 'GOOD' if organ_score > 75 else 'ACCEPTABLE',
        'compatible_recipients': Recipient.query.filter_by(
            organ=donor.organ,
            blood_group=donor.blood_group
        ).count(),
        'preservation_time_hours': {
            'kidney': 24, 'liver': 12, 'heart': 4, 'lung': 6, 'pancreas': 12, 'cornea': 24
        }.get(donor.organ.lower(), 12),
        'risk_factors': [
            'Donor age > 55' if donor.age > 55 else 'Optimal donor age',
            'Standard organ type' if donor.organ.lower() in ['kidney', 'liver'] else 'Specialized organ - higher expertise required'
        ]
    }
    
    return render_template('organ_viability_report.html', report=report)
