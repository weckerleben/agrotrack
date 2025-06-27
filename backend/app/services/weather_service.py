import httpx
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os
import logging
import re
from ..core.config import settings

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not found. Weather service will not work.")
    
    def _parse_location_string(self, location: str) -> tuple[str, Optional[str]]:
        """Parse location string to extract city and country code"""
        if not location:
            return "", None
            
        # Clean up the location string
        location = location.strip()
        
        # Common patterns to extract city and country
        patterns = [
            r'^(.+),\s*([A-Z]{2})$',  # "City, PY"
            r'^(.+),\s*([A-Za-z]+)$',  # "City, Paraguay" 
        ]
        
        for pattern in patterns:
            match = re.match(pattern, location)
            if match:
                city = match.group(1).strip()
                country_part = match.group(2).strip()
                
                # Convert country name to code if needed
                country_code = self._get_country_code(country_part)
                return city, country_code
        
        # If no pattern matches, treat entire string as city name
        return location, None
    
    def _get_country_code(self, country_part: str) -> Optional[str]:
        """Convert country name or code to ISO country code"""
        country_part = country_part.lower()
        
        country_mapping = {
            # Country codes (already correct)
            'py': 'PY', 'ar': 'AR', 'br': 'BR', 'uy': 'UY', 'bo': 'BO',
            'cl': 'CL', 'pe': 'PE', 'co': 'CO', 'ec': 'EC', 've': 'VE',
            'us': 'US', 'ca': 'CA', 'mx': 'MX', 'gb': 'GB', 'fr': 'FR',
            'de': 'DE', 'it': 'IT', 'es': 'ES', 'pt': 'PT',
            
            # Country names to codes
            'paraguay': 'PY', 'argentina': 'AR', 'brasil': 'BR', 'brazil': 'BR',
            'uruguay': 'UY', 'bolivia': 'BO', 'chile': 'CL', 'peru': 'PE',
            'colombia': 'CO', 'ecuador': 'EC', 'venezuela': 'VE',
            'united states': 'US', 'usa': 'US', 'canada': 'CA', 'mexico': 'MX',
            'united kingdom': 'GB', 'uk': 'GB', 'england': 'GB', 'france': 'FR',
            'germany': 'DE', 'italy': 'IT', 'spain': 'ES', 'portugal': 'PT'
        }
        
        return country_mapping.get(country_part)

    async def get_silo_weather(self, silo_data: Dict) -> Optional[Dict]:
        """Get weather for a silo using coordinates or location name fallback"""
        if not self.api_key:
            return None
        
        silo_id = silo_data.get("id")
        silo_name = silo_data.get("name", "Unknown Silo")
        location = silo_data.get("location", "")
        latitude = silo_data.get("latitude")
        longitude = silo_data.get("longitude")
        
        weather_data = None
        method_used = None
        
        # Try coordinates first if available
        if latitude is not None and longitude is not None:
            try:
                weather_data = await self.get_current_weather(
                    float(latitude), float(longitude), location
                )
                method_used = "coordinates"
                logger.info(f"Got weather for silo {silo_id} using coordinates")
            except Exception as e:
                logger.warning(f"Failed to get weather by coordinates for silo {silo_id}: {e}")
        
        # Fall back to location name if coordinates failed or unavailable
        if weather_data is None and location:
            try:
                city, country_code = self._parse_location_string(location)
                if city:
                    weather_data = await self.get_current_weather_by_name(city, country_code)
                    method_used = "location_name"
                    logger.info(f"Got weather for silo {silo_id} using location name: {city}, {country_code}")
            except Exception as e:
                logger.warning(f"Failed to get weather by location name for silo {silo_id}: {e}")
        
        # Add silo information to weather data
        if weather_data:
            weather_data["silo_id"] = silo_id
            weather_data["silo_name"] = silo_name
            weather_data["weather_method"] = method_used
            return weather_data
        
        logger.error(f"Could not get weather for silo {silo_id} ({silo_name}) at {location}")
        return None

    async def get_silo_weather_forecast(self, silo_data: Dict) -> Optional[Dict]:
        """Get weather forecast for a silo using coordinates or location name fallback"""
        if not self.api_key:
            return None
        
        silo_id = silo_data.get("id")
        silo_name = silo_data.get("name", "Unknown Silo")
        location = silo_data.get("location", "")
        latitude = silo_data.get("latitude")
        longitude = silo_data.get("longitude")
        
        forecast_data = None
        method_used = None
        
        # Try coordinates first if available
        if latitude is not None and longitude is not None:
            try:
                forecast_data = await self.get_weather_forecast(
                    float(latitude), float(longitude), location
                )
                method_used = "coordinates"
                logger.info(f"Got forecast for silo {silo_id} using coordinates")
            except Exception as e:
                logger.warning(f"Failed to get forecast by coordinates for silo {silo_id}: {e}")
        
        # Fall back to location name if coordinates failed or unavailable
        if forecast_data is None and location:
            try:
                city, country_code = self._parse_location_string(location)
                if city:
                    forecast_data = await self.get_weather_forecast_by_name(city, country_code)
                    method_used = "location_name"
                    logger.info(f"Got forecast for silo {silo_id} using location name: {city}, {country_code}")
            except Exception as e:
                logger.warning(f"Failed to get forecast by location name for silo {silo_id}: {e}")
        
        # Add silo information to forecast data
        if forecast_data:
            forecast_data["silo_id"] = silo_id
            forecast_data["silo_name"] = silo_name
            forecast_data["weather_method"] = method_used
            return forecast_data
        
        logger.error(f"Could not get forecast for silo {silo_id} ({silo_name}) at {location}")
        return None

    async def get_multiple_silos_weather(self, silos: List[Dict]) -> List[Dict]:
        """Get weather for multiple silos using coordinates or location name fallback"""
        if not self.api_key:
            return []
            
        tasks = []
        for silo in silos:
            task = self.get_silo_weather(silo)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error for silo {silos[i].get('id', 'unknown')}: {result}")
            elif result is not None:
                valid_results.append(result)
        
        return valid_results
    
    async def get_current_weather(self, lat: float, lon: float, location_name: str) -> Optional[Dict]:
        """Get current weather for a specific location using coordinates"""
        if not self.api_key:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric",  # Celsius, m/s, etc.
                        "lang": "en"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._format_current_weather(data, location_name)
                else:
                    logger.error(f"Weather API error for {location_name}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching weather for {location_name}: {e}")
            return None

    async def get_current_weather_by_name(self, city_name: str, country_code: str = None) -> Optional[Dict]:
        """Get current weather for a location using city name"""
        if not self.api_key:
            return None
            
        try:
            # Format location query
            location_query = city_name
            if country_code:
                location_query = f"{city_name},{country_code}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": location_query,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "en"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Extract the actual location name from the API response
                    actual_location = f"{data['name']}, {data['sys']['country']}"
                    return self._format_current_weather(data, actual_location)
                else:
                    logger.error(f"Weather API error for {location_query}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching weather for {location_query}: {e}")
            return None

    async def get_weather_forecast_by_name(self, city_name: str, country_code: str = None) -> Optional[Dict]:
        """Get 5-day weather forecast for a location using city name"""
        if not self.api_key:
            return None
            
        try:
            # Format location query
            location_query = city_name
            if country_code:
                location_query = f"{city_name},{country_code}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.forecast_url}",
                    params={
                        "q": location_query,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "en"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Extract the actual location name from the API response
                    actual_location = f"{data['city']['name']}, {data['city']['country']}"
                    return self._format_forecast_weather(data, actual_location)
                else:
                    logger.error(f"Forecast API error for {location_query}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching forecast for {location_query}: {e}")
            return None
    
    async def get_weather_forecast(self, lat: float, lon: float, location_name: str) -> Optional[Dict]:
        """Get 5-day weather forecast for a specific location using coordinates"""
        if not self.api_key:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.forecast_url}",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "en"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._format_forecast_weather(data, location_name)
                else:
                    logger.error(f"Forecast API error for {location_name}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching forecast for {location_name}: {e}")
            return None
    
    async def get_multiple_locations_weather(self, locations: List[Dict]) -> List[Dict]:
        """Get weather for multiple locations concurrently (legacy method for backward compatibility)"""
        if not self.api_key:
            return []
            
        tasks = []
        for location in locations:
            task = self.get_current_weather(
                location["latitude"], 
                location["longitude"], 
                location["location"]
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error for location {locations[i]['location']}: {result}")
            elif result is not None:
                result["silo_id"] = locations[i]["id"]
                result["silo_name"] = locations[i]["name"]
                valid_results.append(result)
        
        return valid_results

    async def search_locations(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for locations by name using OpenWeatherMap's geocoding API"""
        if not self.api_key:
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://api.openweathermap.org/geo/1.0/direct",
                    params={
                        "q": query,
                        "limit": limit,
                        "appid": self.api_key
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    locations = []
                    for item in data:
                        location = {
                            "name": item["name"],
                            "country": item["country"],
                            "state": item.get("state", ""),
                            "latitude": item["lat"],
                            "longitude": item["lon"],
                            "display_name": f"{item['name']}, {item.get('state', '')}, {item['country']}".replace(", ,", ",").strip(", ")
                        }
                        locations.append(location)
                    return locations
                else:
                    logger.error(f"Geocoding API error for query '{query}': {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching locations for '{query}': {e}")
            return []
    
    def _format_current_weather(self, data: Dict, location_name: str) -> Dict:
        """Format current weather data for agricultural use"""
        return {
            "location": location_name,
            "timestamp": datetime.now().isoformat(),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "visibility": data.get("visibility", 0) / 1000,  # Convert to km
            "uv_index": data.get("uvi", 0),  # May not be available in current weather
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"].get("deg", 0),
            "weather_condition": data["weather"][0]["main"],
            "weather_description": data["weather"][0]["description"],
            "weather_icon": data["weather"][0]["icon"],
            "clouds": data["clouds"]["all"],
            "precipitation": {
                "rain_1h": data.get("rain", {}).get("1h", 0),
                "rain_3h": data.get("rain", {}).get("3h", 0),
                "snow_1h": data.get("snow", {}).get("1h", 0),
                "snow_3h": data.get("snow", {}).get("3h", 0)
            },
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).isoformat(),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).isoformat(),
            "country": data["sys"]["country"],
            "coordinates": {
                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"]
            },
            "agricultural_metrics": self._calculate_agricultural_metrics(data)
        }
    
    def _format_forecast_weather(self, data: Dict, location_name: str) -> Dict:
        """Format forecast weather data"""
        forecasts = []
        
        for item in data["list"][:16]:  # Next 5 days (3-hour intervals)
            forecast = {
                "datetime": datetime.fromtimestamp(item["dt"]).isoformat(),
                "temperature": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "weather_condition": item["weather"][0]["main"],
                "weather_description": item["weather"][0]["description"],
                "weather_icon": item["weather"][0]["icon"],
                "precipitation_probability": item.get("pop", 0) * 100,  # Convert to percentage
                "precipitation": {
                    "rain_3h": item.get("rain", {}).get("3h", 0),
                    "snow_3h": item.get("snow", {}).get("3h", 0)
                },
                "wind_speed": item["wind"]["speed"],
                "wind_direction": item["wind"].get("deg", 0),
                "clouds": item["clouds"]["all"]
            }
            forecasts.append(forecast)
        
        return {
            "location": location_name,
            "forecasts": forecasts,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_agricultural_metrics(self, data: Dict) -> Dict:
        """Calculate agricultural-specific metrics"""
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        
        # Heat Index calculation (simplified)
        heat_index = temp
        if temp >= 27 and humidity >= 40:
            heat_index = temp + (0.5 * (humidity - 40))
        
        # Evapotranspiration estimate (simplified Penman equation factors)
        et_estimate = max(0, (temp - 5) * 0.1 + wind_speed * 0.05 - humidity * 0.01)
        
        # Growing Degree Days (base 10°C for most crops)
        gdd = max(0, temp - 10)
        
        # Disease pressure risk (high humidity + moderate temp)
        disease_risk = "low"
        if 20 <= temp <= 30 and humidity >= 75:
            disease_risk = "high"
        elif 15 <= temp <= 35 and humidity >= 60:
            disease_risk = "medium"
        
        # Frost risk
        frost_risk = "high" if temp <= 2 else "low"
        
        # Irrigation recommendation
        irrigation_need = "low"
        if et_estimate > 3 and data.get("rain", {}).get("1h", 0) < 1:
            irrigation_need = "high"
        elif et_estimate > 1.5:
            irrigation_need = "medium"
        
        return {
            "heat_index": round(heat_index, 1),
            "evapotranspiration_estimate": round(et_estimate, 2),
            "growing_degree_days": round(gdd, 1),
            "disease_pressure_risk": disease_risk,
            "frost_risk": frost_risk,
            "irrigation_recommendation": irrigation_need
        }

# Singleton instance
weather_service = WeatherService() 