"""
Example: ML Model Integration for Farm Copilot

This script shows how to:
1. Train a simple ML model for farm predictions
2. Save the model
3. Integrate it into the Flask app

NOTE: This is a SIMPLIFIED example using dummy data.
In production, use real historical farm data.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

# ============================================================================
# STEP 1: Create Training Data (Replace with your real data)
# ============================================================================

def create_dummy_training_data(n_samples=1000):
    """
    Create synthetic training data for demonstration.
    
    In production, replace this with real historical farm data:
    - Soil moisture readings
    - Weather history
    - Labor logs
    - Equipment maintenance records
    - Crop yield data
    """
    np.random.seed(42)
    
    data = {
        # Input features
        'crop_type_encoded': np.random.randint(0, 5, n_samples),  # 5 crop types
        'crop_stage_encoded': np.random.randint(0, 5, n_samples),  # 5 stages
        'soil_moisture': np.random.uniform(20, 80, n_samples),
        'days_since_irrigation': np.random.randint(0, 14, n_samples),
        'temperature_avg': np.random.uniform(20, 40, n_samples),
        'humidity_avg': np.random.uniform(40, 90, n_samples),
        'rainfall_last_week': np.random.uniform(0, 50, n_samples),
        'farm_size_acres': np.random.uniform(5, 50, n_samples),
        'current_labor_count': np.random.randint(2, 20, n_samples),
        'equipment_age_years': np.random.uniform(0, 15, n_samples),
        'equipment_hours': np.random.uniform(0, 5000, n_samples),
        'season': np.random.randint(0, 4, n_samples),  # 4 seasons
        
        # Target variables (what we want to predict)
        'labor_demand': np.random.uniform(0, 1, n_samples),
        'irrigation_urgency': np.random.uniform(0, 1, n_samples),
        'equipment_risk': np.random.uniform(0, 1, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Add some realistic correlations
    # High temperature + low soil moisture = high irrigation urgency
    df.loc[
        (df['temperature_avg'] > 35) & (df['soil_moisture'] < 40),
        'irrigation_urgency'
    ] = np.random.uniform(0.7, 1.0, len(df[(df['temperature_avg'] > 35) & (df['soil_moisture'] < 40)]))
    
    # Flowering stage = higher labor demand
    df.loc[df['crop_stage_encoded'] == 2, 'labor_demand'] = np.random.uniform(0.6, 1.0, len(df[df['crop_stage_encoded'] == 2]))
    
    # Old equipment = higher risk
    df.loc[df['equipment_age_years'] > 10, 'equipment_risk'] = np.random.uniform(0.5, 1.0, len(df[df['equipment_age_years'] > 10]))
    
    return df

# ============================================================================
# STEP 2: Train the Models
# ============================================================================

def train_models():
    """Train separate models for each prediction task"""
    
    print("Creating training data...")
    df = create_dummy_training_data(n_samples=2000)
    
    # Features for prediction
    feature_columns = [
        'crop_type_encoded', 'crop_stage_encoded', 'soil_moisture',
        'days_since_irrigation', 'temperature_avg', 'humidity_avg',
        'rainfall_last_week', 'farm_size_acres', 'current_labor_count',
        'equipment_age_years', 'equipment_hours', 'season'
    ]
    
    X = df[feature_columns]
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Train Labor Demand Model
    print("\nTraining Labor Demand model...")
    y_labor = df['labor_demand']
    X_train, X_test, y_train, y_test = train_test_split(X, y_labor, test_size=0.2, random_state=42)
    
    labor_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    labor_model.fit(X_train, y_train)
    labor_score = labor_model.score(X_test, y_test)
    print(f"Labor Demand Model R² Score: {labor_score:.3f}")
    
    # Save model
    joblib.dump(labor_model, 'models/labor_demand_model.pkl')
    
    # Train Irrigation Urgency Model
    print("\nTraining Irrigation Urgency model...")
    y_irrigation = df['irrigation_urgency']
    X_train, X_test, y_train, y_test = train_test_split(X, y_irrigation, test_size=0.2, random_state=42)
    
    irrigation_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    irrigation_model.fit(X_train, y_train)
    irrigation_score = irrigation_model.score(X_test, y_test)
    print(f"Irrigation Urgency Model R² Score: {irrigation_score:.3f}")
    
    # Save model
    joblib.dump(irrigation_model, 'models/irrigation_urgency_model.pkl')
    
    # Train Equipment Risk Model
    print("\nTraining Equipment Risk model...")
    y_equipment = df['equipment_risk']
    X_train, X_test, y_train, y_test = train_test_split(X, y_equipment, test_size=0.2, random_state=42)
    
    equipment_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    equipment_model.fit(X_train, y_train)
    equipment_score = equipment_model.score(X_test, y_test)
    print(f"Equipment Risk Model R² Score: {equipment_score:.3f}")
    
    # Save model
    joblib.dump(equipment_model, 'models/equipment_risk_model.pkl')
    
    # Save feature names for later use
    joblib.dump(feature_columns, 'models/feature_columns.pkl')
    
    print("\n✅ All models trained and saved to 'models/' directory!")
    print("\nModel files created:")
    print("  - models/labor_demand_model.pkl")
    print("  - models/irrigation_urgency_model.pkl")
    print("  - models/equipment_risk_model.pkl")
    print("  - models/feature_columns.pkl")

# ============================================================================
# STEP 3: Preprocessing Functions
# ============================================================================

def encode_crop_type(crop_type: str) -> int:
    """Convert crop type to numerical encoding"""
    crop_mapping = {
        'wheat': 0, 'rice': 1, 'corn': 2, 'tomatoes': 3, 'potatoes': 4
    }
    return crop_mapping.get(crop_type.lower(), 0)

def encode_crop_stage(crop_stage: str) -> int:
    """Convert crop stage to numerical encoding"""
    stage_mapping = {
        'sowing': 0, 'vegetative': 1, 'flowering': 2, 
        'fruiting': 3, 'harvest-ready': 4
    }
    return stage_mapping.get(crop_stage.lower(), 1)

def encode_season(date_str: str) -> int:
    """Determine season from date"""
    from datetime import datetime
    date = datetime.strptime(date_str, "%Y-%m-%d")
    month = date.month
    
    if month in [12, 1, 2]:
        return 0  # Winter
    elif month in [3, 4, 5]:
        return 1  # Spring
    elif month in [6, 7, 8]:
        return 2  # Summer
    else:
        return 3  # Fall

def preprocess_farm_data(farm_info: dict, weather_data: list, current_date: str) -> np.ndarray:
    """
    Convert farm information into model input features
    
    This function should match the feature engineering used during training
    """
    
    # Calculate weather statistics
    temps = [day.get('temp_max', 30) for day in weather_data[:7]]
    humidity = [day.get('humidity', 60) for day in weather_data[:7]]
    rainfall_week = sum([day.get('rainfall', 0) for day in weather_data[:7]])
    
    # Extract farm size number
    farm_size_str = farm_info.get('farm_size', '10 acres')
    farm_size_acres = float(''.join(filter(str.isdigit, farm_size_str.split()[0]))) if farm_size_str else 10
    
    # Create feature vector
    features = {
        'crop_type_encoded': encode_crop_type(farm_info.get('crop_type', 'wheat')),
        'crop_stage_encoded': encode_crop_stage(farm_info.get('crop_stage', 'vegetative')),
        'soil_moisture': 50,  # TODO: Get from soil sensors
        'days_since_irrigation': 3,  # TODO: Track from irrigation logs
        'temperature_avg': np.mean(temps),
        'humidity_avg': np.mean(humidity),
        'rainfall_last_week': rainfall_week,
        'farm_size_acres': farm_size_acres,
        'current_labor_count': farm_info.get('available_labor', 5),
        'equipment_age_years': 5,  # TODO: Extract from equipment_status
        'equipment_hours': 1000,  # TODO: Track equipment usage
        'season': encode_season(current_date)
    }
    
    # Load feature columns to ensure correct order
    feature_columns = joblib.load('models/feature_columns.pkl')
    
    # Create feature array in correct order
    feature_array = np.array([[features[col] for col in feature_columns]])
    
    return feature_array

# ============================================================================
# STEP 4: Prediction Function (Use in app.py)
# ============================================================================

def get_ml_predictions(farm_info: dict, weather_data: list, current_date: str) -> dict:
    """
    Get ML predictions for farm operations
    
    Replace the dummy function in app.py with this one
    """
    
    try:
        # Load models
        labor_model = joblib.load('models/labor_demand_model.pkl')
        irrigation_model = joblib.load('models/irrigation_urgency_model.pkl')
        equipment_model = joblib.load('models/equipment_risk_model.pkl')
        
        # Preprocess input
        features = preprocess_farm_data(farm_info, weather_data, current_date)
        
        # Get predictions
        labor_demand = float(labor_model.predict(features)[0])
        irrigation_urgency = float(irrigation_model.predict(features)[0])
        equipment_risk = float(equipment_model.predict(features)[0])
        
        # Clip to [0, 1] range
        labor_demand = np.clip(labor_demand, 0, 1)
        irrigation_urgency = np.clip(irrigation_urgency, 0, 1)
        equipment_risk = np.clip(equipment_risk, 0, 1)
        
        return {
            'labor_demand': labor_demand,
            'irrigation_urgency': irrigation_urgency,
            'equipment_risk': equipment_risk
        }
        
    except FileNotFoundError:
        print("Warning: ML models not found. Using default values.")
        return {
            'labor_demand': 0.5,
            'irrigation_urgency': 0.5,
            'equipment_risk': 0.5
        }

# ============================================================================
# STEP 5: Integration with Flask App
# ============================================================================

"""
To integrate into app.py:

1. Copy the get_ml_predictions() function above
2. Replace the existing get_ml_predictions() in app.py
3. Modify the /get_plan endpoint to use ML predictions:

@app.route('/get_plan', methods=['POST'])
def get_plan():
    try:
        data = request.get_json()
        farm_info = data.get('farm_info', {})
        weather_data = data.get('weather_data', [])
        current_date = get_current_date()
        
        # Get ML predictions instead of using user input
        ml_predictions = get_ml_predictions(farm_info, weather_data, current_date)
        
        # Generate tasks
        task_generator = TaskGenerator(farm_info, ml_predictions, weather_data, current_date)
        result = task_generator.generate_all_tasks()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AI Farm Copilot - ML Model Training")
    print("=" * 60)
    
    # Train and save models
    train_models()
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Replace dummy data with real historical farm data")
    print("2. Add more relevant features (soil sensors, IoT data)")
    print("3. Tune hyperparameters for better accuracy")
    print("4. Copy get_ml_predictions() function to app.py")
    print("5. Test predictions with real farm scenarios")
    print("\nTo use the models:")
    print("  from ml_model import get_ml_predictions")
    print("  predictions = get_ml_predictions(farm_info, weather_data, date)")
