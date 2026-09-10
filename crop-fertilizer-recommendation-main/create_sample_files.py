import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

print("Creating sample model files...")

# Create sample training data
np.random.seed(42)

# Generate sample features: [N, P, K, temperature, humidity, ph, rainfall]
X_sample = np.random.rand(1000, 7) * 100  # Scale to reasonable ranges
y_sample = np.random.choice(['rice', 'wheat', 'corn', 'tomato', 'potato', 'cotton', 'sugarcane'], 1000)

print("✓ Sample data created")

# Create and train a Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_sample, y_sample)

print("✓ Model trained")

# Create a StandardScaler
scaler = StandardScaler()
scaler.fit(X_sample)

print("✓ Scaler fitted")

# Create crop information dictionary
crop_info = {
    'rice': {'N': 80, 'P': 40, 'K': 40, 'rainfall': 180},
    'wheat': {'N': 64, 'P': 64, 'K': 64, 'rainfall': 58},
    'corn': {'N': 77, 'P': 48, 'K': 38, 'rainfall': 65},
    'tomato': {'N': 23, 'P': 22, 'K': 37, 'rainfall': 60},
    'potato': {'N': 50, 'P': 50, 'K': 50, 'rainfall': 90},
    'cotton': {'N': 120, 'P': 46, 'K': 50, 'rainfall': 100},
    'sugarcane': {'N': 75, 'P': 50, 'K': 50, 'rainfall': 150}
}

print("✓ Crop info created")

# Save all files
try:
    with open('crop_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("✓ crop_model.pkl saved")

    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    print("✓ scaler.pkl saved")

    with open('crop_info.pkl', 'wb') as f:
        pickle.dump(crop_info, f)
    print("✓ crop_info.pkl saved")

    print("\n🎉 SUCCESS! All files created successfully!")
    print("\nFiles created in current directory:")
    print("- crop_model.pkl")
    print("- scaler.pkl") 
    print("- crop_info.pkl")
    print("\nYou can now run your Streamlit app!")

except Exception as e:
    print(f"❌ Error creating files: {e}")