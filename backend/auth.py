import json
import hashlib
import os
from datetime import datetime, timedelta
import jwt

class AuthManager:
    def __init__(self):
        self.user_file = 'data/users.json'
        self.secret_key = 'medimotion-secret-key-2024'
        os.makedirs('data', exist_ok=True)
        
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def add_user(self, username, password, email):
        try:
            users = {}
            if os.path.exists(self.user_file):
                with open(self.user_file, 'r') as f:
                    users = json.load(f)
            
            if username in users:
                return False
                
            users[username] = {
                'password': self.hash_password(password),
                'email': email,
                'created_at': datetime.now().isoformat()
            }
            
            with open(self.user_file, 'w') as f:
                json.dump(users, f, indent=2)
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
    
    def authenticate_user(self, username, password):
        try:
            if not os.path.exists(self.user_file):
                return False
                
            with open(self.user_file, 'r') as f:
                users = json.load(f)
                
            if username not in users:
                return False
                
            return users[username]['password'] == self.hash_password(password)
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return False
    
    def generate_token(self, username):
        try:
            payload = {
                'username': username,
                'exp': datetime.utcnow() + timedelta(days=1)
            }
            return jwt.encode(payload, self.secret_key, algorithm='HS256')
        except Exception as e:
            print(f"Error generating token: {e}")
            return None
