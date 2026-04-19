from flask import Blueprint, jsonify
import requests
import urllib3

# Disable warnings about unverified HTTPS requests (common in some networks)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

utils_bp = Blueprint('utils_bp', __name__)

def get_state_from_pin_prefix(pin):
    """Fallback: Guess state based on first 2 digits if API fails"""
    try:
        prefix = int(pin[:2])
    except:
        return ""
    
    if 11 <= prefix <= 11: return "Delhi"
    if 12 <= prefix <= 13: return "Haryana"
    if 14 <= prefix <= 16: return "Punjab"
    if 17 <= prefix <= 17: return "Himachal Pradesh"
    if 18 <= prefix <= 19: return "Jammu & Kashmir"
    if 20 <= prefix <= 28: return "Uttar Pradesh"
    if 30 <= prefix <= 34: return "Rajasthan"
    if 36 <= prefix <= 39: return "Gujarat"
    if 40 <= prefix <= 44: return "Maharashtra"
    if 45 <= prefix <= 48: return "Madhya Pradesh"
    if 50 <= prefix <= 50: return "Telangana"
    if 51 <= prefix <= 53: return "Andhra Pradesh"
    if 56 <= prefix <= 59: return "Karnataka"
    if 60 <= prefix <= 64: return "Tamil Nadu"
    if 67 <= prefix <= 69: return "Kerala"
    if 70 <= prefix <= 74: return "West Bengal"
    if 75 <= prefix <= 77: return "Odisha"
    if 78 <= prefix <= 78: return "Assam"
    if 80 <= prefix <= 85: return "Bihar/Jharkhand"
    
    return ""

@utils_bp.route('/get_location/<pin>')
def get_location(pin):
    print(f"--- FETCHING LOCATION FOR PIN: {pin} ---") 

    # 1. IMMEDIATE FALLBACK (Works offline for Demo)
    known_pins = {
        # Metros
        "110001": {"city": "New Delhi", "state": "Delhi"},
        "560001": {"city": "Bangalore", "state": "Karnataka"},
        "400001": {"city": "Mumbai", "state": "Maharashtra"},
        "600001": {"city": "Chennai", "state": "Tamil Nadu"},
        "700001": {"city": "Kolkata", "state": "West Bengal"},
        "500001": {"city": "Hyderabad", "state": "Telangana"},
        
        # Tech Hubs / Major Cities
        "411001": {"city": "Pune", "state": "Maharashtra"},
        "380001": {"city": "Ahmedabad", "state": "Gujarat"},
        "122001": {"city": "Gurugram", "state": "Haryana"},
        "201301": {"city": "Noida", "state": "Uttar Pradesh"},
        "605001": {"city": "Pondicherry", "state": "Puducherry"},
        "695001": {"city": "Thiruvananthapuram", "state": "Kerala"},
        "682001": {"city": "Kochi", "state": "Kerala"},
        "302001": {"city": "Jaipur", "state": "Rajasthan"},
        "226001": {"city": "Lucknow", "state": "Uttar Pradesh"},
        "160017": {"city": "Chandigarh", "state": "Chandigarh"},
        "440001": {"city": "Nagpur", "state": "Maharashtra"},
        "452001": {"city": "Indore", "state": "Madhya Pradesh"},
        "800001": {"city": "Patna", "state": "Bihar"},
        "462001": {"city": "Bhopal", "state": "Madhya Pradesh"},
        "530001": {"city": "Visakhapatnam", "state": "Andhra Pradesh"},
        "395001": {"city": "Surat", "state": "Gujarat"},
    }

    if pin in known_pins:
        print("✅ Found in Hardcoded List")
        data = known_pins[pin]
        return jsonify({"city": data['city'], "state": data['state'], "status": "success"})

    if len(pin) != 6 or not pin.isdigit():
        return jsonify({"city": "", "state": "", "error": "Invalid PIN"})

    # 2. TRY OFFICIAL API (Robust Mode)
    # We add headers to mimic a browser, and verify=False to bypass strict SSL checks
    try:
        url = f"https://api.postalpincode.in/pincode/{pin}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        print(f"🌍 API Request to {url}...")
        response = requests.get(url, headers=headers, timeout=4, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and data[0]["Status"] == "Success":
                city = data[0]["PostOffice"][0]["District"]
                state = data[0]["PostOffice"][0]["State"]
                print(f"✅ API Success: {city}, {state}")
                return jsonify({"city": city, "state": state, "status": "success"})

    except Exception as e:
        print(f"❌ API Failed: {e}")

    # 3. FINAL FALLBACK: GUESS STATE
    # If API fails, we return just the State (better than nothing!)
    guessed_state = get_state_from_pin_prefix(pin)
    if guessed_state:
        print(f"⚠️ API Failed, but inferred State: {guessed_state}")
        # Return empty city, but valid State
        return jsonify({"city": "", "state": guessed_state, "status": "success"})
    
    return jsonify({"city": "", "state": "", "error": "Not Found"})