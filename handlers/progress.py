from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database as db

router = Router()

@router.callback_query(F.data == "progress")
async def progress_handler(callback: CallbackQuery):
    stats = await db.get_stats(callback.from_user.id)
    history = await db.get_writing_history(callback.from_user.id, limit=5)

    if not stats:
        await callback.answer("Ma'lumot topilmadi!")
        return

    writing_count, quiz_score, is_premium_user = stats

    premium_text = "💎 Premium" if is_premium_user else "🆓 Bepul"

    text = f"""📊 <b>Mening Natijalarim</b>

👤 <b>{callback.from_user.full_name}</b>
🏷 Tarif: {premium_text}

📈 <b>Statistika:</b>
• ✍️ Writing tekshirildi: {writing_count} ta
• 🎯 Quiz to'g'ri javobi: {quiz_score} ta

"""

    if history:
        text += "📝 <b>So'nggi Writing natijalari:</b>\n"
        for i, (topic, band, created_at) in enumerate(history, 1):
            short_topic = topic[:40] + "..." if len(topic) > 40 else topic
            text += f"{i}. Band {band} — {short_topic}\n"
    else:
        text += "📝 Hali writing tekshirmadingiz.\n"

    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Writing boshlash", callback_data="writing_new")
    builder.button(text="🏠 Menyu", callback_data="menu")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "premium")
async def premium_handler(callback: CallbackQuery):
    is_premium_user = await db.is_premium(callback.from_user.id)

    if is_premium_user:
        await callback.message.edit_text(
            "💎 <b>Siz allaqachon Premium foydalanuvchisiz!</b>\n\n"
            "✅ Cheksiz writing tekshirish\n"
            "✅ Barcha funksiyalar ochiq\n"
            "✅ Ustunlik xizmati",
            reply_markup=InlineKeyboardBuilder().button(
                text="🏠 Menyu", callback_data="menu"
            ).as_markup(),
            parse_mode="HTML"
        )
        return

    text = """💎 <b>Premium Tarif</b>

<b>Bepul tarif:</b>
• ✍️ 3 ta writing tekshirish
• 🎯 Kunlik quiz
• 📚 IELTS Tips

<b>💎 Premium tarif:</b>
• ✍️ Cheksiz writing tekshirish
• 🎯 Kunlik quiz
• 📚 Barcha materiallar
• 🏃 Marathon va challengelar
• 📊 Batafsil statistika
• ⚡️ Tezkor javob

💰 <b>Narx: 49,000 so'm/oy</b>

📲 To'lov uchun admin bilan bog'laning:"""

    builder = InlineKeyboardBuilder()
    builder.button(text="👨‍💼 Admin bilan bog'lanish", url="https://t.me/Akbarxonaminjonov")
    builder.button(text="🏠 Menyu", callback_data="menu")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "marathon")
async def marathon_handler(callback: CallbackQuery):
    text = """🏃 <b>30 Kunlik IELTS Marathon</b>

<b>Nima bu?</b>
Har kuni bitta topshiriq — 30 kunda IELTS ga to'liq tayyorgarlik!

<b>Marathon tarkibi:</b>
• 📝 Kunlik writing topshirig'i
• 🎯 Grammar & Vocabulary
• 🗣 Speaking practice
• 📖 Reading strategiyalar

<b>Keyingi marathon:</b>
🗓 Tez orada boshlanadi!

📢 Kanal orqali xabar beriladi."""

    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Kanalga o'tish", url="https://t.me/+3STzzcyleVIzZTc6")
    builder.button(text="🏠 Menyu", callback_data="menu")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
