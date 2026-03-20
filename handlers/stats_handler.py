"""
Stats Handler
=============
Handles leaderboards and stats
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import matplotlib.pyplot as plt
import io
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db

class StatsHandler:
    
    async def moneyboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show money leaderboard"""
        users = await db.get_money_leaderboard(10)
        
        if not users:
            await update.message.reply_text("🌱 No data yet!")
            return
        
        text = "💰 <b>Global Money Leaderboard</b>\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, user in enumerate(users[:10]):
            medal = medals[i] if i < 3 else f"{i+1}."
            name = user.get('first_name', 'Unknown')
            money = user.get('money', 0)
            text += f"{medal} {name}: ${money:,}\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show family leaderboard"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        async with db.conn.execute(
            """SELECT u.user_id, u.first_name, u.username, COUNT(fr.id) as family_count
               FROM users u
               JOIN family_relations fr ON u.user_id = fr.user_id
               WHERE fr.chat_id = ?
               GROUP BY u.user_id
               ORDER BY family_count DESC
               LIMIT 10""",
            (chat.id,)
        ) as cursor:
            rows = await cursor.fetchall()
        
        if not rows:
            await update.message.reply_text("🌱 No family data yet!")
            return
        
        text = f"🌳 <b>{chat.title} Family Leaderboard</b>\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, row in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i+1}."
            text += f"{medal} {row['first_name']}: {row['family_count']} relations\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def moneygraph_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show money graph"""
        users = await db.get_money_leaderboard(10)
        
        if not users:
            await update.message.reply_text("🌱 No data yet!")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = [u.get('first_name', 'Unknown')[:10] for u in users[:10]]
        money = [u.get('money', 0) for u in users[:10]]
        
        colors = plt.cm.viridis([i/len(names) for i in range(len(names))])
        bars = ax.barh(names[::-1], money[::-1], color=colors[::-1])
        
        ax.set_xlabel('Money ($)')
        ax.set_title('Money Leaderboard')
        ax.set_xlim(0, max(money) * 1.1)
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'${int(width):,}', 
                   ha='left', va='center', fontsize=8)
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        await update.message.reply_photo(
            photo=buf,
            caption="📊 <b>Money Graph</b>"
        )
    
    async def showstats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user stats"""
        user = update.effective_user
        
        db_user = await db.get_user(user.id)
        
        async with db.conn.execute(
            """SELECT 
                SUM(CASE WHEN proposal_type = 'marry' THEN 1 ELSE 0 END) as marriages,
                SUM(CASE WHEN proposal_type = 'adopt' THEN 1 ELSE 0 END) as adoptions,
                SUM(CASE WHEN proposal_type = 'friend' THEN 1 ELSE 0 END) as friendships
               FROM pending_proposals
               WHERE from_user_id = ?""",
            (user.id,)
        ) as cursor:
            row = await cursor.fetchone()
            marriages, adoptions, friendships = row if row else (0, 0, 0)
        
        text = f"""📊 <b>{user.first_name}'s Stats</b>

💍 Marriages: {marriages or 0}
👶 Adoptions: {adoptions or 0}
🌐 Friendships: {friendships or 0}

🌾 Total Crops: {db_user.get('total_crops_grown', 0)}
💰 Total Money: ${db_user.get('money', 0):,}
⭐ Reputation: {db_user.get('reputation', 100)}

🗓 Joined: {str(db_user['created_at'])[:10] if db_user.get('created_at') else 'Unknown'}"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def waifu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's waifu"""
        user = update.effective_user
        
        friends = await db.get_friends(user.id)
        
        if not friends:
            await update.message.reply_text("🌸 You need friends to have a waifu!")
            return
        
        waifu = random.choice(friends)
        
        await update.message.reply_text(
            f"🌸 <b>Your Waifu</b>\n\n"
            f"💖 {waifu['first_name']} is your waifu!\n\n"
            f"💡 Waifu is randomly selected from your friends!",
            parse_mode=ParseMode.HTML
        )
    
    async def waifus_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show group's waifu graph"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        await update.message.reply_text(
            "🌸 <b>Group Waifus</b>\n\n"
            "Waifu graph would be shown here!\n\n"
            "💡 Use /waifu to see your waifu!"
        )
    
    async def interactions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user interactions"""
        user = update.effective_user
        
        async with db.conn.execute(
            """SELECT u.first_name, i.count, i.interaction_type
               FROM interactions i
               JOIN users u ON i.to_user_id = u.user_id
               WHERE i.from_user_id = ?
               ORDER BY i.count DESC
               LIMIT 10""",
            (user.id,)
        ) as cursor:
            rows = await cursor.fetchall()
        
        if not rows:
            await update.message.reply_text("🌱 No interactions yet!")
            return
        
        text = f"📊 <b>{user.first_name}'s Interactions</b>\n\n"
        text += "<b>People you interact with most:</b>\n\n"
        
        for row in rows:
            text += f"• {row['first_name']}: {row['count']} {row['interaction_type']}s\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def setloc_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set location"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text("Usage: <code>/setloc [location]</code>\nExample: <code>/setloc New York</code>")
            return
        
        location = ' '.join(context.args)
        await db.update_user(user.id, location=location)
        
        await update.message.reply_text(f"📍 Location set to: {location}")
    
    async def showmap_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show map of family members"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        family = await db.get_family_tree(user.id, chat.id)
        
        locations = []
        for member in family['parents'] + family['partners'] + family['children']:
            if member.get('location'):
                locations.append(f"• {member['first_name']}: {member['location']}")
        
        if not locations:
            await update.message.reply_text("🌱 No family members have set their location!")
            return
        
        text = "🗺 <b>Family Locations</b>\n\n"
        text += "\n".join(locations)
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def fsearch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Search for members"""
        if not context.args:
            await update.message.reply_text("Usage: <code>/fsearch [name]</code>")
            return
        
        name = ' '.join(context.args).lower()
        
        async with db.conn.execute(
            "SELECT first_name, username FROM users WHERE LOWER(first_name) LIKE ?",
            (f"%{name}%",)
        ) as cursor:
            rows = await cursor.fetchall()
        
        if not rows:
            await update.message.reply_text("❌ No users found!")
            return
        
        text = f"🔍 <b>Search Results for '{name}'</b>\n\n"
        for row in rows[:10]:
            username_text = f" (@{row['username']})" if row['username'] else ""
            text += f"• {row['first_name']}{username_text}\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
