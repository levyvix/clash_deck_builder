/**
 * Centralized configuration for the frontend application.
 * Handles both build-time and runtime environment variable loading.
 * Supports centralized environment configuration from the project root.
 */

// Extend Window interface to include our ENV object
declare global {
  interface Window {
    ENV?: {
      REACT_APP_API_BASE_URL?: string;
      REACT_APP_GOOGLE_CLIENT_ID?: string;
      REACT_APP_ENVIRONMENT?: string;
    };
  }
}

/**
 * Environment configuration interface
 */
interface EnvironmentConfig {
  API_BASE_URL: string;
  GOOGLE_CLIENT_ID: string;
  ENVIRONMENT: string;
  DEBUG: boolean;
}

/**
 * Get environment variable with fallback support.
 * Priority: window.ENV (runtime) > process.env (build-time) > default value
 * 
 * @param key - Environment variable key
 * @param defaultValue - Default value if not found
 * @returns Environment variable value or default
 */
function getEnvVar(key: string, defaultValue: string): string {
  // Check window.ENV first (runtime configuration for Docker)
  if (typeof window !== 'undefined' && window.ENV && window.ENV[key as keyof typeof window.ENV]) {
    const value = window.ENV[key as keyof typeof window.ENV];
    // Don't use the value if it's still a template string (not replaced) or empty
    if (value && !value.startsWith('${') && value.trim() !== '') {
      return value;
    }
  }
  
  // Fall back to process.env (build-time configuration)
  const processEnvValue = process.env[key];
  if (processEnvValue && processEnvValue.trim() !== '') {
    return processEnvValue;
  }
  
  // Use default value
  return defaultValue;
}

/**
 * Load configuration from centralized environment files
 */
function loadConfiguration(): EnvironmentConfig {
  const environment = getEnvVar('REACT_APP_ENVIRONMENT', 'development');
  
  // Base configuration
  const config: EnvironmentConfig = {
    API_BASE_URL: getEnvVar('REACT_APP_API_BASE_URL', 'http://localhost:8000'),
    GOOGLE_CLIENT_ID: getEnvVar('REACT_APP_GOOGLE_CLIENT_ID', ''),
    ENVIRONMENT: environment,
    DEBUG: environment === 'development' || getEnvVar('REACT_APP_DEBUG', 'false') === 'true'
  };
  
  // Environment-specific overrides
  switch (environment) {
    case 'docker':
      // Docker-specific configuration
      if (!config.API_BASE_URL.includes('localhost')) {
        // If not localhost, assume container networking
        config.API_BASE_URL = config.API_BASE_URL.replace('localhost', 'backend');
      }
      break;
      
    case 'production':
      // Production-specific configuration
      config.DEBUG = false;
      break;
      
    case 'development':
    default:
      // Development-specific configuration
      config.DEBUG = true;
      break;
  }
  
  return config;
}

// Load and export configuration
const config = loadConfiguration();

export const API_BASE_URL = config.API_BASE_URL;
export const GOOGLE_CLIENT_ID = config.GOOGLE_CLIENT_ID;
export const ENVIRONMENT = config.ENVIRONMENT;
export const DEBUG = config.DEBUG;

// Export full config object
export default config;

// Log configuration on module load for debugging
console.log('⚙️  Configuration loaded:');
console.log('   Environment:', ENVIRONMENT);
console.log('   API_BASE_URL:', API_BASE_URL);
console.log('   GOOGLE_CLIENT_ID:', GOOGLE_CLIENT_ID ? `${GOOGLE_CLIENT_ID.substring(0, 20)}...` : 'Not set');
console.log('   DEBUG:', DEBUG);
console.log('   Source:', window.ENV?.REACT_APP_API_BASE_URL ? 'runtime (window.ENV)' : 'build-time (process.env)');
