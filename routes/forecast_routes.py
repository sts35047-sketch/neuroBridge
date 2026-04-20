from flask import Blueprint, render_template, session, redirect, url_for
import random
import statistics

forecast_bp = Blueprint('forecast_bp', __name__)

@forecast_bp.route('/forecast')
def view_forecast():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    # 1. Simulate Historical Data (Last 6 Months)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    kidney_data = [12, 15, 14, 18, 22, 25] # Trending up
    liver_data = [8, 7, 9, 8, 10, 11]      # Stable
    heart_data = [3, 4, 2, 5, 4, 6]        # Fluctuating

    # 2. AI Prediction Logic (Linear Projection with trend analysis)
    def predict_next_3_months(data):
        avg_growth = (data[-1] - data[0]) / len(data)
        last_val = data[-1]
        future = []
        for i in range(1, 4):
            noise = random.uniform(-2, 2)
            prediction = max(0, int(last_val + (avg_growth * i) + noise))
            future.append(prediction)
        return future

    kidney_pred = predict_next_3_months(kidney_data)
    liver_pred = predict_next_3_months(liver_data)
    heart_pred = predict_next_3_months(heart_data)

    future_months = ['Jul (Pred)', 'Aug (Pred)', 'Sep (Pred)']
    
    all_kidney = kidney_data + kidney_pred
    all_liver = liver_data + liver_pred
    all_heart = heart_data + heart_pred

    # 3. Calculate Statistics
    avg_demand = int(statistics.mean(all_kidney + all_liver + all_heart))
    peak_month = months[kidney_data.index(max(kidney_data))]
    accuracy = 92  # Simulated ML model accuracy
    
    peak_kidney = max(kidney_pred)
    current_kidney = kidney_data[-1]
    peak_increase = int(((peak_kidney - current_kidney) / current_kidney) * 100) if current_kidney > 0 else 0
    
    supply_gap = random.randint(2, 5)  # Additional donors needed

    # 4. Enhanced Insight Generation
    insights = []
    
    if kidney_pred[-1] > kidney_data[-1] * 1.15:
        insights.append({
            "type": "critical",
            "title": "High Demand Alert",
            "msg": f"Kidney demand projected to increase by {peak_increase}% in Q3. Urgent action required."
        })
    
    if liver_pred[-1] > liver_data[-1] * 1.1:
        insights.append({
            "type": "warning",
            "title": "Supply Gap Detected",
            "msg": f"Liver organ shortage predicted for {future_months[-1]}. Coordinate with partner hospitals."
        })
    
    if max(heart_pred) <= heart_data[-1]:
        insights.append({
            "type": "info",
            "title": "Stable Demand",
            "msg": "Heart demand remains within normal range. Maintain current protocols."
        })

    if avg_demand > 20:
        insights.append({
            "type": "critical",
            "title": "Resource Scaling",
            "msg": "Average monthly demand exceeds 20 organs. Consider expanding transplant capacity."
        })

    return render_template('forecast.html', 
                         months=months + future_months,
                         kidney=all_kidney,
                         liver=all_liver,
                         heart=all_heart,
                         cut_index=len(months) - 1,
                         insights=insights,
                         avg_demand=avg_demand,
                         peak_month=peak_month,
                         accuracy=accuracy,
                         peak_increase=peak_increase,
                         supply_gap=supply_gap)