from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from database import db
from config import ADMIN_IDS


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Sizda ruxsat yo'q!")
            return
        return await func(update, context)
    return wrapper


@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⏳ Yangi buyurtmalar", callback_data="admin_pending")],
        [InlineKeyboardButton("🔧 Ishlov berilayotgan", callback_data="admin_processing")],
        [InlineKeyboardButton("✅ Bajarilgan", callback_data="admin_done")],
        [InlineKeyboardButton("📊 Barcha buyurtmalar", callback_data="admin_all")],
    ]
    await update.message.reply_text(
        "👨‍💼 *Admin Panel*\n\nQaysi buyurtmalarni ko'rmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    status_map = {
        "admin_pending": "pending",
        "admin_processing": "processing",
        "admin_done": "done",
        "admin_all": None,
    }
    status = status_map.get(query.data)
    orders = await db.get_all_orders(status)
    if not orders:
        await query.edit_message_text("📭 Buyurtmalar yo'q.")
        return
    text = f"📋 *Buyurtmalar ({len(orders)} ta):*\n\n"
    keyboard = []
    for o in orders[:10]:
        e = {"pending": "⏳", "processing": "🔧", "done": "✅", "cancelled": "❌"}.get(o["status"], "📋")
        text += (
            f"{e} *#{o['id']}* — {o['product']}\n"
            f"   👤 {o['full_name']}\n"
            f"   💰 {o['price']:,} so'm\n\n"
        )
        if o["status"] == "pending":
            keyboard.append([
                InlineKeyboardButton(f"✅ #{o['id']} Tasdiqlash", callback_data=f"approve_{o['id']}"),
                InlineKeyboardButton(f"❌ Bekor", callback_data=f"cancel_{o['id']}"),
            ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def approve_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    order_id = int(query.data.split("_")[1])
    await db.update_order_status(order_id, "processing")
    await query.answer(f"✅ #{order_id} tasdiqlandi!", show_alert=True)


async def cancel_order_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    order_id = int(query.data.split("_")[1])
    await db.update_order_status(order_id, "cancelled")
    await query.answer(f"❌ #{order_id} bekor qilindi!", show_alert=True)


def register_admin_handlers(app):
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(admin_orders, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(approve_order, pattern="^approve_"))
    app.add_handler(CallbackQueryHandler(cancel_order_admin, pattern="^cancel_"))
