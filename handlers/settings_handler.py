"""
Settings Handler
================
Handles bot settings
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import json

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db

class SettingsHandler:
    
    async def toggle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle features"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        settings = await db.get_chat_settings(chat.id)
        
        keyboard = [
            [InlineKeyboardButton(
                f"🔫 Rob/Kill: {'✅' if settings['robkill_enabled'] else '❌'}", 
                callback_data=f'toggle_robkill_{chat.id}'
            )],
            [InlineKeyboardButton(
                f"🏡 Garden: {'✅' if settings['garden_enabled'] else '❌'}", 
                callback_data=f'toggle_garden_{chat.id}'
            )],
            [InlineKeyboardButton(
                f"🎮 Games: {'✅' if settings['games_enabled'] else '❌'}", 
                callback_data=f'toggle_games_{chat.id}'
            )],
            [InlineKeyboardButton(
                f"🔞 NSFW: {'✅' if settings['nsfw_enabled'] else '❌'}", 
                callback_data=f'toggle_nsfw_{chat.id}'
            )],
            [InlineKeyboardButton(
                f"🌳 Tree Mode: {settings['tree_mode'].upper()}", 
                callback_data=f'toggle_treemode_{chat.id}'
            )],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ <b>Bot Settings</b>\n\n"
            "Click to toggle features:",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def handle_toggle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle toggle callback"""
        query = update.callback_query
        data = query.data
        
        parts = data.split('_')
        if len(parts) < 3:
            return
        
        setting = parts[1]
        chat_id = int(parts[2])
        
        user = update.effective_user
        chat_member = await context.bot.get_chat_member(chat_id, user.id)
        
        if chat_member.status not in ['administrator', 'creator']:
            await query.answer("❌ Only admins can change settings!", show_alert=True)
            return
        
        settings = await db.get_chat_settings(chat_id)
        
        if setting == 'robkill':
            new_value = 0 if settings['robkill_enabled'] else 1
            await db.update_chat_settings(chat_id, robkill_enabled=new_value)
            status = "enabled" if new_value else "disabled"
            await query.edit_message_text(f"🔫 Rob/Kill {status}!")
        
        elif setting == 'garden':
            new_value = 0 if settings['garden_enabled'] else 1
            await db.update_chat_settings(chat_id, garden_enabled=new_value)
            status = "enabled" if new_value else "disabled"
            await query.edit_message_text(f"🏡 Garden {status}!")
        
        elif setting == 'games':
            new_value = 0 if settings['games_enabled'] else 1
            await db.update_chat_settings(chat_id, games_enabled=new_value)
            status = "enabled" if new_value else "disabled"
            await query.edit_message_text(f"🎮 Games {status}!")
        
        elif setting == 'nsfw':
            new_value = 0 if settings['nsfw_enabled'] else 1
            await db.update_chat_settings(chat_id, nsfw_enabled=new_value)
            status = "enabled" if new_value else "disabled"
            await query.edit_message_text(f"🔞 NSFW {status}!")
        
        elif setting == 'treemode':
            new_mode = 'global' if settings['tree_mode'] == 'local' else 'local'
            await db.update_chat_settings(chat_id, tree_mode=new_mode)
            await query.edit_message_text(f"🌳 Tree mode set to {new_mode.upper()}!")
    
    async def disable_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Disable a command"""
        chat = update.effective_chat
        user = update.effective_user
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        chat_member = await chat.get_member(user.id)
        if chat_member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can disable commands!")
            return
        
        if len(context.args) < 1:
            await update.message.reply_text("Usage: <code>/disable [command]</code>")
            return
        
        command = context.args[0].lower().lstrip('/')
        
        settings = await db.get_chat_settings(chat.id)
        disabled = json.loads(settings.get('disabled_commands', '[]'))
        
        if command not in disabled:
            disabled.append(command)
            await db.update_chat_settings(chat.id, disabled_commands=json.dumps(disabled))
        
        await update.message.reply_text(f"✅ Command <code>/{command}</code> disabled!", parse_mode=ParseMode.HTML)
    
    async def enable_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enable a command"""
        chat = update.effective_chat
        user = update.effective_user
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        chat_member = await chat.get_member(user.id)
        if chat_member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can enable commands!")
            return
        
        if len(context.args) < 1:
            await update.message.reply_text("Usage: <code>/enable [command]</code>")
            return
        
        command = context.args[0].lower().lstrip('/')
        
        settings = await db.get_chat_settings(chat.id)
        disabled = json.loads(settings.get('disabled_commands', '[]'))
        
        if command in disabled:
            disabled.remove(command)
            await db.update_chat_settings(chat.id, disabled_commands=json.dumps(disabled))
        
        await update.message.reply_text(f"✅ Command <code>/{command}</code> enabled!", parse_mode=ParseMode.HTML)
    
    async def disabled_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show disabled commands"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        settings = await db.get_chat_settings(chat.id)
        disabled = json.loads(settings.get('disabled_commands', '[]'))
        
        if not disabled:
            await update.message.reply_text("✅ No commands are disabled!")
            return
        
        text = "🚫 <b>Disabled Commands</b>\n\n"
        for cmd in disabled:
            text += f"• /{cmd}\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def incests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle incest"""
        chat = update.effective_chat
        user = update.effective_user
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        chat_member = await chat.get_member(user.id)
        if chat_member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can change this setting!")
            return
        
        settings = await db.get_chat_settings(chat.id)
        new_value = 0 if settings.get('incest_enabled', 0) else 1
        
        await db.update_chat_settings(chat.id, incest_enabled=new_value)
        
        status = "enabled" if new_value else "disabled"
        await update.message.reply_text(f"🌳 Incest {status}!")
    
    async def gifs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle rob/kill GIFs"""
        await update.message.reply_text(
            "🎭 <b>GIF Settings</b>\n\n"
            "Rob/Kill GIFs are currently enabled!\n\n"
            "💡 Use /addgif to add custom GIFs!"
        )
    
    async def autoprune_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle auto delete"""
        chat = update.effective_chat
        user = update.effective_user
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        chat_member = await chat.get_member(user.id)
        if chat_member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can change this setting!")
            return
        
        settings = await db.get_chat_settings(chat.id)
        new_value = 0 if settings.get('auto_prune', 1) else 1
        
        await db.update_chat_settings(chat.id, auto_prune=new_value)
        
        status = "enabled" if new_value else "disabled"
        await update.message.reply_text(f"🗑 Auto-prune {status}!")
    
    async def prune_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manually prune messages"""
        chat = update.effective_chat
        user = update.effective_user
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        chat_member = await chat.get_member(user.id)
        if chat_member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can prune messages!")
            return
        
        await update.message.reply_text("🗑 <b>Pruning messages...</b>")
