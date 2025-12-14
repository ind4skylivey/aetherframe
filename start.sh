#!/bin/bash

# AetherFrame - Easy Start Script
# This script starts the AetherFrame platform with a single command

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << "EOF"
    ___       __  __             ______
   /   | ____/ /_/ /_  ___  ____/ ____/________ _____ ___  ___
  / /| |/ __  / __/ __ \/ _ \/ ___/ /_  / ___/ __ `/ __ `__ \/ _ \
 / ___ / /_/ / /_/ / / /  __/ /  / __/ / /  / /_/ / / / / / /  __/
/_/  |_\____/\__/_/ /_/\___/_/  /_/   /_/   \____/_/ /_/ /_/\___/

        Advanced Malware Analysis Platform
                Version 0.1.0
EOF
echo -e "${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Error: Docker Compose is not available${NC}"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Error: Docker daemon is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

echo -e "${GREEN}✅ Docker is ready${NC}"
echo ""

# Parse command line arguments
MODE="${1:-start}"

case "$MODE" in
    start)
        echo -e "${BLUE}🚀 Starting AetherFrame...${NC}"
        echo ""

        # Create .env file if it doesn't exist
        if [ ! -f .env ]; then
            echo -e "${YELLOW}📝 Creating default .env file...${NC}"
            cat > .env << 'ENVEOF'
# AetherFrame Configuration
POSTGRES_PASSWORD=aetherpass
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
AETHERFRAME_PORT=3000
ENVEOF
            echo -e "${GREEN}✅ .env file created${NC}"
        fi

        # Build and start services
        echo -e "${BLUE}🏗️  Building AetherFrame container...${NC}"
        docker compose -f docker-compose.allinone.yml build

        echo -e "${BLUE}🚀 Starting services...${NC}"
        docker compose -f docker-compose.allinone.yml up -d

        echo ""
        echo -e "${GREEN}✅ AetherFrame is starting!${NC}"
        echo ""
        echo "Waiting for services to be ready..."
        sleep 10

        # Check health
        echo ""
        echo -e "${BLUE}🏥 Checking service health...${NC}"
        docker compose -f docker-compose.allinone.yml ps

        echo ""
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}🎉 AetherFrame is ready!${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "📊 ${BLUE}Web Interface:${NC} http://localhost:3000"
        echo -e "🔍 ${BLUE}API Docs:${NC}      http://localhost:3000/api/docs"
        echo -e "💾 ${BLUE}MinIO Console:${NC} http://localhost:9001"
        echo ""
        echo -e "${YELLOW}💡 Tips:${NC}"
        echo "  • View logs: ./start.sh logs"
        echo "  • Stop AetherFrame: ./start.sh stop"
        echo "  • Restart: ./start.sh restart"
        echo ""
        ;;

    stop)
        echo -e "${BLUE}🛑 Stopping AetherFrame...${NC}"
        docker compose -f docker-compose.allinone.yml down
        echo -e "${GREEN}✅ AetherFrame stopped${NC}"
        ;;

    restart)
        echo -e "${BLUE}🔄 Restarting AetherFrame...${NC}"
        docker compose -f docker-compose.allinone.yml restart
        echo -e "${GREEN}✅ AetherFrame restarted${NC}"
        ;;

    logs)
        echo -e "${BLUE}📋 Showing AetherFrame logs (Ctrl+C to exit)...${NC}"
        docker compose -f docker-compose.allinone.yml logs -f aetherframe
        ;;

    status)
        echo -e "${BLUE}📊 AetherFrame Status:${NC}"
        docker compose -f docker-compose.allinone.yml ps
        ;;

    clean)
        echo -e "${YELLOW}⚠️  This will remove all data and containers!${NC}"
        read -p "Are you sure? (yes/no): " -r
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            echo -e "${BLUE}🧹 Cleaning up...${NC}"
            docker compose -f docker-compose.allinone.yml down -v
            echo -e "${GREEN}✅ Cleanup complete${NC}"
        else
            echo "Cancelled"
        fi
        ;;

    update)
        echo -e "${BLUE}🔄 Updating AetherFrame...${NC}"
        git pull
        docker compose -f docker-compose.allinone.yml build --no-cache
        docker compose -f docker-compose.allinone.yml up -d
        echo -e "${GREEN}✅ Update complete${NC}"
        ;;

    *)
        echo "Usage: $0 {start|stop|restart|logs|status|clean|update}"
        echo ""
        echo "Commands:"
        echo "  start   - Start AetherFrame (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - Show application logs"
        echo "  status  - Show service status"
        echo "  clean   - Remove all containers and data"
        echo "  update  - Update to latest version"
        exit 1
        ;;
esac
