from flask import Blueprint, session, Response, redirect, url_for
import csv
import io
from models import Donor, Recipient

export_bp = Blueprint('export_bp', __name__)

@export_bp.route('/export/donors')
def export_donors():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    # Get donors for this hospital
    donors = Donor.query.filter_by(hospital_id=session['hospital_id']).all()

    # Create CSV in memory (RAM) instead of saving to a file
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write Header
    writer.writerow(['ID', 'Name', 'Age', 'Blood Group', 'Organ', 'City', 'Phone'])
    
    # Write Data
    for d in donors:
        writer.writerow([d.id, d.name, d.age, d.blood_group, d.organ, d.city, d.phone])
        
    # Return as a download file
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=my_donors.csv"}
    )

@export_bp.route('/export/recipients')
def export_recipients():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    recipients = Recipient.query.filter_by(hospital_id=session['hospital_id']).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Age', 'Blood Group', 'Organ', 'Urgency', 'City', 'Phone'])
    
    for r in recipients:
        writer.writerow([r.id, r.name, r.age, r.blood_group, r.organ, r.urgency, r.city, r.phone])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=my_recipients.csv"}
    )