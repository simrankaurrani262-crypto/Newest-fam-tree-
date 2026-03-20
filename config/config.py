"""
Fam Tree Bot Pro - Configuration
================================
Complete configuration for the bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_database.db")

# Game Constants
DAILY_BONUS_BASE = 1000
GEMSTONE_FUSE_BONUS = 5000
MAX_ROBBERY_PER_DAY = 8
MAX_KILL_PER_DAY = 5
MAX_FRIENDS = 100
MAX_PARTNERS = 7
MAX_CHILDREN = 8

FERTILIZE_COOLDOWN = 600  # 10 minutes
FERTILIZE_REWARD = 30
FERTILIZE_TIME_REDUCTION = 1200  # 20 minutes

# Crops Configuration
CROPS = {
    "corn": {"emoji": "🌽", "buy_price": 10, "sell_price": 18, "grow_time": 3600, "season": "spring"},
    "potato": {"emoji": "🥔", "buy_price": 12, "sell_price": 22, "grow_time": 4200, "season": "autumn"},
    "carrot": {"emoji": "🥕", "buy_price": 15, "sell_price": 28, "grow_time": 4800, "season": "winter"},
    "tomato": {"emoji": "🍅", "buy_price": 18, "sell_price": 32, "grow_time": 5400, "season": "summer"},
    "eggplant": {"emoji": "🍆", "buy_price": 20, "sell_price": 38, "grow_time": 6000, "season": "cloudy"},
    "pepper": {"emoji": "🌶️", "buy_price": 25, "sell_price": 45, "grow_time": 6600, "season": "spring"},
}

# Cooking Recipes
RECIPES = {
    "popcorn": {"emoji": "🍿", "ingredients": {"corn": 3}, "time": 300},
    "corn_flour": {"emoji": "🌾", "ingredients": {"corn": 5}, "time": 400},
    "fries": {"emoji": "🍟", "ingredients": {"potato": 3}, "time": 350},
    "chips": {"emoji": "🥔", "ingredients": {"potato": 5}, "time": 450},
    "sauce": {"emoji": "🥫", "ingredients": {"tomato": 3}, "time": 400},
    "juice": {"emoji": "🧃", "ingredients": {"carrot": 10}, "time": 500},
    "stew": {"emoji": "🍲", "ingredients": {"eggplant": 3}, "time": 450},
    "bread": {"emoji": "🍞", "ingredients": {"corn": 5, "potato": 5}, "time": 600},
    "jam": {"emoji": "🍯", "ingredients": {"carrot": 5, "tomato": 5}, "time": 550},
    "salad": {"emoji": "🥗", "ingredients": {"potato": 2, "tomato": 1}, "time": 300},
    "breadjam": {"emoji": "🥪", "ingredients": {"bread": 2, "jam": 1}, "time": 400},
    "sandwich": {"emoji": "🥪", "ingredients": {"salad": 1, "corn": 5, "bread": 1}, "time": 500},
}

# Gemstones
GEMSTONES = ["💎", "🔷", "🔶", "💚", "💜"]

# Jobs
JOBS = {
    "unemployed": {"salary": 100, "requirement": None},
    "farmer": {"salary": 200, "requirement": None},
    "teacher": {"salary": 300, "requirement": None},
    "doctor": {"salary": 500, "requirement": None},
    "engineer": {"salary": 600, "requirement": None},
    "babysitter": {"salary": 400, "requirement": 3},
}

# Weapons
WEAPONS = {
    "fist": {"price": 0, "power": 1, "emoji": "👊"},
    "knife": {"price": 500, "power": 2, "emoji": "🔪"},
    "gun": {"price": 2000, "power": 3, "emoji": "🔫"},
    "sword": {"price": 5000, "power": 4, "emoji": "⚔️"},
    "laser": {"price": 10000, "power": 5, "emoji": "🔥"},
}

# Reaction GIFs
REACTIONS = {
    "hug": "https://media.giphy.com/media/od5H3PmEG5lT7aPqsz/giphy.gif",
    "kiss": "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
    "pat": "https://media.giphy.com/media/5tmRHwTlHAA9WkVxTU/giphy.gif",
    "cry": "https://media.giphy.com/media/OPU6wzx8JrHna/giphy.gif",
    "smile": "https://media.giphy.com/media/1BcfiGlOGXzQ6pXziP/giphy.gif",
    "sad": "https://media.giphy.com/media/ROF8OQvDmxytW/giphy.gif",
    "angry": "https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.gif",
    "laugh": "https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif",
    "sleep": "https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif",
    "dance": "https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif",
}

# Countries for nation game
COUNTRIES = {
    "Afghanistan": "Asia", "Albania": "Europe", "Algeria": "Africa", "Andorra": "Europe",
    "Angola": "Africa", "Argentina": "South America", "Armenia": "Asia", "Australia": "Oceania",
    "Austria": "Europe", "Azerbaijan": "Asia", "Bahamas": "North America", "Bahrain": "Asia",
    "Bangladesh": "Asia", "Barbados": "North America", "Belarus": "Europe", "Belgium": "Europe",
    "Belize": "North America", "Benin": "Africa", "Bhutan": "Asia", "Bolivia": "South America",
    "Bosnia": "Europe", "Botswana": "Africa", "Brazil": "South America", "Bulgaria": "Europe",
    "Canada": "North America", "Chile": "South America", "China": "Asia", "Colombia": "South America",
    "Croatia": "Europe", "Cuba": "North America", "Cyprus": "Europe", "Czech Republic": "Europe",
    "Denmark": "Europe", "Ecuador": "South America", "Egypt": "Africa", "Estonia": "Europe",
    "Ethiopia": "Africa", "Fiji": "Oceania", "Finland": "Europe", "France": "Europe",
    "Germany": "Europe", "Ghana": "Africa", "Greece": "Europe", "Guatemala": "North America",
    "Haiti": "North America", "Honduras": "North America", "Hungary": "Europe", "Iceland": "Europe",
    "India": "Asia", "Indonesia": "Asia", "Iran": "Asia", "Iraq": "Asia",
    "Ireland": "Europe", "Israel": "Asia", "Italy": "Europe", "Jamaica": "North America",
    "Japan": "Asia", "Jordan": "Asia", "Kazakhstan": "Asia", "Kenya": "Africa",
    "Kuwait": "Asia", "Latvia": "Europe", "Lebanon": "Asia", "Libya": "Africa",
    "Lithuania": "Europe", "Luxembourg": "Europe", "Madagascar": "Africa", "Malaysia": "Asia",
    "Maldives": "Asia", "Mexico": "North America", "Monaco": "Europe", "Mongolia": "Asia",
    "Morocco": "Africa", "Nepal": "Asia", "Netherlands": "Europe", "New Zealand": "Oceania",
    "Nigeria": "Africa", "Norway": "Europe", "Oman": "Asia", "Pakistan": "Asia",
    "Panama": "North America", "Paraguay": "South America", "Peru": "South America", "Philippines": "Asia",
    "Poland": "Europe", "Portugal": "Europe", "Qatar": "Asia", "Romania": "Europe",
    "Russia": "Europe", "Saudi Arabia": "Asia", "Senegal": "Africa", "Serbia": "Europe",
    "Singapore": "Asia", "Slovakia": "Europe", "Slovenia": "Europe", "Somalia": "Africa",
    "South Africa": "Africa", "South Korea": "Asia", "Spain": "Europe", "Sri Lanka": "Asia",
    "Sudan": "Africa", "Sweden": "Europe", "Switzerland": "Europe", "Syria": "Asia",
    "Taiwan": "Asia", "Tajikistan": "Asia", "Tanzania": "Africa", "Thailand": "Asia",
    "Tunisia": "Africa", "Turkey": "Asia", "Turkmenistan": "Asia", "Uganda": "Africa",
    "Ukraine": "Europe", "United Arab Emirates": "Asia", "United Kingdom": "Europe", "United States": "North America",
    "Uruguay": "South America", "Uzbekistan": "Asia", "Venezuela": "South America", "Vietnam": "Asia",
    "Yemen": "Asia", "Zambia": "Africa", "Zimbabwe": "Africa"
}

# Trivia Questions
TRIVIA_QUESTIONS = [
    {"question": "What is the capital of France?", "answer": "Paris", "options": ["London", "Paris", "Berlin", "Madrid"]},
    {"question": "What is 2 + 2?", "answer": "4", "options": ["3", "4", "5", "6"]},
    {"question": "What is the largest planet in our solar system?", "answer": "Jupiter", "options": ["Earth", "Mars", "Jupiter", "Saturn"]},
    {"question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci", "options": ["Van Gogh", "Picasso", "Leonardo da Vinci", "Michelangelo"]},
    {"question": "What is the smallest country in the world?", "answer": "Vatican City", "options": ["Monaco", "Vatican City", "San Marino", "Liechtenstein"]},
    {"question": "What year did World War II end?", "answer": "1945", "options": ["1943", "1944", "1945", "1946"]},
    {"question": "What is the chemical symbol for gold?", "answer": "Au", "options": ["Ag", "Au", "Fe", "Cu"]},
    {"question": "How many continents are there?", "answer": "7", "options": ["5", "6", "7", "8"]},
    {"question": "Who wrote Romeo and Juliet?", "answer": "William Shakespeare", "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"]},
    {"question": "What is the speed of light?", "answer": "299792458", "options": ["199792458", "299792458", "399792458", "499792458"]},
]

# 4 Pics 1 Word Data
FOUR_PICS_WORDS = [
    {"word": "LIFE", "images": ["baby", "nest", "plants", "seed"], "difficulty": 1},
    {"word": "BOOK", "images": ["pages", "library", "reading", "cover"], "difficulty": 1},
    {"word": "FIRE", "images": ["flame", "campfire", "firefighter", "match"], "difficulty": 1},
    {"word": "WATER", "images": ["ocean", "rain", "glass", "faucet"], "difficulty": 2},
    {"word": "LOVE", "images": ["heart", "couple", "kiss", "ring"], "difficulty": 1},
    {"word": "TIME", "images": ["clock", "watch", "hourglass", "calendar"], "difficulty": 2},
    {"word": "DREAM", "images": ["sleep", "cloud", "star", "moon"], "difficulty": 3},
    {"word": "MUSIC", "images": ["note", "guitar", "headphones", "concert"], "difficulty": 2},
    {"word": "SCHOOL", "images": ["student", "books", "blackboard", "backpack"], "difficulty": 3},
    {"word": "FAMILY", "images": ["parents", "children", "home", "tree"], "difficulty": 2},
    {"word": "FOOD", "images": ["pizza", "burger", "pasta", "salad"], "difficulty": 1},
    {"word": "GAME", "images": ["controller", "cards", "dice", "board"], "difficulty": 1},
    {"word": "WORK", "images": ["office", "computer", "meeting", "desk"], "difficulty": 2},
    {"word": "BEACH", "images": ["sand", "ocean", "sun", "umbrella"], "difficulty": 2},
    {"word": "DANCE", "images": ["ballet", "music", "stage", "shoes"], "difficulty": 2},
]

# Bot Messages
START_MESSAGE = """🌲 💘 <b>Welcome to Fam Tree Bot!</b>

