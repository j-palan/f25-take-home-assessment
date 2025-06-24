from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import Dict, Any, Optional
import uvicorn
import uuid
import os
from dotenv import load_dotenv
from datetime import datetime

app = FastAPI(title="Weather Data System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WeatherStack API configuration
load_dotenv()
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")
WEATHERSTACK_BASE_URL = "http://api.weatherstack.com/current"

# In-memory storage for weather data
weather_storage: Dict[str, Dict[str, Any]] = {}

class WeatherRequest(BaseModel):
    date: str
    location: str
    notes: Optional[str] = ""

class WeatherResponse(BaseModel):
    id: str

@app.post("/weather", response_model=WeatherResponse)
async def create_weather_request(request: WeatherRequest):
    """
    Handle weather data requests:
    1. Receive form data (date, location, notes)
    2. Call WeatherStack API for the location
    3. Store combined data with unique ID in memory
    4. Return the ID to frontend
    """
    try:
        # Generate unique ID for this weather request
        weather_id = str(uuid.uuid4())
        
        # Call WeatherStack API to get current weather data
        params = {
            'access_key': WEATHERSTACK_API_KEY,
            'query': request.location
        }
        
        response = requests.get(WEATHERSTACK_BASE_URL, params=params)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500, 
                detail="Failed to fetch weather data from WeatherStack API"
            )
        
        weather_api_data = response.json()
        
        # Check if the API returned an error
        if 'error' in weather_api_data:
            error_msg = weather_api_data['error'].get('info', 'Unknown error from weather API')
            raise HTTPException(status_code=400, detail=f"Weather API error: {error_msg}")
        
        # Combine form data with weather API data
        combined_data = {
            "id": weather_id,
            "request_data": {
                "date": request.date,
                "location": request.location,
                "notes": request.notes,
                "created_at": datetime.now().isoformat()
            },
            "weather_data": weather_api_data
        }
        
        # Store in memory
        weather_storage[weather_id] = combined_data
        
        # Return the ID
        return WeatherResponse(id=weather_id)
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to connect to weather service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/weather/{weather_id}")
async def get_weather_data(weather_id: str):
    """
    Retrieve stored weather data by ID.
    This endpoint is already implemented for the assessment.
    """
    if weather_id not in weather_storage:
        raise HTTPException(status_code=404, detail="Weather data not found")
    
    return weather_storage[weather_id]

# Add some sample data for testing the GET endpoint
@app.on_event("startup")
async def startup_event():
    """Add sample data when the server starts"""
    sample_id = "sample-weather-123"
    weather_storage[sample_id] = {
        "id": sample_id,
        "request_data": {
            "date": "2024-01-15",
            "location": "New York",
            "notes": "Sample weather data for testing",
            "created_at": "2024-01-15T12:00:00"
        },
        "weather_data": {
            "current": {
                "temperature": 22,
                "weather_descriptions": ["Partly cloudy"],
                "humidity": 65,
                "wind_speed": 10,
                "wind_dir": "SW"
            },
            "location": {
                "name": "New York",
                "country": "United States of America",
                "region": "New York"
            }
        }
    }
    print(f"Sample weather ID for testing: {sample_id}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)