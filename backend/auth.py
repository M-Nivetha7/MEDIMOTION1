import json
import hashlib
import os
import jwt
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self):
        self.user_file = 'data/users.json'
        self.secret_key = 'your-secret-key-change-in-production'
        os.makedirs('data', exist_ok=True)
        
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def add_user(self, username, password, email):
        if os.path.exists(self.user_file):
            with open(self.user_file, 'r') as f:
                users = json.load(f)
        else:
            users = {}
            
        if username in users:
            return False
            
        users[username] = {
            'password': self.hash_password(password),
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        
        with open(self.user_file, 'w') as f:
            json.dump(users, f)
        return True
    
    def authenticate_user(self, username, password):
        if not os.path.exists(self.user_file):
            return False
            
        with open(self.user_file, 'r') as f:
            users = json.load(f)
            
        if username not in users:
            return False
            
        return users[username]['password'] == self.hash_password(password)
    
    def generate_token(self, username):
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')