This bot helps you create a virtual family, make friends, and maintain a garden with many mini-games!

🌳 <b>Family Tree</b> - Create your family, adopt, marry
🌐 <b>Friend Circle</b> - Add friends and expand your circle
🏡 <b>Garden</b> - Plant, harvest, trade crops
💸 <b>Rob & Kill</b> - Exciting PvP features
💎 <b>Daily Rewards</b> - Collect salary and fuse gemstones
🏭 <b>Factory</b> - Hire workers and earn money
🎮 <b>Mini Games</b> - Ripple, Nation Guess, 4 Pics 1 Word, and more!

Use /me to get started!
Use /commands to see all available commands!
"""

COMMANDS_MESSAGE = """📜 <b>Available Commands</b>

<b>🌳 Family Tree:</b>
/tree - View your family tree
/adopt @user - Adopt a user
/marry @user - Marry a user
/divorce - Divorce a partner
/disown - Disown a child
/friend @user - Add a friend
/circle - View friend circle
/relations - View close family
/family - View family members

<b>🏡 Garden:</b>
/garden - View your garden
/plant [amount] [crop] - Plant seeds
/harvest - Harvest crops
/barn - View your barn
/add [amount] [crop] - Buy seeds
/sell [amount] [crop] - Sell crops
/fertilise @user - Fertilize garden
/stands - View global stands
/putstand [crop] [amount] [price] - Put crops on stand

