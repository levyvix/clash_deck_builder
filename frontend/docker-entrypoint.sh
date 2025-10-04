#!/bin/sh

# Replace environment variables in env-config.js at runtime
# This allows the same Docker image to work in different environments

echo "🔧 Configuring runtime environment..."

# Default values
REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL:-http://localhost:8000}
REACT_APP_GOOGLE_CLIENT_ID=${REACT_APP_GOOGLE_CLIENT_ID:-${GOOGLE_CLIENT_ID}}

echo "📍 API Base URL: $REACT_APP_API_BASE_URL"
echo "🔑 Google Client ID: ${REACT_APP_GOOGLE_CLIENT_ID:0:20}..."

# Replace template variables in env-config.js
sed -i "s|\${REACT_APP_API_BASE_URL}|$REACT_APP_API_BASE_URL|g" /usr/share/nginx/html/env-config.js
sed -i "s|\${REACT_APP_GOOGLE_CLIENT_ID}|$REACT_APP_GOOGLE_CLIENT_ID|g" /usr/share/nginx/html/env-config.js

echo "✅ Environment configuration complete"

# Start nginx
exec "$@"