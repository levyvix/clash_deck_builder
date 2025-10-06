#!/usr/bin/env python3
"""
Essential Features Verification Script
Tests critical functionality without browser automation
"""

import requests
import json
import sys
from typing import Dict, Any

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def log_test(name: str):
    print(f"\n{BLUE}Testing:{RESET} {name}")

def log_pass(message: str):
    print(f"  {GREEN}✓{RESET} {message}")

def log_fail(message: str):
    print(f"  {RED}✗{RESET} {message}")

def test_backend_health() -> bool:
    """Test backend health endpoint"""
    log_test("Backend Health Check")
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                log_pass(f"Backend is healthy (version: {data.get('version')})")
                if data.get('database', {}).get('status') == 'healthy':
                    log_pass("Database connection is healthy")
                return True
            else:
                log_fail(f"Backend status: {data.get('status')}")
                return False
        else:
            log_fail(f"Backend returned status code {response.status_code}")
            return False
    except Exception as e:
        log_fail(f"Failed to connect to backend: {e}")
        return False

def test_cards_api() -> bool:
    """Test cards API endpoint"""
    log_test("Cards API Endpoint")
    try:
        response = requests.get('http://localhost:8000/api/cards/cards', timeout=10)
        if response.status_code == 200:
            cards = response.json()
            if isinstance(cards, list) and len(cards) > 0:
                log_pass(f"Successfully retrieved {len(cards)} cards")

                # Verify card structure
                first_card = cards[0]
                required_fields = ['id', 'name', 'elixir_cost', 'rarity', 'type', 'image_url']
                missing_fields = [field for field in required_fields if field not in first_card]

                if not missing_fields:
                    log_pass(f"Card structure is valid (sample: {first_card['name']})")
                    return True
                else:
                    log_fail(f"Card missing fields: {missing_fields}")
                    return False
            else:
                log_fail("Cards endpoint returned empty array")
                return False
        else:
            log_fail(f"Cards API returned status code {response.status_code}")
            return False
    except Exception as e:
        log_fail(f"Failed to fetch cards: {e}")
        return False

def test_frontend_serving() -> bool:
    """Test frontend is being served"""
    log_test("Frontend Service")
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            html = response.text
            if 'Clash Royale' in html or 'Deck Builder' in html or 'react' in html.lower():
                log_pass("Frontend is serving correctly")
                return True
            else:
                log_fail("Frontend HTML doesn't contain expected content")
                return False
        else:
            log_fail(f"Frontend returned status code {response.status_code}")
            return False
    except Exception as e:
        log_fail(f"Failed to connect to frontend: {e}")
        return False

def test_cors_headers() -> bool:
    """Test CORS headers are properly configured"""
    log_test("CORS Configuration")
    try:
        response = requests.options(
            'http://localhost:8000/api/cards/cards',
            headers={'Origin': 'http://localhost:3000'},
            timeout=5
        )
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            log_pass(f"CORS headers configured: {cors_header}")
            return True
        else:
            # Try a GET request to check CORS
            response = requests.get(
                'http://localhost:8000/api/cards/cards',
                headers={'Origin': 'http://localhost:3000'},
                timeout=5
            )
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header:
                log_pass(f"CORS headers configured: {cors_header}")
                return True
            log_fail("CORS headers not found")
            return False
    except Exception as e:
        log_fail(f"Failed to check CORS: {e}")
        return False

def test_evolution_cards() -> bool:
    """Test that evolution-capable cards are properly marked"""
    log_test("Evolution Cards Support")
    try:
        response = requests.get('http://localhost:8000/api/cards/cards', timeout=10)
        if response.status_code == 200:
            cards = response.json()
            evo_cards = [c for c in cards if c.get('image_url_evo')]
            if len(evo_cards) > 0:
                log_pass(f"Found {len(evo_cards)} evolution-capable cards")
                sample_names = [c['name'] for c in evo_cards[:3]]
                log_pass(f"Sample evolution cards: {', '.join(sample_names)}")
                return True
            else:
                log_fail("No evolution-capable cards found")
                return False
        return False
    except Exception as e:
        log_fail(f"Failed to check evolution cards: {e}")
        return False

def test_card_filtering() -> bool:
    """Test that cards have proper filtering attributes"""
    log_test("Card Filtering Attributes")
    try:
        response = requests.get('http://localhost:8000/api/cards/cards', timeout=10)
        if response.status_code == 200:
            cards = response.json()

            # Check rarities
            rarities = set(c.get('rarity') for c in cards)
            expected_rarities = {'Common', 'Rare', 'Epic', 'Legendary'}
            if expected_rarities.issubset(rarities):
                log_pass(f"All rarity types present: {rarities}")
            else:
                log_fail(f"Missing rarities. Found: {rarities}")

            # Check types
            types = set(c.get('type') for c in cards)
            if len(types) > 1:
                log_pass(f"Multiple card types present: {types}")
                return True
            else:
                log_fail(f"Only one card type found: {types}")
                return False
        return False
    except Exception as e:
        log_fail(f"Failed to check card attributes: {e}")
        return False

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Essential Features Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    results = []

    # Run all tests
    results.append(("Backend Health", test_backend_health()))
    results.append(("Cards API", test_cards_api()))
    results.append(("Frontend Service", test_frontend_serving()))
    results.append(("CORS Configuration", test_cors_headers()))
    results.append(("Evolution Cards", test_evolution_cards()))
    results.append(("Card Filtering", test_card_filtering()))

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {name:.<40} {status}")

    print(f"\n{BLUE}Total:{RESET} {passed}/{total} tests passed")

    if passed == total:
        print(f"\n{GREEN}✓ All essential features are working!{RESET}\n")
        return 0
    else:
        print(f"\n{RED}✗ Some tests failed. Please check the errors above.{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
