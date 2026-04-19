from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from models import Donor, Recipient
import requests

map_bp = Blueprint('map_bp', __name__)

# 1. EXPANDED In-Memory Cache 
# Includes major metros, tier-2 cities, and state capitals for instant loading.
CITY_COORDS_CACHE = {
    # Metros
    'New Delhi': [28.6139, 77.2090], 'Delhi': [28.6139, 77.2090],
    'Bangalore': [12.9716, 77.5946], 'Bengaluru': [12.9716, 77.5946],
    'Mumbai': [19.0760, 72.8777],
    'Chennai': [13.0827, 80.2707],
    'Kolkata': [22.5726, 88.3639],
    'Hyderabad': [17.3850, 78.4867],
    
    # North
    'Chandigarh': [30.7333, 76.7794],
    'Jaipur': [26.9124, 75.7873],
    'Lucknow': [26.8467, 80.9462],
    'Kanpur': [26.4499, 80.3319],
    'Varanasi': [25.3176, 82.9739],
    'Agra': [27.1767, 78.0081],
    'Ludhiana': [30.9010, 75.8573],
    'Amritsar': [31.6340, 74.8723],
    'Dehradun': [30.3165, 78.0322],
    'Srinagar': [34.0837, 74.7973],
    'Jammu': [32.7266, 74.8570],
    'Gurgaon': [28.4595, 77.0266], 'Gurugram': [28.4595, 77.0266],
    'Noida': [28.5355, 77.3910],
    
    # West
    'Pune': [18.5204, 73.8567],
    'Ahmedabad': [23.0225, 72.5714],
    'Surat': [21.1702, 72.8311],
    'Vadodara': [22.3072, 73.1812],
    'Rajkot': [22.3039, 70.8022],
    'Nashik': [19.9975, 73.7898],
    'Nagpur': [21.1458, 79.0882],
    'Aurangabad': [19.8762, 75.3433],
    'Goa': [15.2993, 74.1240], 'Panaji': [15.4909, 73.8278],
    
    # South
    'Mysore': [12.2958, 76.6394], 'Mysuru': [12.2958, 76.6394],
    'Coimbatore': [11.0168, 76.9558],
    'Madurai': [9.9252, 78.1198],
    'Kochi': [9.9312, 76.2673], 'Cochin': [9.9312, 76.2673],
    'Thiruvananthapuram': [8.5241, 76.9366], 'Trivandrum': [8.5241, 76.9366],
    'Visakhapatnam': [17.6868, 83.2185], 'Vizag': [17.6868, 83.2185],
    'Vijayawada': [16.5062, 80.6480],
    'Warangal': [17.9689, 79.5941],
    
    # East & Central
    'Patna': [25.5941, 85.1376],
    'Ranchi': [23.3441, 85.3096],
    'Bhubaneswar': [20.2961, 85.8245],
    'Guwahati': [26.1445, 91.7362],
    'Bhopal': [23.2599, 77.4126],
    'Indore': [22.7196, 75.8577],
    'Raipur': [21.2514, 81.6296],
    'Jabalpur': [23.1815, 79.9864]
}

def get_coordinates(city_name):
    """
    Robust Geocoding: Cache -> API -> Fallback
    """
    clean_city = city_name.strip().title()
    
    # 1. Check Cache (Instant)
    if clean_city in CITY_COORDS_CACHE:
        return CITY_COORDS_CACHE[clean_city]
        
    # 2. API Call (Nominatim)
    try:
        # Crucial: User-Agent prevents blocking by OpenStreetMap
        headers = {'User-Agent': 'NeuroBridgeApp/1.0 (internal-demo)'}
        
        # Try finding the specific city
        url = f"https://nominatim.openstreetmap.org/search?city={clean_city}&country=India&format=json&limit=1"
        response = requests.get(url, headers=headers, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                CITY_COORDS_CACHE[clean_city] = [lat, lon]
                return [lat, lon]
                
        # 3. Fallback: If city fails, try searching broadly (e.g. just passing the query)
        # This helps if the API doesn't recognize it as a "city" but maybe a "town"
        url_fallback = f"https://nominatim.openstreetmap.org/search?q={clean_city}, India&format=json&limit=1"
        response = requests.get(url_fallback, headers=headers, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                CITY_COORDS_CACHE[clean_city] = [lat, lon]
                return [lat, lon]

    except Exception as e:
        print(f"Map API Error for {clean_city}: {e}")
        
    return None

@map_bp.route('/live_map')
def live_map():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    donors = Donor.query.filter_by(hospital_id=session['hospital_id']).all()
    recipients = Recipient.query.filter_by(hospital_id=session['hospital_id']).all()
    
    # Collect donor and recipient data with coordinates
    donor_data = []
    for donor in donors:
        city_key = donor.city.split(',')[0].strip() if donor.city else 'New Delhi'
        coords = get_coordinates(city_key)
        if coords:
            donor_data.append({
                'name': donor.name,
                'organ': donor.organ,
                'blood': donor.blood_group,
                'lat': coords[0],
                'lon': coords[1],
                'type': 'donor'
            })
    
    recipient_data = []
    for recipient in recipients:
        city_key = recipient.city.split(',')[0].strip() if recipient.city else 'New Delhi'
        coords = get_coordinates(city_key)
        if coords:
            recipient_data.append({
                'name': recipient.name,
                'organ': recipient.organ,
                'blood': recipient.blood_group,
                'urgency': recipient.urgency,
                'lat': coords[0],
                'lon': coords[1],
                'type': 'recipient'
            })
    
    markers = donor_data + recipient_data
    
    return render_template('map.html', markers=markers)

@map_bp.route('/api/map_data')
def map_data():
    if 'hospital_id' not in session:
        return jsonify([])
    
    donors = Donor.query.filter_by(hospital_id=session['hospital_id']).all()
    recipients = Recipient.query.filter_by(hospital_id=session['hospital_id']).all()
    
    data = []
    for donor in donors:
        city_key = donor.city.split(',')[0].strip() if donor.city else 'New Delhi'
        coords = get_coordinates(city_key)
        if coords:
            data.append({
                'name': donor.name,
                'organ': donor.organ,
                'blood': donor.blood_group,
                'lat': coords[0],
                'lon': coords[1],
                'type': 'donor'
            })
    
    for recipient in recipients:
        city_key = recipient.city.split(',')[0].strip() if recipient.city else 'New Delhi'
        coords = get_coordinates(city_key)
        if coords:
            data.append({
                'name': recipient.name,
                'organ': recipient.organ,
                'blood': recipient.blood_group,
                'urgency': recipient.urgency,
                'lat': coords[0],
                'lon': coords[1],
                'type': 'recipient'
            })
    
    return jsonify(data)