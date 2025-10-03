"""
Pytest configuration and fixtures for testing
"""
import pytest
import asyncio
import os
from typing import Generator
from tests.fixtures.test_db_manager import test_db_manager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_database_setup():
    """Set up test database for the entire test session"""
    # Setup test database
    success = test_db_manager.setup_test_database()
    if not success:
        pytest.fail("Failed to setup test database")
    
    yield test_db_manager
    
    # Teardown test database
    test_db_manager.teardown_test_database()


@pytest.fixture(scope="function")
def clean_database(test_database_setup):
    """Clean database before each test function"""
    # Clean and seed before test
    test_db_manager.clean_database()
    test_db_manager.seed_test_data()
    
    yield test_database_setup
    
    # Clean after test (optional, but good for isolation)
    test_db_manager.clean_database()


@pytest.fixture(scope="function")
def db_connection(clean_database):
    """Provide database connection for tests"""
    return test_db_manager


@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment variables"""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_env = {
        "TESTING": "true",
        "DATABASE_URL": "mysql+pymysql://test_user:test_password@localhost:3307/clash_deck_builder_test",
        "DB_HOST": "localhost",
        "DB_PORT": "3307",
        "DB_NAME": "clash_deck_builder_test",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password",
        "CLASH_ROYALE_API_KEY": "test_api_key",
        "DEBUG": "true",
        "LOG_LEVEL": "debug"
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "test_user_new",
        "email": "test_new@example.com"
    }


@pytest.fixture
def sample_deck_data():
    """Sample deck data for testing"""
    return {
        "name": "Test Deck New",
        "user_id": 1,
        "cards": [26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 28000000, 28000001],
        "evolution_slots": [26000000],
        "average_elixir": 3.75
    }


@pytest.fixture
def sample_card_data():
    """Sample card data for testing"""
    return {
        "id": 99999999,
        "name": "Test Card",
        "elixir_cost": 4,
        "rarity": "Common",
        "type": "Troop",
        "arena": "Test Arena",
        "image_url": "https://example.com/test_card.png",
        "image_url_evo": None
    }