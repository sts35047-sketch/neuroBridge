from flask import Blueprint, render_template, session, redirect, url_for
from models import Hospital

network_bp = Blueprint('network_bp', __name__)

@network_bp.route('/network')
def view_network():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    # Get all hospitals EXCLUDING the one currently logged in
    my_id = session['hospital_id']
    hospitals = Hospital.query.filter(Hospital.id != my_id).all()
    
    return render_template('network.html', hospitals=hospitals)