import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("lamvest_bot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/+O_ftPKkrKKxhNzBk")
# Optional: only auto-approve requests for this channel (e.g. -1001234567890)
CHANNEL_ID = os.getenv("CHANNEL_ID")

WELCOME_TEXT = (
    "👋 Welcome to Lamvest!\n\n"
    "Please join the Lamvest channel to get updates, news and opportunities.\n\n"
    "👇 Tap the button below to join."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📢 Join Lamvest Channel", url=CHANNEL_LINK)]]
    )
    await update.message.reply_text(
        f"{WELCOME_TEXT}\n\n{CHANNEL_LINK}",
        reply_markup=keyboard,
    )


async def approve_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Instantly approves anyone who requests to join the channel."""
    req = update.chat_join_request
    if CHANNEL_ID and str(req.chat.id) != str(CHANNEL_ID):
        return
    try:
        await req.approve()
        log.info("Approved %s (%s) for %s", req.from_user.full_name, req.from_user.id, req.chat.title)
        await context.bot.send_message(
            chat_id=req.user_chat_id,
            text=f"✅ You've been approved! Welcome to {req.chat.title}.",
        )
    except Exception as e:
        log.warning("Could not approve/notify %s: %s", req.from_user.id, e)


class HealthHandler(BaseHTTPRequestHandler):
    """Tiny web page so Render's free Web Service (and uptime pingers) get a 200 OK."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Lamvest bot is alive")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


def start_health_server() -> None:
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log.info("Health server listening on port %s", port)


def main() -> None:
    start_health_server()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatJoinRequestHandler(approve_join_request))
    log.info("Lamvest bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)


if __name__ == "__main__":
    main()
