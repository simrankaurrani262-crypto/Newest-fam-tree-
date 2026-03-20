"""
Fam Tree Bot Pro - Main Bot
===========================
Complete Telegram Bot Implementation
"""

import logging
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from telegram.constants import ParseMode

from config.config import BOT_TOKEN, START_MESSAGE, COMMANDS_MESSAGE, HELP_MESSAGES, ADMIN_IDS
from models.database import db

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import handlers
from handlers.family_handler import FamilyHandler
from handlers.garden_handler import GardenHandler
from handlers.account_handler import AccountHandler
from handlers.daily_handler import DailyHandler
from handlers.factory_handler import FactoryHandler
from handlers.games_handler import GamesHandler
from handlers.stats_handler import StatsHandler
from handlers.settings_handler import SettingsHandler
from handlers.utility_handler import UtilityHandler

class FamTreeBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.family_handler = FamilyHandler()
        self.garden_handler = GardenHandler()
        self.account_handler = AccountHandler()
        self.daily_handler = DailyHandler()
        self.factory_handler = FactoryHandler()
        self.games_handler = GamesHandler()
        self.stats_handler = StatsHandler()
        self.settings_handler = SettingsHandler()
        self.utility_handler = UtilityHandler()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all command handlers"""
        
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("commands", self.commands_command))
        self.application.add_handler(CommandHandler("me", self.me_command))
        
        # Family commands
        self.application.add_handler(CommandHandler("tree", self.family_handler.tree_command))
        self.application.add_handler(CommandHandler("adopt", self.family_handler.adopt_command))
        self.application.add_handler(CommandHandler("marry", self.family_handler.marry_command))
        self.application.add_handler(CommandHandler("divorce", self.family_handler.divorce_command))
        self.application.add_handler(CommandHandler("disown", self.family_handler.disown_command))
        self.application.add_handler(CommandHandler("friend", self.family_handler.friend_command))
        self.application.add_handler(CommandHandler("circle", self.family_handler.circle_command))
        self.application.add_handler(CommandHandler("friends", self.family_handler.circle_command))
        self.application.add_handler(CommandHandler("relations", self.family_handler.relations_command))
        self.application.add_handler(CommandHandler("family", self.family_handler.family_command))
        self.application.add_handler(CommandHandler("setpic", self.family_handler.setpic_command))
        self.application.add_handler(CommandHandler("setpfp", self.family_handler.setpfp_command))
        self.application.add_handler(CommandHandler("accept", self.family_handler.accept_command))
        self.application.add_handler(CommandHandler("reject", self.family_handler.reject_command))
        self.application.add_handler(CommandHandler("block", self.family_handler.block_command))
        self.application.add_handler(CommandHandler("unblock", self.family_handler.unblock_command))
        self.application.add_handler(CommandHandler("blocklist", self.family_handler.blocklist_command))
        self.application.add_handler(CommandHandler("wedcard", self.family_handler.wedcard_command))
        
        # Garden commands
        self.application.add_handler(CommandHandler("garden", self.garden_handler.garden_command))
        self.application.add_handler(CommandHandler("plant", self.garden_handler.plant_command))
        self.application.add_handler(CommandHandler("harvest", self.garden_handler.harvest_command))
        self.application.add_handler(CommandHandler("barn", self.garden_handler.barn_command))
        self.application.add_handler(CommandHandler("add", self.garden_handler.add_command))
        self.application.add_handler(CommandHandler("buy", self.garden_handler.add_command))
        self.application.add_handler(CommandHandler("sell", self.garden_handler.sell_command))
        self.application.add_handler(CommandHandler("fertilise", self.garden_handler.fertilise_command))
        self.application.add_handler(CommandHandler("fertilize", self.garden_handler.fertilise_command))
        self.application.add_handler(CommandHandler("gardens", self.garden_handler.gardens_command))
        self.application.add_handler(CommandHandler("stands", self.garden_handler.stands_command))
        self.application.add_handler(CommandHandler("putstand", self.garden_handler.putstand_command))
        self.application.add_handler(CommandHandler("stand", self.garden_handler.stand_command))
        self.application.add_handler(CommandHandler("gift", self.garden_handler.gift_command))
        self.application.add_handler(CommandHandler("cook", self.garden_handler.cook_command))
        self.application.add_handler(CommandHandler("stove", self.garden_handler.stove_command))
        
        # Account commands
        self.application.add_handler(CommandHandler("account", self.account_handler.account_command))
        self.application.add_handler(CommandHandler("profile", self.account_handler.account_command))
        self.application.add_handler(CommandHandler("acc", self.account_handler.account_command))
        self.application.add_handler(CommandHandler("rob", self.account_handler.rob_command))
        self.application.add_handler(CommandHandler("kill", self.account_handler.kill_command))
        self.application.add_handler(CommandHandler("insurance", self.account_handler.insurance_command))
        self.application.add_handler(CommandHandler("pay", self.account_handler.pay_command))
        self.application.add_handler(CommandHandler("weapon", self.account_handler.weapon_command))
        self.application.add_handler(CommandHandler("reputation", self.account_handler.reputation_command))
        self.application.add_handler(CommandHandler("skills", self.account_handler.skills_command))
        self.application.add_handler(CommandHandler("donateblood", self.account_handler.donateblood_command))
        self.application.add_handler(CommandHandler("medical", self.account_handler.medical_command))
        
        # Daily commands
        self.application.add_handler(CommandHandler("daily", self.daily_handler.daily_command))
        self.application.add_handler(CommandHandler("fuse", self.daily_handler.fuse_command))
        self.application.add_handler(CommandHandler("job", self.daily_handler.job_command))
        self.application.add_handler(CommandHandler("reactions", self.daily_handler.reactions_command))
        self.application.add_handler(CommandHandler("rxns", self.daily_handler.reactions_command))
        self.application.add_handler(CommandHandler("addgif", self.daily_handler.addgif_command))
        self.application.add_handler(CommandHandler("remgifs", self.daily_handler.remgifs_command))
        self.application.add_handler(CommandHandler("showgifs", self.daily_handler.showgifs_command))
        self.application.add_handler(CommandHandler("refer", self.daily_handler.refer_command))
        
        # Factory commands
        self.application.add_handler(CommandHandler("factory", self.factory_handler.factory_command))
        self.application.add_handler(CommandHandler("hire", self.factory_handler.hire_command))
        self.application.add_handler(CommandHandler("fire", self.factory_handler.fire_command))
        self.application.add_handler(CommandHandler("work", self.factory_handler.work_command))
        
        # Games commands
        self.application.add_handler(CommandHandler("ripple", self.games_handler.ripple_command))
        self.application.add_handler(CommandHandler("rbet", self.games_handler.rbet_command))
        self.application.add_handler(CommandHandler("rtake", self.games_handler.rtake_command))
        self.application.add_handler(CommandHandler("bets", self.games_handler.bets_command))
        self.application.add_handler(CommandHandler("nation", self.games_handler.nation_command))
        self.application.add_handler(CommandHandler("lottery", self.games_handler.lottery_command))
        self.application.add_handler(CommandHandler("question", self.games_handler.question_command))
        self.application.add_handler(CommandHandler("4p", self.games_handler.fourpics_command))
        self.application.add_handler(CommandHandler("fourpics", self.games_handler.fourpics_command))
        self.application.add_handler(CommandHandler("whichai", self.games_handler.whichai_command))
        self.application.add_handler(CommandHandler("ftrivia", self.games_handler.ftrivia_command))
        self.application.add_handler(CommandHandler("paper", self.games_handler.paper_command))
        
        # Stats commands
        self.application.add_handler(CommandHandler("mb", self.stats_handler.moneyboard_command))
        self.application.add_handler(CommandHandler("moneyboard", self.stats_handler.moneyboard_command))
        self.application.add_handler(CommandHandler("leaderboard", self.stats_handler.leaderboard_command))
        self.application.add_handler(CommandHandler("moneygraph", self.stats_handler.moneygraph_command))
        self.application.add_handler(CommandHandler("mg", self.stats_handler.moneygraph_command))
        self.application.add_handler(CommandHandler("showstats", self.stats_handler.showstats_command))
        self.application.add_handler(CommandHandler("waifu", self.stats_handler.waifu_command))
        self.application.add_handler(CommandHandler("waifus", self.stats_handler.waifus_command))
        self.application.add_handler(CommandHandler("interactions", self.stats_handler.interactions_command))
        self.application.add_handler(CommandHandler("setloc", self.stats_handler.setloc_command))
        self.application.add_handler(CommandHandler("showmap", self.stats_handler.showmap_command))
        self.application.add_handler(CommandHandler("fsearch", self.stats_handler.fsearch_command))
        
        # Settings commands
        self.application.add_handler(CommandHandler("toggle", self.settings_handler.toggle_command))
        self.application.add_handler(CommandHandler("disable", self.settings_handler.disable_command))
        self.application.add_handler(CommandHandler("enable", self.settings_handler.enable_command))
        self.application.add_handler(CommandHandler("disabled", self.settings_handler.disabled_command))
        self.application.add_handler(CommandHandler("incests", self.settings_handler.incests_command))
        self.application.add_handler(CommandHandler("gifs", self.settings_handler.gifs_command))
        self.application.add_handler(CommandHandler("autoprune", self.settings_handler.autoprune_command))
        self.application.add_handler(CommandHandler("prune", self.settings_handler.prune_command))
        
        # Utility commands
        self.application.add_handler(CommandHandler("2jpg", self.utility_handler.tojpg_command))
        self.application.add_handler(CommandHandler("2png", self.utility_handler.topng_command))
        self.application.add_handler(CommandHandler("figlet", self.utility_handler.figlet_command))
        self.application.add_handler(CommandHandler("2imgur", self.utility_handler.toimgur_command))
        self.application.add_handler(CommandHandler("qotd", self.utility_handler.qotd_command))
        self.application.add_handler(CommandHandler("addcaption", self.utility_handler.addcaption_command))
        self.application.add_handler(CommandHandler("ip2loc", self.utility_handler.ip2loc_command))
        self.application.add_handler(CommandHandler("paste", self.utility_handler.paste_command))
        self.application.add_handler(CommandHandler("shorten", self.utility_handler.shorten_command))
        self.application.add_handler(CommandHandler("qrcode", self.utility_handler.qrcode_command))
        self.application.add_handler(CommandHandler("catfact", self.utility_handler.catfact_command))
        self.application.add_handler(CommandHandler("shibapic", self.utility_handler.shibapic_command))
        self.application.add_handler(CommandHandler("animequote", self.utility_handler.animequote_command))
        self.application.add_handler(CommandHandler("name2gender", self.utility_handler.name2gender_command))
        self.application.add_handler(CommandHandler("activity", self.utility_handler.activity_command))
        self.application.add_handler(CommandHandler("name2nation", self.utility_handler.name2nation_command))
        self.application.add_handler(CommandHandler("name2age", self.utility_handler.name2age_command))
        self.application.add_handler(CommandHandler("foodpic", self.utility_handler.foodpic_command))
        self.application.add_handler(CommandHandler("darkjoke", self.utility_handler.darkjoke_command))
        self.application.add_handler(CommandHandler("joketype", self.utility_handler.joketype_command))
        self.application.add_handler(CommandHandler("randomjoke", self.utility_handler.randomjoke_command))
        self.application.add_handler(CommandHandler("evilinsult", self.utility_handler.evilinsult_command))
        self.application.add_handler(CommandHandler("randomadvice", self.utility_handler.randomadvice_command))
        self.application.add_handler(CommandHandler("dadjoke", self.utility_handler.dadjoke_command))
        
        # Admin commands
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        self.application.add_handler(CommandHandler("botstats", self.botstats_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for text responses
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user = update.effective_user
        chat = update.effective_chat
        
        # Register user
        await db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Register chat if group
        if chat.type != 'private':
            await db.get_chat_settings(chat.id)
        
        keyboard = [
            [InlineKeyboardButton("📜 View Commands", callback_data='commands')],
            [InlineKeyboardButton("💰 My Account", callback_data='account')],
            [InlineKeyboardButton("🏡 My Garden", callback_data='garden')],
            [InlineKeyboardButton("🌳 Family Tree", callback_data='tree')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            START_MESSAGE,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        if context.args:
            command = context.args[0].lower().lstrip('/')
            help_text = HELP_MESSAGES.get(command, f"❌ No help available for /{command}")
            await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(
                "📖 <b>Help Menu</b>\n\n"
                "Use /commands to see all available commands.\n"
                "Use /help [command] for detailed help on a specific command.\n\n"
                "Example: <code>/help adopt</code>",
                parse_mode=ParseMode.HTML
            )
    
    async def commands_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commands command"""
        await update.message.reply_text(
            COMMANDS_MESSAGE,
            parse_mode=ParseMode.HTML
        )
    
    async def me_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Me command - Shows user profile"""
        user = update.effective_user
        
        db_user = await db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        keyboard = [
            [InlineKeyboardButton("🌳 Family Tree", callback_data=f'tree_{user.id}'),
             InlineKeyboardButton("🌐 Friends", callback_data=f'friends_{user.id}')],
            [InlineKeyboardButton("🏡 Garden", callback_data=f'garden_{user.id}'),
             InlineKeyboardButton("💰 Account", callback_data=f'account_{user.id}')],
            [InlineKeyboardButton("🏭 Factory", callback_data=f'factory_{user.id}'),
             InlineKeyboardButton("🎮 Games", callback_data=f'games_{user.id}')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        status = "💀 Dead" if db_user.get('is_dead') else "😊 Alive"
        gemstone = db_user.get('gemstone') or "None"
        
        text = f"""👤 <b>{user.first_name}'s Profile</b>

