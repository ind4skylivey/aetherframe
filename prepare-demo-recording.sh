#!/bin/bash

# AetherFrame Complete Ecosystem Demo Preparation
# This script opens all components for screen recording

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║           AETHERFRAME ECOSYSTEM DEMO SETUP                   ║
║                                                              ║
║  This script will open all components for recording:        ║
║  • Web UI (React Dashboard)                                 ║
║  • API Documentation (Swagger)                              ║
║  • MinIO Console                                            ║
║  • ReverisNoctis Desktop App (if available)                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF

echo ""
echo -e "${CYAN}Preparing demo environment...${NC}"
sleep 2

# Find Zen Browser
ZEN_BROWSER=""
if command -v zen-browser &> /dev/null; then
    ZEN_BROWSER="zen-browser"
elif command -v zen &> /dev/null; then
    ZEN_BROWSER="zen"
elif [ -f "$HOME/.local/bin/zen-browser" ]; then
    ZEN_BROWSER="$HOME/.local/bin/zen-browser"
elif [ -f "/usr/bin/zen-browser" ]; then
    ZEN_BROWSER="/usr/bin/zen-browser"
fi

if [ -z "$ZEN_BROWSER" ]; then
    echo -e "${YELLOW}⚠️  Zen Browser not found, trying firefox...${NC}"
    ZEN_BROWSER="firefox"
fi

echo -e "${GREEN}✓ Will use: $ZEN_BROWSER${NC}"
sleep 1

# Step 1: Open Web UI tabs
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 1: Opening AetherFrame Web Interface${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "  🌐 Opening Main Dashboard..."
$ZEN_BROWSER --new-window "http://localhost:3000" &
sleep 2

echo "  📊 Opening Analytics..."
$ZEN_BROWSER --new-tab "http://localhost:3000/analytics" &
sleep 1

echo "  📈 Opening Launch Interface..."
$ZEN_BROWSER --new-tab "http://localhost:3000/launch" &
sleep 1

echo "  📖 Opening API Documentation..."
$ZEN_BROWSER --new-tab "http://localhost:3000/api/docs" &
sleep 1

echo "  💾 Opening MinIO Console..."
$ZEN_BROWSER --new-tab "http://localhost:9001" &
sleep 2

echo -e "${GREEN}✓ Web interface tabs opened${NC}"

# Step 2: Launch ReverisNoctis if available
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 2: Launching ReverisNoctis Desktop App${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check for ReverisNoctis executable
REVERIS_PATH=""

# Check common locations
if [ -f "ReverisNoctis/src-tauri/target/release/aetherframe" ]; then
    REVERIS_PATH="ReverisNoctis/src-tauri/target/release/aetherframe"
elif [ -f "ReverisNoctis/src-tauri/target/debug/aetherframe" ]; then
    REVERIS_PATH="ReverisNoctis/src-tauri/target/debug/aetherframe"
fi

if [ -n "$REVERIS_PATH" ]; then
    echo "  🖥️  Launching ReverisNoctis from $REVERIS_PATH..."
    ./$REVERIS_PATH &
    sleep 2
    echo -e "${GREEN}✓ ReverisNoctis launched${NC}"
else
    echo -e "${YELLOW}⚠️  ReverisNoctis executable not found${NC}"
    echo "     You can launch it manually from:"
    echo "     npm run tauri:dev (in ReverisNoctis directory)"
fi

# Step 3: Show plugin info
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 3: Available Analysis Plugins${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cat << 'EOF'

  🔌 Core Analysis Plugins:

  1. 🛡️  Umbriel
     → Anti-Analysis Detection (50+ techniques)
     → Anti-debugging, Anti-VM, Anti-Frida

  2. 🧠 Noema
     → Intent Classification
     → Behavioral Pattern Analysis

  3. ⚔️  Valkyrie
     → Binary Validation
     → Integrity Checks

  4. 🔍 LainTrace
     → Dynamic Tracing with Frida
     → Runtime Instrumentation

  5. 💾 Mnemosyne
     → State Reconstruction
     → Memory Dump Analysis

  6. 📊 Static Analyzer
     → Comprehensive Static Analysis
     → Decompilation Support

EOF

sleep 3

# Instructions for recording
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🎬 Ready to Record!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "All components are now open. Start your screen recording tool:"
echo ""
echo -e "${GREEN}Recommended Recording Tools:${NC}"
echo "  • SimpleScreenRecorder (GUI)"
echo "    $ simplescreenrecorder"
echo ""
echo "  • Peek (Simple GIF recorder)"
echo "    $ peek"
echo ""
echo "  • OBS Studio (Professional)"
echo "    $ obs"
echo ""
echo "  • FFmpeg (Command line)"
echo "    $ ffmpeg -f x11grab -s 1920x1080 -i :0.0 demo.mp4"
echo ""
echo -e "${YELLOW}Recording Checklist:${NC}"
echo "  ☐ Show ReverisNoctis desktop app"
echo "  ☐ Navigate through Web UI tabs (Dashboard, Analytics, Launch)"
echo "  ☐ Demo API Docs (Swagger interface)"
echo "  ☐ Show MinIO Console"
echo "  ☐ Demonstrate a sample analysis workflow"
echo ""
echo -e "${CYAN}Press Ctrl+C when you're done to close all components${NC}"
echo ""

# Keep script running
trap "echo -e '\n${GREEN}✓ Demo session ended${NC}'; exit 0" INT TERM

while true; do
    sleep 1
done
