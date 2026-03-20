"""
Daily Handler
=============
Handles daily bonus, jobs, and GIFs
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import datetime, timedelta
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from config.config import DAILY_BONUS_BASE, GEMSTONE_FUSE_BONUS, GEMSTONES, JOBS, REACTIONS

class DailyHandler:
    
    async def daily_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Collect daily bonus"""
        user = update.effective_user
        
        db_user = await db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        last_daily = db_user.get('last_daily')
        if last_daily:
            last_daily = datetime.fromisoformat(str(last_daily))
            if datetime.now() - last_daily < timedelta(days=1):
                time_left = timedelta(days=1) - (datetime.now() - last_daily)
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                
                await update.message.reply_text(
                    f"⏱ <b>Daily Bonus Cooldown</b>\n\n"
                    f"Come back in {hours}h {minutes}m!",
                    parse_mode=ParseMode.HTML
                )
                return
        
        base_bonus = DAILY_BONUS_BASE
        job = JOBS.get(db_user.get('job', 'unemployed'), JOBS['unemployed'])
        job_bonus = job['salary']
        
        # Family bonus
        async with db.conn.execute(
            "SELECT COUNT(*) FROM family_relations WHERE user_id = ?",
            (user.id,)
        ) as cursor:
            family_count = (await cursor.fetchone())[0]
        family_bonus = family_count * 50
        
        total_bonus = base_bonus + job_bonus + family_bonus
        
        gemstone = random.choice(GEMSTONES)
        
        await db.update_user(
            user.id,
            money=db_user['money'] + total_bonus,
            last_daily=datetime.now(),
            gemstone=gemstone,
            daily_streak=db_user.get('daily_streak', 0) + 1
        )
        
        streak_text = f"\n🔥 Streak: {db_user.get('daily_streak', 0) + 1} days" if db_user.get('daily_streak', 0) > 0 else ""
        
        text = f"""💰 <b>Daily Bonus Collected!</b>{streak_text}

💵 Base: ${base_bonus}
💼 Job ({db_user.get('job', 'unemployed').title()}): ${job_bonus}
👨‍👩‍👧 Family: ${family_bonus}
━━━━━━━━━━━━━━
💰 <b>Total: ${total_bonus}</b>

💎 <b>Today's Gemstone:</b> {gemstone}
💡 Find someone with the same gemstone and /fuse for ${GEMSTONE_FUSE_BONUS} bonus!"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def fuse_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Fuse gemstones with another user"""
        user = update.effective_user
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to fuse gemstones!")
            return
        
        if target.id == user.id:
            await update.message.reply_text("❌ You can't fuse with yourself!")
            return
        
        db_user = await db.get_user(user.id)
        target_user = await db.get_user(target.id)
        
        if not db_user.get('gemstone'):
            await update.message.reply_text("❌ You don't have a gemstone! Collect /daily first!")
            return
        
        if not target_user.get('gemstone'):
            await update.message.reply_text(f"❌ {target.first_name} doesn't have a gemstone!")
            return
        
        if db_user['gemstone'] != target_user['gemstone']:
            await update.message.reply_text(
                f"❌ <b>Gemstones don't match!</b>\n\n"
                f"Your gemstone: {db_user['gemstone']}\n"
                f"{target.first_name}'s gemstone: {target_user['gemstone']}\n\n"
                f"💡 Find someone with the same gemstone!",
                parse_mode=ParseMode.HTML
            )
            return
        
        await db.update_user(user.id, gemstone=None)
        await db.update_user(target.id, gemstone=None)
        
        await db.add_money(user.id, GEMSTONE_FUSE_BONUS)
        await db.add_money(target.id, GEMSTONE_FUSE_BONUS)
        
        await update.message.reply_text(
            f"💎 <b>Gemstones Fused!</b>\n\n"
            f"{user.first_name} {db_user['gemstone']} + {target.first_name} {target_user['gemstone']}\n"
            f"💰 Both received ${GEMSTONE_FUSE_BONUS}!",
            parse_mode=ParseMode.HTML
        )
    
    async def job_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select a job"""
        user = update.effective_user
        db_user = await db.get_user(user.id)
        
        if context.args:
            job_name = context.args[0].lower()
            
            if job_name not in JOBS:
                await update.message.reply_text(f"❌ Invalid job! Available: {', '.join(JOBS.keys())}")
                return
            
            job = JOBS[job_name]
            
            if job['requirement']:
                async with db.conn.execute(
                    "SELECT COUNT(*) FROM family_relations WHERE user_id = ? AND relation_type = 'child'",
                    (user.id,)
                ) as cursor:
                    children_count = (await cursor.fetchone())[0]
                
                if children_count < job['requirement']:
                    await update.message.reply_text(
                        f"❌ You need {job['requirement']} children for this job!\n"
                        f"You have: {children_count}"
                    )
                    return
            
            await db.update_user(user.id, job=job_name)
            
            await update.message.reply_text(
                f"💼 <b>Job Changed!</b>\n\n"
                f"New job: {job_name.title()}\n"
                f"💰 Daily salary: ${job['salary']}",
                parse_mode=ParseMode.HTML
            )
            return
        
        text = f"💼 <b>Available Jobs</b>\n\n"
        text += f"Current job: {db_user.get('job', 'unemployed').title()}\n\n"
        
        for job_name, job_data in JOBS.items():
            current = " ✅" if db_user.get('job') == job_name else ""
            req_text = f" (Requires {job_data['requirement']} children)" if job_data['requirement'] else ""
            text += f"💼 <b>{job_name.title()}</b>{current}{req_text}\n"
            text += f"   💰 Salary: ${job_data['salary']}/day\n\n"
        
        text += "💡 Use <code>/job [job_name]</code> to change jobs!"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def reactions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available reaction GIFs"""
        text = "🎭 <b>Available Reactions</b>\n\n"
        
        for reaction_name in REACTIONS.keys():
            text += f"• {reaction_name.title()}\n"
        
        text += "\n💡 Use <code>,{reaction}</code> or <code>.{reaction}</code> to send a GIF!\n"
        text += "Example: <code>,hug</code> or <code>.kiss</code>"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def addgif_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add custom GIF for rob/kill"""
        user = update.effective_user
        chat = update.effective_chat
        
        if len(context.args) < 1:
            await update.message.reply_text(
                "Usage: Reply to a GIF with <code>/addgif [type]</code>\n\n"
                "Types: <code>robyes</code>, <code>robno</code>, <code>killyes</code>, <code>killno</code>"
            )
            return
        
        gif_type = context.args[0].lower()
        
        if gif_type not in ['robyes', 'robno', 'killyes', 'killno']:
            await update.message.reply_text("❌ Invalid type! Use: robyes, robno, killyes, killno")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Please reply to a GIF!")
            return
        
        replied = update.message.reply_to_message
        
        if not replied.animation and not replied.video:
            await update.message.reply_text("❌ Please reply to a GIF or video!")
            return
        
        file_id = replied.animation.file_id if replied.animation else replied.video.file_id
        
        await db.conn.execute(
            "INSERT INTO custom_gifs (chat_id, gif_type, file_id, added_by) VALUES (?, ?, ?, ?)",
            (chat.id, gif_type, file_id, user.id)
        )
        await db.conn.commit()
        
        await update.message.reply_text(f"✅ GIF added for <code>{gif_type}</code>!", parse_mode=ParseMode.HTML)
    
    async def remgifs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove all custom GIFs"""
        chat = update.effective_chat
        
        await db.conn.execute(
            "DELETE FROM custom_gifs WHERE chat_id = ?",
            (chat.id,)
        )
        await db.conn.commit()
        
        await update.message.reply_text("✅ All custom GIFs removed!")
    
    async def showgifs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show custom GIFs"""
        chat = update.effective_chat
        
        async with db.conn.execute(
            "SELECT DISTINCT gif_type FROM custom_gifs WHERE chat_id = ?",
            (chat.id,)
        ) as cursor:
            rows = await cursor.fetchall()
        
        if not rows:
            await update.message.reply_text("🌱 No custom GIFs in this chat!")
            return
        
        text = "🎭 <b>Custom GIFs</b>\n\n"
        
        for row in rows:
            gif_type = row['gif_type']
            
            async with db.conn.execute(
                "SELECT COUNT(*) FROM custom_gifs WHERE chat_id = ? AND gif_type = ?",
                (chat.id, gif_type)
            ) as cursor2:
                count = (await cursor2.fetchone())[0]
            
            text += f"• {gif_type}: {count} GIFs\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def refer_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get referral link"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type != 'private':
            await update.message.reply_text("❌ This command only works in private chat!")
            return
        
        db_user = await db.get_user(user.id)
        refer_code = db_user.get('refer_code')
        
        if not refer_code:
            import random, string
            refer_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            await db.update_user(user.id, refer_code=refer_code)
        
        bot_username = context.bot.username
        refer_link = f"https://t.me/{bot_username}?start={refer_code}"
        
        await update.message.reply_text(
            f"💰 <b>Your Referral Link</b>\n\n"
            f"{refer_link}\n\n"
            f"💵 You'll get $5,000 for each click!\n"
            f"💵 The clicker will get $10,000!",
            parse_mode=ParseMode.HTML
        )
