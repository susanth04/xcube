# X_Cube: Prompt-Driven Gazebo Simulation System

A production-ready system that converts natural language prompts into structured simulation actions using Gazebo Harmonic.

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Gazebo Harmonic 8.0+ (for physical simulation)

### Installation

**1. Install Gazebo Harmonic (Using Conda)**

```bash
# Install Miniconda (if not already installed)
# Download from: https://docs.conda.io/en/latest/miniconda.html

# Create Gazebo environment
conda create -n gazebo-env python=3.10
conda activate gazebo-env

# Install Gazebo Harmonic
conda install libgz-sim8 -c conda-forge

# Verify installation
gz sim --version
```

See **GAZEBO_INSTALLATION.md** for detailed instructions.

**2. Install Project Dependencies**

```bash
# In the gazebo-env conda environment
cd xcube
conda activate gazebo-env

# Install Gazebo Python bindings
conda install gz-sim8 gz-transport13 gz-math7 -c conda-forge

# Install backend dependencies
pip install -r backend/requirements.txt
```

**3. Frontend Setup (Optional)**
```bash
cd xcube/simulation-ui
npm install
```

### Running the System

**Quick Start - Use the launcher script:**

Windows:
```bash
start_all.bat
```

Linux/Mac:
```bash
chmod +x start_all.sh
./start_all.sh
```

**Manual Start:**

**Terminal 1 - Start Gazebo Bridge**
```bash
conda activate gazebo-env
cd xcube
python gazebo_sim_bridge.py
```

**Terminal 2 - Start Backend API**
```bash
conda activate gazebo-env
cd xcube
python -m uvicorn backend.api_server:app --host 0.0.0.0 --port 8000
```

**Terminal 3 - Start Frontend (Optional)**
```bash
cd xcube/simulation-ui
npm run dev
```

**Access:**
- Backend API: **http://localhost:8000**
- Gazebo Bridge: **http://localhost:8002/health**
- Frontend: **http://localhost:3000**

---

## Architecture

```
Frontend (React)        →  Backend API (FastAPI)  →  Gazebo Bridge  →  Gazebo Sim
:3000                      :8000                      :8002              SDF World
```

### Key Components

- **Backend** (`backend/`)
  - `api_server.py` - FastAPI application
  - `services/` - Business logic
  - `schemas/` - Data validation

- **Gazebo Bridge** (`gazebo_sim_bridge.py`)
  - Standalone HTTP server
  - Applies actions to Gazebo world
  - Uses SDF format for models

- **Frontend** (`simulation-ui/`)
  - React Next.js application
  - React Three Fiber visualization

---

## API Usage

### POST /chat
Convert prompt to simulation actions.

**Request**:
```json
{
  "prompt": "Create a warehouse with one robot",
  "session_id": "my_session"
}
```

**Response**:
```json
{
  "prompt": "Create a warehouse with one robot",
  "actions": [
    {"type": "create_scene", "scene_name": "warehouse"},
    {"type": "spawn_robot", "robot_id": "robot_1", "position": [0, 0, 0.5]}
  ],
  "scene_state": {
    "current_scene": "warehouse",
    "robots": {"robot_1": {"position": [0, 0, 0.5]}},
    "objects": {}
  }
}
```

---

## File Structure

```
xcube/
├── backend/
│   ├── api_server.py              # Main FastAPI app
│   ├── requirements.txt
│   ├── schemas/
│   │   └── actions.py             # Pydantic models
│   └── services/
│       ├── mock_llm.py            # Prompt parsing
│       ├── validator.py           # Action validation
│       ├── scene_manager.py       # State management
│       └── gazebo_client.py       # Gazebo HTTP client
│
├── gazebo_sim_bridge.py           # Gazebo bridge server
├── simulation-ui/                 # React frontend
├── GAZEBO_INTEGRATION.md         # Integration guide
├── GAZEBO_INSTALLATION.md        # Installation guide
├── SYSTEM_CONTEXT.md             # Full architecture guide
├── .env.example                   # Configuration template
└── README.md                      # This file
```

---

## Configuration

Copy `.env.example` to `.env` and configure:

```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
GAZEBO_HOST=localhost
GAZEBO_PORT=8002
```

---

## Supported Actions

- `create_scene` - Create new simulation scene
- `spawn_robot` - Add robot to scene
- `add_object` - Add object (cube)
- `move_object` - Move object to position
- `delete_object` - Remove object

---

## Testing

**Automated Test Script:**

Windows:
```bash
# Start services first with start_all.bat
# Then run tests:
test_system.bat
```

**Manual Testing:**
```bash
# Test backend
python test_backend.py

# Test API endpoints
curl http://localhost:8000/
curl http://localhost:8002/health

# Test chat functionality
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Create a scene","session_id":"test"}'
```

---

## Gazebo Harmonic Integration

For physical simulation with Gazebo Harmonic:

1. Install Gazebo Harmonic (see GAZEBO_INSTALLATION.md)
2. Install Python bindings: `pip install gz-sim8 gz-transport13 gz-math7`
3. Run `python gazebo_sim_bridge.py`
4. Backend will auto-connect on startup

See **GAZEBO_INTEGRATION.md** for detailed integration steps, troubleshooting, and advanced usage.

---

## Documentation

- **GAZEBO_INTEGRATION.md** - Complete Gazebo integration guide
- **GAZEBO_INSTALLATION.md** - Installation instructions
- **SYSTEM_CONTEXT.md** - Full architecture guide
- **backend/api_server.py** - API documentation
- **gazebo_sim_bridge.py** - Gazebo bridge details

---

## Features

✅ Prompt-to-action conversion  
✅ Action validation  
✅ Per-session state management  
✅ Gazebo Harmonic integration  
✅ REST API  
✅ CORS enabled  
✅ Thread-safe operations  
✅ Error handling & logging  
✅ Open-source simulation backend

---

## Support

For issues or questions:
1. Check SYSTEM_CONTEXT.md for troubleshooting
2. Review logs in terminal
3. Verify all services are running
4. Run tests with `test_backend.py`

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: April 2026
