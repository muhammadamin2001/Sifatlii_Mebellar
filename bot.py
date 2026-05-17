import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler
)
from database import db
from config import TOKEN

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORY, SUBCATEGORY, SIZE, COLOR, MATERIAL, CONFIRM = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.full_name, user.username)
    keyboard = [
        [InlineKeyboardButton("🛋 Mebel tanlash", callback_data="catalog")],
        [InlineKeyboardButton("📦 Mening buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("📞 Bog'lanish", callback_data="contact")],
    ]
    await update.message.reply_text(
        f"👋 Salom, {user.first_name}!\n\n🏠 *MebelShop* botiga xush kelibsiz!\n\nQuyidagi bo'limlardan birini tanlang:",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🚪 Shkaf / Javon", callback_data="cat_shkaf")],
        [InlineKeyboardButton("🛏 Yotoq xona mebellar", callback_data="cat_yotoq")],
        [InlineKeyboardButton("🍽 Oshxona mebellar", callback_data="cat_oshxona")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_start")],
    ]
    await query.edit_message_text("📂 *Kategoriya tanlang:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return CATEGORY

SUBCATEGORIES = {
    "cat_shkaf": {"name": "Shkaf / Javon", "items": [
        ("Kiyim shkafi", "shkaf_kiyim"), ("Kitob javoni", "shkaf_kitob"),
        ("Burchak shkaf", "shkaf_burchak"), ("Koridorga shkaf", "shkaf_koridor")]},
    "cat_yotoq": {"name": "Yotoq xona", "items": [
        ("Karavot", "yotoq_karavot"), ("Kiyim shkafi", "yotoq_shkaf"),
        ("Tumbochka", "yotoq_tumbochka"), ("Kommode", "yotoq_kommode")]},
    "cat_oshxona": {"name": "Oshxona mebellar", "items": [
        ("Oshxona garnituri", "oshxona_garnit"), ("Oshxona stoli", "oshxona_stol"),
        ("Taomxona stuli", "oshxona_stul"), ("Oshxona javoni", "oshxona_javon")]},
}

async def subcategory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_key = query.data
    context.user_data["category"] = cat_key
    cat = SUBCATEGORIES[cat_key]
    keyboard = [[InlineKeyboardButton(n, callback_data=f"sub_{c}")] for n, c in cat["items"]]
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="catalog")])
    await query.edit_message_text(f"📦 *{cat['name']}* — mahsulot turini tanlang:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return SUBCATEGORY

SIZES = {
    "shkaf_kiyim": [("Kichik (80x180)", "80x180"), ("O'rta (120x200)", "120x200"), ("Katta (160x220)", "160x220"), ("XL (200x240)", "200x240")],
    "shkaf_kitob": [("Kichik (60x150)", "60x150"), ("O'rta (80x180)", "80x180"), ("Katta (100x200)", "100x200")],
    "shkaf_burchak": [("Standart (90x90x180)", "90x90x180"), ("Katta (120x120x220)", "120x120x220")],
    "shkaf_koridor": [("Tor (50x180)", "50x180"), ("Keng (80x200)", "80x200")],
    "yotoq_karavot": [("Bir kishilik (90x200)", "90x200"), ("Yarim (120x200)", "120x200"), ("Ikki kishilik (160x200)", "160x200"), ("King (180x200)", "180x200")],
    "yotoq_shkaf": [("Kichik (100x200)", "100x200"), ("O'rta (150x220)", "150x220"), ("Katta (200x240)", "200x240")],
    "yotoq_tumbochka": [("Kichik (40x50)", "40x50"), ("O'rta (50x60)", "50x60")],
    "yotoq_kommode": [("Tor (60x80)", "60x80"), ("Keng (100x80)", "100x80")],
    "oshxona_garnit": [("2 metr", "200x85"), ("2.4 metr", "240x85"), ("3 metr", "300x85")],
    "oshxona_stol": [("Kichik (60x80)", "60x80"), ("O'rta (80x120)", "80x120"), ("Katta (100x160)", "100x160")],
    "oshxona_stul": [("Standart", "45x90"), ("Balandroq", "45x100")],
    "oshxona_javon": [("Bir qavatli (80x30)", "80x30"), ("Ikki qavatli (80x60)", "80x60")],
}

async def choose_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sub_key = query.data.replace("sub_", "")
    context.user_data["subcategory"] = sub_key
    sizes = SIZES.get(sub_key, [("Standart", "standart")])
    keyboard = [[InlineKeyboardButton(f"📐 {l} sm", callback_data=f"size_{v}")] for l, v in sizes]
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data=context.user_data.get("category", "catalog"))])
    await query.edit_message_text("📏 *O'lcham tanlang:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return SIZE

COLORS = [
    ("⬜ Oq", "oq"), ("⬛ Qora", "qora"), ("🟫 Yong'oq", "yongoch"),
    ("🟤 Jigarrang", "jigar"), ("🔵 Ko'k", "kok"), ("🟢 Yashil", "yashil"),
    ("⚪ Kulrang", "kulrang"), ("🟡 Sariq", "sariq"),
]

async def choose_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["size"] = query.data.replace("size_", "")
    keyboard = []
    row = []
    for label, val in COLORS:
        row.append(InlineKeyboardButton(label, callback_data=f"color_{val}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data=f"sub_{context.user_data['subcategory']}")])
    await query.edit_message_text("🎨 *Rangni tanlang:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return COLOR

MATERIALS = [
    ("🌲 Massiv yog'och", "massiv", 1.5),
    ("🪵 LDSP (laminat)", "ldsp", 1.0),
    ("✨ MDF bo'yalgan", "mdf", 1.2),
    ("🏆 Eman (dub)", "dub", 1.8),
    ("💎 Metall + shisha", "metall_shisha", 1.3),
]

async def choose_material(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["color"] = query.data.replace("color_", "")
    keyboard = [[InlineKeyboardButton(l, callback_data=f"mat_{v}")] for l, v, _ in MATERIALS]
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data=f"size_{context.user_data['size']}")])
    await query.edit_message_text("🪵 *Material tanlang:*\n_(narxga ta'sir qiladi)_", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return MATERIAL

BASE_PRICES = {
    "shkaf_kiyim": {"80x180": 2800000, "120x200": 3800000, "160x220": 5200000, "200x240": 6800000},
    "shkaf_kitob": {"60x150": 1800000, "80x180": 2400000, "100x200": 3200000},
    "shkaf_burchak": {"90x90x180": 4500000, "120x120x220": 6200000},
    "shkaf_koridor": {"50x180": 1500000, "80x200": 2200000},
    "yotoq_karavot": {"90x200": 2500000, "120x200": 3200000, "160x200": 4800000, "180x200": 6000000},
    "yotoq_shkaf": {"100x200": 3000000, "150x220": 4500000, "200x240": 6500000},
    "yotoq_tumbochka": {"40x50": 600000, "50x60": 900000},
    "yotoq_kommode": {"60x80": 1400000, "100x80": 2000000},
    "oshxona_garnit": {"200x85": 8500000, "240x85": 10500000, "300x85": 13500000},
    "oshxona_stol": {"60x80": 1200000, "80x120": 1800000, "100x160": 2500000},
    "oshxona_stul": {"45x90": 450000, "45x100": 600000},
    "oshxona_javon": {"80x30": 700000, "80x60": 1200000},
}
MATERIAL_MULT = {m[1]: m[2] for m in MATERIALS}
COLOR_LABELS = {v: l for l, v in COLORS}
MAT_LABELS = {m[1]: m[0] for m in MATERIALS}
SUB_NAMES = {}
for cat_data in SUBCATEGORIES.values():
    for name, code in cat_data["items"]:
        SUB_NAMES[code] = name

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mat_val = query.data.replace("mat_", "")
    context.user_data["material"] = mat_val
    ud = context.user_data
    base_price = BASE_PRICES.get(ud["subcategory"], {}).get(ud["size"], 1000000)
    final_price = int(base_price * MATERIAL_MULT.get(mat_val, 1.0))
    ud["final_price"] = final_price
    summary = (
        f"✅ *Buyurtma tafsiloti:*\n\n"
        f"🛋 Mahsulot: *{SUB_NAMES.get(ud['subcategory'])}*\n"
        f"📐 O'lcham: *{ud['size']} sm*\n"
        f"🎨 Rang: *{COLOR_LABELS.get(ud['color'])}*\n"
        f"🪵 Material: *{MAT_LABELS.get(mat_val)}*\n\n"
        f"💰 *Narx: {final_price:,} so'm*"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Buyurtma berish", callback_data="place_order")],
        [InlineKeyboardButton("🔄 Qaytadan tanlash", callback_data="catalog")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="back_start")],
    ]
    await query.edit_message_text(summary, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM

async def place_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    ud = context.user_data
    order_id = db.save_order(
        user_id=user.id, product=SUB_NAMES.get(ud["subcategory"]),
        size=ud["size"], color=ud["color"], material=ud["material"], price=ud["final_price"]
    )
    await query.edit_message_text(
        f"🎉 *Buyurtmangiz qabul qilindi!*\n\n📋 Buyurtma raqami: *#{order_id}*\n\nTez orada menejerimiz siz bilan bog'lanadi. 📞",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Bosh sahifa", callback_data="back_start")]])
    )
    context.user_data.clear()
    return ConversationHandler.END

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    orders = db.get_user_orders(update.effective_user.id)
    if not orders:
        text = "📦 Sizda hali buyurtmalar yo'q."
    else:
        text = "📦 *Sizning buyurtmalaringiz:*\n\n"
        for o in orders:
            e = {"pending": "⏳", "processing": "🔧", "done": "✅", "cancelled": "❌"}.get(o["status"], "📋")
            text += f"{e} *#{o['id']}* — {o['product']}\n   💰 {o['price']:,} so'm\n\n"
    await query.edit_message_text(text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="back_start")]]))

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📞 *Biz bilan bog'laning:*\n\n📱 Telefon: +998 99 664 75 14\n📍 Manzil: Toshkent\n🕐 Ish vaqti: Du–Sha 9:00–18:00",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="back_start")]]))

