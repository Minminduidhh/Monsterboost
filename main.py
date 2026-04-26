"""
Spider Bird - Telegram Bot + Web Server
Serves the game HTML and handles Telegram bot commands.
Run on Replit with: python main.py
"""
import os
import json
import threading
import time
import urllib.request
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ===== CONFIG =====
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GAME_URL = os.environ.get("GAME_URL", "")
PORT = int(os.environ.get("PORT", 8080))

API = f"https://api.telegram.org/bot{TOKEN}"
OFFSET = 0


# ===== WEB SERVER =====
class GameHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.path = "/buddy-bird.html"
        return super().do_GET()

    def log_message(self, format, *args):
        pass  # Quiet logs


# ===== TELEGRAM BOT =====
def api_call(method, data=None):
    url = f"{API}/{method}"
    if data:
        req = urllib.request.Request(url, json.dumps(data).encode(), {"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"[Bot] Error: {e}")
        return None


def send_game_message(chat_id, first_name=""):
    if not GAME_URL:
        print("[Bot] GAME_URL not set!")
        return
    greeting = f"မင်္ဂလာပါ {first_name}!" if first_name else "မင်္ဂလာပါ!"
    text = (
        f"{greeting} 🕷️\n\n"
        f"🎮 *Spider Bird* ကို ကစားဖို့ အောက်က ခလုတ်ကို နှိပ်ပါ!\n\n"
        f"🏆 သူငယ်ချင်းတွေကို ဖိတ်ပြီး ယှဥ်ပြိုင်ကစားပါ!"
    )
    api_call("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "🎮 Play Spider Bird", "web_app": {"url": GAME_URL}}
            ]]
        }
    })


def bot_polling():
    global OFFSET
    if not TOKEN:
        print("[Bot] No TELEGRAM_BOT_TOKEN set. Bot disabled.")
        return

    # Verify bot
    me = api_call("getMe")
    if me and me.get("ok"):
        print(f"[Bot] Connected as @{me['result']['username']}")
    else:
        print("[Bot] Failed to connect. Check token.")
        return

    # Set menu button
    if GAME_URL:
        api_call("setChatMenuButton", {
            "menu_button": {"type": "web_app", "text": "🎮 Spider Bird", "web_app": {"url": GAME_URL}}
        })
        api_call("setMyCommands", {
            "commands": [
                {"command": "start", "description": "Start Spider Bird Game"},
                {"command": "play", "description": "Play Spider Bird 🎮"}
            ]
        })
        print(f"[Bot] Menu button set to {GAME_URL}")

    print("[Bot] Polling started...")
    while True:
        try:
            result = api_call("getUpdates", {"offset": OFFSET, "timeout": 25})
            if not result or not result.get("ok"):
                time.sleep(3)
                continue
            for update in result.get("result", []):
                OFFSET = update["update_id"] + 1
                msg = update.get("message")
                if not msg:
                    continue
                text = msg.get("text", "")
                chat_id = msg["chat"]["id"]
                first_name = msg.get("from", {}).get("first_name", "")
                if text in ("/start", "/play", "/start@" + me['result']['username']):
                    send_game_message(chat_id, first_name)
                    print(f"[Bot] Game sent to {first_name} ({chat_id})")
        except Exception as e:
            print(f"[Bot] Poll error: {e}")
            time.sleep(5)


# ===== MAIN =====
if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = threading.Thread(target=bot_polling, daemon=True)
    bot_thread.start()

    # Start web server
    print(f"[Web] Serving game on port {PORT}")
    server = HTTPServer(("0.0.0.0", PORT), GameHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
