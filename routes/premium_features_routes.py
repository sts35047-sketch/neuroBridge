"""
Premium Features Routes - Real-time Notifications, KPIs, Smart Recommendations
"""
from flask import Blueprint, render_template, request, jsonify, session
from models import db, Donor, Recipient, Notification, Hospital, ActivityLog, Message
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json

premium_bp = Blueprint('premium', __name__)

# ============= REAL-TIME NOTIFICATIONS DASHBOARD =============
@premium_bp.route('/notifications/dashboard')
def notifications_dashboard():
    """Real-time notifications hub with filtering and priority levels"""
    try:
        # Get all notifications ordered by recency
        notifications = db.session.query(Notification).order_by(desc(Notification.timestamp)).limit(50).all()
        
        # Count by status
        unread_count = db.session.query(Notification).filter_by(is_read=False).count()
        critical_count = db.session.query(Notification).filter(
            Notification.priority == 'critical'
        ).count()
        
        # Group by type
        notifications_by_type = {}
        for notif in notifications:
            notif_type = notif.type or 'system'
            if notif_type not in notifications_by_type:
                notifications_by_type[notif_type] = []
            notifications_by_type[notif_type].append({
                'id': notif.id,
                'message': notif.message,
                'priority': notif.priority,
                'is_read': notif.is_read,
                'timestamp': notif.timestamp,
                'type': notif_type
            })
        
        return render_template('premium/notifications_dashboard.html',
                             notifications=notifications,
                             unread_count=unread_count,
                             critical_count=critical_count,
                             notifications_by_type=notifications_by_type)
    except Exception as e:
        return render_template('premium/notifications_dashboard.html', error=str(e))

# ============= PERFORMANCE KPI DASHBOARD =============
@premium_bp.route('/kpi/performance')
def performance_kpi():
    """Comprehensive performance metrics and KPIs"""
    try:
        # Total counts
        total_donors = db.session.query(func.count(Donor.id)).scalar() or 0
        total_recipients = db.session.query(func.count(Recipient.id)).scalar() or 0
        total_hospitals = db.session.query(func.count(Hospital.id)).scalar() or 0
        
        # Active records (registered < 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_donors = db.session.query(func.count(Donor.id)).filter(
            Donor.registered_date >= thirty_days_ago
        ).scalar() or 0
        active_recipients = db.session.query(func.count(Recipient.id)).filter(
            Recipient.registered_date >= thirty_days_ago
        ).scalar() or 0
        
        # Success metrics
        successful_matches = db.session.query(func.count(Message.id)).filter(
            Message.message_type == 'match_success'
        ).scalar() or 0
        
        pending_matches = db.session.query(func.count(Message.id)).filter(
            Message.message_type == 'match_pending'
        ).scalar() or 0
        
        # Organ demand breakdown
        kidney_demand = db.session.query(func.count(Recipient.id)).filter(
            Recipient.organ == 'Kidney'
        ).scalar() or 0
        liver_demand = db.session.query(func.count(Recipient.id)).filter(
            Recipient.organ == 'Liver'
        ).scalar() or 0
        heart_demand = db.session.query(func.count(Recipient.id)).filter(
            Recipient.organ == 'Heart'
        ).scalar() or 0
        
        # Blood type distribution
        blood_types = db.session.query(
            Donor.blood_group,
            func.count(Donor.id)
        ).group_by(Donor.blood_group).all()
        
        blood_distribution = {blood: count for blood, count in blood_types}
        
        # Geographic distribution
        top_cities = db.session.query(
            Donor.city,
            func.count(Donor.id)
        ).group_by(Donor.city).order_by(desc(func.count(Donor.id))).limit(10).all()
        
        # Calculate KPIs
        match_success_rate = (successful_matches / (successful_matches + pending_matches) * 100) if (successful_matches + pending_matches) > 0 else 0
        donor_to_recipient_ratio = (total_donors / total_recipients * 100) if total_recipients > 0 else 0
        growth_rate = (active_donors / max(total_donors, 1) * 100)
        
        return render_template('premium/kpi_dashboard.html',
                             total_donors=total_donors,
                             total_recipients=total_recipients,
                             total_hospitals=total_hospitals,
                             active_donors=active_donors,
                             active_recipients=active_recipients,
                             successful_matches=successful_matches,
                             pending_matches=pending_matches,
                             kidney_demand=kidney_demand,
                             liver_demand=liver_demand,
                             heart_demand=heart_demand,
                             blood_distribution=blood_distribution,
                             top_cities=top_cities,
                             match_success_rate=round(match_success_rate, 1),
                             donor_to_recipient_ratio=round(donor_to_recipient_ratio, 1),
                             growth_rate=round(growth_rate, 1))
    except Exception as e:
        return render_template('premium/kpi_dashboard.html', error=str(e))

