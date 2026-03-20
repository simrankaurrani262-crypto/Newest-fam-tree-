"""
Garden Handler
==============
Handles garden-related commands
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import datetime, timedelta
import io
from PIL import Image, ImageDraw

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from config.config import CROPS, RECIPES, FERTILIZE_REWARD, FERTILIZE_TIME_REDUCTION

class GardenHandler:
    
    def get_season(self):
        """Get current season"""
        hour = datetime.now().hour
        if 0 <= hour < 6:
            return "spring", "🌱"
        elif 6 <= hour < 12:
            return "autumn", "🍂"
        elif 12 <= hour < 18:
            return "cloudy", "🌧"
        else:
            return "winter", "❄️"
    
    async def garden_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show garden"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        garden = await db.get_or_create_garden(user.id, chat.id)
        barn = await db.get_barn(user.id)
        seeds = await db.get_seeds(user.id)
        season_emoji, season = self.get_season()
        
        text = f"🏡 <b>{user.first_name}'s Garden</b> {season_emoji}\n\n"
        text += f"📊 Slots: {len(garden['crops'])}/{garden['slots']}\n"
        text += f"🌱 Season: {season.title()}\n\n"
        
        if garden['crops']:
            text += "🌾 <b>Growing Crops:</b>\n"
            for crop in garden['crops']:
                crop_type = crop['crop_type']
                emoji = CROPS.get(crop_type, {}).get('emoji', '🌱')
                ready_at = datetime.fromisoformat(str(crop['ready_at']))
                now = datetime.now()
                
                if ready_at <= now:
                    text += f"  {emoji} {crop_type.title()}: ✅ Ready!\n"
                else:
                    time_left = ready_at - now
                    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
                    minutes = remainder // 60
                    text += f"  {emoji} {crop_type.title()}: {hours}h {minutes}m\n"
        else:
            text += "🌱 Your garden is empty!\n"
        
        text += "\n"
        
        if barn:
            text += "📦 <b>Barn:</b>\n"
            for crop_type, quantity in list(barn.items())[:5]:
                emoji = CROPS.get(crop_type, {}).get('emoji', '🌱')
                text += f"  {emoji} {crop_type.title()}: {quantity}\n"
        
        keyboard = [
            [InlineKeyboardButton("🌱 Plant", callback_data=f'plant_menu_{user.id}'),
             InlineKeyboardButton("🌾 Harvest", callback_data=f'harvest_{user.id}')],
            [InlineKeyboardButton("📦 Barn", callback_data=f'barn_{user.id}'),
             InlineKeyboardButton("🛒 Stands", callback_data=f'stands_{user.id}')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    
    async def plant_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Plant crops"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage:\n"
                "<code>/plant [amount] [crop]</code>\n"
                "<code>/plant * [crop]</code> - Plant all available\n\n"
                "Example: <code>/plant 5 corn</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        amount_str = context.args[0]
        crop_type = context.args[1].lower()
        
        if crop_type not in CROPS:
            await update.message.reply_text(f"❌ Invalid crop! Available: {', '.join(CROPS.keys())}")
            return
        
        garden = await db.get_or_create_garden(user.id, chat.id)
        available_slots = garden['slots'] - len(garden['crops'])
        
        if available_slots <= 0:
            await update.message.reply_text("❌ Your garden is full! Harvest some crops first.")
            return
        
        seeds = await db.get_seeds(user.id)
        available_seeds = seeds.get(crop_type, 0)
        
        if amount_str == '*':
            amount = min(available_seeds, available_slots)
        else:
            try:
                amount = int(amount_str)
            except ValueError:
                await update.message.reply_text("❌ Invalid amount!")
                return
        
        if amount <= 0:
            await update.message.reply_text("❌ Amount must be greater than 0!")
            return
        
        if amount > available_seeds:
            await update.message.reply_text(f"❌ You don't have enough {crop_type} seeds! Available: {available_seeds}")
            return
        
        if amount > available_slots:
            await update.message.reply_text(f"❌ Not enough space! Available slots: {available_slots}")
            return
        
        # Plant crops
        grow_time = CROPS[crop_type]['grow_time']
        season, _ = self.get_season()
        if CROPS[crop_type].get('season') == season:
            grow_time = grow_time // 2
        
        ready_at = datetime.now() + timedelta(seconds=grow_time)
        
        for _ in range(amount):
            await db.plant_crop(garden['id'], crop_type, ready_at)
        
        await db.remove_seeds(user.id, crop_type, amount)
        
        emoji = CROPS[crop_type]['emoji']
        boost_text = " (2x speed - season bonus!)" if CROPS[crop_type].get('season') == season else ""
        
        await update.message.reply_text(
            f"🌱 <b>Planted!</b>\n\n"
            f"{emoji} Planted {amount} {crop_type}{boost_text}\n"
            f"⏱ Will be ready in {grow_time // 3600}h {(grow_time % 3600) // 60}m",
            parse_mode=ParseMode.HTML
        )
    
    async def harvest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Harvest all ready crops"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        garden = await db.get_or_create_garden(user.id, chat.id)
        
        if not garden['crops']:
            await update.message.reply_text("❌ Your garden is empty!")
            return
        
        harvested = {}
        total_harvested = 0
        
        for crop in garden['crops']:
            ready_at = datetime.fromisoformat(str(crop['ready_at']))
            if ready_at <= datetime.now():
                crop_type = crop['crop_type']
                harvested[crop_type] = harvested.get(crop_type, 0) + 1
                total_harvested += 1
                await db.add_to_barn(user.id, crop_type, 1)
                await db.conn.execute("DELETE FROM garden_crops WHERE id = ?", (crop['id'],))
        
        await db.conn.commit()
        
        if not harvested:
            await update.message.reply_text("❌ No crops are ready to harvest yet!")
            return
        
        db_user = await db.get_user(user.id)
        await db.update_user(user.id, total_crops_grown=db_user.get('total_crops_grown', 0) + total_harvested)
        
        text = f"🌾 <b>Harvested!</b>\n\n"
        for crop_type, count in harvested.items():
            emoji = CROPS.get(crop_type, {}).get('emoji', '🌱')
            text += f"{emoji} {crop_type.title()}: {count}\n"
        
        text += f"\n📦 Total: {total_harvested} crops added to barn!"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def barn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show barn contents"""
        user = update.effective_user
        
        barn = await db.get_barn(user.id)
        seeds = await db.get_seeds(user.id)
        
        text = f"📦 <b>{user.first_name}'s Barn</b>\n\n"
        
        if barn:
            text += "🌾 <b>Crops:</b>\n"
            for crop_type, quantity in barn.items():
                emoji = CROPS.get(crop_type, {}).get('emoji', '🌱')
                text += f"  {emoji} {crop_type.title()}: {quantity}\n"
        else:
            text += "🌾 No crops in barn\n"
        
        text += "\n"
        
        if seeds:
            text += "🌱 <b>Seeds:</b>\n"
            for crop_type, quantity in seeds.items():
                emoji = CROPS.get(crop_type, {}).get('emoji', '🌱')
                text += f"  {emoji} {crop_type.title()}: {quantity}\n"
        else:
            text += "🌱 No seeds\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Buy seeds"""
        user = update.effective_user
        
        if len(context.args) < 2:
            text = "💰 <b>Seed Prices</b>\n\n"
            for crop_type, data in CROPS.items():
                text += f"{data['emoji']} {crop_type.title()}: ${data['buy_price']}\n"
            
            text += "\nUsage: <code>/add [amount] [crop]</code>\n"
            text += "Example: <code>/add 10 corn</code>"
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            return
        
        try:
            amount = int(context.args[0])
            crop_type = context.args[1].lower()
        except (ValueError, IndexError):
            await update.message.reply_text("❌ Invalid arguments!\nUsage: <code>/add [amount] [crop]</code>")
            return
        
        if crop_type not in CROPS:
            await update.message.reply_text(f"❌ Invalid crop! Available: {', '.join(CROPS.keys())}")
            return
        
        cost = CROPS[crop_type]['buy_price'] * amount
        
        if not await db.remove_money(user.id, cost):
            await update.message.reply_text("❌ You don't have enough money!")
            return
        
        await db.add_seeds(user.id, crop_type, amount)
        
        emoji = CROPS[crop_type]['emoji']
        await update.message.reply_text(
            f"✅ <b>Purchased!</b>\n\n"
            f"{emoji} {amount} {crop_type} seeds\n"
            f"💰 Cost: ${cost}",
            parse_mode=ParseMode.HTML
        )
    
    async def sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sell crops"""
        user = update.effective_user
        
        if len(context.args) < 2:
            text = "💰 <b>Crop Prices</b>\n\n"
            for crop_type, data in CROPS.items():
                text += f"{data['emoji']} {crop_type.title()}: ${data['sell_price']}\n"
            
            text += "\nUsage: <code>/sell [amount] [crop]</code>\n"
            text += "Example: <code>/sell 10 corn</code>"
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            return
        
        try:
            amount = int(context.args[0])
            crop_type = context.args[1].lower()
        except (ValueError, IndexError):
            await update.message.reply_text("❌ Invalid arguments!\nUsage: <code>/sell [amount] [crop]</code>")
            return
        
        if crop_type not in CROPS:
            await update.message.reply_text(f"❌ Invalid crop! Available: {', '.join(CROPS.keys())}")
            return
        
        if not await db.remove_from_barn(user.id, crop_type, amount):
            await update.message.reply_text("❌ You don't have enough crops!")
            return
        
        earnings = CROPS[crop_type]['sell_price'] * amount
        await db.add_money(user.id, earnings)
        
        emoji = CROPS[crop_type]['emoji']
        await update.message.reply_text(
            f"💰 <b>Sold!</b>\n\n"
            f"{emoji} {amount} {crop_type}\n"
            f"💵 Earnings: ${earnings}",
            parse_mode=ParseMode.HTML
        )
    
    async def fertilise_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Fertilize someone's garden"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Please reply to a user to fertilize their garden!")
            return
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to fertilize their garden!")
            return
        
        if target.id == user.id:
            await update.message.reply_text("❌ You can't fertilize your own garden!")
            return
        
        # Check cooldown
        async with db.conn.execute(
            "SELECT last_fertilize FROM fertilize_cooldowns WHERE user_id = ?",
            (user.id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row and row['last_fertilize']:
                last = datetime.fromisoformat(str(row['last_fertilize']))
                if datetime.now() - last < timedelta(seconds=600):
                    time_left = 600 - (datetime.now() - last).total_seconds()
                    await update.message.reply_text(f"⏱ Fertilize cooldown: {int(time_left // 60)}m {int(time_left % 60)}s")
                    return
        
        garden = await db.get_or_create_garden(target.id, chat.id)
        
        if not garden['crops']:
            await update.message.reply_text(f"❌ {target.first_name}'s garden is empty!")
            return
        
        fertilized = 0
        for crop in garden['crops']:
            ready_at = datetime.fromisoformat(str(crop['ready_at']))
            if ready_at > datetime.now():
                fertilized += 1
        
        if fertilized == 0:
            await update.message.reply_text("❌ No crops need fertilizing!")
            return
        
        # Update cooldown
        await db.conn.execute(
            """INSERT INTO fertilize_cooldowns (user_id, last_fertilize) VALUES (?, ?)
               ON CONFLICT(user_id) DO UPDATE SET last_fertilize = ?""",
            (user.id, datetime.now(), datetime.now())
        )
        await db.conn.commit()
        
        # Give reward
        db_user = await db.get_user(user.id)
        reward = FERTILIZE_REWARD + db_user.get('skills_fertilize', 0) * 5
        await db.add_money(user.id, reward)
        await db.update_user(user.id, skills_fertilize=db_user.get('skills_fertilize', 0) + 1)
        
        await update.message.reply_text(
            f"🌱 <b>Garden Fertilized!</b>\n\n"
            f"You fertilized {fertilized} crops in {target.first_name}'s garden!\n"
            f"💰 Reward: ${reward}",
            parse_mode=ParseMode.HTML
        )
    
    async def gardens_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show active gardens in group"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        async with db.conn.execute(
            """SELECT g.*, u.first_name, u.username FROM gardens g
               JOIN users u ON g.user_id = u.user_id
               WHERE g.chat_id = ?""",
            (chat.id,)
        ) as cursor:
            rows = await cursor.fetchall()
        
        if not rows:
            await update.message.reply_text("🌱 No active gardens in this group!")
            return
        
        text = "🏡 <b>Active Gardens</b>\n\n"
        for row in rows:
            async with db.conn.execute(
                "SELECT COUNT(*) FROM garden_crops WHERE garden_id = ?",
                (row['id'],)
            ) as cursor2:
                crop_count = (await cursor2.fetchone())[0]
            
            text += f"🌱 {row['first_name']}: {crop_count}/{row['slots']} crops\n"
        
        text += "\n💡 Reply to a user with /fertilise to speed up their garden!"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def stands_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show global marketplace"""
        async with db.conn.execute(
            """SELECT s.*, u.first_name, u.username FROM stands s
               JOIN users u ON s.user_id = u.user_id
               ORDER BY s.price ASC LIMIT 20"""
        ) as cursor:
            rows = await cursor.fetchall()
        
        if not rows:
            await update.message.reply_text("🛒 No items in the marketplace!")
            return
        
        text = "🛒 <b>Global Marketplace</b>\n\n"
        
        crops_for_sale = {}
        for row in rows:
            crop_type = row['crop_type']
            if crop_type not in crops_for_sale:
                crops_for_sale[crop_type] = []
            crops_for_sale[crop_type].append({
                'seller': row['first_name'],
                'quantity': row['quantity'],
                'price': row['price'],
                'price_per': row['price'] // row['quantity']
            })
        
        for crop_type, listings in list(crops_for_sale.items())[:10]:
            emoji = CROPS.get(crop_type, {}).get('emoji', '🌱')
            cheapest = min(listings, key=lambda x: x['price_per'])
            text += f"{emoji} {crop_type.title()}: ${cheapest['price_per']}/unit ({len(listings)} sellers)\n"
        
        text += "\n💡 Use <code>/putstand [crop] [amount] [price]</code> to sell your crops!"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def putstand_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Put crops on stand"""
        user = update.effective_user
        
        if len(context.args) < 3:
            await update.message.reply_text(
                "Usage:\n"
                "<code>/putstand [crop] [amount] [price]</code>\n\n"
                "Example: <code>/putstand corn 10 200</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        crop_type = context.args[0].lower()
        try:
            amount = int(context.args[1])
            price = int(context.args[2])
        except ValueError:
            await update.message.reply_text("❌ Invalid amount or price!")
            return
        
        if crop_type not in CROPS:
            await update.message.reply_text(f"❌ Invalid crop! Available: {', '.join(CROPS.keys())}")
            return
        
        if not await db.remove_from_barn(user.id, crop_type, amount):
            await update.message.reply_text(f"❌ You don't have enough {crop_type}!")
            return
        
        max_price = CROPS[crop_type]['sell_price'] * amount * 3
        if price > max_price:
            await update.message.reply_text(f"❌ Price too high! Max: ${max_price}")
            return
        
        await db.conn.execute(
            "INSERT INTO stands (user_id, crop_type, quantity, price) VALUES (?, ?, ?, ?)",
            (user.id, crop_type, amount, price)
        )
        await db.conn.commit()
        
        emoji = CROPS[crop_type]['emoji']
        await update.message.reply_text(
            f"✅ <b>Listed on Marketplace!</b>\n\n"
            f"{emoji} {amount} {crop_type}\n"
            f"💰 Price: ${price}",
            parse_mode=ParseMode.HTML
        )
    
    async def stand_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View your stand or someone's stand"""
        user = update.effective_user
        
        target = user
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        
        async with db.conn.execute(
            "SELECT * FROM stands WHERE user_id = ?",
            (target.id,)
        ) as cursor:
            rows = await cursor.fetchall()
        
        if not rows:
            await update.message.reply_text(f"🛒 {target.first_name} has no items on stand!")
            return
        
        text = f"🛒 <b>{target.first_name}'s Stand</b>\n\n"
        
        for row in rows:
            emoji = CROPS.get(row['crop_type'], {}).get('emoji', '🌱')
            text += f"{emoji} {row['crop_type'].title()}: {row['quantity']} units - ${row['price']}\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def gift_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gift crops to someone"""
        user = update.effective_user
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage:\n"
                "<code>/gift [crop] [amount]</code> (reply to user)\n\n"
                "Example: <code>/gift corn 5</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to gift them crops!")
            return
        
        crop_type = context.args[0].lower()
        try:
            amount = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return
        
        if crop_type not in CROPS:
            await update.message.reply_text(f"❌ Invalid crop! Available: {', '.join(CROPS.keys())}")
            return
        
        if not await db.remove_from_barn(user.id, crop_type, amount):
            await update.message.reply_text(f"❌ You don't have enough {crop_type}!")
            return
        
        await db.add_to_barn(target.id, crop_type, amount)
        
        emoji = CROPS[crop_type]['emoji']
        await update.message.reply_text(
            f"🎁 <b>Gift Sent!</b>\n\n"
            f"{emoji} {amount} {crop_type} gifted to {target.first_name}!",
            parse_mode=ParseMode.HTML
        )
    
    async def cook_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cooking system"""
        user = update.effective_user
        
        if context.args:
            try:
                recipe_name = context.args[0].lower()
                quantity = int(context.args[1]) if len(context.args) > 1 else 1
            except (ValueError, IndexError):
                await update.message.reply_text("Usage: <code>/cook [recipe] [quantity]</code>")
                return
            
            if recipe_name not in RECIPES:
                await update.message.reply_text(f"❌ Invalid recipe! Available: {', '.join(RECIPES.keys())}")
                return
            
            recipe = RECIPES[recipe_name]
            
            for ingredient, needed in recipe['ingredients'].items():
                total_needed = needed * quantity
                if not await db.remove_from_barn(user.id, ingredient, total_needed):
                    await update.message.reply_text(f"❌ Not enough {ingredient}! Need: {total_needed}")
                    return
            
            await db.add_to_barn(user.id, recipe_name, quantity, 'recipe')
            
            emoji = recipe['emoji']
            await update.message.reply_text(
                f"🍳 <b>Cooked!</b>\n\n"
                f"{emoji} {quantity}x {recipe_name.title()}\n"
                f"⏱ Cooking time: {recipe['time']} seconds",
                parse_mode=ParseMode.HTML
            )
            return
        
        text = "🍳 <b>Cooking Menu</b>\n\n"
        text += "<b>Available Recipes:</b>\n\n"
        
        for recipe_name, recipe in RECIPES.items():
            emoji = recipe['emoji']
            ingredients = ", ".join([f"{v} {k}" for k, v in recipe['ingredients'].items()])
            text += f"{emoji} <b>{recipe_name.title()}</b>: {ingredients}\n"
        
        text += "\n💡 Use <code>/cook [recipe] [quantity]</code> to cook!"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def stove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View stove (same as cook)"""
        await self.cook_command(update, context)
