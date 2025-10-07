#!/usr/bin/env python3
"""
Script to generate OpenAPI schema for the Clash Royale Deck Builder API.
"""
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / 'backend' / 'src'))

from main import app  # Import your FastAPI app

def generate_openapi():
    """Generate OpenAPI schema and save it to a file."""
    # Generate the OpenAPI schema
    openapi_schema = app.openapi()
    
    # Save to file
    output_file = Path(__file__).parent.parent / 'docs' / 'api' / 'openapi.json'
    with open(output_file, 'w') as f:
        json.dump(openapi_schema, f, indent=2)
    
    print(f"OpenAPI schema generated at: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_openapi()
