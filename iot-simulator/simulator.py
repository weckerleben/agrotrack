import asyncio
import random
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class AgroTrackIoTSimulator:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
        self.auth_token = None
        self.silos = []
        
        # Simulation parameters
        self.temp_base_ranges = {
            1: (22, 28),    # Silo Central A
            2: (24, 30),    # Silo Norte B  
            3: (21, 27),    # Silo Sur C
            4: (23, 29),    # Silo Este D
            5: (25, 31),    # Silo Oeste E
        }
        
        self.humidity_base_ranges = {
            1: (65, 75),    # Silo Central A
            2: (70, 80),    # Silo Norte B
            3: (60, 70),    # Silo Sur C
            4: (68, 78),    # Silo Este D
            5: (72, 82),    # Silo Oeste E
        }
        
        # Volume simulation (starts high and decreases over time)
        self.volume_states = {
            1: 85.0,  # Starting at 85%
            2: 72.0,  # Starting at 72%
            3: 94.0,  # Starting at 94%
            4: 68.0,  # Starting at 68%
            5: 81.0,  # Starting at 81%
        }
        
        print("🌾 AgroTrack IoT Simulator initialized")

    async def authenticate(self):
        """Authenticate with the API"""
        login_data = {
            "email": "operator@agrotrack.com",
            "password": "operator123"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login/json",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                print(f"✅ Authenticated as: {data['full_name']} ({data['role']})")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    async def get_silos(self):
        """Fetch silos from the API"""
        if not self.auth_token:
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{self.base_url}/silos", headers=headers)
            
            if response.status_code == 200:
                self.silos = response.json()
                print(f"📊 Found {len(self.silos)} silos to monitor")
                for silo in self.silos:
                    print(f"   - {silo['name']} (ID: {silo['id']}) - {silo['location']}")
                return True
            else:
                print(f"❌ Failed to fetch silos: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error fetching silos: {e}")
            return False

    def generate_realistic_reading(self, silo_id: int) -> Dict:
        """Generate realistic sensor reading for a silo"""
        current_hour = datetime.now().hour
        
        # Temperature varies by time of day (warmer during day)
        temp_base_min, temp_base_max = self.temp_base_ranges.get(silo_id, (20, 30))
        
        # Day/night temperature variation
        if 6 <= current_hour <= 18:  # Daytime
            temp_adjustment = random.uniform(2, 6)
        else:  # Nighttime
            temp_adjustment = random.uniform(-3, 1)
            
        temperature = random.uniform(temp_base_min, temp_base_max) + temp_adjustment
        
        # Add some random spikes occasionally (5% chance)
        if random.random() < 0.05:
            temperature += random.uniform(3, 8)
        
        # Humidity varies inversely with temperature (somewhat)
        humidity_base_min, humidity_base_max = self.humidity_base_ranges.get(silo_id, (60, 80))
        humidity = random.uniform(humidity_base_min, humidity_base_max)
        
        # Higher temps tend to reduce humidity slightly
        if temperature > temp_base_max + 2:
            humidity -= random.uniform(5, 15)
        
        # Add humidity spikes occasionally (3% chance)
        if random.random() < 0.03:
            humidity += random.uniform(10, 20)
        
        # Ensure humidity stays within realistic bounds
        humidity = max(40, min(95, humidity))
        
        # Volume decreases slowly over time (consumption simulation)
        current_volume = self.volume_states.get(silo_id, 50.0)
        
        # 70% chance of slight decrease, 20% chance of no change, 10% chance of increase (refill)
        volume_change_type = random.random()
        if volume_change_type < 0.7:
            # Gradual consumption
            volume_change = -random.uniform(0.1, 1.5)
        elif volume_change_type < 0.9:
            # No change
            volume_change = 0
        else:
            # Refill event
            volume_change = random.uniform(5, 25)
            print(f"🚛 Simulated refill event for Silo {silo_id}")
        
        new_volume = current_volume + volume_change
        new_volume = max(0, min(100, new_volume))  # Clamp between 0-100%
        
        self.volume_states[silo_id] = new_volume
        
        # Calculate volume in tons (estimate based on silo capacity)
        silo_capacity = 1000  # Default capacity, should get from silo data
        for silo in self.silos:
            if silo['id'] == silo_id:
                silo_capacity = silo['capacity_tons']
                break
        
        volume_tons = (silo_capacity * new_volume) / 100
        
        return {
            "silo_id": silo_id,
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "volume_percent": round(new_volume, 2),
            "volume_tons": round(volume_tons, 2)
        }

    async def send_reading(self, reading: Dict):
        """Send a reading to the API"""
        if not self.auth_token:
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Remove silo_id from the payload as it's in the URL
        silo_id = reading.pop("silo_id")
        
        try:
            response = requests.post(
                f"{self.base_url}/silos/{silo_id}/readings",
                json=reading,
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"📡 Silo {silo_id}: T={reading['temperature']}°C, H={reading['humidity']}%, V={reading['volume_percent']}%")
                return True
            else:
                print(f"❌ Failed to send reading for Silo {silo_id}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending reading for Silo {silo_id}: {e}")
            return False

    async def check_and_create_alerts(self, reading: Dict, silo_id: int):
        """Check conditions and create alerts if necessary"""
        if not self.auth_token:
            return
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Get silo info for thresholds
        silo_info = next((s for s in self.silos if s['id'] == silo_id), None)
        if not silo_info:
            return
        
        max_temp = float(silo_info.get('max_temperature', 30.0))
        max_humidity = float(silo_info.get('max_humidity', 75.0))
        
        alerts_to_create = []
        
        # Temperature alert
        if reading['temperature'] > max_temp:
            severity = "critical" if reading['temperature'] > max_temp + 5 else "high"
            alerts_to_create.append({
                "silo_id": silo_id,
                "alert_type": "temperature",
                "severity": severity,
                "title": f"High Temperature in {silo_info['name']}",
                "description": f"Temperature {reading['temperature']}°C exceeds threshold {max_temp}°C",
                "value": reading['temperature'],
                "threshold": max_temp
            })
        
        # Humidity alert
        if reading['humidity'] > max_humidity:
            severity = "critical" if reading['humidity'] > max_humidity + 10 else "high"
            alerts_to_create.append({
                "silo_id": silo_id,
                "alert_type": "humidity",
                "severity": severity,
                "title": f"High Humidity in {silo_info['name']}",
                "description": f"Humidity {reading['humidity']}% exceeds threshold {max_humidity}%",
                "value": reading['humidity'],
                "threshold": max_humidity
            })
        
        # Volume alerts - both low and high capacity
        if reading['volume_percent'] < 10:
            # Low volume alert (empty silo)
            severity = "critical" if reading['volume_percent'] < 5 else "medium"
            alerts_to_create.append({
                "silo_id": silo_id,
                "alert_type": "volume",
                "severity": severity,
                "title": f"Low Volume in {silo_info['name']}",
                "description": f"Volume {reading['volume_percent']}% is critically low - refill needed",
                "value": reading['volume_percent'],
                "threshold": 10.0
            })
        elif reading['volume_percent'] >= 90:
            # High volume alert (full silo)
            severity = "critical" if reading['volume_percent'] >= 95 else "high"
            alerts_to_create.append({
                "silo_id": silo_id,
                "alert_type": "volume",
                "severity": severity,
                "title": f"High Capacity in {silo_info['name']}",
                "description": f"Volume {reading['volume_percent']}% is very high - shipment needed",
                "value": reading['volume_percent'],
                "threshold": 90.0
            })
        elif reading['volume_percent'] >= 75:
            # Medium-high volume alert (getting full)
            alerts_to_create.append({
                "silo_id": silo_id,
                "alert_type": "volume",
                "severity": "medium",
                "title": f"High Capacity Warning in {silo_info['name']}",
                "description": f"Volume {reading['volume_percent']}% is getting high - plan shipments",
                "value": reading['volume_percent'],
                "threshold": 75.0
            })
        
        # Send alerts
        for alert in alerts_to_create:
            try:
                response = requests.post(
                    f"{self.base_url}/alerts",
                    json=alert,
                    headers=headers
                )
                
                if response.status_code == 200:
                    print(f"🚨 Alert created: {alert['title']} ({alert['severity']})")
                
            except Exception as e:
                print(f"❌ Error creating alert: {e}")

    async def simulate_reading_cycle(self):
        """Simulate one cycle of readings for all silos"""
        if not self.silos:
            print("❌ No silos available for simulation")
            return
            
        print(f"\n🔄 Starting reading cycle at {datetime.now().strftime('%H:%M:%S')}")
        
        for silo in self.silos:
            if silo['status'] == 'active':
                reading = self.generate_realistic_reading(silo['id'])
                
                # Send reading
                reading_copy = reading.copy()  # Make a copy since send_reading modifies it
                success = await self.send_reading(reading)
                
                if success:
                    # Check for alerts
                    await self.check_and_create_alerts(reading_copy, silo['id'])
                
                # Small delay between readings
                await asyncio.sleep(0.5)

    async def run_simulation(self, interval_seconds: int = 10):
        """Run the continuous simulation"""
        print(f"🚀 Starting AgroTrack IoT Simulation (interval: {interval_seconds}s)")
        
        # Initial setup
        if not await self.authenticate():
            return
            
        if not await self.get_silos():
            return
        
        print(f"\n✅ Simulation ready! Sending readings every {interval_seconds} seconds...")
        print("Press Ctrl+C to stop the simulation\n")
        
        try:
            while True:
                await self.simulate_reading_cycle()
                await asyncio.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Simulation stopped by user")
        except Exception as e:
            print(f"\n❌ Simulation error: {e}")

async def main():
    """Main function"""
    simulator = AgroTrackIoTSimulator()
    
    # Default to 10 second intervals, but can be configured
    interval = int(os.getenv("SIMULATION_INTERVAL", "10"))
    
    await simulator.run_simulation(interval_seconds=interval)

if __name__ == "__main__":
    asyncio.run(main()) 