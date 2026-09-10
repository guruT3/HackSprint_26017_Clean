"""
API Test Script for Farm Copilot

This script tests the Flask API endpoints with sample data
"""

import requests
import json

# API endpoint (change if running on different port)
BASE_URL = "http://localhost:5000"

def test_get_plan():
    """Test the /get_plan endpoint with sample data"""
    
    print("=" * 60)
    print("Testing /get_plan endpoint")
    print("=" * 60)
    
    # Sample request data
    test_data = {
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
            {"day": 1, "rainfall": 0, "temp_max": 36, "temp_min": 21, "humidity": 58},
            {"day": 2, "rainfall": 2, "temp_max": 33, "temp_min": 19, "humidity": 65},
            {"day": 3, "rainfall": 5, "temp_max": 30, "temp_min": 18, "humidity": 75},
            {"day": 4, "rainfall": 12, "temp_max": 28, "temp_min": 17, "humidity": 85},
            {"day": 5, "rainfall": 3, "temp_max": 31, "temp_min": 19, "humidity": 70},
            {"day": 6, "rainfall": 0, "temp_max": 34, "temp_min": 20, "humidity": 62}
        ]
    }
    
    try:
        # Make request
        print("\nSending request to API...")
        response = requests.post(
            f"{BASE_URL}/get_plan",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        if response.status_code == 200:
            print("✅ Request successful!\n")
            
            result = response.json()
            
            # Display results
            print("Farm Summary:")
            print(f"  Crop: {result['farm_summary']['crop']}")
            print(f"  Stage: {result['farm_summary']['stage']}")
            print(f"  Size: {result['farm_summary']['size']}")
            print(f"  Generated at: {result['generated_at']}\n")
            
            # Today's tasks
            print("=" * 60)
            print("TODAY'S TASKS:")
            print("=" * 60)
            if result['today_tasks']:
                for i, task in enumerate(result['today_tasks'], 1):
                    print(f"\n{i}. {task['task_name']}")
                    print(f"   Priority: {task['priority']}")
                    print(f"   Deadline: {task['deadline']}")
                    print(f"   Reason: {task['reason']}")
                    print(f"   Risk: {task['risk_if_delayed']}")
            else:
                print("No urgent tasks for today")
            
            # Weekly tasks
            print("\n" + "=" * 60)
            print("THIS WEEK'S TASKS:")
            print("=" * 60)
            if result['weekly_tasks']:
                for i, task in enumerate(result['weekly_tasks'], 1):
                    print(f"\n{i}. {task['task_name']}")
                    print(f"   Priority: {task['priority']}")
                    print(f"   Deadline: {task['deadline']}")
                    print(f"   Reason: {task['reason']}")
                    print(f"   Risk: {task['risk_if_delayed']}")
            else:
                print("No additional tasks this week")
            
            print("\n" + "=" * 60)
            print("✅ Test completed successfully!")
            print("=" * 60)
            
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error!")
        print("Make sure the Flask app is running on http://localhost:5000")
        print("Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_weather_endpoint():
    """Test the /weather endpoint"""
    
    print("\n\n" + "=" * 60)
    print("Testing /weather endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/weather?location=Delhi")
        
        if response.status_code == 200:
            print("✅ Weather endpoint working!\n")
            weather = response.json()
            print("7-Day Weather Forecast:")
            for day in weather['weather_forecast']:
                print(f"  Day {day['day']}: {day['rainfall']}mm rain, "
                      f"{day['temp_min']}°C - {day['temp_max']}°C, "
                      f"{day['humidity']}% humidity")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_different_scenarios():
    """Test with different farm scenarios"""
    
    print("\n\n" + "=" * 60)
    print("Testing Different Scenarios")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Pre-Harvest Emergency",
            "data": {
                "farm_info": {
                    "crop_type": "Rice",
                    "crop_stage": "Harvest-Ready",
                    "farm_size": "15 acres",
                    "soil_type": "Clay",
                    "irrigation_type": "Flood",
                    "available_labor": 3,
                    "equipment_status": "1 harvester, needs service"
                },
                "ml_predictions": {
                    "labor_demand": 0.95,
                    "irrigation_urgency": 0.3,
                    "equipment_risk": 0.85
                },
                "weather_data": [
                    {"day": i, "rainfall": 25 if i == 2 else 0, 
                     "temp_max": 32, "temp_min": 22, "humidity": 70}
                    for i in range(7)
                ]
            }
        },
        {
            "name": "Early Vegetative Stage",
            "data": {
                "farm_info": {
                    "crop_type": "Corn",
                    "crop_stage": "Vegetative",
                    "farm_size": "20 acres",
                    "soil_type": "Sandy",
                    "irrigation_type": "Sprinkler",
                    "available_labor": 6,
                    "equipment_status": "All equipment operational"
                },
                "ml_predictions": {
                    "labor_demand": 0.4,
                    "irrigation_urgency": 0.6,
                    "equipment_risk": 0.2
                },
                "weather_data": [
                    {"day": i, "rainfall": 0, "temp_max": 35, 
                     "temp_min": 20, "humidity": 50}
                    for i in range(7)
                ]
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- Scenario: {scenario['name']} ---")
        
        try:
            response = requests.post(
                f"{BASE_URL}/get_plan",
                json=scenario['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Today's tasks: {len(result['today_tasks'])}")
                print(f"Weekly tasks: {len(result['weekly_tasks'])}")
                
                if result['today_tasks']:
                    print("Top priority task:", result['today_tasks'][0]['task_name'])
            else:
                print(f"Failed: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("\n🌾 Farm Copilot API Test Suite\n")
    
    # Run tests
    test_get_plan()
    test_weather_endpoint()
    test_different_scenarios()
    
    print("\n\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
