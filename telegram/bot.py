"""
Bot Telegram para Proxy Aggregator
Comandos: /start, /proxies, /stats, /random
"""
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu principal"""
    await update.message.reply_text(
        "🤖 <b>Proxy Aggregator Bot</b>\n\n"
        "Escolha uma opção:\n\n"
        "/proxies - Ver proxies vivos\n"
        "/stats - Estatísticas\n"
        "/random - Proxy aleatório\n"
        "/help - Ajuda",
        parse_mode="HTML"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ajuda"""
    await update.message.reply_text(
        "<b>Comandos disponíveis:</b>\n\n"
        "/start - Menu principal\n"
        "/proxies [protocolo] [limite] - Lista proxies\n"
        "/stats - Estatísticas do pool\n"
        "/random [protocolo] - Proxy aleatório\n"
        "/help - Esta ajuda",
        parse_mode="HTML"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Estatísticas"""
    try:
        resp = requests.get(f"{API_URL}/api/v1/stats", timeout=10)
        data = resp.json()
        
        total = data.get("total_alive", 0)
        by_proto = data.get("by_protocol", {})
        
        msg = f"📊 <b>Estatísticas</b>\n\n"
        msg += f"Total vivos: <b>{total}</b>\n\n"
        
        for proto, count in by_proto.items():
            emoji = {"socks5": "🔴", "http": "🟢", "socks4": "🟡"}.get(proto, "⚪")
            msg += f"{emoji} {proto.upper()}: {count}\n"
        
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")

async def proxies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista proxies"""
    protocol = None
    limit = 10
    
    args = context.args
    if args:
        if args[0] in ["socks5", "http", "socks4"]:
            protocol = args[0]
        if len(args) > 1:
            try:
                limit = min(int(args[1]), 50)
            except:
                pass
    
    try:
        url = f"{API_URL}/api/v1/proxies?limit={limit}"
        if protocol:
            url += f"&protocol={protocol}"
        
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        proxies_list = data.get("proxies", [])
        
        if not proxies_list:
            await update.message.reply_text("❌ Nenhum proxy encontrado")
            return
        
        msg = f"🔌 <b>Proxies ({len(proxies_list)})</b>\n\n"
        
        for p in proxies_list[:20]:
            lat = f"{p['latency']}ms" if p.get("latency") else "?"
            msg += f"• {p['ip']}:{p['port']} [{p['protocol']}] ⚡{lat}\n"
        
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")

async def random_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Proxy aleatório"""
    protocol = context.args[0] if context.args and context.args[0] in ["socks5", "http", "socks4"] else None
    
    try:
        url = f"{API_URL}/api/v1/proxies/random"
        if protocol:
            url += f"?protocol={protocol}"
        
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if "error" in data:
            await update.message.reply_text("❌ " + data["error"])
            return
        
        p = data
        lat = f"{p['latency']}ms" if p.get("latency") else "?"
        
        msg = f"🎲 <b>Proxy Aleatório</b>\n\n"
        msg += f"IP: <code>{p['ip']}</code>\n"
        msg += f"Porta: <code>{p['port']}</code>\n"
        msg += f"Protocolo: {p['protocol'].upper()}\n"
        msg += f"Latência: {lat}"
        
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")

def run_bot(token: str):
    """Executa o bot"""
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("proxies", proxies))
    app.add_handler(CommandHandler("random", random_proxy))
    
    logger.info("Bot Telegram iniciado!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "SEU_TOKEN_AQUI"
    run_bot(TOKEN)