# ============= SMART RECOMMENDATIONS ENGINE =============
@premium_bp.route('/recommendations/smart')
def smart_recommendations():
    """AI-powered smart recommendations for optimizations"""
    try:
        recommendations = []
        
        # Check organ supply imbalance
        donor_organs = db.session.query(
            Donor.organ,
            func.count(Donor.id)
        ).group_by(Donor.organ).all()
        
        recipient_organs = db.session.query(
            Recipient.organ,
            func.count(Recipient.id)
        ).group_by(Recipient.organ).all()
        
        donor_dict = {organ: count for organ, count in donor_organs}
        recipient_dict = {organ: count for organ, count in recipient_organs}
        
        # Check for critical shortages
        for organ, demand in recipient_dict.items():
            supply = donor_dict.get(organ, 0)
            if demand > 0:
                supply_ratio = supply / demand
                if supply_ratio < 0.5:
                    recommendations.append({
                        'type': 'critical',
                        'icon': 'warning',
                        'title': f'{organ} Shortage',
                        'description': f'{organ} supply is {supply_ratio*100:.0f}% of demand. Urgently increase donor recruitment.',
                        'action': 'Initiate targeted campaign',
                        'priority': 1
                    })
                elif supply_ratio < 0.8:
                    recommendations.append({
                        'type': 'warning',
                        'icon': 'trending_down',
                        'title': f'{organ} Gap Alert',
                        'description': f'{organ} supply is {supply_ratio*100:.0f}% of demand. Consider expansion.',
                        'action': 'Plan recruitment drive',
                        'priority': 2
                    })
        
        # Check average wait time
        high_urgency_recipients = db.session.query(func.count(Recipient.id)).filter(
            Recipient.urgency == 'High'
        ).scalar() or 0
        
        if high_urgency_recipients > total_donors * 0.5:
            recommendations.append({
                'type': 'critical',
                'icon': 'schedule',
                'title': 'High Wait Time Alert',
                'description': f'{high_urgency_recipients} recipients in critical condition. Expedite matching.',
                'action': 'Review priority cases',
                'priority': 1
            })
        
        # Blood type matching efficiency
        total_donors = db.session.query(func.count(Donor.id)).scalar() or 1
        o_positive_donors = db.session.query(func.count(Donor.id)).filter(
            Donor.blood_group == 'O+'
        ).scalar() or 0
        
        o_positive_ratio = o_positive_donors / total_donors
        if o_positive_ratio > 0.4:
            recommendations.append({
                'type': 'info',
                'icon': 'info',
                'title': 'Universal Donor Concentration',
                'description': f'O+ donors are {o_positive_ratio*100:.0f}% of supply. Leverage for AB recipients.',
                'action': 'Optimize O+ allocation',
                'priority': 3
            })
        
        # Geographic optimization
        if len(top_cities := db.session.query(Donor.city, func.count(Donor.id)).group_by(Donor.city).order_by(desc(func.count(Donor.id))).limit(3).all()) > 0:
            recommendations.append({
                'type': 'info',
                'icon': 'location_on',
                'title': 'Geographic Concentration',
                'description': f'Donor concentration in {top_cities[0][0]}. Expand network to underserved areas.',
                'action': 'Analyze regional gaps',
                'priority': 3
            })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'])
        
        return render_template('premium/smart_recommendations.html',
                             recommendations=recommendations)
    except Exception as e:
        return render_template('premium/smart_recommendations.html', error=str(e))

# ============= COMPLIANCE & AUDIT TRAIL =============
@premium_bp.route('/compliance/audit')
def compliance_audit():
    """Complete audit trail and compliance tracking"""
    try:
        # Get activity logs
        activities = db.session.query(ActivityLog).order_by(desc(ActivityLog.timestamp)).limit(100).all()
        
        # Categorize activities
        activity_summary = {}
        for activity in activities:
            action_type = activity.action
            if action_type not in activity_summary:
                activity_summary[action_type] = 0
            activity_summary[action_type] += 1
        
        # Timeline data for chart
        timeline = {}
        for activity in activities:
            date_key = activity.timestamp.strftime('%Y-%m-%d')
            if date_key not in timeline:
                timeline[date_key] = 0
            timeline[date_key] += 1
        
        # Get user activity by hospital
        hospital_activities = db.session.query(
            Hospital.name,
            func.count(ActivityLog.id)
        ).join(ActivityLog).group_by(Hospital.id).order_by(
            desc(func.count(ActivityLog.id))
        ).limit(10).all()
        
        return render_template('premium/compliance_audit.html',
                             activities=activities,
                             activity_summary=activity_summary,
                             timeline=timeline,
                             hospital_activities=hospital_activities)
    except Exception as e:
        return render_template('premium/compliance_audit.html', error=str(e))

# ============= API ENDPOINTS FOR REAL-TIME UPDATES =============
@premium_bp.route('/api/notifications/unread')
def get_unread_notifications():
    """Get unread notifications count for real-time updates"""
    try:
        unread_count = db.session.query(func.count(Notification.id)).filter_by(is_read=False).scalar() or 0
        critical_count = db.session.query(func.count(Notification.id)).filter(
            Notification.priority == 'critical',
            Notification.is_read == False
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'unread_count': unread_count,
            'critical_count': critical_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@premium_bp.route('/api/kpi/quick-stats')
def get_quick_stats():
    """Get quick KPI stats for dashboard widgets"""
    try:
        total_donors = db.session.query(func.count(Donor.id)).scalar() or 0
        total_recipients = db.session.query(func.count(Recipient.id)).scalar() or 0
        pending_matches = db.session.query(func.count(Message.id)).filter(
            Message.message_type == 'match_pending'
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'total_donors': total_donors,
            'total_recipients': total_recipients,
            'pending_matches': pending_matches
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@premium_bp.route('/api/notifications/mark-read/<int:notif_id>', methods=['POST'])
def mark_notification_read(notif_id):
    """Mark notification as read"""
    try:
        notif = db.session.query(Notification).get(notif_id)
        if notif:
            notif.is_read = True
            db.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Notification not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
