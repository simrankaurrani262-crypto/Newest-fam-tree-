"""
Family Handler
==============
Handles all family-related commands
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
import io
import numpy as np
import json
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from config.config import MAX_PARTNERS, MAX_CHILDREN, MAX_FRIENDS

class FamilyHandler:
    
    async def tree_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show family tree"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        # Get target user
        target_user = user
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("Reply to a user or use /tree to see your own tree!")
            return
        
        await db.get_or_create_user(
            user_id=target_user.id,
            username=target_user.username,
            first_name=target_user.first_name,
            last_name=target_user.last_name
        )
        
        family = await db.get_family_tree(target_user.id, chat.id)
        
        # Generate tree image
        try:
            tree_image = await self.generate_tree_image(target_user, family)
            
            caption = f"🌳 <b>{target_user.first_name}'s Family Tree</b>\n\n"
            
            if family['partners']:
                caption += f"💍 Partners: {len(family['partners'])}\n"
            if family['children']:
                caption += f"👶 Children: {len(family['children'])}\n"
            if family['parents']:
                caption += f"👨‍👩‍👧 Parents: {len(family['parents'])}\n"
            
            if not any([family['partners'], family['children'], family['parents']]):
                caption += "🌱 Your tree is just you!\n"
                caption += "Use /adopt or /marry to grow your family!"
            
            keyboard = [
                [InlineKeyboardButton("👨‍👩‍👧 Relations", callback_data=f'relations_{target_user.id}'),
                 InlineKeyboardButton("🌐 Friends", callback_data=f'friends_{target_user.id}')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_photo(
                photo=tree_image,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        except Exception as e:
            # Fallback to text if image generation fails
            text = f"🌳 <b>{target_user.first_name}'s Family Tree</b>\n\n"
            
            if family['parents']:
                text += "<b>Parents:</b>\n"
                for p in family['parents']:
                    text += f"  • {p['first_name']}\n"
            
            if family['partners']:
                text += "<b>Partners:</b>\n"
                for p in family['partners']:
                    text += f"  • {p['first_name']}\n"
            
            if family['children']:
                text += "<b>Children:</b>\n"
                for c in family['children']:
                    text += f"  • {c['first_name']}\n"
            
            if not any([family['parents'], family['partners'], family['children']]):
                text += "🌱 Your tree is just you!\nUse /adopt or /marry to grow your family!"
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def generate_tree_image(self, user, family):
        """Generate family tree visualization"""
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        fig.patch.set_facecolor('#f0f8ff')
        ax.set_facecolor('#f0f8ff')
        
        # Title
        ax.text(7, 9.5, f"{user.first_name}'s Family Tree", 
                ha='center', va='center', fontsize=22, fontweight='bold', color='#2c3e50')
        
        # Center user
        self._draw_person(ax, 7, 5, user.first_name, user.username, '#3498db', True)
        
        # Draw partners (horizontal)
        partner_count = len(family['partners'])
        if partner_count > 0:
            start_x = 7 - (partner_count * 1.5) / 2
            for i, partner in enumerate(family['partners']):
                x = start_x + i * 1.5
                self._draw_person(ax, x, 5, partner['first_name'], partner['username'], '#e91e63')
                ax.plot([x + 0.5, 6.5], [5, 5], 'r-', linewidth=3, alpha=0.6)
        
        # Draw parents (top)
        parent_count = len(family['parents'])
        if parent_count > 0:
            start_x = 7 - (parent_count * 1.5) / 2
            for i, parent in enumerate(family['parents']):
                x = start_x + i * 1.5
                self._draw_person(ax, x, 7.5, parent['first_name'], parent['username'], '#9b59b6')
                ax.plot([x, 7], [7, 5.5], '#9b59b6', linewidth=2, alpha=0.5)
        
        # Draw children (bottom)
        child_count = len(family['children'])
        if child_count > 0:
            start_x = 7 - (child_count * 1.5) / 2
            for i, child in enumerate(family['children']):
                x = start_x + i * 1.5
                self._draw_person(ax, x, 2.5, child['first_name'], child['username'], '#2ecc71')
                ax.plot([7, x], [4.5, 3], '#2ecc71', linewidth=2, alpha=0.5)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                   facecolor='#f0f8ff', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return buf
    
    def _draw_person(self, ax, x, y, name, username, color, is_main=False):
        """Draw a person node"""
        size = 0.7 if is_main else 0.6
        circle = Circle((x, y), size, facecolor=color, edgecolor='white', linewidth=3, zorder=3)
        ax.add_patch(circle)
        
        display_name = name[:10] + '...' if len(name) > 10 else name
        ax.text(x, y + 0.05, display_name, ha='center', va='center', 
               fontsize=9 if is_main else 8, fontweight='bold', color='white', zorder=4)
        
        if username:
            ax.text(x, y - 0.9, f"@{username[:12]}", ha='center', va='center', 
                   fontsize=7, color='#555', zorder=4)
    
    async def adopt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Adopt a user"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Please reply to a user to adopt them!")
            return
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to adopt them!")
            return
        
        if target.id == user.id:
            await update.message.reply_text("❌ You can't adopt yourself!")
            return
        
        # Check if already related
        family = await db.get_family_tree(user.id, chat.id)
        children_ids = [c['related_user_id'] for c in family['children']]
        
        if target.id in children_ids:
            await update.message.reply_text("❌ This user is already your child!")
            return
        
        if len(family['children']) >= MAX_CHILDREN:
            await update.message.reply_text(f"❌ You already have maximum children ({MAX_CHILDREN})!")
            return
        
        await db.create_proposal(user.id, target.id, 'adopt', chat.id)
        
        keyboard = [
            [InlineKeyboardButton("✅ Yes", callback_data=f'accept_adopt_{user.id}'),
             InlineKeyboardButton("❌ No", callback_data=f'reject_adopt_{user.id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🌳 <b>Adoption Request</b>\n\n"
            f"{user.first_name} wants to adopt {target.first_name}!\n\n"
            f"{target.first_name}, do you accept?",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def marry_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Marry a user"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Please reply to a user to marry them!")
            return
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to marry them!")
            return
        
        if target.id == user.id:
            await update.message.reply_text("❌ You can't marry yourself!")
            return
        
        family = await db.get_family_tree(user.id, chat.id)
        partners_ids = [p['related_user_id'] for p in family['partners']]
        
        if target.id in partners_ids:
            await update.message.reply_text("❌ You are already married to this user!")
            return
        
        if len(family['partners']) >= MAX_PARTNERS:
            await update.message.reply_text(f"❌ You already have maximum partners ({MAX_PARTNERS})!")
            return
        
        await db.create_proposal(user.id, target.id, 'marry', chat.id)
        
        keyboard = [
            [InlineKeyboardButton("💍 Yes, I do!", callback_data=f'accept_marry_{user.id}'),
             InlineKeyboardButton("❌ No", callback_data=f'reject_marry_{user.id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"💍 <b>Marriage Proposal</b>\n\n"
            f"{user.first_name} wants to marry {target.first_name}!\n\n"
            f"{target.first_name}, do you accept?",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def accept_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Accept a proposal"""
        user = update.effective_user
        chat = update.effective_chat
        
        proposals = await db.get_pending_proposals(user.id)
        
        if not proposals:
            await update.message.reply_text("❌ You have no pending proposals!")
            return
        
        proposal = proposals[-1]
        
        if proposal['proposal_type'] == 'adopt':
            await db.add_family_relation(proposal['from_user_id'], user.id, 'child', chat.id)
            await db.add_family_relation(user.id, proposal['from_user_id'], 'parent', chat.id)
            
            await update.message.reply_text(
                f"🎉 <b>Adoption Complete!</b>\n\n"
                f"{user.first_name} is now the child of {proposal['from_name']}!",
                parse_mode=ParseMode.HTML
            )
        
        elif proposal['proposal_type'] == 'marry':
            await db.add_family_relation(proposal['from_user_id'], user.id, 'partner', chat.id)
            await db.add_family_relation(user.id, proposal['from_user_id'], 'partner', chat.id)
            
            await update.message.reply_text(
                f"💒 <b>Wedding Bells!</b> 💒\n\n"
                f"💍 {proposal['from_name']} and {user.first_name} are now married! 💍\n\n"
                f"🎊 Congratulations! 🎊",
                parse_mode=ParseMode.HTML
            )
        
        elif proposal['proposal_type'] == 'friend':
            await db.add_friend(proposal['from_user_id'], user.id)
            await db.add_money(user.id, 3000)
            await db.add_money(proposal['from_user_id'], 3000)
            
            await update.message.reply_text(
                f"🤝 <b>Friendship Made!</b>\n\n"
                f"{user.first_name} and {proposal['from_name']} are now friends!\n"
                f"💰 Both received $3,000!",
                parse_mode=ParseMode.HTML
            )
        
        await db.delete_proposal(proposal['id'])
    
    async def reject_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reject a proposal"""
        user = update.effective_user
        
        proposals = await db.get_pending_proposals(user.id)
        
        if not proposals:
            await update.message.reply_text("❌ You have no pending proposals!")
            return
        
        proposal = proposals[-1]
        await db.delete_proposal(proposal['id'])
        
        await update.message.reply_text("❌ Proposal rejected!")
    
    async def handle_accept_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle accept callback"""
        query = update.callback_query
        data = query.data
        
        parts = data.split('_')
        if len(parts) < 3:
            return
        
        action = parts[1]
        from_user_id = int(parts[2])
        user = update.effective_user
        chat = update.effective_chat
        
        async with db.conn.execute(
            "SELECT * FROM pending_proposals WHERE from_user_id = ? AND to_user_id = ?",
            (from_user_id, user.id)
        ) as cursor:
            row = await cursor.fetchone()
        
        if not row:
            await query.edit_message_text("❌ Proposal expired!")
            return
        
        proposal = dict(row)
        
        if proposal['proposal_type'] == 'adopt':
            await db.add_family_relation(from_user_id, user.id, 'child', chat.id)
            await db.add_family_relation(user.id, from_user_id, 'parent', chat.id)
            
            await query.edit_message_text(
                f"🎉 <b>Adoption Complete!</b>\n\n"
                f"{user.first_name} is now the child of the adopter!",
                parse_mode=ParseMode.HTML
            )
        
        elif proposal['proposal_type'] == 'marry':
            await db.add_family_relation(from_user_id, user.id, 'partner', chat.id)
            await db.add_family_relation(user.id, from_user_id, 'partner', chat.id)
            
            await query.edit_message_text(
                f"💒 <b>Wedding Bells!</b> 💒\n\n"
                f"💍 The couple is now married! 💍\n\n"
                f"🎊 Congratulations! 🎊",
                parse_mode=ParseMode.HTML
            )
        
        elif proposal['proposal_type'] == 'friend':
            await db.add_friend(from_user_id, user.id)
            await db.add_money(user.id, 3000)
            await db.add_money(from_user_id, 3000)
            
            await query.edit_message_text(
                f"🤝 <b>Friendship Made!</b>\n\n"
                f"You are now friends!\n"
                f"💰 Both received $3,000!",
                parse_mode=ParseMode.HTML
            )
        
        await db.delete_proposal(proposal['id'])
    
    async def handle_reject_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle reject callback"""
        query = update.callback_query
        data = query.data
        
        parts = data.split('_')
        if len(parts) < 3:
            return
        
        from_user_id = int(parts[2])
        user = update.effective_user
        
        async with db.conn.execute(
            "SELECT * FROM pending_proposals WHERE from_user_id = ? AND to_user_id = ?",
            (from_user_id, user.id)
        ) as cursor:
            row = await cursor.fetchone()
        
        if row:
            await db.delete_proposal(row['id'])
        
        await query.edit_message_text("❌ Proposal rejected!")
    
    async def divorce_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Divorce a partner"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        family = await db.get_family_tree(user.id, chat.id)
        
        if not family['partners']:
            await update.message.reply_text("❌ You have no partners to divorce!")
            return
        
        keyboard = []
        for partner in family['partners']:
            keyboard.append([InlineKeyboardButton(
                f"💔 Divorce {partner['first_name']}",
                callback_data=f'divorce_{partner["related_user_id"]}'
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "💔 <b>Select partner to divorce:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def handle_divorce_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle divorce callback"""
        query = update.callback_query
        data = query.data
        
        parts = data.split('_')
        if len(parts) < 2:
            return
        
        partner_id = int(parts[1])
        user = update.effective_user
        chat = update.effective_chat
        
        await db.remove_family_relation(user.id, partner_id, 'partner', chat.id)
        await db.remove_family_relation(partner_id, user.id, 'partner', chat.id)
        
        await query.edit_message_text("💔 You are now divorced!")
    
    async def disown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Disown a child"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        family = await db.get_family_tree(user.id, chat.id)
        
        if not family['children']:
            await update.message.reply_text("❌ You have no children to disown!")
            return
        
        keyboard = []
        for child in family['children']:
            keyboard.append([InlineKeyboardButton(
                f"👋 Disown {child['first_name']}",
                callback_data=f'disown_{child["related_user_id"]}'
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👋 <b>Select child to disown:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def handle_disown_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle disown callback"""
        query = update.callback_query
        data = query.data
        
        parts = data.split('_')
        if len(parts) < 2:
            return
        
        child_id = int(parts[1])
        user = update.effective_user
        chat = update.effective_chat
        
        await db.remove_family_relation(user.id, child_id, 'child', chat.id)
        await db.remove_family_relation(child_id, user.id, 'parent', chat.id)
        
        await query.edit_message_text("👋 Child disowned!")
    
    async def friend_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a friend"""
        user = update.effective_user
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Please reply to a user to add them as friend!")
            return
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to add them as friend!")
            return
        
        if target.id == user.id:
            await update.message.reply_text("❌ You can't add yourself as friend!")
            return
        
        if await db.are_friends(user.id, target.id):
            await update.message.reply_text("❌ You are already friends with this user!")
            return
        
        friend_count = await db.count_friends(user.id)
        if friend_count >= MAX_FRIENDS:
            await update.message.reply_text(f"❌ You have reached the maximum friends limit ({MAX_FRIENDS})!")
            return
        
        await db.create_proposal(user.id, target.id, 'friend', 0)
        
        keyboard = [
            [InlineKeyboardButton("✅ Accept", callback_data=f'accept_friend_{user.id}'),
             InlineKeyboardButton("❌ Decline", callback_data=f'reject_friend_{user.id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🌐 <b>Friend Request</b>\n\n"
            f"{user.first_name} wants to be your friend!\n\n"
            f"{target.first_name}, do you accept?",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def circle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show friend circle"""
        user = update.effective_user
        
        friends = await db.get_friends(user.id)
        
        if not friends:
            await update.message.reply_text("🌐 You have no friends yet! Use /friend to add some!")
            return
        
        text = f"🌐 <b>{user.first_name}'s Friend Circle</b>\n\n"
        text += f"Total Friends: {len(friends)}\n\n"
        
        for friend in friends[:20]:
            text += f"• {friend['first_name']}\n"
        
        if len(friends) > 20:
            text += f"\n... and {len(friends) - 20} more!"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def relations_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show close family relations"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        family = await db.get_family_tree(user.id, chat.id)
        
        text = f"👨‍👩‍👧 <b>{user.first_name}'s Close Relations</b>\n\n"
        
        if family['parents']:
            text += "<b>Parents:</b>\n"
            for parent in family['parents']:
                text += f"  • {parent['first_name']}\n"
            text += "\n"
        
        if family['partners']:
            text += "<b>Partners:</b>\n"
            for partner in family['partners']:
                text += f"  • {partner['first_name']}\n"
            text += "\n"
        
        if family['children']:
            text += "<b>Children:</b>\n"
            for child in family['children']:
                text += f"  • {child['first_name']}\n"
            text += "\n"
        
        if not any([family['parents'], family['partners'], family['children']]):
            text += "🌱 You have no close relations yet!\n"
            text += "Use /adopt or /marry to start your family!"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def family_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show extended family"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        family = await db.get_family_tree(user.id, chat.id)
        friends = await db.get_friends(user.id)
        
        total_members = 1 + len(family['parents']) + len(family['partners']) + len(family['children'])
        
        text = f"🌳 <b>{user.first_name}'s Extended Family</b>\n\n"
        text += f"📊 <b>Total Family Members:</b> {total_members}\n\n"
        
        if family['parents']:
            text += f"👨‍👩‍👧 Parents: {len(family['parents'])}\n"
        if family['partners']:
            text += f"💍 Partners: {len(family['partners'])}\n"
        if family['children']:
            text += f"👶 Children: {len(family['children'])}\n"
        
        text += f"🌐 Friends: {len(friends)}\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def setpic_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set profile picture"""
        user = update.effective_user
        
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Please reply to a photo/sticker/GIF to set it as your profile picture!")
            return
        
        replied = update.message.reply_to_message
        file_id = None
        
        if replied.photo:
            file_id = replied.photo[-1].file_id
        elif replied.sticker:
            file_id = replied.sticker.file_id
        elif replied.animation:
            file_id = replied.animation.file_id
        elif replied.video:
            file_id = replied.video.file_id
        
        if not file_id:
            await update.message.reply_text("❌ Please reply to a photo, sticker, GIF, or video!")
            return
        
        await db.update_user(user.id, profile_pic=file_id)
        await update.message.reply_text("✅ Profile picture updated!")
    
    async def setpfp_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set profile picture from Telegram photo"""
        user = update.effective_user
        
        try:
            photos = await context.bot.get_user_profile_photos(user.id, limit=1)
            
            if not photos.photos:
                await update.message.reply_text("❌ You don't have a profile picture!")
                return
            
            file_id = photos.photos[0][-1].file_id
            await db.update_user(user.id, profile_pic=file_id)
            await update.message.reply_text("✅ Profile picture updated from your Telegram photo!")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def block_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Block a user"""
        user = update.effective_user
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Please reply to a user to block them!")
            return
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to block them!")
            return
        
        db_user = await db.get_user(user.id)
        blocked = json.loads(db_user.get('blocked_users', '[]'))
        
        if target.id in blocked:
            await update.message.reply_text("❌ This user is already blocked!")
            return
        
        blocked.append(target.id)
        await db.update_user(user.id, blocked_users=json.dumps(blocked))
        await update.message.reply_text(f"✅ {target.first_name} has been blocked!")
    
    async def unblock_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unblock a user"""
        user = update.effective_user
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Please reply to a user to unblock them!")
            return
        
        if not target:
            await update.message.reply_text("❌ Please reply to a user to unblock them!")
            return
        
        db_user = await db.get_user(user.id)
        blocked = json.loads(db_user.get('blocked_users', '[]'))
        
        if target.id not in blocked:
            await update.message.reply_text("❌ This user is not blocked!")
            return
        
        blocked.remove(target.id)
        await db.update_user(user.id, blocked_users=json.dumps(blocked))
        await update.message.reply_text(f"✅ {target.first_name} has been unblocked!")
    
    async def blocklist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show blocked users"""
        user = update.effective_user
        
        db_user = await db.get_user(user.id)
        blocked = json.loads(db_user.get('blocked_users', '[]'))
        
        if not blocked:
            await update.message.reply_text("🌱 You have no blocked users!")
            return
        
        text = "🚫 <b>Blocked Users</b>\n\n"
        for user_id in blocked:
            text += f"• User ID: {user_id}\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def wedcard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create wedding card"""
        user = update.effective_user
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        
        if not target:
            await update.message.reply_text("❌ Please reply to your partner to create a wedding card!")
            return
        
        text = f"""💒 ═══════════════════ 💒

    🌸 <b>WEDDING INVITATION</b> 🌸

    💍 {user.first_name} 💍
         &
    💍 {target.first_name} 💍

    Are now married!

💒 ═══════════════════ 💒"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
