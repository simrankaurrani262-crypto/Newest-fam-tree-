"""
Utility Handler
===============
Handles utility commands
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import pyqrcode
import io
import pyfiglet
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db

class UtilityHandler:
    
    async def tojpg_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Convert sticker to JPG"""
        if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
            await update.message.reply_text("❌ Please reply to a sticker!")
            return
        
        await update.message.reply_text("🖼 Converting sticker to JPG... (Coming soon!)")
    
    async def topng_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Convert sticker to PNG"""
        if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
            await update.message.reply_text("❌ Please reply to a sticker!")
            return
        
        await update.message.reply_text("🖼 Converting sticker to PNG... (Coming soon!)")
    
    async def figlet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create ASCII art text"""
        if not context.args:
            await update.message.reply_text("Usage: <code>/figlet [text]</code>")
            return
        
        text = ' '.join(context.args)
        
        try:
            ascii_art = pyfiglet.figlet_format(text[:20])
            await update.message.reply_text(f"<pre>{ascii_art}</pre>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def toimgur_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Upload image to Imgur"""
        await update.message.reply_text("📤 Upload to Imgur - Coming soon!")
    
    async def qotd_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quote of the day"""
        quotes = [
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Life is what happens when you're busy making other plans. - John Lennon",
            "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
            "It is during our darkest moments that we must focus to see the light. - Aristotle",
            "Whoever is happy will make others happy too. - Anne Frank",
        ]
        
        quote = random.choice(quotes)
        await update.message.reply_text(f"📜 <b>Quote of the Day</b>\n\n{quote}")
    
    async def addcaption_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add caption to image"""
        if not context.args:
            await update.message.reply_text("Usage: Reply to image with <code>/addcaption [text]</code>")
            return
        
        caption = ' '.join(context.args)
        await update.message.reply_text(f"📝 Caption: {caption}")
    
    async def ip2loc_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get location from IP"""
        if not context.args:
            await update.message.reply_text("Usage: <code>/ip2loc [IP address]</code>")
            return
        
        ip = context.args[0]
        
        await update.message.reply_text(
            f"🌍 <b>IP Location</b>\n\n"
            f"IP: {ip}\n"
            f"Country: Unknown\n"
            f"City: Unknown\n\n"
            f"💡 This is a demo response!"
        )
    
    async def paste_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Paste text to pastebin"""
        if not context.args:
            await update.message.reply_text("Usage: <code>/paste [text]</code> or reply to message")
            return
        
        text = ' '.join(context.args)
        
        await update.message.reply_text(
            f"📋 <b>Pastebin</b>\n\n"
            f"Your text has been pasted!\n"
            f"🔗 URL: https://pastebin.com/demo123\n\n"
            f"💡 This is a demo response!"
        )
    
    async def shorten_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Shorten URL"""
        if not context.args:
            await update.message.reply_text("Usage: <code>/shorten [URL]</code>")
            return
        
        url = context.args[0]
        
        await update.message.reply_text(
            f"🔗 <b>URL Shortener</b>\n\n"
            f"Original: {url}\n"
            f"Short: https://short.link/demo123\n\n"
            f"💡 This is a demo response!"
        )
    
    async def qrcode_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate QR code"""
        if not context.args:
            await update.message.reply_text("Usage: <code>/qrcode [text]</code>")
            return
        
        text = ' '.join(context.args)
        
        try:
            qr = pyqrcode.create(text)
            buf = io.BytesIO()
            qr.png(buf, scale=6)
            buf.seek(0)
            
            await update.message.reply_photo(
                photo=buf,
                caption=f"📱 <b>QR Code</b>\n\nContent: <code>{text[:50]}</code>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def catfact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get random cat fact"""
        facts = [
            "Cats spend 70% of their lives sleeping.",
            "A group of cats is called a clowder.",
            "Cats have 32 muscles in each ear.",
            "Cats can rotate their ears 180 degrees.",
            "The average cat sleeps 12-16 hours per day.",
        ]
        
        fact = random.choice(facts)
        await update.message.reply_text(f"🐱 <b>Cat Fact</b>\n\n{fact}")
    
    async def shibapic_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get random shiba pic"""
        await update.message.reply_text("🐕 Shiba Inu picture - Coming soon!")
    
    async def animequote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get random anime quote"""
        quotes = [
            "The world isn't perfect. But it's there for us, doing the best it can. - Fullmetal Alchemist",
            "Hard work is worthless for those that don't believe in themselves. - Naruto",
            "If you don't like your destiny, don't accept it. - Naruto",
            "People die when they are killed. - Fate/Stay Night",
            "I am the bone of my sword. - Fate/Stay Night",
        ]
        
        quote = random.choice(quotes)
        await update.message.reply_text(f"🎌 <b>Anime Quote</b>\n\n{quote}")
    
    async def name2gender_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Predict gender from name"""
        if not context.args:
            await update.message.reply_text("Usage: <code>/name2gender [name]</code>")
            return
        
        name = context.args[0]
        
        if name[-1].lower() in 'aeiouy':
            gender = "Female"
            emoji = "👩"
        else:
            gender = "Male"
            emoji = "👨"
        
        await update.message.reply_text(f"{emoji} <b>Gender Prediction</b>\n\nName: {name}\nGender: {gender}\n\n💡 This is just a prediction!")
    
    async def activity_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get random activity"""
        activities = [
            "Go for a walk 🚶",
            "Read a book 📚",
            "Learn something new 🎓",
            "Call a friend 📞",
            "Try a new recipe 🍳",
            "Do some exercise 💪",
            "Meditate for 10 minutes 🧘",
            "Write in a journal 📝",
        ]
        
        activity = random.choice(activities)
        await update.message.reply_text(f"🎯 <b>Random Activity</b>\n\n{activity}")
    
    async def name2nation_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Predict nation from name"""
        if not context.args:
            await update.message.reply_text("Usage: <code>/name2nation [name]</code>")
            return
        
        name = context.args[0]
        nations = ["United States", "United Kingdom", "India", "Japan", "Germany", "France", "Brazil", "Australia"]
        nation = random.choice(nations)
        
        await update.message.reply_text(f"🌍 <b>Nation Prediction</b>\n\nName: {name}\nNation: {nation}\n\n💡 This is just a prediction!")
    
    async def name2age_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Predict age from name"""
        if not context.args:
            await update.message.reply_text("Usage: <code>/name2age [name]</code>")
            return
        
        name = context.args[0]
        age = random.randint(18, 65)
        
        await update.message.reply_text(f"🎂 <b>Age Prediction</b>\n\nName: {name}\nEstimated Age: {age}\n\n💡 This is just a prediction!")
    
    async def foodpic_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get random food pic"""
        await update.message.reply_text("🍕 Food picture - Coming soon!")
    
    async def darkjoke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get random dark joke"""
        jokes = [
            "I have a fish that can breakdance! Only for 20 seconds though, and only once.",
            "I threw a boomerang a few years ago. I now live in constant fear.",
            "My girlfriend's dog died, so I tried to cheer her up by getting her an identical one. It just made her more upset. Now I have two dead dogs.",
        ]
        
        joke = random.choice(jokes)
        await update.message.reply_text(f"⚫ <b>Dark Joke</b>\n\n{joke}")
    
    async def joketype_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select joke type"""
        await update.message.reply_text(
            "😂 <b>Joke Types</b>\n\n"
            "Available types:\n"
            "• /randomjoke - Random joke\n"
            "• /darkjoke - Dark humor\n"
            "• /dadjoke - Dad jokes\n\n"
            "Pick your poison!"
        )
    
    async def randomjoke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look sad? Because it had too many problems.",
        ]
        
        joke = random.choice(jokes)
        await update.message.reply_text(f"😂 <b>Random Joke</b>\n\n{joke}")
    
    async def evilinsult_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get evil insult"""
        insults = [
            "You're not stupid; you just have bad luck thinking.",
            "I'd agree with you but then we'd both be wrong.",
            "You're like a cloud. When you disappear, it's a beautiful day.",
        ]
        
        insult = random.choice(insults)
        await update.message.reply_text(f"😈 <b>Evil Insult</b>\n\n{insult}")
    
    async def randomadvice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get random advice"""
        advices = [
            "Never go to bed angry. Stay awake and plot your revenge.",
            "If at first you don't succeed, skydiving is not for you.",
            "Always borrow money from a pessimist. They won't expect it back.",
            "Don't take life too seriously. You'll never get out alive.",
        ]
        
        advice = random.choice(advices)
        await update.message.reply_text(f"💡 <b>Random Advice</b>\n\n{advice}")
    
    async def dadjoke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get dad joke"""
        jokes = [
            "I'm afraid for the calendar. Its days are numbered.",
            "Why do fathers take an extra pair of socks when they go golfing? In case they get a hole in one!",
            "Singing in the shower is fun until you get soap in your mouth. Then it's a soap opera.",
            "What do a tick and the Eiffel Tower have in common? They're both Paris sites.",
        ]
        
        joke = random.choice(jokes)
        await update.message.reply_text(f"👨 <b>Dad Joke</b>\n\n{joke}")
