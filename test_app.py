"""
Unit tests for Facebook Fanpage Manager
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from config import Config


class TestApp(unittest.TestCase):
    """Test cases for the Flask application"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = self.app.test_client()
    
    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Quản lý Fanpage Facebook'.encode('utf-8'), response.data)
    
    def test_login_redirect(self):
        """Test login redirects to Facebook OAuth"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 302)
        self.assertIn('facebook.com', response.location)
    
    def test_fanpages_requires_auth(self):
        """Test fanpages route requires authentication"""
        response = self.client.get('/fanpages')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.location)
    
    def test_logout(self):
        """Test logout clears session"""
        with self.client.session_transaction() as sess:
            sess['access_token'] = 'test_token'
            sess['user_name'] = 'Test User'
        
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.client.session_transaction() as sess:
            self.assertNotIn('access_token', sess)
    
    def test_config_loaded(self):
        """Test configuration is loaded correctly"""
        self.assertIsNotNone(Config.FACEBOOK_GRAPH_API)
        self.assertEqual(Config.FACEBOOK_GRAPH_API, 'https://graph.facebook.com/v18.0')
    
    @patch('app.requests.get')
    def test_fanpages_with_session(self, mock_get):
        """Test fanpages page with active session"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': [
                {'id': '123', 'name': 'Test Page', 'access_token': 'page_token'}
            ]
        }
        mock_get.return_value = mock_response
        
        with self.client.session_transaction() as sess:
            sess['access_token'] = 'test_token'
            sess['user_name'] = 'Test User'
        
        response = self.client.get('/fanpages')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Fanpage'.encode('utf-8'), response.data)
    
    def test_create_post_requires_auth(self):
        """Test create post requires authentication"""
        response = self.client.get('/fanpage/123/create_post')
        self.assertEqual(response.status_code, 302)
    
    def test_delete_post_requires_auth(self):
        """Test delete post requires authentication"""
        response = self.client.post('/fanpage/123/delete_post/456')
        self.assertEqual(response.status_code, 401)


class TestRoutes(unittest.TestCase):
    """Test route registration"""
    
    def test_routes_registered(self):
        """Test all required routes are registered"""
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        required_routes = [
            '/',
            '/login',
            '/callback',
            '/logout',
            '/fanpages',
            '/fanpage/<page_id>',
            '/fanpage/<page_id>/post/<post_id>',
            '/fanpage/<page_id>/create_post',
            '/fanpage/<page_id>/edit_post/<post_id>',
            '/fanpage/<page_id>/delete_post/<post_id>'
        ]
        
        for route in required_routes:
            self.assertIn(route, routes, f"Route {route} not found")


if __name__ == '__main__':
    unittest.main()