💰 Money: ${db_user['money']:,}
💎 Gemstone: {gemstone}
💼 Job: {db_user.get('job', 'Unemployed').title()}
⚔️ Weapon: {db_user.get('weapon', 'Fist').title()}
⭐ Reputation: {db_user.get('reputation', 100)}
🩺 Status: {status}
📅 Joined: {str(db_user['created_at'])[:10]}

Use buttons below to explore!"""
        
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message (Admin only)"""
        user = update.effective_user
        
        if user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ You are not authorized!")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /broadcast [message]")
            return
        
        message = ' '.join(context.args)
        await update.message.reply_text(f"📢 Broadcast: {message}")
    
    async def botstats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot statistics (Admin only)"""
        user = update.effective_user
        
        if user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ You are not authorized!")
            return
        
        async with db.conn.execute("SELECT COUNT(*) FROM users") as cursor:
            total_users = (await cursor.fetchone())[0]
        
        async with db.conn.execute("SELECT COUNT(*) FROM family_relations") as cursor:
            total_relations = (await cursor.fetchone())[0]
        
        async with db.conn.execute("SELECT COUNT(*) FROM gardens") as cursor:
            total_gardens = (await cursor.fetchone())[0]
        
        async with db.conn.execute("SELECT COUNT(*) FROM friends") as cursor:
            total_friends = (await cursor.fetchone())[0]
        
        text = f"""📊 <b>Bot Statistics</b>

