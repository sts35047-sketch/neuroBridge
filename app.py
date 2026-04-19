from flask import Flask, render_template, request, redirect, session, url_for
from models import db, Hospital, Donor, Recipient, Notification, ActivityLog
from sqlalchemy import func
from datetime import datetime

# --- IMPORT FEATURES ---
from routes.recipient_routes import recipient_bp
from routes.matching_routes import match_bp
from routes.admin_routes import admin_bp
from routes.search_routes import search_bp
from routes.export_routes import export_bp
from routes.manage_routes import manage_bp
from routes.report_routes import report_bp
from routes.utils_routes import utils_bp
from routes.settings_routes import settings_bp
from routes.card_routes import card_bp
from routes.waitlist_routes import waitlist_bp
from routes.viability_routes import viability_bp
from routes.map_routes import map_bp
from routes.analytics_routes import analytics_bp
from routes.network_routes import network_bp
from routes.support_routes import support_bp
from routes.logistics_routes import logistics_bp
from routes.forecast_routes import forecast_bp
from routes.docs_routes import docs_bp
from routes.message_routes import message_bp
from routes.chatbot_routes import chatbot_bp # <--- NEW: Import Chatbot

app = Flask(__name__)
app.config['SECRET_KEY'] = 'neurobridge_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neurobridge_v3.db' 

db.init_app(app)

# --- REGISTER FEATURES ---
app.register_blueprint(recipient_bp)
app.register_blueprint(match_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(search_bp)
app.register_blueprint(export_bp)
app.register_blueprint(manage_bp)
app.register_blueprint(report_bp)
app.register_blueprint(utils_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(card_bp)
app.register_blueprint(waitlist_bp)
app.register_blueprint(viability_bp)
app.register_blueprint(map_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(network_bp)
app.register_blueprint(support_bp)
app.register_blueprint(logistics_bp)
app.register_blueprint(forecast_bp)
app.register_blueprint(docs_bp)
app.register_blueprint(message_bp)
app.register_blueprint(chatbot_bp) # <--- NEW: Register Chatbot

# Create tables
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            new_hospital = Hospital(
                name=request.form['name'],
                email=request.form['email'],
                password=request.form['password'],
                city=request.form['city']
            )
            db.session.add(new_hospital)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return "Email already exists!"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hospital = Hospital.query.filter_by(email=email).first()
        if hospital and hospital.password == password:
            session['hospital_id'] = hospital.id
            session['hospital_name'] = hospital.name
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Credentials"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    my_donors = Donor.query.filter_by(hospital_id=session['hospital_id']).all()
    my_recipients = Recipient.query.filter_by(hospital_id=session['hospital_id']).all()
    notifications = Notification.query.filter_by(hospital_id=session['hospital_id']).order_by(Notification.id.desc()).all()
    
    recent_activity = ActivityLog.query.filter_by(hospital_id=session['hospital_id']).order_by(ActivityLog.timestamp.desc()).limit(10).all()

    blood_counts = db.session.query(Donor.blood_group, func.count(Donor.id)).filter_by(hospital_id=session['hospital_id']).group_by(Donor.blood_group).all()
    d_labels = [x[0] for x in blood_counts]
    d_values = [x[1] for x in blood_counts]

    urgency_counts = db.session.query(Recipient.urgency, func.count(Recipient.id)).filter_by(hospital_id=session['hospital_id']).group_by(Recipient.urgency).all()
    r_labels = [x[0] for x in urgency_counts]
    r_values = [x[1] for x in urgency_counts]

    return render_template('dashboard.html', 
                         hospital_name=session['hospital_name'], 
                         donors=my_donors,
                         recipients=my_recipients,
                         notifications=notifications,
                         activities=recent_activity,
                         d_labels=d_labels, d_values=d_values,
                         r_labels=r_labels, r_values=r_values)

@app.route('/add_donor', methods=['POST'])
def add_donor():
    if 'hospital_id' not in session: return redirect(url_for('login'))
    name = request.form['name']
    new_donor = Donor(
        name=name,
        age=request.form['age'],
        blood_group=request.form['blood_group'],
        organ=request.form['organ'],
        phone=request.form['phone'],
        city=request.form['city'], 
        hospital_id=session['hospital_id']
    )
    db.session.add(new_donor)
    log = ActivityLog(hospital_id=session['hospital_id'], action="Added Donor", details=f"Name: {name}")
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_recipient', methods=['POST'])
def add_recipient():
    if 'hospital_id' not in session: return redirect(url_for('login'))
    name = request.form['name']
    new_recipient = Recipient(
        name=name,
        age=request.form['age'],
        blood_group=request.form['blood_group'],
        organ=request.form['organ'],
        urgency=request.form['urgency'],
        phone=request.form['phone'],
        city=request.form['city'],
        hospital_id=session['hospital_id']
    )
    db.session.add(new_recipient)
    log = ActivityLog(hospital_id=session['hospital_id'], action="Added Recipient", details=f"Name: {name}")
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)