#!/bin/bash

# Workaround for EGL/hardware acceleration issues on Linux
# This forces WebKit to use software rendering

export WEBKIT_DISABLE_COMPOSITING_MODE=1
export WEBKIT_DISABLE_DMABUF_RENDERER=1
export LIBGL_ALWAYS_SOFTWARE=1

# Run the Tauri app
cd "$(dirname "$0")"
npm run tauri:dev
