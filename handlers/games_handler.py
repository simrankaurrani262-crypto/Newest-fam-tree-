"""
Games Handler
=============
Handles mini games
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import datetime, timedelta
import random
import json

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from config.config import COUNTRIES, TRIVIA_QUESTIONS, FOUR_PICS_WORDS

class GamesHandler:
    
    async def ripple_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ripple betting game"""
        user = update.effective_user
        
        if len(context.args) < 1:
            await update.message.reply_text(
                "🌻 <b>Ripple Game</b>\n\n"
                "Bet money and step on grass to multiply your reward!\n\n"
                "Usage: <code>/ripple [amount]</code>\n"
                "Example: <code>/ripple 100</code>\n\n"
                "🌻 Sunflower = 1.5x multiplier\n"
                "🐍 Snake = Lose everything!\n\n"
                "Use <code>/rtake</code> to collect your winnings!",
                parse_mode=ParseMode.HTML
            )
            return
        
        try:
            amount = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return
        
        if amount <= 0:
            await update.message.reply_text("❌ Amount must be positive!")
            return
        
        # Check if already in a game
        active_ripple = await db.get_active_ripple(user.id)
        if active_ripple:
            await update.message.reply_text("❌ You already have an active ripple game! Use /rtake to collect!")
            return
        
        if not await db.remove_money(user.id, amount):
            await update.message.reply_text("❌ You don't have enough money!")
            return
        
        await db.create_ripple(user.id, amount)
        
        keyboard = [
            [InlineKeyboardButton("🌱 Step", callback_data=f'ripple_step_{user.id}'),
             InlineKeyboardButton("💰 Take", callback_data=f'ripple_take_{user.id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🌻 <b>Ripple Game</b>\n\n"
            f"💰 Bet: ${amount}\n"
            f"📈 Current: ${amount}\n"
            f"🌟 Multiplier: 1.0x\n\n"
            f"Choose: Step or Take?",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def rbet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick ripple bet"""
        user = update.effective_user
        
        active_ripple = await db.get_active_ripple(user.id)
        
        if not active_ripple:
            if len(context.args) < 1:
                await update.message.reply_text("Usage: <code>/rbet [amount]</code>")
                return
            
            try:
                amount = int(context.args[0])
            except ValueError:
                await update.message.reply_text("❌ Invalid amount!")
                return
            
            if not await db.remove_money(user.id, amount):
                await update.message.reply_text("❌ You don't have enough money!")
                return
            
            await db.create_ripple(user.id, amount)
            active_ripple = await db.get_active_ripple(user.id)
        
        # Step
        result = random.choice(['snake', 'sunflower', 'sunflower'])
        
        if result == 'snake':
            await db.end_ripple(user.id)
            await update.message.reply_text(
                f"🐍 <b>Ripple Lost!</b>\n\n"
                f"You stepped on a snake and lost everything!",
                parse_mode=ParseMode.HTML
            )
        else:
            new_multiplier = active_ripple['multiplier'] * 1.5
            new_amount = int(active_ripple['bet_amount'] * new_multiplier)
            new_step = active_ripple['step'] + 1
            
            await db.update_ripple(user.id, multiplier=new_multiplier, step=new_step)
            
            keyboard = [
                [InlineKeyboardButton("🌱 Continue", callback_data=f'rbet_{user.id}'),
                 InlineKeyboardButton("💰 Take", callback_data=f'rtake_{user.id}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🌻 <b>Ripple Win!</b>\n\n"
                f"💰 Bet: ${active_ripple['bet_amount']}\n"
                f"📈 Current: ${new_amount}\n"
                f"🌟 Multiplier: {new_multiplier:.1f}x\n"
                f"🦶 Steps: {new_step}\n\n"
                f"Continue or Take?",
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
    
    async def rtake_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Take ripple winnings"""
        user = update.effective_user
        
        active_ripple = await db.get_active_ripple(user.id)
        
        if not active_ripple:
            await update.message.reply_text("❌ You don't have an active ripple game!")
            return
        
        winnings = active_ripple['current_amount']
        
        await db.add_money(user.id, winnings)
        await db.end_ripple(user.id)
        
        profit = winnings - active_ripple['bet_amount']
        
        await update.message.reply_text(
            f"💰 <b>Ripple Collected!</b>\n\n"
            f"💵 Collected: ${winnings}\n"
            f"📊 Profit: ${profit}\n"
            f"🦶 Steps: {active_ripple['step']}",
            parse_mode=ParseMode.HTML
        )
    
    async def bets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show ripple bet history"""
        await update.message.reply_text(
            "📊 <b>Ripple Stats</b>\n\n"
            "Your ripple history would be shown here!\n\n"
            "💡 Play with <code>/ripple [amount]</code>!"
        )
    
    async def nation_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Guess the nation game"""
        chat = update.effective_chat
        user = update.effective_user
        
        # Select random country
        if context.args:
            continent = context.args[0].title()
            countries_in_continent = [c for c, cont in COUNTRIES.items() if cont == continent]
            if countries_in_continent:
                country = random.choice(countries_in_continent)
            else:
                country = random.choice(list(COUNTRIES.keys()))
        else:
            country = random.choice(list(COUNTRIES.keys()))
        
        # Create game session
        await db.create_game_session(
            chat_id=chat.id,
            user_id=user.id,
            game_type='nation',
            data={'answer': country.lower(), 'hint_shown': False},
            expires_minutes=2
        )
        
        hint = country[0] + "_" * (len(country) - 2) + country[-1]
        
        await update.message.reply_text(
            f"🌍 <b>Guess the Nation!</b>\n\n"
            f"Which country is this?\n\n"
            f"🏳️ Hint: <code>{hint}</code>\n\n"
            f"💡 Just type your answer!",
            parse_mode=ParseMode.HTML
        )
    
    async def lottery_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start a lottery"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        if len(context.args) < 1:
            await update.message.reply_text("Usage: <code>/lottery [amount]</code>")
            return
        
        try:
            amount = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return
        
        if not await db.remove_money(user.id, amount):
            await update.message.reply_text("❌ You don't have enough money!")
            return
        
        # Create lottery session
        await db.create_game_session(
            chat_id=chat.id,
            user_id=user.id,
            game_type='lottery',
            data={'starter': user.id, 'amount': amount, 'participants': [user.id]},
            expires_minutes=5
        )
        
        keyboard = [
            [InlineKeyboardButton("🎟 Join Lottery", callback_data=f'lottery_join_{chat.id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🎰 <b>Lottery Started!</b>\n\n"
            f"💰 Entry: ${amount}\n"
            f"👤 Started by: {user.first_name}\n"
            f"🎟 Participants: 1\n\n"
            f"Click to join! Winner gets everything!",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    async def question_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trivia question"""
        chat = update.effective_chat
        user = update.effective_user
        
        question = random.choice(TRIVIA_QUESTIONS)
        
        await db.create_game_session(
            chat_id=chat.id,
            user_id=user.id,
            game_type='trivia',
            data={'answer': question['answer'].lower(), 'question': question['question']},
            expires_minutes=2
        )
        
        await update.message.reply_text(
            f"❓ <b>Trivia Question</b>\n\n"
            f"{question['question']}\n\n"
            f"💡 You have 2 minutes to answer!",
            parse_mode=ParseMode.HTML
        )
    
    async def fourpics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """4 Pics 1 Word game"""
        chat = update.effective_chat
        user = update.effective_user
        
        word_data = random.choice(FOUR_PICS_WORDS)
        word = word_data['word']
        
        await db.create_game_session(
            chat_id=chat.id,
            user_id=user.id,
            game_type='4pics',
            data={'word': word.lower(), 'guesses': []},
            expires_minutes=5
        )
        
        await update.message.reply_text(
            f"🖼 <b>4 Pics 1 Word</b>\n\n"
            f"What do these pictures have in common?\n\n"
            f"📷 Images: {', '.join(word_data['images'])}\n\n"
            f"💡 Word has {len(word)} letters!\n"
            f"⏱ You have 5 minutes!",
            parse_mode=ParseMode.HTML
        )
    
    async def whichai_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Which image is AI generated"""
        await update.message.reply_text(
            "🤖 <b>Which AI?</b>\n\n"
            "Two images will be shown. Guess which one is AI generated!\n\n"
            "💡 Coming soon!"
        )
    
    async def ftrivia_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Family trivia"""
        await update.message.reply_text(
            "👨‍👩‍👧 <b>Family Trivia</b>\n\n"
            "Guess the relationship between family members!\n\n"
            "💡 Coming soon!"
        )
    
    async def paper_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Paper tactics game"""
        await update.message.reply_text(
            "📄 <b>Paper Tactics</b>\n\n"
            "A strategic paper-based game!\n\n"
            "💡 Coming soon!\n"
            "🌐 Check paper-tactics.com for rules!"
        )
    
    async def handle_game_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text responses for games"""
        user = update.effective_user
        chat = update.effective_chat
        text = update.message.text.strip().lower()
        
        # Check for nation game
        session = await db.get_game_session(chat.id, user.id, 'nation')
        if session:
            answer = session['data']['answer']
            if text == answer.lower():
                await db.add_money(user.id, 100)
                await db.delete_game_session(session['id'])
                await update.message.reply_text(
                    f"🎉 <b>Correct!</b>\n\n"
                    f"The answer was {answer.title()}!\n"
                    f"💰 You won $100!",
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(f"❌ Wrong! Try again!")
            return
        
        # Check for 4pics game
        session = await db.get_game_session(chat.id, user.id, '4pics')
        if session:
            answer = session['data']['word']
            if text == answer.lower():
                reward = 200
                await db.add_money(user.id, reward)
                await db.delete_game_session(session['id'])
                await update.message.reply_text(
                    f"🎉 <b>Correct!</b>\n\n"
                    f"The answer was {answer.upper()}!\n"
                    f"💰 You won ${reward}!",
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(f"❌ Wrong! Try again!")
            return
        
        # Check for trivia game
        session = await db.get_game_session(chat.id, user.id, 'trivia')
        if session:
            answer = session['data']['answer']
            if text == answer.lower():
                reward = 150
                await db.add_money(user.id, reward)
                await db.delete_game_session(session['id'])
                await update.message.reply_text(
                    f"🎉 <b>Correct!</b>\n\n"
                    f"The answer was {answer.title()}!\n"
                    f"💰 You won ${reward}!",
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(f"❌ Wrong! Try again!")
            return
