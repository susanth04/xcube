# Gazebo Harmonic Installation Guide - Windows

## Installation Steps (Using Conda - Recommended)

### 1. Install Miniconda (if not already installed)
- Download from: https://docs.conda.io/en/latest/miniconda.html
- Install for your user account

### 2. Create Gazebo Environment
```bash
conda create -n gazebo-env python=3.10
conda activate gazebo-env
```

### 3. Install Gazebo Harmonic
```bash
conda install libgz-sim8 -c conda-forge
```

### 4. Verify Installation
```bash
gz sim --version
# Should show: Gazebo Sim, version 8.x.x
```

### 5. Test Gazebo
**GUI Mode:**
```bash
gz sim shapes.sdf
```

**Headless Mode:**
```bash
gz sim -s shapes.sdf
```

## Install Python Dependencies

After Gazebo is installed, install the Python bindings and backend dependencies:

```bash
# Activate the gazebo-env conda environment
conda activate gazebo-env
cd C:\xcube

# Install Gazebo Python bindings via conda (recommended)
conda install gz-sim8 gz-transport13 gz-math7 -c conda-forge

# Install backend dependencies
pip install -r backend\requirements.txt
```

**Note**: We use conda to install Gazebo Python bindings instead of pip for better compatibility on Windows.

## Troubleshooting

### Command Not Found
- Ensure Gazebo is in your PATH
- Restart your terminal after installation
- Check: `where gz`

### Python Import Errors
- Verify Python bindings: `python -c "import gz.sim8; print('OK')"`
- Reinstall: `pip install --upgrade gz-sim8`

### Graphics Issues
- Update GPU drivers
- Try headless mode: `gz sim -s`

## Next Steps

After successful installation:
1. Run `python gazebo_sim_bridge.py` to start the bridge
2. Test with: `curl http://localhost:8002/health`
3. Start the backend API and frontend

## Resources

- Official Docs: https://gazebosim.org/docs/harmonic
- Python API: https://gazebosim.org/api/sim/8/
- Model Library: https://app.gazebosim.org/fuel
