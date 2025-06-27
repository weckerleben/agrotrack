# 🌾 AgroTrack - Smart Agricultural Monitoring Platform

A comprehensive real-time monitoring and traceability platform for Paraguay's agro-export sector, integrating data from field operations, silo storage, and logistics operations. **Currently operational and generating live data!**

## 🚀 Current Status

✅ **Fully Functional System**  
✅ **5 Paraguay Silos** with real-time monitoring  
✅ **Live IoT Data Simulation** generating sensor readings every 10 seconds  
✅ **Automated Alert System** with threshold monitoring  
✅ **Complete Web Dashboard** with all pages functional  
✅ **Role-based Authentication** system  
✅ **PostgreSQL Database** with sample data  
✅ **Advanced Analytics** with Grafana dashboards  
✅ **Database Administration** with pgAdmin interface  

## 🎯 Features

### 📊 **Real-time Silo Monitoring**
- **5 Active Silos** across Paraguay (Asunción, San Lorenzo, Luque, Capiatá, Mariano Roque Alonso)
- **Live sensor readings**: Temperature, humidity, volume levels
- **Visual progress indicators** with color-coded status
- **Capacity monitoring** and utilization tracking
- **Historical data** with 24-hour statistics

### 🚨 **Smart Alerts System**
- **Automated threshold monitoring** for temperature, humidity, and volume
- **Real-time alert generation** when conditions exceed safe limits
- **Severity levels**: Critical, High, Medium, Low
- **Alert filtering** and resolution tracking
- **Visual dashboard** with active alert counts

### 🚛 **Logistics Tracking**
- **Shipment management** with status tracking
- **Route monitoring** (origin → destination)
- **Driver and vehicle management**
- **Delivery status updates** (pending, in transit, delivered, delayed)
- **Performance analytics**

### 👥 **User Management**
- **Role-based access control**: Admin, Operator, Logistics
- **User authentication** with JWT tokens
- **Permission management** by role
- **User activity tracking**

### 📈 **Interactive Dashboard**
- **Real-time KPIs** and system metrics
- **Storage overview** with capacity utilization
- **System health monitoring**
- **Quick action buttons**

### 📊 **Advanced Analytics (Grafana)**
- **Comprehensive monitoring dashboards** with real-time data visualization
- **Silo Monitoring Dashboard**: Temperature/humidity trends, volume patterns, capacity gauges
- **Alerts Analytics Dashboard**: Alert frequency, severity analysis, resolution tracking
- **Logistics Analytics Dashboard**: Shipment performance, route efficiency, delivery metrics
- **Historical data analysis** with customizable time ranges
- **Automated refresh** every 5-30 seconds for live monitoring

## 🏗️ Architecture

```
[IoT Simulator] → [FastAPI Backend] → [PostgreSQL Database]
       ↓               ↓                       ↓
[Python asyncio]   [SQLAlchemy]         [Sample Data]
       ↓               ↓                       ↓
   [Live Data]    [REST API]          [5 Paraguay Silos]
                      ↓                       ↓
              [React Frontend]          [pgAdmin Interface]
                      ↓                       ↓
           [Real-time Dashboard]      [Database Management]
                                              ↓
                                      [Grafana Analytics]
                                              ↓
                                   [Advanced Monitoring]
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **Pydantic** - Data validation
- **JWT** - Authentication
- **bcrypt** - Password hashing

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Router** - Navigation
- **Lucide React** - Icons

### IoT Simulation
- **Python asyncio** - Async simulation
- **Realistic data generation** - Day/night cycles, random events
- **HTTP requests** - Real API integration

### Analytics & Administration
- **Grafana** - Advanced analytics and monitoring dashboards
- **pgAdmin** - Web-based PostgreSQL database administration
- **Pre-configured dashboards** - Silo monitoring, alerts, logistics analytics

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration

## 📦 Project Structure

```
agrotrack/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/endpoints/  # API routes
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── silos.py       # Silo management
│   │   │   ├── alerts.py      # Alert system
│   │   │   ├── users.py       # User management
│   │   │   └── logistics.py   # Logistics tracking
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py      # Configuration
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # JWT & auth utilities
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   └── Layout.tsx     # Main layout
│   │   ├── pages/             # Page components
│   │   │   ├── Dashboard.tsx  # Main dashboard
│   │   │   ├── SilosPage.tsx  # Silo monitoring
│   │   │   ├── AlertsPage.tsx # Alert management
│   │   │   ├── UsersPage.tsx  # User management
│   │   │   └── LogisticsPage.tsx # Logistics
│   │   ├── contexts/          # React contexts
│   │   │   └── AuthContext.tsx # Authentication
│   │   └── services/          # API integration
│   │       └── api.ts         # Axios configuration
│   ├── package.json          # Node.js dependencies
│   └── Dockerfile           # Frontend container
├── iot-simulator/            # IoT data simulator
│   ├── simulator.py         # Main simulation script
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Simulator container
├── database/               # Database initialization
│   └── init.sql           # Schema & sample data
├── docker-compose.yml     # Full stack orchestration
├── env.example           # Environment variables
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites
- **Docker** and **Docker Compose**
- **Node.js 18+** (for local frontend development)
- **Python 3.9+** (for local development)

