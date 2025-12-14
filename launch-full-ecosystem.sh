#!/bin/bash

# AetherFrame Complete Ecosystem Launcher
# Launches all components for demo recording

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

clear

cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║              AETHERFRAME FULL ECOSYSTEM LAUNCHER              ║
║                                                              ║
║  Starting all components:                                    ║
║  ✓ Backend API (FastAPI)                                    ║
║  ✓ Frontend Dashboard (React)                               ║
║  ✓ ReverisNoctis Desktop App (Tauri)                        ║
║  ✓ MinIO Console                                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF

echo ""
sleep 2

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Step 1: Verify Docker services
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 1: Checking Backend Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if check_port 8000; then
    echo -e "${GREEN}✓ FastAPI Backend running on :8000${NC}"
else
    echo -e "${RED}✗ Backend not running. Start with: cd packages/core && docker compose up -d${NC}"
fi

if check_port 9001; then
    echo -e "${GREEN}✓ MinIO Console running on :9001${NC}"
else
    echo -e "${YELLOW}⚠ MinIO not detected${NC}"
fi

sleep 2

# Step 2: Start Frontend Dashboard
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 2: Starting Frontend Dashboard${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Kill any existing Vite server on port 3001
if check_port 3001; then
    echo -e "${YELLOW}⚠ Port 3001 in use, killing existing process...${NC}"
    lsof -ti:3001 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "  🌐 Starting React Dashboard on port 3001..."
cd packages/frontend
npm run dev -- --port 3001 > /tmp/aetherframe-frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

sleep 3

if check_port 3001; then
    echo -e "${GREEN}✓ Frontend Dashboard started on http://localhost:3001${NC}"
else
    echo -e "${RED}✗ Frontend failed to start. Check /tmp/aetherframe-frontend.log${NC}"
fi

# Step 3: Start ReverisNoctis
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 3: Starting ReverisNoctis Desktop App${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Kill any existing ReverisNoctis on port 3000
if check_port 3000; then
    echo -e "${YELLOW}⚠ Port 3000 in use, killing existing process...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "  🖥️  Starting ReverisNoctis (this may take a moment)..."
cd ReverisNoctis
WEBKIT_DISABLE_COMPOSITING_MODE=1 npm run tauri:dev > /tmp/reveris-noctis.log 2>&1 &
REVERIS_PID=$!
cd ..

sleep 5

echo -e "${GREEN}✓ ReverisNoctis launched${NC}"
echo -e "${YELLOW}  Note: If you see a black screen, check /tmp/reveris-noctis.log${NC}"

# Step 4: Open browser tabs
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 4: Opening Browser Tabs${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Find browser
BROWSER=""
for browser in zen-browser zen firefox chromium google-chrome; do
    if command -v $browser &> /dev/null; then
        BROWSER=$browser
        break
    fi
done

if [ -z "$BROWSER" ]; then
    echo -e "${YELLOW}⚠ No browser found. Please open manually:${NC}"
    BROWSER="echo"
else
    echo -e "${GREEN}✓ Using browser: $BROWSER${NC}"

    sleep 2

    echo "  📊 Opening Dashboard..."
    $BROWSER --new-window "http://localhost:3001" &
    sleep 1

    echo "  📈 Opening Analytics..."
    $BROWSER --new-tab "http://localhost:3001/analytics" &
    sleep 1

    echo "  🚀 Opening Launch..."
    $BROWSER --new-tab "http://localhost:3001/launch" &
    sleep 1

    echo "  📖 Opening API Docs..."
    $BROWSER --new-tab "http://localhost:8000/docs" &
    sleep 1

    echo "  💾 Opening MinIO Console..."
    $BROWSER --new-tab "http://localhost:9001" &
    sleep 1
fi

# Step 5: Display Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🎉 Ecosystem Ready for Recording!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Active Components:${NC}"
echo ""
echo "  🌐 AetherFrame Dashboard:"
echo "     → http://localhost:3001"
echo "     → http://localhost:3001/analytics"
echo "     → http://localhost:3001/launch"
echo ""
echo "  🖥️  ReverisNoctis Desktop App:"
echo "     → Should be visible in separate window"
echo ""
echo "  📖 Backend API Documentation:"
echo "     → http://localhost:8000/docs"
echo ""
echo "  💾 MinIO Storage Console:"
echo "     → http://localhost:9001"
echo "     → Username: minioadmin / Password: minioadmin"
echo ""
echo -e "${YELLOW}Plugin Architecture:${NC}"
echo "  🔌 Umbriel → Anti-Analysis Detection"
echo "  🔌 Noema → Intent Classification"
echo "  🔌 Valkyrie → Binary Validation"
echo "  🔌 LainTrace → Dynamic Tracing"
echo "  🔌 Mnemosyne → State Reconstruction"
echo "  🔌 Static Analyzer → Comprehensive Analysis"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎬 Now start SimpleScreenRecorder:${NC}"
echo "   $ simplescreenrecorder"
echo ""
echo -e "${YELLOW}Recording Checklist:${NC}"
echo "  ☐ Show AetherFrame Dashboard (main UI)"
echo "  ☐ Navigate to Analytics (charts & metrics)"
echo "  ☐ Show Launch interface (pipeline submission)"
echo "  ☐ Display API Documentation (Swagger UI)"
echo "  ☐ Show MinIO Console (storage)"
echo "  ☐ Demonstrate ReverisNoctis desktop app"
echo ""
echo -e "${CYAN}Press Ctrl+C to stop all services and exit${NC}"
echo ""

# Keep running and handle cleanup
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down ecosystem...${NC}"

    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$REVERIS_PID" ]; then
        kill $REVERIS_PID 2>/dev/null || true
    fi

    # Kill any remaining processes on our ports
    lsof -ti:3000,3001 | xargs kill -9 2>/dev/null || true

    echo -e "${GREEN}✓ Ecosystem stopped${NC}"
    exit 0
}

trap cleanup INT TERM

# Keep script running
while true; do
    sleep 1
done
