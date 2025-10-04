#!/usr/bin/env python3
"""
Environment Configuration Loader
Loads and validates environment variables from centralized configuration files.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class EnvironmentLoader:
    """Loads environment variables from centralized configuration files."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.env_dir = self.project_root / "env"
        
    def detect_environment(self) -> str:
        """Detect the current environment based on various indicators."""
        # Check explicit environment variable
        if env := os.getenv("ENVIRONMENT"):
            return env
            
        # Check for Docker environment
        if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER"):
            return "docker"
            
        # Check for production indicators
        if any(os.getenv(var) for var in ["PRODUCTION", "PROD", "RAILWAY_ENVIRONMENT"]):
            return "production"
            
        # Default to development
        return "development"
    
    def load_env_file(self, file_path: Path) -> Dict[str, str]:
        """Load environment variables from a file."""
        env_vars = {}
        
        if not file_path.exists():
            return env_vars
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                        
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                            
                        env_vars[key] = value
                    else:
                        print(f"Warning: Invalid line {line_num} in {file_path}: {line}")
                        
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
        return env_vars
    
    def load_environment(self, environment: Optional[str] = None) -> Dict[str, str]:
        """Load environment variables for the specified environment."""
        if environment is None:
            environment = self.detect_environment()
            
        print(f"Loading environment: {environment}")
        
        # Load in order of precedence (later files override earlier ones)
        env_vars = {}
        
        # 1. Load base template (lowest priority)
        template_file = self.project_root / ".env.template"
        if template_file.exists():
            env_vars.update(self.load_env_file(template_file))
            
        # 2. Load environment-specific file
        env_file = self.env_dir / f"{environment}.env"
        if env_file.exists():
            env_vars.update(self.load_env_file(env_file))
        else:
            print(f"Warning: Environment file not found: {env_file}")
            
        # 3. Load local .env file (highest priority)
        local_env = self.project_root / ".env"
        if local_env.exists():
            env_vars.update(self.load_env_file(local_env))
            
        # 4. Override with actual environment variables
        for key in env_vars.keys():
            if key in os.environ:
                env_vars[key] = os.environ[key]
                
        return env_vars
    
    def validate_environment(self, env_vars: Dict[str, str]) -> List[str]:
        """Validate required environment variables."""
        errors = []
        
        # Required variables for all environments
        required_vars = [
            "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD",
            "JWT_SECRET_KEY", "BACKEND_PORT"
        ]
        
        # Additional required variables for production
        if env_vars.get("ENVIRONMENT") == "production":
            required_vars.extend([
                "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET",
                "CLASH_ROYALE_API_KEY"
            ])
            
        for var in required_vars:
            if not env_vars.get(var):
                errors.append(f"Missing required variable: {var}")
                
        # Validate JWT secret length
        jwt_secret = env_vars.get("JWT_SECRET_KEY", "")
        if len(jwt_secret) < 32:
            errors.append("JWT_SECRET_KEY must be at least 32 characters long")
            
        # Validate database port
        try:
            db_port = int(env_vars.get("DB_PORT", "0"))
            if not (1 <= db_port <= 65535):
                errors.append("DB_PORT must be a valid port number (1-65535)")
        except ValueError:
            errors.append("DB_PORT must be a valid integer")
            
        return errors
    
    def export_to_file(self, env_vars: Dict[str, str], output_file: Path):
        """Export environment variables to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Generated environment configuration\n")
            f.write(f"# Generated at: {os.popen('date').read().strip()}\n\n")
            
            for key, value in sorted(env_vars.items()):
                # Quote values that contain spaces or special characters
                if ' ' in value or any(char in value for char in ['$', '`', '"', "'"]):
                    value = f'"{value}"'
                f.write(f"{key}={value}\n")
                
    def set_environment_variables(self, env_vars: Dict[str, str]):
        """Set environment variables in the current process."""
        for key, value in env_vars.items():
            os.environ[key] = value


def main():
    """Main entry point for the environment loader."""
    parser = argparse.ArgumentParser(description="Load centralized environment configuration")
    parser.add_argument(
        "--environment", "-e",
        choices=["development", "docker", "production"],
        help="Environment to load (auto-detected if not specified)"
    )
    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Validate environment configuration"
    )
    parser.add_argument(
        "--export", "-o",
        type=Path,
        help="Export configuration to file"
    )
    parser.add_argument(
        "--set-env",
        action="store_true",
        help="Set environment variables in current process"
    )
    
    args = parser.parse_args()
    
    # Initialize loader
    loader = EnvironmentLoader()
    
    # Load environment
    try:
        env_vars = loader.load_environment(args.environment)
        print(f"Loaded {len(env_vars)} environment variables")
        
        # Validate if requested
        if args.validate:
            errors = loader.validate_environment(env_vars)
            if errors:
                print("\nValidation errors:")
                for error in errors:
                    print(f"  ❌ {error}")
                sys.exit(1)
            else:
                print("✅ Environment validation passed")
                
        # Export if requested
        if args.export:
            loader.export_to_file(env_vars, args.export)
            print(f"Configuration exported to: {args.export}")
            
        # Set environment variables if requested
        if args.set_env:
            loader.set_environment_variables(env_vars)
            print("Environment variables set in current process")
            
        # Print summary
        print(f"\nEnvironment: {env_vars.get('ENVIRONMENT', 'unknown')}")
        print(f"Database: {env_vars.get('DB_HOST')}:{env_vars.get('DB_PORT')}/{env_vars.get('DB_NAME')}")
        print(f"Backend: {env_vars.get('BACKEND_HOST')}:{env_vars.get('BACKEND_PORT')}")
        print(f"API URL: {env_vars.get('REACT_APP_API_BASE_URL')}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()