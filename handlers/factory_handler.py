"""
Factory Handler
===============
Handles factory/worker related commands
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db

class FactoryHandler:
    
    async def factory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show factory"""
        user = update.effective_user
        
        db_user = await db.get_user(user.id)
        
        async with db.conn.execute(
            """SELECT fw.*, u.first_name, u.username FROM factory_workers fw
               JOIN users u ON fw.worker_id = u.user_id
               WHERE fw.owner_id = ?""",
            (user.id,)
        ) as cursor:
            workers = await cursor.fetchall()
        
        async with db.conn.execute(
            """SELECT fw.*, u.first_name FROM factory_workers fw
               JOIN users u ON fw.owner_id = u.user_id
               WHERE fw.worker_id = ?""",
            (user.id,)
        ) as cursor:
            my_work = await cursor.fetchone()
        
        text = f"🏭 <b>{user.first_name}'s Factory</b>\n\n"
        
        text += f"📊 <b>Your Stats:</b>\n"
        text += f"💰 Money: ${db_user['money']:,}\n"
        text += f"⭐ Rating: {db_user.get('rating', 0)}\n"
        text += f"💵 Price: ${db_user.get('price', 100)}\n\n"
        
        if my_work:
            owner_name = my_work['first_name']
            is_working = my_work['is_working']
            work_status = "🔨 Working" if is_working else "😴 Idle"
            text += f"👔 <b>Employment:</b>\n"
            text += f"   Owner: {owner_name}\n"
            text += f"   Status: {work_status}\n\n"
        else:
            text += f"👔 <b>Employment:</b> Unemployed\n\n"
        
        if workers:
            text += f"👷 <b>Your Workers ({len(workers)}/5):</b>\n\n"
            for worker in workers:
                status = "🔨 Working" if worker['is_working'] else "😴 Idle"
                text += f"👤 {worker['first_name']}\n"
                text += f"   💵 Price: ${worker['price']} | ⭐ Rating: {worker['rating']}\n"
                text += f"   Status: {status}\n\n"
        else:
            text += f"👷 <b>Workers:</b> None\n"
            text += f"💡 Hire workers with <code>/hire @user</code>\n\n"
        
        keyboard = [
            [InlineKeyboardButton("👷 Hire Worker", callback_data=f'hire_{user.id}'),
             InlineKeyboardButton("🔥 Fire Worker", callback_data=f'fire_{user.id}')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    
    async def hire_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hire a worker"""
        user = update.effective_user
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Please reply to a user to hire them!")
            return
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to hire them!")
            return
        
        if target.id == user.id:
            await update.message.reply_text("❌ You can't hire yourself!")
            return
        
        async with db.conn.execute(
            "SELECT COUNT(*) FROM factory_workers WHERE owner_id = ?",
            (user.id,)
        ) as cursor:
            worker_count = (await cursor.fetchone())[0]
        
        if worker_count >= 5:
            await update.message.reply_text("❌ You already have 5 workers (maximum)!")
            return
        
        async with db.conn.execute(
            "SELECT * FROM factory_workers WHERE worker_id = ?",
            (target.id,)
        ) as cursor:
            existing = await cursor.fetchone()
        
        if existing:
            await update.message.reply_text("❌ This user is already hired by someone!")
            return
        
        target_user = await db.get_or_create_user(
            user_id=target.id,
            username=target.username,
            first_name=target.first_name,
            last_name=target.last_name
        )
        
        price = target_user.get('price', 100)
        
        db_user = await db.get_user(user.id)
        if db_user['money'] < price:
            await update.message.reply_text(f"❌ You need ${price} to hire this worker!")
            return
        
        await db.remove_money(user.id, price)
        await db.conn.execute(
            "INSERT INTO factory_workers (worker_id, owner_id, price) VALUES (?, ?, ?)",
            (target.id, user.id, price)
        )
        await db.conn.commit()
        
        await update.message.reply_text(
            f"✅ <b>Worker Hired!</b>\n\n"
            f"👤 {target.first_name} is now your worker!\n"
            f"💵 Price: ${price}",
            parse_mode=ParseMode.HTML
        )
    
    async def fire_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Fire a worker"""
        user = update.effective_user
        
        async with db.conn.execute(
            """SELECT fw.worker_id, u.first_name, fw.price FROM factory_workers fw
               JOIN users u ON fw.worker_id = u.user_id
               WHERE fw.owner_id = ?""",
            (user.id,)
        ) as cursor:
            workers = await cursor.fetchall()
        
        if not workers:
            await update.message.reply_text("❌ You have no workers to fire!")
            return
        
        keyboard = []
        for worker in workers:
            keyboard.append([InlineKeyboardButton(
                f"🔥 Fire {worker['first_name']} (+${worker['price']})",
                callback_data=f'fire_worker_{worker["worker_id"]}'
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔥 <b>Select worker to fire:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def handle_fire_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle fire callback"""
        query = update.callback_query
        data = query.data
        
        parts = data.split('_')
        if len(parts) < 3:
            return
        
        worker_id = int(parts[2])
        
        async with db.conn.execute(
            "SELECT price FROM factory_workers WHERE worker_id = ?",
            (worker_id,)
        ) as cursor:
            row = await cursor.fetchone()
        
        if row:
            price = row['price']
            user = update.effective_user
            
            await db.add_money(user.id, price)
            await db.conn.execute(
                "DELETE FROM factory_workers WHERE worker_id = ?",
                (worker_id,)
            )
            await db.conn.commit()
            
            await query.edit_message_text(f"🔥 Worker fired! You received ${price}.")
        
    async def work_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send workers to work"""
        user = update.effective_user
        
        async with db.conn.execute(
            """SELECT fw.*, u.first_name FROM factory_workers fw
               JOIN users u ON fw.worker_id = u.user_id
               WHERE fw.owner_id = ? AND fw.is_working = 0""",
            (user.id,)
        ) as cursor:
            idle_workers = await cursor.fetchall()
        
        if not idle_workers:
            await update.message.reply_text("❌ You have no idle workers!")
            return
        
        sent = 0
        for worker in idle_workers:
            await db.conn.execute(
                """UPDATE factory_workers 
                   SET is_working = 1, work_started_at = ?
                   WHERE worker_id = ?""",
                (datetime.now(), worker['worker_id'])
            )
            sent += 1
        
        await db.conn.commit()
        
        await update.message.reply_text(
            f"🔨 <b>Workers Sent!</b>\n\n"
            f"{sent} workers sent to work!\n"
            f"They'll complete work in 1 hour.",
            parse_mode=ParseMode.HTML
        )