<b>💰 Account:</b>
/account - View your profile
/rob @user - Rob a user
/kill @user - Kill a user
/insurance - Apply for insurance
/pay [amount] @user - Pay a user
/weapon - Select weapon

<b>📅 Daily:</b>
/daily - Collect daily bonus
/fuse @user - Fuse gemstones
/job - Select a job

<b>🏭 Factory:</b>
/factory - View factory
/hire @user - Hire a worker
/fire - Fire a worker

<b>🎮 Games:</b>
/ripple [amount] - Play ripple
/rbet [amount] - Quick ripple bet
/rtake - Take winnings
/nation - Guess the nation
/4p - 4 Pics 1 Word
/lottery [amount] - Start a lottery
/question - Trivia question

<b>📊 Stats:</b>
/mb - Money leaderboard
/leaderboard - Family leaderboard
/moneygraph - Money graph
/waifu - View your waifu

<b>⚙️ Settings:</b>
/toggle - Toggle features
/disable [command] - Disable command
/enable [command] - Enable command

<b>🔧 Utility:</b>
/2jpg - Sticker to JPG
/2png - Sticker to PNG
/figlet [text] - ASCII art
/qrcode [text] - Generate QR code
/catfact - Random cat fact
/animequote - Random anime quote

Use /help [command] for more info on a specific command.
"""

HELP_MESSAGES = {
    "adopt": """🌳 <b>/adopt</b>

