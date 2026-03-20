"""
Database Models
===============
Complete database implementation for Fam Tree Bot
"""

import aiosqlite
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import asyncio
import os

class Database:
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """Connect to database and create tables"""
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        await self._create_tables()
    
    async def close(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
    
    async def _create_tables(self):
        """Create all database tables"""
        
        # Users table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                profile_pic TEXT,
                money INTEGER DEFAULT 1000,
                reputation INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_daily TIMESTAMP,
                daily_streak INTEGER DEFAULT 0,
                gemstone TEXT,
                job TEXT DEFAULT 'unemployed',
                weapon TEXT DEFAULT 'fist',
                location TEXT,
                is_dead INTEGER DEFAULT 0,
                death_time TIMESTAMP,
                rob_count INTEGER DEFAULT 0,
                kill_count INTEGER DEFAULT 0,
                last_rob_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_kill_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                skills_fertilize INTEGER DEFAULT 0,
                total_crops_grown INTEGER DEFAULT 0,
                refer_code TEXT UNIQUE,
                referred_by INTEGER,
                blocked_users TEXT DEFAULT '[]',
                rating INTEGER DEFAULT 0,
                price INTEGER DEFAULT 100
            )
        """)
        
        # Family relations table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS family_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                related_user_id INTEGER,
                relation_type TEXT,
                chat_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (related_user_id) REFERENCES users(user_id)
            )
        """)
        
        # Friends table (global)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                friend_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (friend_id) REFERENCES users(user_id),
                UNIQUE(user_id, friend_id)
            )
        """)
        
        # Pending proposals table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS pending_proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER,
                to_user_id INTEGER,
                proposal_type TEXT,
                chat_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_user_id) REFERENCES users(user_id),
                FOREIGN KEY (to_user_id) REFERENCES users(user_id)
            )
        """)
        
        # Gardens table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS gardens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chat_id INTEGER,
                slots INTEGER DEFAULT 9,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, chat_id)
            )
        """)
        
        # Garden crops table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS garden_crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                garden_id INTEGER,
                crop_type TEXT,
                planted_at TIMESTAMP,
                ready_at TIMESTAMP,
                fertilized_count INTEGER DEFAULT 0,
                FOREIGN KEY (garden_id) REFERENCES gardens(id)
            )
        """)
        
        # Barn table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS barn (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_type TEXT,
                item_name TEXT,
                quantity INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, item_type, item_name)
            )
        """)
        
        # Seeds table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS seeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                crop_type TEXT,
                quantity INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, crop_type)
            )
        """)
        
        # Stands table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS stands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                crop_type TEXT,
                quantity INTEGER,
                price INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Orders table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                crop_type TEXT,
                quantity INTEGER,
                reward INTEGER,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Cooking sessions table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cooking_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_name TEXT,
                quantity INTEGER,
                participants TEXT,
                ingredients TEXT,
                started_at TIMESTAMP,
                completes_at TIMESTAMP,
                completed INTEGER DEFAULT 0
            )
        """)
        
        # Factory workers table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS factory_workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER UNIQUE,
                owner_id INTEGER,
                price INTEGER DEFAULT 100,
                rating INTEGER DEFAULT 0,
                is_working INTEGER DEFAULT 0,
                work_started_at TIMESTAMP,
                shield_until TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES users(user_id),
                FOREIGN KEY (owner_id) REFERENCES users(user_id)
            )
        """)
        
        # Insurance table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS insurance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insurer_id INTEGER,
                insured_id INTEGER,
                amount INTEGER,
                premium INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (insurer_id) REFERENCES users(user_id),
                FOREIGN KEY (insured_id) REFERENCES users(user_id),
                UNIQUE(insurer_id, insured_id)
            )
        """)
        
        # Custom GIFs table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS custom_gifs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                gif_type TEXT,
                file_id TEXT,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (added_by) REFERENCES users(user_id)
            )
        """)
        
        # Chat settings table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_settings (
                chat_id INTEGER PRIMARY KEY,
                robkill_enabled INTEGER DEFAULT 0,
                garden_enabled INTEGER DEFAULT 1,
                games_enabled INTEGER DEFAULT 1,
                nsfw_enabled INTEGER DEFAULT 0,
                incest_enabled INTEGER DEFAULT 0,
                tree_mode TEXT DEFAULT 'local',
                language TEXT DEFAULT 'en',
                auto_prune INTEGER DEFAULT 1,
                disabled_commands TEXT DEFAULT '[]'
            )
        """)
        
        # Game sessions table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                game_type TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        
        # Interactions table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER,
                to_user_id INTEGER,
                interaction_type TEXT,
                count INTEGER DEFAULT 1,
                last_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_user_id) REFERENCES users(user_id),
                FOREIGN KEY (to_user_id) REFERENCES users(user_id),
                UNIQUE(from_user_id, to_user_id, interaction_type)
            )
        """)
        
        # Fertilize cooldowns table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fertilize_cooldowns (
                user_id INTEGER PRIMARY KEY,
                last_fertilize TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Referrals table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                refer_code TEXT,
                user_id INTEGER,
                clicked_by INTEGER,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (clicked_by) REFERENCES users(user_id)
            )
        """)
        
        # Money rain table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS money_rain (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                collected_by TEXT DEFAULT '[]'
            )
        """)
        
        # Ripple games table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ripple_games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bet_amount INTEGER,
                current_amount INTEGER,
                multiplier REAL DEFAULT 1.0,
                step INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        await self.conn.commit()
    
    # User methods
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        async with self.conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def create_user(self, user_id: int, username: str = None, 
                         first_name: str = None, last_name: str = None) -> Dict:
        """Create a new user"""
        import random, string
        refer_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        await self.conn.execute(
            """INSERT OR IGNORE INTO users 
               (user_id, username, first_name, last_name, refer_code, last_rob_reset, last_kill_reset)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, username, first_name, last_name, refer_code, 
             datetime.now(), datetime.now())
        )
        await self.conn.commit()
        return await self.get_user(user_id)
    
    async def get_or_create_user(self, user_id: int, username: str = None,
                                  first_name: str = None, last_name: str = None) -> Dict:
        """Get or create user"""
        user = await self.get_user(user_id)
        if not user:
            user = await self.create_user(user_id, username, first_name, last_name)
        return user
    
    async def update_user(self, user_id: int, **kwargs):
        """Update user fields"""
        if not kwargs:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        
        await self.conn.execute(
            f"UPDATE users SET {set_clause} WHERE user_id = ?",
            values
        )
        await self.conn.commit()
    
    async def add_money(self, user_id: int, amount: int):
        """Add money to user"""
        await self.conn.execute(
            "UPDATE users SET money = money + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await self.conn.commit()
    
    async def remove_money(self, user_id: int, amount: int) -> bool:
        """Remove money from user"""
        user = await self.get_user(user_id)
        if user and user['money'] >= amount:
            await self.conn.execute(
                "UPDATE users SET money = money - ? WHERE user_id = ?",
                (amount, user_id)
            )
            await self.conn.commit()
            return True
        return False
    
    async def transfer_money(self, from_user_id: int, to_user_id: int, amount: int) -> bool:
        """Transfer money between users"""
        if await self.remove_money(from_user_id, amount):
            await self.add_money(to_user_id, amount)
            return True
        return False
    
    # Family methods
    async def get_family_tree(self, user_id: int, chat_id: int) -> Dict[str, List[Dict]]:
        """Get family tree for a user"""
        result = {"parents": [], "children": [], "partners": []}
        
        async with self.conn.execute(
            """SELECT fr.*, u.user_id, u.first_name, u.username, u.profile_pic 
               FROM family_relations fr
               JOIN users u ON fr.related_user_id = u.user_id
               WHERE fr.user_id = ? AND fr.chat_id = ?""",
            (user_id, chat_id)
        ) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                data = dict(row)
                if data['relation_type'] == 'parent':
                    result["parents"].append(data)
                elif data['relation_type'] == 'child':
                    result["children"].append(data)
                elif data['relation_type'] == 'partner':
                    result["partners"].append(data)
        
        return result
    
    async def add_family_relation(self, user_id: int, related_user_id: int, 
                                   relation_type: str, chat_id: int):
        """Add family relation"""
        await self.conn.execute(
            """INSERT INTO family_relations (user_id, related_user_id, relation_type, chat_id)
               VALUES (?, ?, ?, ?)""",
            (user_id, related_user_id, relation_type, chat_id)
        )
        await self.conn.commit()
    
    async def remove_family_relation(self, user_id: int, related_user_id: int, 
                                      relation_type: str, chat_id: int):
        """Remove family relation"""
        await self.conn.execute(
            """DELETE FROM family_relations 
               WHERE user_id = ? AND related_user_id = ? AND relation_type = ? AND chat_id = ?""",
            (user_id, related_user_id, relation_type, chat_id)
        )
        await self.conn.commit()
    
    async def count_relations(self, user_id: int, chat_id: int, relation_type: str) -> int:
        """Count relations of a specific type"""
        async with self.conn.execute(
            """SELECT COUNT(*) FROM family_relations 
               WHERE user_id = ? AND chat_id = ? AND relation_type = ?""",
            (user_id, chat_id, relation_type)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
    
    # Friend methods
    async def get_friends(self, user_id: int) -> List[Dict]:
        """Get user's friends"""
        async with self.conn.execute(
            """SELECT u.* FROM users u
               JOIN friends f ON u.user_id = f.friend_id
               WHERE f.user_id = ?""",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def are_friends(self, user_id: int, friend_id: int) -> bool:
        """Check if two users are friends"""
        async with self.conn.execute(
            "SELECT 1 FROM friends WHERE user_id = ? AND friend_id = ?",
            (user_id, friend_id)
        ) as cursor:
            return await cursor.fetchone() is not None
    
    async def add_friend(self, user_id: int, friend_id: int):
        """Add friend (bidirectional)"""
        await self.conn.execute(
            "INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)",
            (user_id, friend_id)
        )
        await self.conn.execute(
            "INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)",
            (friend_id, user_id)
        )
        await self.conn.commit()
    
    async def remove_friend(self, user_id: int, friend_id: int):
        """Remove friend"""
        await self.conn.execute(
            "DELETE FROM friends WHERE user_id = ? AND friend_id = ?",
            (user_id, friend_id)
        )
        await self.conn.execute(
            "DELETE FROM friends WHERE user_id = ? AND friend_id = ?",
            (friend_id, user_id)
        )
        await self.conn.commit()
    
    async def count_friends(self, user_id: int) -> int:
        """Count user's friends"""
        async with self.conn.execute(
            "SELECT COUNT(*) FROM friends WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
    
    # Pending proposals
    async def create_proposal(self, from_user_id: int, to_user_id: int, 
                              proposal_type: str, chat_id: int):
        """Create a proposal"""
        await self.conn.execute(
            """INSERT INTO pending_proposals (from_user_id, to_user_id, proposal_type, chat_id)
               VALUES (?, ?, ?, ?)""",
            (from_user_id, to_user_id, proposal_type, chat_id)
        )
        await self.conn.commit()
    
    async def get_pending_proposals(self, user_id: int) -> List[Dict]:
        """Get pending proposals for user"""
        async with self.conn.execute(
            """SELECT pp.*, u.first_name as from_name, u.username as from_username
               FROM pending_proposals pp
               JOIN users u ON pp.from_user_id = u.user_id
               WHERE pp.to_user_id = ?""",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_proposal(self, proposal_id: int) -> Optional[Dict]:
        """Get specific proposal"""
        async with self.conn.execute(
            """SELECT pp.*, u.first_name as from_name, u2.first_name as to_name
               FROM pending_proposals pp
               JOIN users u ON pp.from_user_id = u.user_id
               JOIN users u2 ON pp.to_user_id = u2.user_id
               WHERE pp.id = ?""",
            (proposal_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def delete_proposal(self, proposal_id: int):
        """Delete a proposal"""
        await self.conn.execute(
            "DELETE FROM pending_proposals WHERE id = ?",
            (proposal_id,)
        )
        await self.conn.commit()
    
    # Garden methods
    async def get_or_create_garden(self, user_id: int, chat_id: int) -> Dict:
        """Get or create garden"""
        async with self.conn.execute(
            "SELECT * FROM gardens WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                garden = dict(row)
            else:
                await self.conn.execute(
                    "INSERT INTO gardens (user_id, chat_id) VALUES (?, ?)",
                    (user_id, chat_id)
                )
                await self.conn.commit()
                garden = await self.get_or_create_garden(user_id, chat_id)
        
        # Get crops
        async with self.conn.execute(
            "SELECT * FROM garden_crops WHERE garden_id = ?",
            (garden['id'],)
        ) as cursor:
            rows = await cursor.fetchall()
            garden['crops'] = [dict(row) for row in rows]
        
        return garden
    
    async def plant_crop(self, garden_id: int, crop_type: str, ready_at: datetime):
        """Plant a crop"""
        await self.conn.execute(
            """INSERT INTO garden_crops (garden_id, crop_type, planted_at, ready_at)
               VALUES (?, ?, ?, ?)""",
            (garden_id, crop_type, datetime.now(), ready_at)
        )
        await self.conn.commit()
    
    async def harvest_crop(self, crop_id: int) -> Optional[Dict]:
        """Harvest a crop"""
        async with self.conn.execute(
            "SELECT * FROM garden_crops WHERE id = ?",
            (crop_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                crop = dict(row)
                await self.conn.execute(
                    "DELETE FROM garden_crops WHERE id = ?",
                    (crop_id,)
                )
                await self.conn.commit()
                return crop
        return None
    
    # Barn methods
    async def get_barn(self, user_id: int) -> Dict[str, int]:
        """Get user's barn"""
        async with self.conn.execute(
            "SELECT item_name, quantity FROM barn WHERE user_id = ? AND item_type = 'crop'",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}
    
    async def add_to_barn(self, user_id: int, item_name: str, quantity: int, item_type: str = 'crop'):
        """Add items to barn"""
        await self.conn.execute(
            """INSERT INTO barn (user_id, item_type, item_name, quantity) VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id, item_type, item_name) 
               DO UPDATE SET quantity = quantity + ?""",
            (user_id, item_type, item_name, quantity, quantity)
        )
        await self.conn.commit()
    
    async def remove_from_barn(self, user_id: int, item_name: str, quantity: int, item_type: str = 'crop') -> bool:
        """Remove items from barn"""
        async with self.conn.execute(
            "SELECT quantity FROM barn WHERE user_id = ? AND item_type = ? AND item_name = ?",
            (user_id, item_type, item_name)
        ) as cursor:
            row = await cursor.fetchone()
            if not row or row[0] < quantity:
                return False
        
        await self.conn.execute(
            """UPDATE barn SET quantity = quantity - ? 
               WHERE user_id = ? AND item_type = ? AND item_name = ?""",
            (quantity, user_id, item_type, item_name)
        )
        await self.conn.execute(
            "DELETE FROM barn WHERE user_id = ? AND item_type = ? AND item_name = ? AND quantity <= 0",
            (user_id, item_type, item_name)
        )
        await self.conn.commit()
        return True
    
    # Seeds methods
    async def get_seeds(self, user_id: int) -> Dict[str, int]:
        """Get user's seeds"""
        async with self.conn.execute(
            "SELECT crop_type, quantity FROM seeds WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}
    
    async def add_seeds(self, user_id: int, crop_type: str, quantity: int):
        """Add seeds"""
        await self.conn.execute(
            """INSERT INTO seeds (user_id, crop_type, quantity) VALUES (?, ?, ?)
               ON CONFLICT(user_id, crop_type) 
               DO UPDATE SET quantity = quantity + ?""",
            (user_id, crop_type, quantity, quantity)
        )
        await self.conn.commit()
    
    async def remove_seeds(self, user_id: int, crop_type: str, quantity: int) -> bool:
        """Remove seeds"""
        async with self.conn.execute(
            "SELECT quantity FROM seeds WHERE user_id = ? AND crop_type = ?",
            (user_id, crop_type)
        ) as cursor:
            row = await cursor.fetchone()
            if not row or row[0] < quantity:
                return False
        
        await self.conn.execute(
            """UPDATE seeds SET quantity = quantity - ? 
               WHERE user_id = ? AND crop_type = ?""",
            (quantity, user_id, crop_type)
        )
        await self.conn.execute(
            "DELETE FROM seeds WHERE user_id = ? AND crop_type = ? AND quantity <= 0",
            (user_id, crop_type)
        )
        await self.conn.commit()
        return True
    
    # Leaderboard methods
    async def get_money_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get global money leaderboard"""
        async with self.conn.execute(
            "SELECT * FROM users ORDER BY money DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # Chat settings
    async def get_chat_settings(self, chat_id: int) -> Dict:
        """Get chat settings"""
        async with self.conn.execute(
            "SELECT * FROM chat_settings WHERE chat_id = ?",
            (chat_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            else:
                await self.conn.execute(
                    "INSERT INTO chat_settings (chat_id) VALUES (?)",
                    (chat_id,)
                )
                await self.conn.commit()
                return await self.get_chat_settings(chat_id)
    
    async def update_chat_settings(self, chat_id: int, **kwargs):
        """Update chat settings"""
        if not kwargs:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [chat_id]
        
        await self.conn.execute(
            f"UPDATE chat_settings SET {set_clause} WHERE chat_id = ?",
            values
        )
        await self.conn.commit()
    
    # Game sessions
    async def create_game_session(self, chat_id: int, user_id: int, game_type: str, data: Dict, expires_minutes: int = 5):
        """Create a game session"""
        expires_at = datetime.now() + timedelta(minutes=expires_minutes)
        await self.conn.execute(
            """INSERT INTO game_sessions (chat_id, user_id, game_type, data, expires_at)
               VALUES (?, ?, ?, ?, ?)""",
            (chat_id, user_id, game_type, json.dumps(data), expires_at)
        )
        await self.conn.commit()
    
    async def get_game_session(self, chat_id: int, user_id: int, game_type: str) -> Optional[Dict]:
        """Get active game session"""
        async with self.conn.execute(
            """SELECT * FROM game_sessions 
               WHERE chat_id = ? AND user_id = ? AND game_type = ? AND expires_at > ?
               ORDER BY created_at DESC LIMIT 1""",
            (chat_id, user_id, game_type, datetime.now())
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                data = dict(row)
                data['data'] = json.loads(data['data'])
                return data
            return None
    
    async def delete_game_session(self, session_id: int):
        """Delete game session"""
        await self.conn.execute(
            "DELETE FROM game_sessions WHERE id = ?",
            (session_id,)
        )
        await self.conn.commit()
    
    # Ripple game methods
    async def get_active_ripple(self, user_id: int) -> Optional[Dict]:
        """Get active ripple game"""
        async with self.conn.execute(
            "SELECT * FROM ripple_games WHERE user_id = ? AND active = 1",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def create_ripple(self, user_id: int, bet_amount: int):
        """Create new ripple game"""
        await self.conn.execute(
            """INSERT INTO ripple_games (user_id, bet_amount, current_amount)
               VALUES (?, ?, ?)""",
            (user_id, bet_amount, bet_amount)
        )
        await self.conn.commit()
    
    async def update_ripple(self, user_id: int, **kwargs):
        """Update ripple game"""
        if not kwargs:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        
        await self.conn.execute(
            f"UPDATE ripple_games SET {set_clause} WHERE user_id = ? AND active = 1",
            values
        )
        await self.conn.commit()
    
    async def end_ripple(self, user_id: int):
        """End ripple game"""
        await self.conn.execute(
            "UPDATE ripple_games SET active = 0 WHERE user_id = ? AND active = 1",
            (user_id,)
        )
        await self.conn.commit()

# Global database instance
db = Database()
