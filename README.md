# 🌲 💘 Fam Tree Bot Pro

A comprehensive Telegram bot for creating virtual families, managing gardens, playing mini-games, and more!

## ✨ Features

### 🌳 Family Tree System
- Create and manage family trees with visual graphs
- Adopt users as children (max 8)
- Marry other users (max 7 partners)
- Divorce and disown
- Custom profile pictures

### 🌐 Friend Circle
- Add friends globally (not tied to groups)
- Get $3,000 bonus for each new friendship
- View friend circles
- Block/unblock users

### 🏡 Garden System
- Plant and harvest crops
- 6 different crops with seasonal bonuses
- Buy and sell seeds
- Trade at marketplace stands
- Fertilize gardens for bonuses
- Cooking system with 12 recipes

### 💰 Account System
- Daily bonuses with gemstones
- Rob and kill other players (with limits)
- Insurance system
- Weapons and jobs
- Reputation and skills
- Medical system (revive dead players)

### 🏭 Factory System
- Hire workers (max 5)
- Send workers to work
- Build rating and price
- Fire workers for refund

### 🎮 Mini Games
- **Ripple**: Betting game with 1.5x multipliers
- **Nation Guess**: Guess countries
- **4 Pics 1 Word**: Guess words from images
- **Lottery**: Group betting
- **Trivia**: Answer questions

### 📊 Stats & Leaderboards
- Money leaderboard with graphs
- Family leaderboard
- Waifu system
- Interaction tracking
- Location maps

### 🔧 Utility Commands (25+)
- QR code generator
- ASCII art
- Cat facts
- Jokes and quotes
- And more!

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Step 1: Clone/Download
```bash
cd fam_tree_bot_pro
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Bot Token
1. Copy `.env.example` to `.env`
2. Get your bot token from [@BotFather](https://t.me/BotFather)
3. Add your token to `.env`:
```
BOT_TOKEN=your_bot_token_here
```

### Step 4: Run the Bot
```bash
python run.py
```

## 📋 Commands List

### Family Commands
| Command | Description |
|---------|-------------|
| `/tree` | View family tree |
| `/adopt @user` | Adopt a user |
| `/marry @user` | Marry a user |
| `/divorce` | Divorce a partner |
| `/disown` | Disown a child |
| `/friend @user` | Add a friend |
| `/circle` | View friend circle |
| `/relations` | View close relations |
| `/family` | View extended family |
| `/setpic` | Set profile picture |
| `/setpfp` | Update to Telegram photo |
| `/block @user` | Block a user |
| `/unblock @user` | Unblock a user |
| `/blocklist` | View blocked users |
| `/wedcard` | Create wedding card |

### Garden Commands
| Command | Description |
|---------|-------------|
| `/garden` | View your garden |
| `/plant [amount] [crop]` | Plant seeds |
| `/harvest` | Harvest ready crops |
| `/barn` | View your barn |
| `/add [amount] [crop]` | Buy seeds |
| `/sell [amount] [crop]` | Sell crops |
| `/fertilise @user` | Fertilize garden |
| `/gardens` | View active gardens |
| `/stands` | View marketplace |
| `/putstand [crop] [amount] [price]` | List crops |
| `/gift [crop] [amount]` | Gift crops |
| `/cook` | Cooking menu |

### Account Commands
| Command | Description |
|---------|-------------|
| `/account` | View your profile |
| `/rob @user` | Rob a user |
| `/kill @user` | Kill a user |
| `/insurance` | View/apply insurance |
| `/pay [amount] @user` | Pay a user |
| `/weapon` | Select weapon |
| `/reputation` | View reputation |
| `/skills` | View skills |
| `/medical` | Revive yourself |
| `/donateblood @user` | Revive someone |

### Daily Commands
| Command | Description |
|---------|-------------|
| `/daily` | Collect daily bonus |
| `/fuse @user` | Fuse gemstones |
| `/job` | Select job |
| `/reactions` | View reaction GIFs |
| `/addgif` | Add custom GIF |
| `/refer` | Get referral link |

### Factory Commands
| Command | Description |
|---------|-------------|
| `/factory` | View factory |
| `/hire @user` | Hire worker |
| `/fire` | Fire worker |
| `/work` | Send workers to work |

### Game Commands
| Command | Description |
|---------|-------------|
| `/ripple [amount]` | Play ripple |
| `/rbet [amount]` | Quick ripple |
| `/rtake` | Take winnings |
| `/nation [continent]` | Guess nation |
| `/4p` | 4 Pics 1 Word |
| `/lottery [amount]` | Start lottery |
| `/question` | Trivia |

### Stats Commands
| Command | Description |
|---------|-------------|
| `/mb` | Money leaderboard |
| `/leaderboard` | Family leaderboard |
| `/moneygraph` | Money graph |
| `/waifu` | Your waifu |
| `/interactions` | Your interactions |
| `/setloc [location]` | Set location |
| `/showmap` | Show family locations |
| `/fsearch [name]` | Search members |

### Settings Commands
| Command | Description |
|---------|-------------|
| `/toggle` | Toggle features |
| `/disable [cmd]` | Disable command |
| `/enable [cmd]` | Enable command |
| `/disabled` | List disabled |
| `/incests` | Toggle incest |

### Utility Commands
| Command | Description |
|---------|-------------|
| `/2jpg` | Sticker to JPG |
| `/2png` | Sticker to PNG |
| `/figlet [text]` | ASCII art |
| `/qrcode [text]` | Generate QR |
| `/catfact` | Cat fact |
| `/animequote` | Anime quote |
| `/randomjoke` | Random joke |
| `/darkjoke` | Dark joke |
| `/dadjoke` | Dad joke |
| And more! |

## 🗄 Database

The bot uses SQLite for data storage. Database is automatically created on first run.

## ⚙️ Configuration

Edit `config/config.py` to customize:
- Daily bonus amounts
- Crop prices and grow times
- Recipe ingredients
- Weapon stats
- Job salaries
- Game settings

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Credits

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Inspired by @fam_tree_bot

---

Made with ❤️ for the Telegram community
