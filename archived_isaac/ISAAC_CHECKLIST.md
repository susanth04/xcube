# X_Cube - Isaac Sim Integration Checklist

## Pre-Deployment Verification

### System Requirements
- [ ] NVIDIA Isaac Sim 4.0+ installed
- [ ] Python 3.9+ available
- [ ] Node.js 16+ installed
- [ ] Network connectivity verified

### File Structure
- [ ] `backend/api_server.py` exists (renamed from main.py)
- [ ] `isaac_sim_bridge.py` exists (renamed from isaac_server.py)
- [ ] `backend/schemas/actions.py` contains Pydantic models
- [ ] `backend/services/` contains all 4 service files:
  - [ ] `mock_llm.py`
  - [ ] `validator.py`
  - [ ] `scene_manager.py`
  - [ ] `isaac_client.py`
- [ ] `backend/__init__.py` exists
- [ ] `backend/schemas/__init__.py` exists
- [ ] `backend/services/__init__.py` exists

### Configuration Files
- [ ] `.env.example` updated with full config options
- [ ] `SYSTEM_CONTEXT.md` complete and readable
- [ ] `ISAAC_INTEGRATION.md` with setup steps
- [ ] `README.md` with quick start guide
- [ ] `START_SYSTEM.bat` (Windows) or `START_SYSTEM.sh` (Linux/Mac)

### Backend Code
- [ ] `api_server.py` imports from correct modules
  - [ ] `from schemas.actions import ...`
  - [ ] `from services.mock_llm import ...`
  - [ ] `from services.validator import ...`
  - [ ] `from services.scene_manager import ...`
  - [ ] `from services.isaac_client import ...`
- [ ] `/chat` endpoint properly defined
- [ ] CORS middleware enabled
- [ ] Error handling implemented
- [ ] Logging configured

### Isaac Bridge Code
- [ ] `isaac_sim_bridge.py` imports optional Isaac packages
- [ ] Mock mode works without Isaac installed
- [ ] `/apply_actions` endpoint receives POST requests
- [ ] `/health` endpoint returns status
- [ ] Action handlers implemented:
  - [ ] `_create_scene_action()`
  - [ ] `_spawn_robot_action()`
  - [ ] `_add_object_action()`
  - [ ] `_move_object_action()`
  - [ ] `_delete_object_action()`

### Action Validation
- [ ] Pydantic models validate all fields
- [ ] Position validation: exactly 3 numeric values
- [ ] Action type validation: only 5 allowed types
- [ ] Error messages are clear and actionable

### Service Tests
- [ ] MockLLM generates correct actions
- [ ] Validator rejects invalid actions
- [ ] SceneManager maintains separate sessions
- [ ] IsaacClient handles timeouts and retries

### Frontend Integration
- [ ] Frontend can call `/chat` endpoint
- [ ] CORS allows frontend requests
- [ ] Response format matches expected structure
- [ ] Scene state displays correctly

### Networks & Ports
- [ ] Backend port 8000 is available
- [ ] Isaac port 8001 is available
- [ ] Frontend port 3000 is available
- [ ] Firewall allows inter-service communication

---

## Local Testing (No Isaac Required)

```bash
# 1. Test Backend
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.api_server:app --reload

# 2. Test API (new terminal)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"create a warehouse","session_id":"test"}'

# Expected: 200 OK with actions and scene_state

# 3. Test Validator
python -c "from backend.services.validator import create_validator; v = create_validator(); print('✓ Validator OK')"

# 4. Test MockLLM
python -c "from backend.services.mock_llm import create_mock_llm; llm = create_mock_llm(); actions = llm.generate_actions('test'); print(f'✓ Generated {len(actions)} actions')"
```

---

## Isaac Sim Integration Testing

```bash
# 1. Verify Isaac environment
python -c "from pxr import Usd; print('✓ USD available')"
python -c "from omni.isaac.kit import SimulationApp; print('✓ Isaac available')"

# 2. Test Bridge in mock mode
python isaac_sim_bridge.py
# Should show: Isaac Sim not available - running in mock mode
# Verify: curl http://localhost:8001/health

# 3. Test Bridge inside Isaac Sim
# (With Isaac Sim running)
# Should show: Isaac Sim initialized
# Verify: curl http://localhost:8001/health returns {"status":"ok"}

# 4. Test Backend ↔ Isaac connection
# Backend logs should show: Isaac Sim response: {...}
```

---

## Deployment Checklist

### Before Production Deployment
- [ ] All tests pass
- [ ] No hardcoded credentials in code
- [ ] Environment variables properly configured
- [ ] Logging is enabled and working
- [ ] Error handling for all failure cases
- [ ] Network security configured (firewall rules)
- [ ] Authentication/authorization considered
- [ ] Rate limiting configured (if needed)

### Single-Machine Deployment
- [ ] Backend, Frontend, Isaac on localhost
- [ ] Ports 8000, 3000, 8001 available
- [ ] Virtual environments properly configured
- [ ] Services auto-start on system reboot (optional)

### Distributed Deployment
- [ ] Network connectivity between machines tested
- [ ] Firewall allows cross-machine communication
- [ ] Isaac client configured with correct hostname
- [ ] DNS resolution verified
- [ ] VPN/SSH tunneling configured (if needed)

### Monitoring & Logging
- [ ] Log files written to persistent location
- [ ] Logs rotated to prevent disk fill
- [ ] Health check endpoints monitored
- [ ] Error alerts configured

---

## Post-Deployment Verification

```bash
# 1. Check all services running
curl http://localhost:8000/
curl http://localhost:3000/
curl http://localhost:8001/health

# 2. Test full workflow
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"create a scene","session_id":"prod_test"}'

# 3. Verify Isaac connection
# Backend logs should show Isaac Sim response

# 4. Monitor for errors
# Check logs in each terminal for errors

# 5. Load test (optional)
# Send multiple concurrent requests
# Monitor response times and errors
```

---

## Troubleshooting Matrix

| Issue | Cause | Solution |
|-------|-------|----------|
| Backend won't start | Import error | Check module paths in api_server.py |
| Isaac won't connect | Isaac not running | Start isaac_sim_bridge.py inside Isaac |
| Frontend can't reach API | CORS issue | Verify CORS middleware in api_server.py |
| Actions not applied | Invalid action | Check validator output, check action schema |
| Bridge errors | USD environment | Run from Isaac Python environment |

---

## Documentation Files

✓ Created & Updated:
- [x] `README.md` - Quick start guide
- [x] `SYSTEM_CONTEXT.md` - Full architecture
- [x] `ISAAC_INTEGRATION.md` - Isaac setup
- [x] `.env.example` - Configuration template
- [x] `START_SYSTEM.bat` - Windows launcher
- [x] `START_SYSTEM.sh` - Linux/Mac launcher
- [x] `ISAAC_CHECKLIST.md` - This file

---

## Sign-Off

**System Ready for Production**: [ ]

Verified by: _________________  
Date: _________________  
Notes: _________________

---

**Version**: 1.0.0  
**Last Updated**: April 2026