async def back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛋 Mebel tanlash", callback_data="catalog")],
        [InlineKeyboardButton("📦 Mening buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("📞 Bog'lanish", callback_data="contact")],
    ]
    await query.edit_message_text("🏠 *MebelShop* — Bosh sahifa\n\nQuyidagi bo'limlardan birini tanlang:",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

def main():
    db.connect()
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(catalog, pattern="^catalog$")],
        states={
            CATEGORY:    [CallbackQueryHandler(subcategory, pattern="^cat_")],
            SUBCATEGORY: [CallbackQueryHandler(choose_size, pattern="^sub_")],
            SIZE:        [CallbackQueryHandler(choose_color, pattern="^size_")],
            COLOR:       [CallbackQueryHandler(choose_material, pattern="^color_")],
            MATERIAL:    [CallbackQueryHandler(confirm_order, pattern="^mat_")],
            CONFIRM:     [CallbackQueryHandler(place_order, pattern="^place_order$")],
        },
        fallbacks=[
            CallbackQueryHandler(back_start, pattern="^back_start$"),
            CallbackQueryHandler(catalog, pattern="^catalog$"),
        ],
        per_message=False,
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(my_orders, pattern="^my_orders$"))
    app.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(back_start, pattern="^back_start$"))
    logger.info("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
