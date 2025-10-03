#!/bin/sh

# Replace environment variables in env-config.js at runtime
# This allows the same Docker image to work in different environments

echo "🔧 Configuring runtime environment..."

# Default values
REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL:-http://localhost:8000}

echo "📍 API Base URL: $REACT_APP_API_BASE_URL"

# Replace template variables in env-config.js
sed -i "s|\${REACT_APP_API_BASE_URL}|$REACT_APP_API_BASE_URL|g" /usr/share/nginx/html/env-config.js

echo "✅ Environment configuration complete"

# Start nginx
exec "$@"