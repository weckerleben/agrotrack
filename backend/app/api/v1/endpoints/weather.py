from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....models.silo import Silo
from ....services.weather_service import weather_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/current")
async def get_all_silos_current_weather(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current weather for all silo locations"""
    try:
        # Get all active silos
        silos = db.query(Silo).filter(Silo.status == 'active').all()
        
        if not silos:
            return {"message": "No active silos found", "weather_data": []}
        
        # Prepare silo data for weather service (coordinates and location name)
        silo_data = []
        for silo in silos:
            silo_info = {
                "id": silo.id,
                "name": silo.name,
                "location": silo.location,
                "latitude": float(silo.latitude) if silo.latitude else None,
                "longitude": float(silo.longitude) if silo.longitude else None
            }
            silo_data.append(silo_info)
        
        # Get weather data for all silos (with coordinate/location fallback)
        weather_data = await weather_service.get_multiple_silos_weather(silo_data)
        
        # Count results by method used
        coord_count = sum(1 for w in weather_data if w.get("weather_method") == "coordinates")
        location_count = sum(1 for w in weather_data if w.get("weather_method") == "location_name")
        
        return {
            "message": f"Weather data retrieved for {len(weather_data)} of {len(silos)} locations",
            "weather_data": weather_data,
            "total_silos": len(silos),
            "total_with_weather": len(weather_data),
            "method_breakdown": {
                "by_coordinates": coord_count,
                "by_location_name": location_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

@router.get("/current/{silo_id}")
async def get_silo_current_weather(
    silo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current weather for a specific silo (uses coordinates or location name fallback)"""
    try:
        # Get the silo
        silo = db.query(Silo).filter(Silo.id == silo_id).first()
        
        if not silo:
            raise HTTPException(status_code=404, detail="Silo not found")
        
        # Check if we have either coordinates or location
        if not silo.location and (not silo.latitude or not silo.longitude):
            raise HTTPException(status_code=400, detail="Silo has no location data (coordinates or location name)")
        
        # Prepare silo data
        silo_data = {
            "id": silo.id,
            "name": silo.name,
            "location": silo.location,
            "latitude": float(silo.latitude) if silo.latitude else None,
            "longitude": float(silo.longitude) if silo.longitude else None
        }
        
        # Get weather data using coordinate/location fallback
        weather_data = await weather_service.get_silo_weather(silo_data)
        
        if not weather_data:
            raise HTTPException(status_code=503, detail="Weather service unavailable or location not found")
        
        return weather_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather for silo {silo_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

@router.get("/forecast/{silo_id}")
async def get_silo_weather_forecast(
    silo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get 5-day weather forecast for a specific silo (uses coordinates or location name fallback)"""
    try:
        # Get the silo
        silo = db.query(Silo).filter(Silo.id == silo_id).first()
        
        if not silo:
            raise HTTPException(status_code=404, detail="Silo not found")
        
        # Check if we have either coordinates or location
        if not silo.location and (not silo.latitude or not silo.longitude):
            raise HTTPException(status_code=400, detail="Silo has no location data (coordinates or location name)")
        
        # Prepare silo data
        silo_data = {
            "id": silo.id,
            "name": silo.name,
            "location": silo.location,
            "latitude": float(silo.latitude) if silo.latitude else None,
            "longitude": float(silo.longitude) if silo.longitude else None
        }
        
        # Get forecast data using coordinate/location fallback
        forecast_data = await weather_service.get_silo_weather_forecast(silo_data)
        
        if not forecast_data:
            raise HTTPException(status_code=503, detail="Weather service unavailable or location not found")
        
        return forecast_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching forecast for silo {silo_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch forecast data")

@router.get("/location")
async def get_weather_by_coordinates(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    location_name: str = Query("Custom Location", description="Location name"),
    current_user: User = Depends(get_current_user)
):
    """Get current weather for custom coordinates"""
    try:
        weather_data = await weather_service.get_current_weather(lat, lon, location_name)
        
        if not weather_data:
            raise HTTPException(status_code=503, detail="Weather service unavailable")
        
        return weather_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather for coordinates ({lat}, {lon}): {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

@router.get("/city")
async def get_weather_by_city_name(
    city: str = Query(..., description="City name"),
    country: str = Query(None, description="Country code (optional, e.g., 'PY' for Paraguay)"),
    current_user: User = Depends(get_current_user)
):
    """Get current weather for a city by name"""
    try:
        weather_data = await weather_service.get_current_weather_by_name(city, country)
        
        if not weather_data:
            raise HTTPException(status_code=404, detail="City not found or weather service unavailable")
        
        return weather_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather for city '{city}': {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

@router.get("/city/forecast")
async def get_forecast_by_city_name(
    city: str = Query(..., description="City name"),
    country: str = Query(None, description="Country code (optional, e.g., 'PY' for Paraguay)"),
    current_user: User = Depends(get_current_user)
):
    """Get 5-day weather forecast for a city by name"""
    try:
        forecast_data = await weather_service.get_weather_forecast_by_name(city, country)
        
        if not forecast_data:
            raise HTTPException(status_code=404, detail="City not found or weather service unavailable")
        
        return forecast_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching forecast for city '{city}': {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch forecast data")

@router.get("/search")
async def search_locations(
    query: str = Query(..., description="Search query for location name"),
    limit: int = Query(5, description="Maximum number of results", ge=1, le=20),
    current_user: User = Depends(get_current_user)
):
    """Search for locations by name"""
    try:
        locations = await weather_service.search_locations(query, limit)
        
        return {
            "query": query,
            "results": locations,
            "total_found": len(locations)
        }
        
    except Exception as e:
        logger.error(f"Error searching locations for '{query}': {e}")
        raise HTTPException(status_code=500, detail="Failed to search locations")

@router.get("/agricultural-summary")
async def get_agricultural_weather_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agricultural weather summary for all silo locations"""
    try:
        # Get all active silos
        silos = db.query(Silo).filter(Silo.status == 'active').all()
        
        if not silos:
            return {"message": "No active silos found", "summary": []}
        
        # Prepare silo data for weather service (coordinates and location name)
        silo_data = []
        for silo in silos:
            silo_info = {
                "id": silo.id,
                "name": silo.name,
                "location": silo.location,
                "latitude": float(silo.latitude) if silo.latitude else None,
                "longitude": float(silo.longitude) if silo.longitude else None
            }
            silo_data.append(silo_info)
        
        # Get weather data for all silos
        weather_data = await weather_service.get_multiple_silos_weather(silo_data)
        
        # Create summary focused on agricultural metrics
        summary = []
        for weather in weather_data:
            if "agricultural_metrics" in weather:
                ag_summary = {
                    "silo_id": weather["silo_id"],
                    "silo_name": weather["silo_name"],
                    "location": weather["location"],
                    "weather_method": weather.get("weather_method", "unknown"),
                    "temperature": weather["temperature"],
                    "humidity": weather["humidity"],
                    "precipitation": weather["precipitation"],
                    "wind_speed": weather["wind_speed"],
                    "weather_condition": weather["weather_condition"],
                    "agricultural_alerts": [],
                    **weather["agricultural_metrics"]
                }
                
                # Generate agricultural alerts
                alerts = []
                metrics = weather["agricultural_metrics"]
                
                if metrics["frost_risk"] == "high":
                    alerts.append({"type": "frost_warning", "message": "Frost risk detected"})
                
                if metrics["disease_pressure_risk"] == "high":
                    alerts.append({"type": "disease_risk", "message": "High disease pressure conditions"})
                
                if metrics["irrigation_recommendation"] == "high":
                    alerts.append({"type": "irrigation_needed", "message": "High irrigation need recommended"})
                
                if weather["temperature"] > 35:
                    alerts.append({"type": "heat_stress", "message": "Extreme heat conditions"})
                
                if weather["wind_speed"] > 10:
                    alerts.append({"type": "high_wind", "message": "High wind conditions"})
                
                ag_summary["agricultural_alerts"] = alerts
                summary.append(ag_summary)
        
        # Count results by method used
        coord_count = sum(1 for s in summary if s.get("weather_method") == "coordinates")
        location_count = sum(1 for s in summary if s.get("weather_method") == "location_name")
        
        return {
            "summary": summary,
            "total_locations": len(summary),
            "total_silos": len(silos),
            "method_breakdown": {
                "by_coordinates": coord_count,
                "by_location_name": location_count
            },
            "timestamp": weather_data[0]["timestamp"] if weather_data else None
        }
        
    except Exception as e:
        logger.error(f"Error generating agricultural weather summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate weather summary") 