#!/bin/bash

# AetherFrame Ecosystem Demo Script
# This script demonstrates the full ecosystem startup and verification

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print with delay (for better recording)
print_step() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    sleep 2
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    sleep 1
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
    sleep 0.5
}

clear

# Banner
cat << 'EOF'
 █████╗ ███████╗████████╗██╗  ██╗███████╗██████╗ ███████╗██████╗  █████╗ ███╗   ███╗███████╗
██╔══██╗██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
███████║█████╗     ██║   ███████║█████╗  ██████╔╝█████╗  ██████╔╝███████║██╔████╔██║█████╗
██╔══██║██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
██║  ██║███████╗   ██║   ██║  ██║███████╗██║  ██║██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

                    Advanced Malware Analysis Platform
                           Ecosystem Demo v1.0.0
EOF

sleep 3

# Step 1: Check if services are already running
print_step "🔍 Step 1: Checking Current Service Status"

print_info "Checking Web UI (http://localhost:3000)..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    print_success "Web UI is running"
else
    echo "  ⚠️  Web UI not detected"
fi

print_info "Checking API Docs (http://localhost:3000/api/docs)..."
if curl -s http://localhost:3000/api/docs > /dev/null 2>&1; then
    print_success "API Docs accessible"
else
    echo "  ⚠️  API Docs not accessible"
fi

print_info "Checking MinIO Console (http://localhost:9001)..."
if curl -s http://localhost:9001 > /dev/null 2>&1; then
    print_success "MinIO Console is running"
else
    echo "  ⚠️  MinIO Console not detected"
fi

# Step 2: Show Docker containers
print_step "🐳 Step 2: Docker Containers Status"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "aetherframe|postgres|redis|minio" || echo "No AetherFrame containers running"
sleep 2

# Step 3: API Health Check
print_step "🏥 Step 3: System Health Check"

print_info "Querying /status endpoint..."
if curl -s http://localhost:8000/status 2>&1 | jq -C '.' 2>/dev/null || curl -s http://localhost:8000/status; then
    print_success "Backend API is healthy"
else
    echo "  ⚠️  Backend API not responding"
fi

# Step 4: Show available endpoints
print_step "🌐 Step 4: Access Points"

echo ""
echo -e "${GREEN}Web Interface:${NC}"
echo "  🌐 Main UI:      http://localhost:3000"
echo "  📊 Dashboard:    http://localhost:3000/dashboard"
echo "  📈 Analytics:    http://localhost:3000/analytics"
echo ""
echo -e "${GREEN}API Documentation:${NC}"
echo "  📖 Swagger UI:   http://localhost:3000/api/docs"
echo "  📝 ReDoc:        http://localhost:3000/api/redoc"
echo ""
echo -e "${GREEN}Storage Console:${NC}"
echo "  💾 MinIO Console: http://localhost:9001"
echo "     Username: minioadmin"
echo "     Password: minioadmin"
echo ""
sleep 3

# Step 5: Sample API Call
print_step "🔬 Step 5: Sample API Interaction"

print_info "Fetching available plugins..."
curl -s http://localhost:8000/plugins 2>&1 | jq -C '.' 2>/dev/null || echo "  ⚠️  Could not fetch plugins"
sleep 2

print_info "Fetching recent jobs..."
curl -s http://localhost:8000/jobs?limit=3 2>&1 | jq -C '.' 2>/dev/null || echo "  ⚠️  Could not fetch jobs"
sleep 2

# Step 6: Architecture Overview
print_step "🏗️ Step 6: Architecture Overview"

cat << 'EOF'
┌─────────────────────────────────────────────────────────────┐
│                    AETHERFRAME ECOSYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Frontend Layer                                              │
│  ├─ React UI (Vite)          → Port 3000                    │
│  ├─ Analytics Dashboard                                      │
│  └─ Real-time Monitoring                                     │
│                                                              │
│  Backend Layer                                               │
│  ├─ FastAPI Server           → Port 8000                    │
│  ├─ Celery Workers                                          │
│  └─ Redis Queue                                             │
│                                                              │
│  Storage Layer                                               │
│  ├─ PostgreSQL               → Port 5432                    │
│  ├─ MinIO (S3)               → Port 9000/9001              │
│  └─ Redis Cache              → Port 6379                    │
│                                                              │
│  Analysis Plugins                                            │
│  ├─ Umbriel (Anti-Analysis Detection)                       │
│  ├─ Noema (Intent Classification)                           │
│  ├─ Valkyrie (Binary Validation)                            │
│  ├─ LainTrace (Dynamic Tracing)                             │
│  ├─ Mnemosyne (State Reconstruction)                        │
│  └─ Static Analyzer                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
EOF

sleep 3

# Final message
print_step "✨ Demo Complete!"

echo ""
echo -e "${GREEN}🎉 AetherFrame Ecosystem is ready!${NC}"
echo ""
echo "Next steps:"
echo "  1. Open your browser to http://localhost:3000"
echo "  2. Explore the interactive dashboard"
echo "  3. Try the API at http://localhost:3000/api/docs"
echo "  4. Check MinIO storage at http://localhost:9001"
echo ""
echo -e "${CYAN}Happy analyzing! 🔬${NC}"
echo ""
