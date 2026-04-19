from flask import Blueprint, render_template, session, redirect, url_for, request
from models import db, ActivityLog, Hospital
from datetime import datetime, timedelta

logistics_bp = Blueprint('logistics_bp', __name__)

@logistics_bp.route('/logistics')
def view_logistics():
    if 'hospital_id' not in session: return redirect(url_for('login'))
    
    # Fetch Transport Logs initiated by this hospital
    # Using 'Dispatch' action to filter logistics logs
    logs = ActivityLog.query.filter_by(hospital_id=session['hospital_id'], action="Dispatch").order_by(ActivityLog.timestamp.desc()).all()
    
    active_shipments = []
    past_shipments = []
    
    now = datetime.now()
    
    for log in logs:
        # Details format expected: "Organ: Kidney | To: City Hospital | Via: Drone | ETA: 2 hours"
        try:
            parts = log.details.split('|')
            organ = parts[0].split(':')[1].strip()
            dest = parts[1].split(':')[1].strip()
            mode = parts[2].split(':')[1].strip()
            # Extract ETA hours safely
            eta_str = parts[3].split(':')[1].strip()
            eta_hours = int(eta_str.split(' ')[0])
            
            arrival_time = log.timestamp + timedelta(hours=eta_hours)
            
            shipment = {
                'id': log.id,
                'organ': organ,
                'destination': dest,
                'mode': mode,
                'start_time': log.timestamp.strftime("%H:%M"),
                'arrival_time': arrival_time.strftime("%H:%M"),
                'progress': 0
            }
            
            if now > arrival_time:
                shipment['status'] = "DELIVERED"
                shipment['css'] = "success"
                shipment['progress'] = 100
                past_shipments.append(shipment)
            else:
                shipment['status'] = "IN TRANSIT"
                shipment['css'] = "warning"
                # Calculate progress percentage
                total_seconds = (arrival_time - log.timestamp).total_seconds()
                elapsed = (now - log.timestamp).total_seconds()
                if total_seconds > 0:
                    shipment['progress'] = int((elapsed / total_seconds) * 100)
                else:
                    shipment['progress'] = 0
                active_shipments.append(shipment)
                
        except Exception as e:
            # Skip logs that don't match the expected format to prevent crashing
            continue 

    return render_template('logistics.html', active=active_shipments, history=past_shipments)

@logistics_bp.route('/create_shipment', methods=['POST'])
def create_shipment():
    if 'hospital_id' not in session: return redirect(url_for('login'))
    
    organ = request.form.get('organ')
    destination = request.form.get('destination')
    mode = request.form.get('mode')
    
    # Simulate ETA based on mode
    if mode == 'Drone': eta = 1
    elif mode == 'Ambulance': eta = 3
    else: eta = 5 # Airlift
    
    details = f"Organ: {organ} | To: {destination} | Via: {mode} | ETA: {eta} hours"
    
    # Log the dispatch
    log = ActivityLog(hospital_id=session['hospital_id'], action="Dispatch", details=details)
    db.session.add(log)
    db.session.commit()
    
    return redirect(url_for('logistics_bp.view_logistics'))