👥 Total Users: {total_users}
🌳 Total Relations: {total_relations}
🏡 Total Gardens: {total_gardens}
🌐 Total Friendships: {total_friends // 2}

🤖 Bot Status: Online ✅"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == 'commands':
            await query.edit_message_text(
                COMMANDS_MESSAGE,
                parse_mode=ParseMode.HTML
            )
        elif data == 'account':
            await query.edit_message_text(
                "💰 <b>Account Menu</b>\n\n"
                "Use /account to view your profile\n"
                "Use /daily to collect daily bonus\n"
                "Use /weapon to select weapon\n"
                "Use /rob to rob someone\n"
                "Use /kill to kill someone\n"
                "Use /insurance for insurance",
                parse_mode=ParseMode.HTML
            )
        elif data == 'garden':
            await query.edit_message_text(
                "🏡 <b>Garden Menu</b>\n\n"
                "Use /garden to view your garden\n"
                "Use /plant to plant seeds\n"
                "Use /harvest to harvest crops\n"
                "Use /barn to view your barn\n"
                "Use /add to buy seeds\n"
                "Use /stands to view marketplace",
                parse_mode=ParseMode.HTML
            )
        elif data == 'tree':
            await query.edit_message_text(
                "🌳 <b>Family Tree Menu</b>\n\n"
                "Use /tree to view your family\n"
                "Use /adopt to adopt someone\n"
                "Use /marry to marry someone\n"
                "Use /friend to add friends\n"
                "Use /circle to view friend circle",
                parse_mode=ParseMode.HTML
            )
        elif data.startswith('accept_'):
            await self.family_handler.handle_accept_callback(update, context)
        elif data.startswith('reject_'):
            await self.family_handler.handle_reject_callback(update, context)
        elif data.startswith('divorce_'):
            await self.family_handler.handle_divorce_callback(update, context)
        elif data.startswith('disown_'):
            await self.family_handler.handle_disown_callback(update, context)
        elif data.startswith('fire_'):
            await self.factory_handler.handle_fire_callback(update, context)
        elif data.startswith('toggle_'):
            await self.settings_handler.handle_toggle_callback(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages for games"""
        await self.games_handler.handle_game_response(update, context)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again later."
            )
    
    async def run(self):
        """Run the bot"""
        await db.connect()
        logger.info("Database connected!")
        
        await self.application.initialize()
        await self.application.start()
        logger.info("Bot started!")
        
        await self.application.updater.start_polling(drop_pending_updates=True)
        
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    bot = FamTreeBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\nBot stopped!")
