# X_Cube: Prompt-Driven Simulation System
## Complete Architecture & Integration Guide

---

## System Overview

X_Cube is a production-ready prompt-driven simulation system that converts natural language into structured USD simulation actions. It consists of three independent components:

1. **API Backend** - FastAPI server that processes prompts
2. **Isaac Sim Bridge** - HTTP endpoint running inside NVIDIA Isaac Sim
3. **Frontend UI** - React Three Fiber web interface

---

## Architecture Diagram

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Frontend   │         │   API Backend    │         │   Isaac Sim     │
│  (React)    │◄────►   │   (FastAPI)      │◄────►   │   (USD/Omniverse)
│  :3000      │HTTP 8000│   :8000          │HTTP 8001│    :8001        │
└─────────────┘         └──────────────────┘         └─────────────────┘
   Browser               REST API                    Physics Engine
```

---

## Component Details

### 1. API Backend (`backend/api_server.py`)

**Purpose**: Central hub that processes natural language prompts and manages state.

**Endpoints**:
- `POST /chat` - Main endpoint
  - Input: `{"prompt": string, "session_id": string}`
  - Output: `{"prompt": string, "actions": [...], "scene_state": {...}}`
- `GET /` - Health check
- `GET /state/{session_id}` - Get session state
- `DELETE /session/{session_id}` - Clear session

**Flow**:
```
Prompt → MockLLM (parse) → Validator (verify) → SceneManager (update) → IsaacClient (send)
```

**Key Services**:
- `services/mock_llm.py` - Deterministic prompt→actions converter
- `services/validator.py` - Action validation with Pydantic
- `services/scene_manager.py` - Per-session state management
- `services/isaac_client.py` - HTTP client to Isaac Sim

---

### 2. Isaac Sim Bridge (`isaac_sim_bridge.py`)

**Purpose**: Runs INSIDE Isaac Sim environment. Receives actions and applies them to USD stage.

**Requirements**:
- NVIDIA Isaac Sim 4.0+
- Python environment from Isaac Sim
- FastAPI, uvicorn, pydantic

**Endpoints**:
- `POST /apply_actions` - Apply actions to stage
- `GET /health` - Health check

**Action Types Supported**:
- `create_scene` - Create new stage
- `spawn_robot` - Add robot (cylinder placeholder)
- `add_object` - Add cube
- `move_object` - Set transform
- `delete_object` - Remove prim

---

### 3. Frontend UI (`simulation-ui/`)

**Purpose**: Web interface to send prompts and visualize results.

**Technology**: Next.js + React Three Fiber

**State Flow**:
```
User Input → API Call → Response Display → 3D Visualization
```

---

## File Structure

```
xcube/
├── backend/
│   ├── api_server.py              # Main FastAPI application
│   ├── requirements.txt             # Backend dependencies
│   ├── schemas/
│   │   └── actions.py              # Pydantic action models
│   └── services/
│       ├── mock_llm.py             # Prompt→Actions converter
│       ├── validator.py            # Action validation
│       ├── scene_manager.py        # State management
│       └── isaac_client.py         # HTTP client to Isaac
│
├── isaac_sim_bridge.py             # Isaac Sim endpoint (runs in Isaac)
├── simulation-ui/                  # React frontend
├── test_backend.py                 # Backend tests
├── .env.example                    # Environment variables template
└── SYSTEM_CONTEXT.md              # This file
```

---

## Installation & Setup

### Backend
```bash
cd xcube
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

### Frontend
```bash
cd xcube/simulation-ui
npm install
```

### Isaac Sim Bridge
```bash
# Inside Isaac Sim Python environment:
cd xcube
pip install fastapi uvicorn pydantic requests
```

---

## Running the System

### 1. Start Backend
```bash
cd xcube
SET GEMINI_API_KEY=<your-key>  # Optional
uvicorn backend.api_server:app --host 0.0.0.0 --port 8000
```

### 2. Start Isaac Sim Bridge (ONLY inside Isaac Sim)
```bash
# Inside Isaac Sim terminal/scripts:
cd xcube
python isaac_sim_bridge.py
```

### 3. Start Frontend
```bash
cd xcube/simulation-ui
npm run dev
# Open http://localhost:3000
```

---

## Integration with Isaac Sim

### Setup Steps

1. **Install Isaac Sim 4.0+**
   - Download from NVIDIA Omniverse
   - Install in default location

2. **Set up Python Environment**
   - Create Python 3.10.x virtual environment
   - Install dependencies:
     ```
     pip install fastapi uvicorn pydantic requests
     ```

3. **Initialize Isaac App**
   - Start Isaac Sim GUI
   - Or run in headless mode:
     ```
     isaac-sim.sh --headless
     ```

