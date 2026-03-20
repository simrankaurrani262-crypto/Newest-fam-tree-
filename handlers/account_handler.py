"""
Account Handler
===============
Handles account-related commands
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
from config.config import WEAPONS, MAX_ROBBERY_PER_DAY, MAX_KILL_PER_DAY

class AccountHandler:
    
    async def account_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user account"""
        user = update.effective_user
        
        db_user = await db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        weapon = WEAPONS.get(db_user.get('weapon', 'fist'), WEAPONS['fist'])
        is_dead = db_user.get('is_dead', 0)
        death_status = "💀 Dead" if is_dead else "😊 Alive"
        
        last_rob_reset = datetime.fromisoformat(str(db_user.get('last_rob_reset', datetime.now())))
        last_kill_reset = datetime.fromisoformat(str(db_user.get('last_kill_reset', datetime.now())))
        
        # Reset counts if it's a new day
        if datetime.now() - last_rob_reset >= timedelta(days=1):
            await db.update_user(user.id, rob_count=0, last_rob_reset=datetime.now())
            db_user['rob_count'] = 0
        
        if datetime.now() - last_kill_reset >= timedelta(days=1):
            await db.update_user(user.id, kill_count=0, last_kill_reset=datetime.now())
            db_user['kill_count'] = 0
        
        rob_remaining = MAX_ROBBERY_PER_DAY - db_user.get('rob_count', 0)
        kill_remaining = MAX_KILL_PER_DAY - db_user.get('kill_count', 0)
        
        text = f"""👤 <b>{user.first_name}'s Account</b>

💰 Money: ${db_user['money']:,}
💎 Gemstone: {db_user.get('gemstone') or 'None'}
💼 Job: {db_user.get('job', 'Unemployed').title()}
⚔️ Weapon: {weapon['emoji']} {weapon['power']}
⭐ Reputation: {db_user.get('reputation', 100)}
🩺 Status: {death_status}

📊 <b>Daily Actions:</b>
🔫 Rob: {rob_remaining}/{MAX_ROBBERY_PER_DAY} remaining
⚔️ Kill: {kill_remaining}/{MAX_KILL_PER_DAY} remaining

🌱 <b>Skills:</b>
🌾 Fertilize: Level {db_user.get('skills_fertilize', 0)}
🌾 Total Crops: {db_user.get('total_crops_grown', 0)}"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def weapon_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show/select weapons"""
        user = update.effective_user
        db_user = await db.get_user(user.id)
        
        text = "⚔️ <b>Weapons Shop</b>\n\n"
        
        for weapon_name, weapon_data in WEAPONS.items():
            emoji = weapon_data['emoji']
            power = weapon_data['power']
            price = weapon_data['price']
            current = " ✅" if db_user.get('weapon') == weapon_name else ""
            
            text += f"{emoji} <b>{weapon_name.title()}</b>{current}\n"
            text += f"   💪 Power: {power} | 💰 Price: ${price}\n\n"
        
        text += "💡 Reply with weapon name to buy/change!"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def rob_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Rob a user"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Please reply to a user to rob them!")
            return
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to rob them!")
            return
        
        if target.id == user.id:
            await update.message.reply_text("❌ You can't rob yourself!")
            return
        
        db_user = await db.get_user(user.id)
        
        if db_user.get('is_dead', 0):
            await update.message.reply_text("💀 You are dead! Use /medical to revive.")
            return
        
        if db_user.get('rob_count', 0) >= MAX_ROBBERY_PER_DAY:
            await update.message.reply_text("❌ You've used all your robberies for today!")
            return
        
        target_user = await db.get_or_create_user(
            user_id=target.id,
            username=target.username,
            first_name=target.first_name,
            last_name=target.last_name
        )
        
        if target_user.get('is_dead', 0):
            await update.message.reply_text("💀 You can't rob a dead person!")
            return
        
        weapon = WEAPONS.get(db_user.get('weapon', 'fist'), WEAPONS['fist'])
        success_chance = 0.3 + (weapon['power'] * 0.1)
        
        await db.update_user(user.id, rob_count=db_user.get('rob_count', 0) + 1)
        
        if random.random() < success_chance:
            amount = min(random.randint(50, 200), target_user['money'] // 10)
            if target_user['money'] > 10000:
                amount = random.randint(200, 1000)
            
            amount = min(amount, target_user['money'])
            
            if amount > 0:
                await db.transfer_money(target.id, user.id, amount)
                
                await update.message.reply_text(
                    f"🎉 <b>Robbery Successful!</b>\n\n"
                    f"💰 You robbed ${amount} from {target.first_name}!\n"
                    f"⚔️ Weapon used: {weapon['emoji']} {weapon['power']}",
                    parse_mode=ParseMode.HTML
                )
                
                try:
                    await context.bot.send_message(
                        chat_id=target.id,
                        text=f"🚨 <b>You were robbed!</b>\n\n"
                             f"{user.first_name} robbed ${amount} from you!",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
            else:
                await update.message.reply_text(f"❌ {target.first_name} has no money to rob!")
        else:
            await update.message.reply_text(
                f"❌ <b>Robbery Failed!</b>\n\n"
                f"You tried to rob {target.first_name} but failed!",
                parse_mode=ParseMode.HTML
            )
        
        new_rep = max(0, db_user.get('reputation', 100) - 2)
        await db.update_user(user.id, reputation=new_rep)
    
    async def kill_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kill a user"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Please reply to a user to kill them!")
            return
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to kill them!")
            return
        
        if target.id == user.id:
            await update.message.reply_text("❌ You can't kill yourself!")
            return
        
        db_user = await db.get_user(user.id)
        
        if db_user.get('is_dead', 0):
            await update.message.reply_text("💀 You are dead! Use /medical to revive.")
            return
        
        if db_user.get('kill_count', 0) >= MAX_KILL_PER_DAY:
            await update.message.reply_text("❌ You've used all your kills for today!")
            return
        
        target_user = await db.get_or_create_user(
            user_id=target.id,
            username=target.username,
            first_name=target.first_name,
            last_name=target.last_name
        )
        
        if target_user.get('is_dead', 0):
            await update.message.reply_text("💀 This user is already dead!")
            return
        
        weapon = WEAPONS.get(db_user.get('weapon', 'fist'), WEAPONS['fist'])
        success_chance = 0.2 + (weapon['power'] * 0.1)
        
        await db.update_user(user.id, kill_count=db_user.get('kill_count', 0) + 1)
        
        if random.random() < success_chance:
            await db.update_user(target.id, is_dead=1, death_time=datetime.now())
            
            kill_reward = 100
            await db.add_money(user.id, kill_reward)
            
            # Insurance payouts
            async with db.conn.execute(
                "SELECT * FROM insurance WHERE insured_id = ?",
                (target.id,)
            ) as cursor:
                insurances = await cursor.fetchall()
            
            insurance_payout = 0
            for insurance in insurances:
                insurer_id = insurance['insurer_id']
                amount = insurance['amount']
                await db.add_money(insurer_id, amount)
                insurance_payout += amount
                
                try:
                    await context.bot.send_message(
                        chat_id=insurer_id,
                        text=f"💰 <b>Insurance Payout!</b>\n\n"
                             f"Your insured user {target.first_name} was killed!\n"
                             f"💵 You received ${amount} insurance payout!",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
            
            payout_text = f"\n💰 Insurance payouts: ${insurance_payout}" if insurance_payout > 0 else ""
            
            await update.message.reply_text(
                f"⚔️ <b>Kill Successful!</b>\n\n"
                f"💀 You killed {target.first_name}!\n"
                f"💰 Reward: ${kill_reward}{payout_text}",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"❌ <b>Kill Failed!</b>\n\n"
                f"You tried to kill {target.first_name} but failed!",
                parse_mode=ParseMode.HTML
            )
        
        new_rep = max(0, db_user.get('reputation', 100) - 5)
        await db.update_user(user.id, reputation=new_rep)
    
    async def insurance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Apply for insurance"""
        user = update.effective_user
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        
        if target:
            # Apply for insurance on target
            if target.id == user.id:
                await update.message.reply_text("❌ You can't insure yourself!")
                return
            
            premium = 500  # Base premium
            amount = 2000  # Payout amount
            
            if not await db.remove_money(user.id, premium):
                await update.message.reply_text("❌ You don't have enough money for the premium!")
                return
            
            await db.conn.execute(
                "INSERT OR REPLACE INTO insurance (insurer_id, insured_id, amount, premium) VALUES (?, ?, ?, ?)",
                (user.id, target.id, amount, premium)
            )
            await db.conn.commit()
            
            await update.message.reply_text(
                f"💰 <b>Insurance Applied!</b>\n\n"
                f"👤 Insured: {target.first_name}\n"
                f"💵 Premium: ${premium}\n"
                f"💰 Payout: ${amount}",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Show current insurances
        async with db.conn.execute(
            """SELECT i.*, u.first_name FROM insurance i
               JOIN users u ON i.insured_id = u.user_id
               WHERE i.insurer_id = ?""",
            (user.id,)
        ) as cursor:
            insurances = await cursor.fetchall()
        
        text = f"💰 <b>{user.first_name}'s Insurance</b>\n\n"
        
        if insurances:
            text += "<b>Your Insurances:</b>\n"
            for insurance in insurances:
                text += f"👤 {insurance['first_name']}: ${insurance['amount']} (Premium: ${insurance['premium']})\n"
        else:
            text += "🌱 You have no active insurances.\n"
        
        text += "\n💡 Reply to a user to insure them!"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def pay_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Pay a user"""
        user = update.effective_user
        
        if len(context.args) < 1:
            await update.message.reply_text("Usage: <code>/pay [amount]</code> (reply to user)")
            return
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to pay them!")
            return
        
        amount_str = context.args[0]
        try:
            if '+' in amount_str:
                parts = amount_str.split('+')
                amount = sum(int(p.strip()) for p in parts)
            else:
                amount = int(amount_str)
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return
        
        if amount <= 0:
            await update.message.reply_text("❌ Amount must be positive!")
            return
        
        if await db.transfer_money(user.id, target.id, amount):
            await update.message.reply_text(
                f"💰 <b>Payment Sent!</b>\n\n"
                f"You paid ${amount} to {target.first_name}!",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text("❌ You don't have enough money!")
    
    async def reputation_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show reputation"""
        user = update.effective_user
        db_user = await db.get_user(user.id)
        
        reputation = db_user.get('reputation', 100)
        
        if reputation >= 150:
            level = "🌟 Legendary"
        elif reputation >= 120:
            level = "⭐ Excellent"
        elif reputation >= 80:
            level = "😊 Good"
        elif reputation >= 50:
            level = "😐 Average"
        else:
            level = "😈 Notorious"
        
        text = f"""⭐ <b>{user.first_name}'s Reputation</b>

📊 Score: {reputation}/200
🏆 Level: {level}

💡 Reputation increases by:
   • Fertilizing gardens (+1)
   • Marrying/Adopting (+2)
   
💡 Reputation decreases by:
   • Robbing (-2)
   • Killing (-5)"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def skills_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show skills"""
        user = update.effective_user
        db_user = await db.get_user(user.id)
        
        text = f"""🌟 <b>{user.first_name}'s Skills</b>

🌾 <b>Fertilize Skill:</b> Level {db_user.get('skills_fertilize', 0)}
   💰 Bonus: +${db_user.get('skills_fertilize', 0) * 5} per fertilize

🌱 <b>Total Crops Grown:</b> {db_user.get('total_crops_grown', 0)}

💡 Fertilize more gardens to level up!"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def donateblood_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Donate blood to revive someone"""
        user = update.effective_user
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        
        if not target:
            await update.message.reply_text("❌ Please reply to a dead user to revive them!")
            return
        
        target_user = await db.get_user(target.id)
        if not target_user.get('is_dead', 0):
            await update.message.reply_text("❌ This user is not dead!")
            return
        
        await db.update_user(target.id, is_dead=0, death_time=None)
        
        await update.message.reply_text(
            f"🩸 <b>Blood Donated!</b>\n\n"
            f"You revived {target.first_name}!\n"
            f"❤️ They are now alive!",
            parse_mode=ParseMode.HTML
        )
    
    async def medical_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Use medical services to revive"""
        user = update.effective_user
        
        db_user = await db.get_user(user.id)
        
        if not db_user.get('is_dead', 0):
            await update.message.reply_text("❌ You are not dead!")
            return
        
        cost = 500
        
        if await db.remove_money(user.id, cost):
            await db.update_user(user.id, is_dead=0, death_time=None)
            await update.message.reply_text(
                f"🏥 <b>Medical Treatment!</b>\n\n"
                f"💰 Cost: ${cost}\n"
                f"❤️ You are now revived!",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text("❌ You need $500 for medical treatment!")
