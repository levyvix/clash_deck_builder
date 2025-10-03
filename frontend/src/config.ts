// Configuration module that supports both build-time and runtime environment variables
// This allows the app to work in both development (process.env) and production Docker (window.ENV)

// Extend Window interface to include ENV
declare global {
  interface Window {
    ENV?: {
      REACT_APP_API_BASE_URL?: string;
    };
  }
}

/**
 * Get environment variable with fallback support
 * Priority: window.ENV (runtime) > process.env (build-time) > default value
 */
const getEnvVar = (key: string, defaultValue: string): string => {
  // Check window.ENV first (runtime configuration for Docker)
  if (typeof window !== 'undefined' && window.ENV && window.ENV[key as keyof typeof window.ENV]) {
    const value = window.ENV[key as keyof typeof window.ENV];
    // Don't use the value if it's still a template string (not replaced)
    if (value && !value.startsWith('${')) {
      return value;
    }
  }
  
  // Fall back to process.env (build-time configuration)
  const processEnvValue = process.env[key];
  if (processEnvValue) {
    return processEnvValue;
  }
  
  // Use default value
  return defaultValue;
};

// Export configuration values
export const API_BASE_URL = getEnvVar('REACT_APP_API_BASE_URL', 'http://localhost:8000');

// Log configuration on module load for debugging
console.log('⚙️  Configuration loaded:');
console.log('   API_BASE_URL:', API_BASE_URL);
console.log('   Source:', window.ENV?.REACT_APP_API_BASE_URL ? 'runtime (window.ENV)' : 'build-time (process.env)');