### 🐳 Full Stack Setup with Docker (Recommended)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd agrotrack
```

2. **Start all services:**
```bash
docker-compose up --build -d
```

3. **Access the application:**
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Documentation**: http://localhost:8000/redoc
- **Database Admin (pgAdmin)**: http://localhost:5050
- **Analytics & Monitoring (Grafana)**: http://localhost:3001

4. **Login with default credentials:**
- **Admin**: `admin@agrotrack.com` / `admin123`
- **Operator**: `operator@agrotrack.com` / `operator123`
- **Logistics**: `logistics@agrotrack.com` / `logistics123`
- **Database Admin (pgAdmin)**: `admin@agrotrack.com` / `admin123`
- **Analytics (Grafana)**: `admin` / `admin123`

### 🔧 Local Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL with Docker
docker-compose up db -d

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:3000
```

#### IoT Simulator
```bash
cd iot-simulator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python simulator.py
```

## 📊 Live Data & Features

### 🏗️ **Paraguay Silos Currently Monitored**
1. **Silo Central A** - Asunción, Paraguay (1,000 tons capacity)
2. **Silo Norte B** - San Lorenzo, Paraguay (800 tons capacity)
3. **Silo Sur C** - Luque, Paraguay (1,200 tons capacity)
4. **Silo Este D** - Capiatá, Paraguay (900 tons capacity)
5. **Silo Oeste E** - Mariano Roque Alonso, Paraguay (750 tons capacity)

### 📡 **IoT Simulation Features**
- **Real-time data generation** every 10 seconds
- **Realistic temperature cycles** (day/night variations)
- **Random events**: refill operations, equipment variations
- **Automatic alert generation** when thresholds exceeded
- **Volume consumption simulation** with gradual decrease

### 🎯 **Alert Thresholds**
- **Temperature**: > 30°C triggers alerts
- **Humidity**: > 75% triggers alerts
- **Volume**: < 10% triggers low volume alerts
- **Severity escalation**: Automatic critical alerts for extreme values

## 🎯 Default User Accounts

| Role | Email | Password | Permissions |
|------|-------|----------|-------------|
| **Admin** | `admin@agrotrack.com` | `admin123` | Full system access, user management |
| **Operator** | `operator@agrotrack.com` | `operator123` | Silo monitoring, alert management |
| **Logistics** | `logistics@agrotrack.com` | `logistics123` | Logistics operations, shipment tracking |

## 📊 Key Metrics Dashboard

The system currently tracks:
- **Storage capacity**: 4,650 tons total across 5 silos
- **Current volume**: Live tracking with percentage and tons
- **Temperature monitoring**: Real-time readings with threshold alerts
- **Humidity levels**: Continuous monitoring for optimal storage
- **Alert frequency**: Active, critical, and resolved alert counts
- **Reading statistics**: 24-hour reading counts and averages

## 📈 Analytics & Monitoring (Grafana)

### Pre-built Dashboards
Access advanced analytics at **http://localhost:3001** with `admin` / `admin123`

#### 🌾 **Silo Monitoring Dashboard**
- **Real-time temperature trends** across all 5 Paraguay silos
- **Humidity level monitoring** with threshold visualization
- **Volume level gauges** with color-coded status indicators
- **Historical trends** showing consumption and refill patterns
- **Auto-refresh every 5 seconds** for live monitoring

#### 🚨 **Alerts Analytics Dashboard**
- **Active alerts counter** with critical alert highlighting
- **Alert frequency charts** showing patterns by severity over time
- **Alert type distribution** pie charts for the last 7 days
- **Recent alerts table** with silo information and timestamps
- **Resolution tracking** showing 24-hour alert handling performance

