import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.metrics import classification_report, accuracy_score

# Load dataset
dataset = pd.read_csv("Crop_recommendation.csv")
features = dataset.iloc[:, 0:7].values
labels = dataset.iloc[:, 7].values

# Split data
x_train, x_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=10)

# Standardize
scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

# Train SVM model
model = svm.SVC(probability=True)
model.fit(x_train, y_train)

# Test accuracy
y_pred = model.predict(x_test)
print("Model Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save model and scaler
pickle.dump(model, open("crop_model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))

# Compute ideal NPK & rainfall for each crop (data-driven)
crop_info = dataset.groupby("label")[["N", "P", "K", "rainfall"]].mean().round(2).to_dict(orient="index")
pickle.dump(crop_info, open("crop_info.pkl", "wb"))

print("Model, scaler, and crop info saved successfully!")
