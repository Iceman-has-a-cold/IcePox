# Project Snapshot - Proxmox VM Manager

## Project Overview
A Vue.js frontend application for managing Proxmox VMs with a FastAPI backend.

## Key Components

### 1. Frontend (Vue.js + TypeScript)
**Location:** `frontend/src/views/DashboardView.vue`
**Features:**
- VM Status monitoring (CPU, Memory, Disk, Uptime)
- Control actions (Start, Stop, Shutdown, Reset)
- Progress bars for CPU and Memory usage
- Success message overlays
- Real-time updates via polling

### 2. Backend (FastAPI + Python)
**Location:** `backend/app/proxmox.py`
**Features:**
- Proxmox VE API integration
- VM status retrieval
- VM control actions
- Resource usage monitoring

## Current State

### Working Features
- VM status display
- Control buttons with animations
- Success messages
- Resource usage bars
- Real-time updates

### Removed Features
- Performance graphs (removed due to issues)

## Future Improvements
1. Re-implement performance graphs similar to Proxmox UI
2. Add network usage monitoring
3. Improve error handling
4. Add more VM management features

## Project Structure
frontend/
└── src/
└── views/
└── DashboardView.vue # Main dashboard component
└── services/
└── vmService.ts # API service layer
backend/
└── app/
└── proxmox.py # Proxmox integration
└── main.py # FastAPI application


## Dependencies
- Vue 3
- TypeScript
- Tailwind CSS
- Heroicons
- Chart.js (currently removed)
- FastAPI
- Proxmoxer

## Last Updated
- Date: [Current Date]
- Status: Working dashboard with basic VM management features
- Next Steps: Implementation of performance graphs and network monitoring

## Notes
- The performance graphs were removed due to stability issues
- Current focus is on stability and core functionality
- Real-time updates implemented via polling mechanism