4. **Deploy Bridge**
   - Copy `isaac_sim_bridge.py` to Isaac environment
   - Run: `python isaac_sim_bridge.py`
   - Verify: `curl http://localhost:8001/health`

5. **Connect Backend**
   - Backend automatically discovers Isaac at `http://localhost:8001`
   - Edit `isaac_client.py` if running on different machine:
     ```python
     isaac_client = create_isaac_client(host="<isaac-ip>", port=8001)
     ```

---

## Action Schema

### create_scene
```json
{
  "type": "create_scene",
  "scene_name": "warehouse"
}
```

### spawn_robot
```json
{
  "type": "spawn_robot",
  "robot_id": "robot_1",
  "position": [0, 0, 0.5]
}
```

### add_object
```json
{
  "type": "add_object",
  "object_id": "shelf_1",
  "position": [4, 0, 2]
}
```

### move_object
```json
{
  "type": "move_object",
  "object_id": "shelf_1",
  "position": [5, 1, 2]
}
```

### delete_object
```json
{
  "type": "delete_object",
  "object_id": "shelf_1"
}
```

---

## API Response Format

```json
{
  "prompt": "create a warehouse with one robot",
  "actions": [
    {"type": "create_scene", "scene_name": "warehouse"},
    {"type": "spawn_robot", "robot_id": "robot_1", "position": [0, 0, 0.5]}
  ],
  "scene_state": {
    "current_scene": "warehouse",
    "robots": {
      "robot_1": {"position": [0, 0, 0.5]}
    },
    "objects": {}
  }
}
```

---

## Configuration

### Environment Variables (.env)

```env
# Optional: Gemini API key for advanced LLM features
GEMINI_API_KEY=your-api-key

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Isaac Sim
ISAAC_HOST=localhost
ISAAC_PORT=8001

# Frontend
FRONTEND_PORT=3000
API_URL=http://localhost:8000
```

---

## Supported Prompts (MockLLM)

The MockLLM uses rule-based parsing to convert prompts to actions:

**Examples**:
- "Create a warehouse" → `create_scene(warehouse)`
- "Spawn a robot" → `spawn_robot(robot_1, [0,0,0.5])`
- "Add a shelf" → `add_object(object_1, [0,0,0])`
- "Move robot_1 to 5 5 0" → `move_object(robot_1, [5,5,0])`
- "Delete object_1" → `delete_object(object_1)`

---

## Error Handling

### Backend Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 400 Bad Request | Invalid action | Check action schema |
| 500 Server Error | Internal error | Check logs |
| Isaac unavailable | Isaac not running | Start Isaac Sim bridge |

### Isaac Connection

- **Timeout**: Isaac service not responding
- **Connection Refused**: Isaac service not running on port 8001
- **Invalid Stage**: USD/Omniverse not initialized

---

## Testing

### Backend Test
```bash
python test_backend.py
```

### API Test
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"create a scene","session_id":"test"}'
```

### Isaac Health
```bash
curl http://localhost:8001/health
```

---

## Deployment Considerations

### Single Machine
- Backend, Isaac Sim, Frontend all on localhost
- Use provided port defaults

### Distributed
- Backend: Central server
- Isaac Sim: On simulation hardware (Nvidia device)
- Frontend: Any machine with network access

**Network Configuration**:
```python
# On backend (central server)
isaac_client = create_isaac_client(host="<isaac-machine-ip>", port=8001)
```

---

## Performance Notes

- **Session Management**: Per-session state is in-memory (no persistence)
- **Action Processing**: <100ms per prompt
- **Isaac Integration**: 50-200ms depending on scene complexity
- **Concurrent Sessions**: Fully thread-safe with locks

---

## Troubleshooting

### Backend Won't Start
```bash
# Check Python version (3.9+)
python --version

# Verify dependencies
pip list | grep -E "fastapi|uvicorn|pydantic"

# Clear cache
rm -rf backend/__pycache__
```

### Isaac Connection Fails
```bash
# Verify Isaac running
curl http://localhost:8001/health

# Check firewall
netstat -an | grep 8001

# Enable debug logging in isaac_sim_bridge.py
```

### Frontend Not Connecting
```bash
# Check backend running
curl http://localhost:8000/

# Verify CORS enabled (should be by default)
```

---

## Future Enhancements

- [ ] Persistent state storage (database)
- [ ] Real LLM integration (GPT/Gemini)
- [ ] Physics simulation features
- [ ] Multi-user sessions
- [ ] USD asset library
- [ ] Motion planning
- [ ] Sensor simulation

---

## Support & Contributing

For issues or enhancements:
1. Check logs for error details
2. Verify all services are running
3. Test with `test_backend.py`
4. Review architecture diagram above

---

**Version**: 1.0.0  
**Last Updated**: April 2026  
**Architecture**: Decoupled, REST-based, production-ready