Adopt a user into your family.

<b>Usage:</b>
<code>/adopt @username</code>
Or reply to a user with <code>/adopt</code>

The user must accept your proposal.

<b>Limits:</b>
• Max 8 children
• Cannot adopt yourself
• Cannot adopt existing family members""",
    
    "marry": """💍 <b>/marry</b>

Marry a user.

<b>Usage:</b>
<code>/marry @username</code>
Or reply to a user with <code>/marry</code>

The user must accept your proposal.

<b>Limits:</b>
• Max 7 partners
• Cannot marry yourself
• Cannot marry existing partners""",
    
    "tree": """🌳 <b>/tree</b>

View your family tree.

<b>Usage:</b>
<code>/tree</code> - View your tree
<code>/tree @username</code> - View someone's tree

Shows a visual representation of your family with parents, partners, and children.""",
    
    "garden": """🏡 <b>/garden</b>

View and manage your garden.

<b>Usage:</b>
<code>/garden</code> - View your garden

<b>Related Commands:</b>
• /plant [amount] [crop] - Plant seeds
• /harvest - Harvest ready crops
• /barn - View your barn
• /add [amount] [crop] - Buy seeds
• /stands - View marketplace""",
    
    "rob": """💰 <b>/rob</b>

Rob a user for money.

<b>Usage:</b>
<code>/rob @username</code>
Or reply to a user with <code>/rob</code>

<b>Limits:</b>
• Max 8 robberies per day
• Cannot rob when dead
• Cannot rob dead users
• Success chance depends on weapon

<b>Note:</b> Robbing decreases reputation!""",
    
    "daily": """💎 <b>/daily</b>

Collect your daily bonus.

Includes:
• Base bonus: $1,000
• Job salary
• Family bonus based on size
• Random gemstone

💡 Find someone with the same gemstone and /fuse for $5,000 bonus!""",
}
