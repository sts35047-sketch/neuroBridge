from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint('chatbot_bp', __name__)

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').lower()
    
    # Simple Rule-Based Logic
    if 'donor' in user_msg and 'add' in user_msg:
        response = "To add a donor, click the 'Register Donor' button on the dashboard or use the Quick Actions menu."
    elif 'match' in user_msg:
        response = "You can run the AI Matcher by clicking 'Find Matches' on the dashboard. It checks blood group and organ compatibility."
    elif 'map' in user_msg:
        response = "The Live Map shows real-time locations of all registered donors and recipients. Click 'Live Map' in the Analytics section."
    elif 'contact' in user_msg or 'support' in user_msg:
        response = "You can contact support via the 'Help & Support' page or email admin@neurobridge.com."
    elif 'hello' in user_msg or 'hi' in user_msg:
        response = "Hello! I am NeuroBot. How can I help you manage your transplant logistics today?"
    else:
        response = "I'm not sure about that. Try asking about 'donors', 'matches', 'map', or 'support'."
        
    return jsonify({'response': response})