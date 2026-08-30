import os
import pickle
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'escalation_model.pkl')
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
except Exception as e:
    model = None
    print(f"Failed to load model: {e}")

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'success',
        'message': 'ML Backend is running',
        'model_loaded': model is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500
        
    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({'error': 'No input data provided'}), 400
        
        df = pd.DataFrame([req_data])
        
        expected_features = ['incident_number', 'days_since_last_incident', 'GravityOffenceID', 
                             'max_gravity_so_far', 'prior_arrest_made', 'accused_has_other_victims']
        df = df[expected_features]
        
        prediction = model.predict(df)[0]
        
        try:
            prob = model.predict_proba(df)[0]
            risk_probability = float(prob[1]) if len(prob) > 1 else None
        except:
            risk_probability = None
            
        return jsonify({
            'status': 'success',
            'prediction': int(prediction),
            'risk_probability': risk_probability
        })
        
    except KeyError as e:
        return jsonify({'error': f'Missing required feature: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable for platforms like Render/Heroku
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
