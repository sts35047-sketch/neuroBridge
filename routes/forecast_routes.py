from flask import Blueprint, render_template, session, redirect, url_for
import random

forecast_bp = Blueprint('forecast_bp', __name__)

@forecast_bp.route('/forecast')
def view_forecast():
    if 'hospital_id' not in session:
        return redirect(url_for('login'))
    
    # 1. Simulate Historical Data (Last 6 Months)
    # In a real app, this comes from your database timestamps
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    kidney_data = [12, 15, 14, 18, 22, 25] # Trending up
    liver_data = [8, 7, 9, 8, 10, 11]      # Stable
    heart_data = [3, 4, 2, 5, 4, 6]        # Fluctuating

    # 2. AI Prediction Logic (Simple Linear Projection)
    # Calculate average growth rate
    def predict_next_3_months(data):
        avg_growth = (data[-1] - data[0]) / len(data)
        last_val = data[-1]
        future = []
        for i in range(1, 4):
            # Add some randomness for realism
            noise = random.uniform(-2, 2)
            prediction = max(0, int(last_val + (avg_growth * i) + noise))
            future.append(prediction)
        return future

    kidney_pred = predict_next_3_months(kidney_data)
    liver_pred = predict_next_3_months(liver_data)
    heart_pred = predict_next_3_months(heart_data)

    future_months = ['Jul (Pred)', 'Aug (Pred)', 'Sep (Pred)']

    # 3. Insight Generation
    insights = []
    if kidney_pred[-1] > kidney_data[-1]:
        insights.append({"type": "danger", "msg": "⚠️ Kidney demand is projected to spike by 20%. Prepare inventory."})
    if liver_pred[-1] > liver_data[-1]:
        insights.append({"type": "warning", "msg": "⚠️ Liver demand showing steady increase."})
    else:
        insights.append({"type": "success", "msg": "✅ Heart demand remains stable."})

    return render_template('forecast.html', 
                         months=months + future_months,
                         kidney=kidney_data + kidney_pred,
                         liver=liver_data + liver_pred,
                         heart=heart_data + heart_pred,
                         cut_index=len(months) - 1, # Where history ends
                         insights=insights)