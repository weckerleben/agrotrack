
---

# ✅ **Resumen Técnico para Desarrollo – Proyecto AgroTrack**

---

## 🧠 **Objetivo General del Proyecto**

Desarrollar una plataforma inteligente de monitoreo y trazabilidad en tiempo real para el sector agroexportador paraguayo, que integre datos desde el campo, el silo y la logística, y permita optimizar decisiones operativas, reducir pérdidas y mejorar la competitividad.

---

## 🧩 **Componentes del Sistema**

### 1. **Backend**

* **Tecnología recomendada:** Python (FastAPI o Flask)
* **Responsabilidades:**

  * Gestión de usuarios, autenticación
  * Recepción de datos desde sensores (simulados o reales)
  * Endpoints para:

    * Consulta de estado de silos
    * Rutas logísticas
    * Historial de eventos
  * Integración futura con ERP (simulada por ahora)

### 2. **Base de datos**

* **Motor recomendado:** PostgreSQL
* **Esquema tentativo:**

  * `users` (operadores, admin, logísticos)
  * `silos` (ubicación, capacidad, estado)
  * `silo_readings` (fecha, humedad, temperatura, volumen)
  * `logistics` (camión, ruta, estado, ETA)
  * `alerts` (tipo, descripción, silo\_id, timestamp)

### 3. **Frontend (Web)**

* **Tecnología recomendada:** React con Vite
* **Componentes:**

  * Login
  * Dashboard principal

    * Panel de silos con indicadores de estado
    * Alertas activas
    * Mapa de trazabilidad/logística
    * KPIs (rendimiento, humedad promedio, capacidad ocupada)
  * Gestión de usuarios
  * Vista detallada por silo
  * Panel histórico (tendencias por tiempo)

### 4. **IoT / Datos simulados**

* En esta fase, los sensores pueden ser **simulados**.
* Script Python que envíe datos cada X segundos a una API REST:

  ```json
  {
    "silo_id": 1,
    "temperature": 28.5,
    "humidity": 74,
    "volume_percent": 65,
    "timestamp": "2025-06-26T12:00:00Z"
  }
  ```
* (Opcional) Uso de MQTT para emular recepción real

### 5. **Dashboard de datos**

* Integración con Power BI, Grafana o visualización propia en React
* Indicadores claves:

  * Humedad promedio por silo
  * Tasa de ocupación
  * Volumen total en stock
  * Tiempo promedio sin vaciado
  * Alertas en tiempo real

---

## 🧱 **Arquitectura sugerida**

```
[Sensores simulados (Python)] → [API Backend (FastAPI)] → [PostgreSQL DB]
                                                 ↓
                                            [Frontend React]
                                                 ↓
                                        [Dashboard / KPIs]
```

---

## 🎯 **Funcionalidades clave del prototipo (mínimo viable)**

* [ ] Backend con endpoints `/silo`, `/silo/:id/readings`, `/alerts`
* [ ] Frontend con login + dashboard + vista silo + mapa
* [ ] Simulador de datos cada 10 segundos para 3 silos distintos
* [ ] Cálculo de alertas (ej. si humedad > 75% o temp > 32°C)
* [ ] Visualización de tendencias por silo
* [ ] Registro básico de usuarios y roles

---

## 🗓 **Plan de trabajo sugerido**

| Semana | Tareas                                                      |
| ------ | ----------------------------------------------------------- |
| 1      | Definir esquema DB + montar entorno local (Docker opcional) |
| 1–2    | Desarrollar backend + endpoints básicos                     |
| 2–3    | Crear simulador de sensores                                 |
| 2–3    | Frontend con login + dashboard (datos mockeados)            |
| 3–4    | Integración frontend-backend                                |
| 4      | Implementar alertas y KPIs                                  |
| 4      | Preparar demo navegable y presentación final                |

---

## 📦 **Tecnologías sugeridas por stack**

| Capa          | Herramientas sugeridas                      |
| ------------- | ------------------------------------------- |
| Backend       | Python + FastAPI / Flask, Uvicorn, Pydantic |
| Base de datos | PostgreSQL (SQLAlchemy o raw SQL)           |
| Frontend      | React + Vite, Chart.js o Recharts, Mapbox   |
| Datos sim     | Python scripts + requests + cron o asyncio  |
| Hosting demo  | Railway / Render / Local con ngrok          |

---

## 🧪 Extras opcionales para sumar puntos

* Panel de configuración de alertas
* Reportes PDF descargables
* Monitoreo con Grafana o Prometheus (si usan MQTT)
* Mobile view (si da el tiempo)

---
