from typing import Dict, Optional
import hashlib
import json
from datetime import datetime

class AuthManager:
    """Simple authentication for prototype - replace with proper auth in production"""
    
    def __init__(self):
        # In production, this would use AWS Cognito or similar
        # For prototype, we use simple in-memory storage
        self.users = {
            # Demo users
            'parent_demo': {
                'id': 'parent_001',
                'password_hash': self._hash_password('parent123'),
                'role': 'parent',
                'name': 'Demo Parent',
                'email': 'parent@demo.com',
                'children': ['child_001']
            },
            'child_demo': {
                'id': 'child_001',
                'password_hash': self._hash_password('child123'),
                'role': 'child',
                'name': 'Demo Child',
                'age': 10,
                'parent_id': 'parent_001',
                'interests': ['science', 'animals', 'space'],
                'learning_level': 'grade_4'
            },
            'teacher_demo': {
                'id': 'teacher_001',
                'password_hash': self._hash_password('teacher123'),
                'role': 'teacher',
                'name': 'Demo Teacher',
                'email': 'teacher@school.com',
                'classes': ['class_001']
            }
        }
        
        self.sessions = {}
        self.parental_consents = {
            'child_001': {
                'parent_id': 'parent_001',
                'consented': True,
                'consent_date': '2025-01-01',
                'data_sharing': 'educational_only',
                'monitoring_enabled': True
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Simple password hashing - use bcrypt in production"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        user = self.users.get(username)
        
        if not user:
            return None
        
        if user['password_hash'] != self._hash_password(password):
            return None
        
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user['id']}"
        self.sessions[session_id] = {
            'user_id': user['id'],
            'username': username,
            'role': user['role'],
            'created_at': datetime.now().isoformat()
        }
        
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        user_data['session_id'] = session_id
        
        return user_data
    
    def get_user_by_session(self, session_id: str) -> Optional[Dict]:
        """Get user data from session ID"""
        session = self.sessions.get(session_id)
        
        if not session:
            return None
        
        username = session['username']
        user = self.users.get(username)
        
        if not user:
            return None
        
        return {k: v for k, v in user.items() if k != 'password_hash'}
    
    def verify_parental_consent(self, child_id: str) -> bool:
        """Check if child has parental consent"""
        consent = self.parental_consents.get(child_id)
        return consent and consent['consented']
    
    def verify_parent_child_relationship(self, parent_id: str, child_id: str) -> bool:
        """Verify parent-child relationship"""
        for username, user in self.users.items():
            if user['id'] == child_id and user.get('parent_id') == parent_id:
                return True
        return False
    
    def create_child_account(
        self, 
        username: str,
        password: str,
        name: str,
        age: int,
        parent_id: str
    ) -> Optional[str]:
        """Create a new child account with parental consent"""
        
        if username in self.users:
            return None
        
        child_id = f"child_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.users[username] = {
            'id': child_id,
            'password_hash': self._hash_password(password),
            'role': 'child',
            'name': name,
            'age': age,
            'parent_id': parent_id,
            'interests': [],
            'learning_level': f'grade_{age - 5}'  
        }
        
        
        self.parental_consents[child_id] = {
            'parent_id': parent_id,
            'consented': True,
            'consent_date': datetime.now().isoformat(),
            'data_sharing': 'educational_only',
            'monitoring_enabled': True
        }
        
        
        for username, user in self.users.items():
            if user['id'] == parent_id:
                if 'children' not in user:
                    user['children'] = []
                user['children'].append(child_id)
                break
        
        return child_id
    
    def logout(self, session_id: str) -> bool:
        """Logout user"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False