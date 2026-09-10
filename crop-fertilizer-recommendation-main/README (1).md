# 🌾 AI Farm Operations Copilot

An intelligent farm management system that generates actionable tasks based on ML predictions, weather forecasts, and farm conditions. Built with Flask backend and vanilla JavaScript frontend.

## 🚀 Features

- **Smart Task Generation**: Automatically creates prioritized tasks based on:
  - ML predictions (labor demand, irrigation urgency, equipment risk)
  - Real-time weather forecasts
  - Crop stage and farm conditions
  
- **Dynamic Planning**: 
  - Today's urgent tasks with immediate deadlines
  - Weekly task schedule with calculated deadlines
  - Weather-aware recommendations (e.g., postpone irrigation if rain expected)

- **Risk Assessment**: Clear warnings about consequences of delayed tasks

- **Farmer-Friendly**: Simple explanations without technical jargon

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🛠️ Installation

1. **Clone or download the project**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python app.py
```

4. **Access the application**:
Open your browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
farm-copilot/
│
├── app.py                  # Flask backend with all logic
├── templates/
│   └── index.html         # Frontend interface
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎯 Usage

### Frontend Interface

1. **Fill in Farm Information**:
   - Crop type (e.g., Wheat, Rice)
   - Crop stage (Sowing, Vegetative, Flowering, etc.)
   - Farm size
   - Soil type
   - Irrigation type
   - Available workers
   - Equipment status

2. **Adjust ML Predictions** (using sliders):
   - Labor demand (0-1)
   - Irrigation urgency (0-1)
   - Equipment risk (0-1)

3. **Enter Weather Forecast** (7 days):
   - Rainfall (mm)
   - Max/Min temperature (°C)
   - Humidity (%)

4. **Click "Generate Action Plan"**

5. **View Results**:
   - Today's priority tasks
   - This week's scheduled tasks
   - Each task shows:
     - Priority level (High/Medium/Low)
     - Deadline
     - Reason
     - Risk if delayed

### API Endpoints

#### 1. Generate Farm Plan
```
POST /get_plan
Content-Type: application/json

{
  "farm_info": {
    "crop_type": "Wheat",
    "crop_stage": "Flowering",
    "farm_size": "10 acres",
    "soil_type": "Loam",
    "irrigation_type": "Drip",
    "available_labor": 5,
    "equipment_status": "2 tractors operational, 1 pump needs repair"
  },
  "ml_predictions": {
    "labor_demand": 0.8,
    "irrigation_urgency": 0.9,
    "equipment_risk": 0.6
  },
  "weather_data": [
    {"day": 0, "rainfall": 0, "temp_max": 35, "temp_min": 20, "humidity": 60},
    {"day": 1, "rainfall": 2, "temp_max": 34, "temp_min": 19, "humidity": 65}
    // ... more days
  ]
}
```

**Response**:
```json
{
  "today_tasks": [
    {
      "task_name": "Irrigate Wheat Field",
      "priority": "High",
      "deadline": "2026-02-03",
      "reason": "Soil moisture is critically low (90% urgency) and no significant rainfall expected",
      "risk_if_delayed": "Severe crop stress, wilting, reduced yield by 15-30%"
    }
  ],
  "weekly_tasks": [...],
  "generated_at": "2026-02-03 14:30:00",
  "farm_summary": {
    "crop": "Wheat",
    "stage": "Flowering",
    "size": "10 acres"
  }
}
```

#### 2. Get Weather Data (Placeholder)
```
GET /weather?location=Delhi
```

## 🔧 Customization & Extension

### 1. Integrate Real Weather API

In `app.py`, update the `/weather` endpoint:

```python
@app.route('/weather', methods=['GET'])
def get_weather():
    import requests
    location = request.args.get('location', 'Delhi')
    
    # OpenWeatherMap example
    url = f"{WEATHER_API_URL}?q={location}&appid={WEATHER_API_KEY}&units=metric&cnt=56"
    response = requests.get(url)
    data = response.json()
    
    # Process and format weather data
    weather_forecast = process_weather_data(data)
    return jsonify({"weather_forecast": weather_forecast}), 200
```

Add your API key at the top of `app.py`:
```python
WEATHER_API_KEY = "your_actual_api_key"
```

### 2. Integrate ML Model

Replace the `get_ml_predictions()` function in `app.py`:

```python
def get_ml_predictions(farm_data: Dict) -> Dict:
    import joblib
    
    # Load your trained model
    model = joblib.load('models/farm_predictor.pkl')
    
    # Preprocess features
    features = preprocess_features(farm_data)
    
    # Run inference
    predictions = model.predict(features)
    
    return {
        'labor_demand': float(predictions[0]),
        'irrigation_urgency': float(predictions[1]),
        'equipment_risk': float(predictions[2])
    }
