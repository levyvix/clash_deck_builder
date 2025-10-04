// Runtime environment configuration
// This file is loaded before React app initialization to provide runtime environment variables
// Values are replaced at container startup time for Docker deployments

window.ENV = {
  REACT_APP_API_BASE_URL: '${REACT_APP_API_BASE_URL}',
  REACT_APP_GOOGLE_CLIENT_ID: '${REACT_APP_GOOGLE_CLIENT_ID}'
};
