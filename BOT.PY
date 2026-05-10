import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# ================= CONFIGURATION =================
BOT_TOKEN = "8698275644:AAF09mlsf_BH8hOBiHwvjeVGxdM8PC2n9Q0"

# 👇 Owner ka ID (Admin)
OWNER_ID = 5286579067

# 👇 Dusre admin IDs (agar ho toh)
ADMIN_IDS = {5286579067, 8154938365}

DATA_FILE = "channels.json"
START_IMAGE_URL = "https://files.catbox.moe/i4ea8t.jpg"

# Style mapping for Telegram v22.7
# Valid styles: "PRIMARY", "SECONDARY", "DANGER", "SUCCESS"
STYLE_MAP = {
    "primary": "PRIMARY",
    "danger": "DANGER", 
    "success": "SUCCESS",
}
# ==================================================

# Load channels from file
def load_channels():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    
    # Default 3 buttons
    default = {
        "FREE VIP": {
            "url": "https://t.me/+YOUR_VIP_LINK",  # 👈 CHANGE KARO
            "style": "primary"
        },
        "FREE HACK": {
            "url": "https://t.me/+YOUR_HACK_LINK",  # 👈 CHANGE KARO
            "style": "danger"
        },
        "FREE DEPOSIT": {
            "url": "https://t.me/+YOUR_DEPOSIT_LINK",  # 👈 CHANGE KARO
            "style": "success"
        }
    }
    save_channels(default)
    return default

def save_channels(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Create keyboard with STYLE support (CORRECTED)
def get_main_keyboard(channels):
    keyboard = []
    for name, info in channels.items():
        style = info.get("style", "primary").upper()
        
        # Valid styles as per Telegram API
        if style == "DANGER":
            btn_style = "DANGER"
        elif style == "SUCCESS":
            btn_style = "SUCCESS"
        elif style == "PRIMARY":
            btn_style = "PRIMARY"
        else:
            btn_style = "PRIMARY"
        
        # ✅ Style argument directly as string
        button = InlineKeyboardButton(
            text=name,
            url=info["url"],
            style=btn_style  # Style is string: "PRIMARY", "DANGER", "SUCCESS"
        )
        keyboard.append([button])
    
    return InlineKeyboardMarkup(keyboard)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    channels = load_channels()
    keyboard = get_main_keyboard(channels)
    
    caption = (
        f"✨ *Welcome {user.first_name}!* ✨\n\n"
        f"👇 *Click any button to join:* 👇\n\n"
    )
    
    await update.message.reply_photo(
        photo=START_IMAGE_URL,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# /addchannel - Admin only command
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ *Access Denied!* Only bot admin can add channels.", parse_mode="Markdown")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "📖 *Usage:* `/addchannel <Name> <invite_link> [style]`\n\n"
            "📌 *Example:*\n"
            "`/addchannel \"FREE TOOLS\" https://t.me/+xyzabc success`\n\n"
            "🎨 *Styles:* `primary`, `danger`, `success`\n"
            "Default: `primary`",
            parse_mode="Markdown"
        )
        return
    
    # Parse arguments
    if len(args) >= 3 and args[-1].lower() in ["primary", "danger", "success"]:
        style = args[-1].lower()
        link = args[-2]
        name_parts = args[:-2]
        name = " ".join(name_parts)
    elif len(args) >= 2:
        style = "primary"
        link = args[-1]
        name_parts = args[:-1]
        name = " ".join(name_parts)
    else:
        await update.message.reply_text("❌ Invalid format! Use: `/addchannel Name link style`", parse_mode="Markdown")
        return
    
    # Validate link
    if not (link.startswith("https://t.me/") or link.startswith("http://t.me/")):
        await update.message.reply_text("❌ Invalid link! Must start with `https://t.me/`", parse_mode="Markdown")
        return
    
    channels = load_channels()
    if name in channels:
        await update.message.reply_text(f"⚠️ Button `{name}` already exists!", parse_mode="Markdown")
        return
    
    # Add new button
    channels[name] = {"url": link, "style": style}
    save_channels(channels)
    
    style_emoji = {"primary": "🔵", "danger": "🔴", "success": "🟢"}
    
    await update.message.reply_text(
        f"✅ *Button added successfully!*\n\n"
        f"📛 *Name:* {name}\n"
        f"🔗 *Link:* {link}\n"
        f"🎨 *Style:* {style_emoji.get(style, '🔵')} {style.upper()}\n\n"
        f"Users will see it in /start menu.",
        parse_mode="Markdown"
    )

# /listchannels - Show all buttons
async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    channels = load_channels()
    if not channels:
        await update.message.reply_text("📭 No channels added yet.")
        return
    
    text = "📋 *Current Channel Buttons:*\n\n"
    style_emoji = {"primary": "🔵", "danger": "🔴", "success": "🟢"}
    for name, info in channels.items():
        emoji = style_emoji.get(info.get("style", "primary"), "🔵")
        text += f"{emoji} *{name}*\n   └ {info['url']}\n\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

# /removechannel - Remove a button
async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Usage: `/removechannel <ButtonName>`", parse_mode="Markdown")
        return
    
    name = " ".join(args)
    channels = load_channels()
    
    if name not in channels:
        await update.message.reply_text(f"❌ Button `{name}` not found!", parse_mode="Markdown")
        return
    
    del channels[name]
    save_channels(channels)
    await update.message.reply_text(f"✅ Removed button: `{name}`", parse_mode="Markdown")

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addchannel", add_channel))
    app.add_handler(CommandHandler("listchannels", list_channels))
    app.add_handler(CommandHandler("removechannel", remove_channel))
    
    print("🤖 Bot is running...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"📁 Data file: {DATA_FILE}")
    
    app.run_polling()

if __name__ == "__main__":
    main()
