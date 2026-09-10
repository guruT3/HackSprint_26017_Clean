# 🚀 Quick Start Guide - AI Farm Operations Copilot

## Installation (5 minutes)

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Application
```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### Step 3: Open Your Browser
Navigate to: **http://localhost:5000**

---

## First Use - Example Scenario

Let's create a plan for a wheat farm approaching harvest:

### 1. Fill the Form:
- **Crop Type**: Wheat
- **Crop Stage**: Harvest-Ready
- **Farm Size**: 10 acres
- **Soil Type**: Loam
- **Irrigation Type**: Drip
- **Available Workers**: 5
- **Equipment Status**: 2 tractors operational, 1 pump needs repair

### 2. Set ML Predictions (using sliders):
- **Labor Demand**: 0.8 (High - harvest needs workers)
- **Irrigation Urgency**: 0.3 (Low - crop is mature)
- **Equipment Risk**: 0.7 (High - equipment needs service)

### 3. Enter Weather (keep defaults or customize):
The form pre-fills with reasonable values. For this example:
- Days 1-3: No rain, temp 30-35°C
- Day 4: Some rain expected

### 4. Click "Generate Action Plan"

### 5. View Results:
You'll see prioritized tasks like:
- **Today**: Prepare harvesting equipment (High priority)
- **Today**: Emergency equipment inspection (High priority)
- **This Week**: Arrange grain storage/transportation
- **This Week**: Hire additional workers

---

## API Usage

### Using cURL:
```bash
curl -X POST http://localhost:5000/get_plan \
  -H "Content-Type: application/json" \
  -d '{
    "farm_info": {
      "crop_type": "Wheat",
      "crop_stage": "Flowering",
      "farm_size": "10 acres",
      "soil_type": "Loam",
      "irrigation_type": "Drip",
      "available_labor": 5,
      "equipment_status": "2 tractors operational"
    },
    "ml_predictions": {
      "labor_demand": 0.7,
      "irrigation_urgency": 0.8,
      "equipment_risk": 0.5
    },
    "weather_data": [
      {"day": 0, "rainfall": 0, "temp_max": 35, "temp_min": 20, "humidity": 60}
    ]
  }'
```

### Using Python:
```python
import requests

response = requests.post('http://localhost:5000/get_plan', json={
    "farm_info": {
        "crop_type": "Rice",
        "crop_stage": "Vegetative",
        # ... other fields
    },
    "ml_predictions": {
        "labor_demand": 0.6,
        "irrigation_urgency": 0.5,
        "equipment_risk": 0.3
    },
    "weather_data": [...]
})

result = response.json()
print(result['today_tasks'])
```

### Using the Test Script:
```bash
python test_api.py
```

---

## Understanding the Output

### Task Priority Levels:
- 🔴 **High**: Urgent action needed today/tomorrow
- 🟡 **Medium**: Important but can wait 2-5 days  
- 🔵 **Low**: General maintenance tasks

### Task Deadlines:
- Automatically calculated based on urgency
- Today's date for critical tasks
- Within 7 days for weekly planning

### Risk Warnings:
Each task shows what happens if delayed:
- Yield impact percentage
- Crop stress indicators
- Financial consequences

---

## Common Scenarios

### Scenario 1: Drought Conditions
**Settings:**
- Irrigation Urgency: 0.9
- Weather: No rain for 7 days
- Temperature: >35°C

**Expected Output:**
- Immediate irrigation tasks
- Water conservation planning
- Crop stress monitoring

### Scenario 2: Harvest Rush
**Settings:**
- Crop Stage: Harvest-Ready
- Labor Demand: 0.9
- Equipment Risk: 0.8

**Expected Output:**
- Equipment inspection
- Labor hiring
- Storage arrangement
- Transportation planning

### Scenario 3: Growing Season
**Settings:**
- Crop Stage: Vegetative
- Irrigation Urgency: 0.5
- Labor Demand: 0.4

**Expected Output:**
- Fertilizer application
- Routine monitoring
- Moderate irrigation schedule

---

## Troubleshooting

### "Connection refused" error:
Make sure Flask is running: `python app.py`

### "Template not found":
Check folder structure:
```
project/
├── app.py
└── templates/
    └── index.html
```

### Blank results:
Check browser console (F12) for JavaScript errors

### Wrong date calculations:
The app uses system date - ensure your computer's date/time is correct

---

## Next Steps

1. ✅ **Test with your farm data** - Input real values
2. 📊 **Review task accuracy** - Are recommendations helpful?
3. 🤖 **Add ML models** - Run `python ml_model_example.py`
4. 🌤️ **Connect weather API** - Add your API key to `.env`
5. 📱 **Mobile access** - Access from phone browser
6. 🔔 **Add notifications** - Set up SMS/email alerts

---

## Getting Help

- Read the full **README.md** for detailed documentation
- Check **ml_model_example.py** for ML integration
- Run **test_api.py** to verify API functionality
- Review code comments in **app.py** for customization

---

**Happy Farming! 🌾**
