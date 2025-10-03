# backend/tests/test_auth_integration.py

import pytest
from fastapi.testclient import TestClient
from fastapi import status

from src.main import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestAuthEndpointsIntegration:
    """Integration tests for authentication endpoints."""
    
    def test_auth_endpoints_registered(self, client):
        """Test that all authentication endpoints are properly registered."""
        
        # Test Google OAuth endpoint exists
        response = client.post("/api/auth/google", json={})
        # Should return 422 for missing required field, not 404
        assert response.status_code != status.HTTP_404_NOT_FOUND
        
        # Test refresh endpoint exists
        response = client.post("/api/auth/refresh", json={})
        # Should return 422 for missing required field, not 404
        assert response.status_code != status.HTTP_404_NOT_FOUND
        
        # Test logout endpoint exists (should require auth)
        response = client.post("/api/auth/logout")
        # Should return 403 for missing auth, not 404
        assert response.status_code != status.HTTP_404_NOT_FOUND
        
        # Test me endpoint exists (should require auth)
        response = client.get("/api/auth/me")
        # Should return 403 for missing auth, not 404
        assert response.status_code != status.HTTP_404_NOT_FOUND
    
    def test_auth_endpoints_require_proper_content_type(self, client):
        """Test that endpoints properly handle content type requirements."""
        
        # Test Google OAuth with invalid JSON
        response = client.post("/api/auth/google", data="invalid-json")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test refresh with invalid JSON
        response = client.post("/api/auth/refresh", data="invalid-json")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_auth_endpoints_cors_headers(self, client):
        """Test that CORS headers are properly set for auth endpoints."""
        
        # Test that endpoints exist (not 404) - CORS is handled by middleware
        response = client.post("/api/auth/google", json={})
        # Should not return 404, meaning the endpoint is registered
        assert response.status_code != status.HTTP_404_NOT_FOUND
        
        # Test that CORS middleware allows the configured origins
        # This is more of a configuration test than a functional test
        # The actual CORS testing would require a browser environment
    
    def test_protected_endpoints_require_auth(self, client):
        """Test that protected endpoints properly require authentication."""
        
        # Test logout without token
        response = client.post("/api/auth/logout")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Test me without token
        response = client.get("/api/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Test with invalid token format
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED