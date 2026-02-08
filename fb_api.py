"""
Facebook Graph API helper
Wrapper for Facebook Graph API operations
"""

import requests
import os
import logging

logger = logging.getLogger(__name__)

class FacebookAPI:
    """Facebook Graph API helper class"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = 'https://graph.facebook.com/v18.0'
    
    def get_page_info(self, page_id):
        """Get page information including followers and likes"""
        url = f'{self.base_url}/{page_id}'
        params = {
            'fields': 'name,fan_count,followers_count',
            'access_token': self.access_token
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting page info: {e}")
            return None
    
    def create_post(self, page_id, message, link=None):
        """Create a new post on the fanpage"""
        url = f'{self.base_url}/{page_id}/feed'
        data = {
            'message': message,
            'access_token': self.access_token
        }
        if link:
            data['link'] = link
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating post: {e}")
            return None
    
    def get_posts(self, page_id, limit=25):
        """Get recent posts from the fanpage"""
        url = f'{self.base_url}/{page_id}/posts'
        params = {
            'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares',
            'limit': limit,
            'access_token': self.access_token
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting posts: {e}")
            return None
    
    def get_conversations(self, page_id, limit=25):
        """Get conversations (messages) for the fanpage"""
        url = f'{self.base_url}/{page_id}/conversations'
        params = {
            'fields': 'id,updated_time,unread_count,participants,messages{from,message,created_time}',
            'limit': limit,
            'access_token': self.access_token
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting conversations: {e}")
            return None
    
    def send_message(self, recipient_id, message):
        """Send a message to a user"""
        url = f'{self.base_url}/me/messages'
        data = {
            'recipient': {'id': recipient_id},
            'message': {'text': message},
            'access_token': self.access_token
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def delete_post(self, post_id):
        """Delete a post"""
        url = f'{self.base_url}/{post_id}'
        params = {
            'access_token': self.access_token
        }
        try:
            response = requests.delete(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting post: {e}")
            return None
