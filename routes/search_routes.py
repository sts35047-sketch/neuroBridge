from flask import Blueprint, render_template, request, session, redirect, url_for
from models import Donor

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/search_donors', methods=['GET', 'POST'])
def search_donors():
    # Security: Must be logged in
    if 'hospital_id' not in session:
        return redirect(url_for('login'))

    results = None # No results initially

    if request.method == 'POST':
        # Get filters from the form
        blood = request.form.get('blood_group')
        organ = request.form.get('organ')
        city = request.form.get('city')

        # Start by selecting ALL donors belonging to THIS hospital
        query = Donor.query.filter_by(hospital_id=session['hospital_id'])

        # Apply filters only if the user typed something
        if blood and blood != 'All':
            query = query.filter_by(blood_group=blood)
        
        if organ:
            # ilike means "Case Insensitive" (Kidney == kidney)
            query = query.filter(Donor.organ.ilike(f'%{organ}%'))
            
        if city:
            query = query.filter(Donor.city.ilike(f'%{city}%'))
        
        results = query.all()

    return render_template('search.html', results=results)