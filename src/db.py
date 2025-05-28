import os
import random
import sqlite3
from typing import Dict, List, Optional, Tuple


class Database:
    def __init__(self, db_name: str = "dating_bot.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    city TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    looking_gender TEXT NOT NULL,
                    looking_age_min INTEGER NOT NULL,
                    looking_age_max INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    photo TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Likes table (for tracking who liked whom)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS likes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user_id INTEGER NOT NULL,
                    to_user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (from_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (to_user_id) REFERENCES users (user_id),
                    UNIQUE(from_user_id, to_user_id)
                )
            ''')
            
            # Matches table (for mutual likes)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user1_id) REFERENCES users (user_id),
                    FOREIGN KEY (user2_id) REFERENCES users (user_id),
                    UNIQUE(user1_id, user2_id)
                )
            ''')
            
            # Viewed profiles table (to avoid showing same profiles repeatedly)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS viewed_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    viewer_id INTEGER NOT NULL,
                    viewed_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (viewer_id) REFERENCES users (user_id),
                    FOREIGN KEY (viewed_id) REFERENCES users (user_id),
                    UNIQUE(viewer_id, viewed_id)
                )
            ''')
            
            conn.commit()
    
    def save_user(self, user_data: Dict) -> bool:
        """Save or update user data"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, name, age, city, gender, looking_gender, 
                     looking_age_min, looking_age_max, description, photo, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    user_data['user_id'],
                    user_data['name'],
                    user_data['age'],
                    user_data['city'],
                    user_data['gender'],
                    user_data['looking_gender'],
                    user_data['looking_age_min'],
                    user_data['looking_age_max'],
                    user_data['description'],
                    user_data.get('photo')
                ))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data by user_id"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def user_exists(self, user_id: int) -> bool:
        """Check if user exists in database"""
        return self.get_user(user_id) is not None
    
    def activate_user(self, user_id: int) -> bool:
        """Activate user profile"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET is_active = 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user profile"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET is_active = 0 WHERE user_id = ?', (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def is_user_active(self, user_id: int) -> bool:
        """Check if user is active"""
        user = self.get_user(user_id)
        return user and user['is_active']
    
    def find_potential_matches(self, user_id: int, limit: int = 1) -> List[Dict]:
        """Find potential matches based on user preferences"""
        user = self.get_user(user_id)
        if not user:
            return []
        
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Build the query based on looking_gender preference
                if user['looking_gender'] == "Doesn't matter":
                    gender_condition = "1=1"
                    params = []
                else:
                    gender_condition = "gender = ?"
                    params = [user['looking_gender']]
                
                # Add other parameters
                params.extend([
                    user['city'],
                    user['looking_age_min'],
                    user['looking_age_max'],
                    user_id,  # exclude self
                    user_id,  # exclude already viewed
                    user_id   # exclude already liked
                ])
                
                query = f'''
                    SELECT * FROM users 
                    WHERE {gender_condition}
                    AND LOWER(TRIM(city)) = LOWER(TRIM(?))
                    AND age BETWEEN ? AND ?
                    AND user_id != ?
                    AND is_active = 1
                    AND user_id NOT IN (
                        SELECT viewed_id FROM viewed_profiles WHERE viewer_id = ?
                    )
                    AND user_id NOT IN (
                        SELECT to_user_id FROM likes WHERE from_user_id = ?
                    )
                    ORDER BY RANDOM()
                    LIMIT ?
                '''
                
                params.append(limit)
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def add_like(self, from_user_id: int, to_user_id: int) -> bool:
        """Add a like and check for mutual match"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Add the like
                cursor.execute('''
                    INSERT OR IGNORE INTO likes (from_user_id, to_user_id)
                    VALUES (?, ?)
                ''', (from_user_id, to_user_id))
                
                # Check if it's a mutual like
                cursor.execute('''
                    SELECT 1 FROM likes 
                    WHERE from_user_id = ? AND to_user_id = ?
                ''', (to_user_id, from_user_id))
                
                is_match = cursor.fetchone() is not None
                
                # If it's a match, add to matches table
                if is_match:
                    # Ensure consistent ordering (smaller ID first)
                    user1_id = min(from_user_id, to_user_id)
                    user2_id = max(from_user_id, to_user_id)
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO matches (user1_id, user2_id)
                        VALUES (?, ?)
                    ''', (user1_id, user2_id))
                
                conn.commit()
                return is_match
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def add_viewed_profile(self, viewer_id: int, viewed_id: int) -> bool:
        """Mark a profile as viewed"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO viewed_profiles (viewer_id, viewed_id)
                    VALUES (?, ?)
                ''', (viewer_id, viewed_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_matches(self, user_id: int) -> List[Dict]:
        """Get all matches for a user"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.* FROM users u
                    INNER JOIN matches m ON (
                        (m.user1_id = ? AND m.user2_id = u.user_id) OR
                        (m.user2_id = ? AND m.user1_id = u.user_id)
                    )
                    WHERE u.is_active = 1
                ''', (user_id, user_id))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def reset_viewed_profiles(self, user_id: int) -> bool:
        """Reset viewed profiles for a user (useful when no more matches available)"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM viewed_profiles WHERE viewer_id = ?', (user_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