#### 🚛 **Logistics Analytics Dashboard**
- **Shipment status overview** with real-time counters
- **Transportation metrics**: In transit, delivered today, delayed shipments
- **Status distribution charts** showing logistics performance
- **Daily activity trends** comparing departures vs arrivals
- **Recent shipments table** with route and driver information

### Advanced Features
- **Custom time ranges**: Last hour, 6 hours, 24 hours, 7 days, 30 days
- **Interactive charts**: Zoom, pan, and drill-down capabilities  
- **Real-time updates**: Live data streaming every 5-30 seconds
- **Multi-silo comparison**: Compare performance across Paraguay locations
- **Threshold monitoring**: Visual indicators when values exceed limits

## 🔧 Configuration

### Environment Variables
Copy `env.example` to `.env` and modify as needed:
```bash
cp env.example .env
```

Key configurations:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing secret (change in production!)
- `ALLOWED_ORIGINS`: CORS origins for frontend access
- `VITE_API_URL`: Frontend API endpoint configuration
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key for weather data

### Weather API Setup
1. **Get OpenWeatherMap API Key** (free tier available):
   - Sign up at https://openweathermap.org/api
   - Subscribe to "Current Weather Data" (free for 1000 calls/day)
   - Copy your API key

2. **Configure the API key**:
   ```bash
   # In your .env file
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```

3. **Weather features include**:
   - Real-time weather for all silo locations in Paraguay
   - Agricultural metrics (Growing Degree Days, Heat Index, Evapotranspiration)
   - Disease pressure risk assessment
   - Irrigation recommendations
   - Frost warnings
   - 5-day weather forecasts

### Database
- **Automatic initialization** with sample data
- **5 Paraguay silos** with realistic coordinates
- **3 default users** with different roles
- **Database migrations** handled automatically

## 🚨 Troubleshooting

### Common Issues

1. **Blank Silos Page**
   - Ensure you're logged in with valid credentials
   - Check browser console for API errors
   - Verify backend is running on port 8000

2. **Authentication Issues**
   - Clear browser localStorage and login again
   - Check backend logs for JWT errors
   - Verify credentials match default accounts

3. **Docker Issues**
   - Run `docker-compose down -v` to reset volumes
   - Check `docker-compose logs` for service errors
   - Ensure ports 3000, 8000, 5432 are available

4. **IoT Simulator Not Working**
   - Check authentication credentials in simulator
   - Verify backend API is accessible
   - Look for 422 errors indicating data format issues

5. **Frontend Docker Container Won't Start**
   - TypeScript compilation errors prevent container startup
   - Fix unused imports: `TrendingUp` in Dashboard.tsx, `Calendar` in LogisticsPage.tsx
   - Resolve type conflicts in SilosPage.tsx (string/number mismatches)
   - Run `npm run build` locally to identify all compilation errors

### Logs and Debugging
```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Real-time log following
docker-compose logs -f backend
```

## 📖 API Documentation

When the backend is running, comprehensive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints
- `POST /api/v1/auth/login/json` - User authentication
- `GET /api/v1/silos/` - List all silos with latest readings
- `POST /api/v1/silos/{silo_id}/readings` - Submit sensor readings
- `GET /api/v1/alerts/` - List system alerts
- `GET /api/v1/users/` - User management (admin only)

## 🛡️ Security Features

- **JWT-based authentication** with configurable expiration
- **bcrypt password hashing** for secure storage
- **Role-based access control** (RBAC)
- **CORS protection** with configurable origins
- **SQL injection protection** via SQLAlchemy ORM
- **Request validation** with Pydantic schemas

## 🚀 Production Deployment

### Docker Production Setup
1. Update `env.example` with production values
2. Change default passwords and secret keys
3. Configure proper database credentials
4. Set up reverse proxy (nginx/Apache)
5. Enable HTTPS with SSL certificates
6. Configure backup strategies for PostgreSQL

### Security Checklist
- [ ] Change all default passwords
- [ ] Generate secure SECRET_KEY
- [ ] Configure production database
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Enable database backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for all new React components
- Add unit tests for new features
- Update API documentation for new endpoints
- Test with different user roles

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for Paraguay's agricultural sector
- Inspired by modern IoT monitoring solutions
- Designed for scalability and real-world deployment

---

**🌾 AgroTrack - Monitoring Paraguay's Agricultural Future** 🇵🇾 