```

### 3. Add New Task Types

In the `TaskGenerator` class, add new methods:

```python
def generate_pest_control_tasks(self):
    """Generate pest control tasks"""
    # Your logic here
    pass

def generate_fertilization_tasks(self):
    """Generate fertilization tasks"""
    # Your logic here
    pass
```

Then call them in `generate_all_tasks()`:
```python
def generate_all_tasks(self):
    self.generate_irrigation_tasks()
    self.generate_labor_tasks()
    self.generate_pest_control_tasks()  # New
    self.generate_fertilization_tasks()  # New
    # ... rest of the code
```

### 4. Customize Task Prioritization

Modify the priority calculation logic in any task generation method:

```python
# Example: More complex priority based on multiple factors
def calculate_priority(urgency, weather_risk, crop_stage_sensitivity):
    score = (urgency * 0.5) + (weather_risk * 0.3) + (crop_stage_sensitivity * 0.2)
    if score >= 0.7:
        return "High"
    elif score >= 0.4:
        return "Medium"
    else:
        return "Low"
```

## 🧪 Testing

### Manual Testing

Use the provided frontend interface or test with curl:

```bash
curl -X POST http://localhost:5000/get_plan \
  -H "Content-Type: application/json" \
  -d '{
    "farm_info": {
      "crop_type": "Rice",
      "crop_stage": "Vegetative",
      "farm_size": "15 acres",
      "soil_type": "Clay",
      "irrigation_type": "Flood",
      "available_labor": 8,
      "equipment_status": "All equipment operational"
    },
    "ml_predictions": {
      "labor_demand": 0.6,
      "irrigation_urgency": 0.4,
      "equipment_risk": 0.3
    },
    "weather_data": [
      {"day": 0, "rainfall": 5, "temp_max": 32, "temp_min": 24, "humidity": 75}
    ]
  }'
```

## 🎨 Frontend Customization

### Change Color Scheme

Edit the CSS in `templates/index.html`:

```css
/* Primary color */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Success/Green color */
background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);

/* Change to your brand colors */
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Add More Form Fields

In the HTML form section:
```html
<div class="form-group">
    <label for="newField">New Field</label>
    <input type="text" id="newField" placeholder="Enter value">
</div>
```

In the JavaScript `collectFormData()` function:
```javascript
const farmInfo = {
    // ... existing fields
    new_field: document.getElementById('newField').value
};
```

## 📊 Example Scenarios

### Scenario 1: Pre-Harvest Emergency
```
Input:
- Crop: Wheat (Harvest-Ready)
- Labor Demand: 0.9 (High)
- Equipment Risk: 0.8 (High)
- Weather: Heavy rain expected in 2 days

Output:
- TODAY: Prepare harvesting equipment (High priority)
- TODAY: Arrange additional harvest labor urgently (High priority)
- TODAY: Emergency equipment inspection (High priority)
- WEEKLY: Arrange grain storage/transportation (High priority)
```

### Scenario 2: Flowering Stage Care
```
Input:
- Crop: Tomatoes (Flowering)
- Irrigation Urgency: 0.85 (High)
- Weather: No rain expected, high temperatures (>38°C)

Output:
- TODAY: Irrigate crop field (High priority)
- TODAY: Protect flowering crop from temperature stress (High priority)
- WEEKLY: Apply flowering stage nutrients (High priority)
```

## 🐛 Troubleshooting

### Port 5000 already in use
```bash
# Use a different port
python app.py
# Then in app.py, change:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Template not found error
Ensure your directory structure is correct:
```
project/
├── app.py
└── templates/
    └── index.html
```

### CORS errors (if using separate frontend)
Add Flask-CORS:
```bash
pip install flask-cors
```

```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
```

## 📝 Future Enhancements

- [ ] User authentication and multi-farm support
- [ ] Historical task completion tracking
- [ ] Mobile app (React Native/Flutter)
- [ ] SMS/WhatsApp notifications for urgent tasks
- [ ] Integration with IoT sensors for real-time soil/weather data
- [ ] Multi-language support
- [ ] Export to PDF/Excel
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Advanced ML models for yield prediction
- [ ] Marketplace integration for labor/equipment rental

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Open an issue on the repository

---

**Built with ❤️ for farmers everywhere** 🌾
