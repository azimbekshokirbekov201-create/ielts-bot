from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database as db

router = Router()

def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Writing tekshirish", callback_data="writing")
    builder.button(text="🎯 Kunlik Quiz", callback_data="quiz")
    builder.button(text="📚 IELTS Tips", callback_data="tips")
    builder.button(text="🏃 Marathon", callback_data="marathon")
    builder.button(text="📊 Mening natijalarim", callback_data="progress")
    builder.button(text="💎 Premium", callback_data="premium")
    builder.adjust(2)
    return builder.as_markup()

@router.message(CommandStart())
async def start_handler(message: Message):
    await db.add_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username or ""
    )

    text = f"""👋 Salom, <b>{message.from_user.first_name}</b>!

🎓 <b>Akbar's IELTS Bot</b> ga xush kelibsiz!

Bu bot sizga IELTS imtihoniga tayyorlanishda yordam beradi:

✍️ <b>Writing</b> — Essayingizni AI tekshiradi
🎯 <b>Quiz</b> — Kunlik grammar & vocabulary
📚 <b>Tips</b> — Speaking, Listening, Reading
🏃 <b>Marathon</b> — 30 kunlik intensiv tayyorgarlik
📊 <b>Progress</b> — Natijalaringizni kuzating

Boshlaylik! 👇"""

    await message.answer(text, reply_markup=main_menu(), parse_mode="HTML")

@router.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 <b>Asosiy menyu</b>\n\nNimani xohlaysiz?",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "tips")
async def tips_handler(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Writing Tips", callback_data="tips_writing")
    builder.button(text="🗣 Speaking Tips", callback_data="tips_speaking")
    builder.button(text="👂 Listening Tips", callback_data="tips_listening")
    builder.button(text="📖 Reading Tips", callback_data="tips_reading")
    builder.button(text="🔙 Orqaga", callback_data="menu")
    builder.adjust(2)

    await callback.message.edit_text(
        "📚 <b>IELTS Tips</b>\n\nQaysi bo'lim haqida ma'lumot olmoqchisiz?",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "tips_writing")
async def tips_writing(callback: CallbackQuery):
    text = """✍️ <b>Writing Tips</b>

<b>Task 2 uchun:</b>
• Har doim 250+ so'z yozing
• Kirish (intro), 2 asosiy paragraf, xulosa bo'lsin
• Har paragrafda topic sentence bo'lsin
• Linking words ishlating: However, Moreover, Furthermore
• Shaxsiy fikringizni bildiring

<b>Band 7+ olish uchun:</b>
• Murakkab grammatika ishlating
• Sinonimlardan foydalaning
• Aniq misollar keltiring
• Vaqtni to'g'ri taqsimlang (40 daqiqa)"""

    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="tips")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data == "tips_speaking")
async def tips_speaking(callback: CallbackQuery):
    text = """🗣 <b>Speaking Tips</b>

<b>Part 1:</b>
• Qisqa emas, batafsil javob bering
• Misollar keltiring

<b>Part 2 (Cue Card):</b>
• 1 daqiqa tayyorlaning
• Barcha savollarga javob bering
• 2 daqiqa gapiring

<b>Part 3:</b>
• Chuqur fikr bildiring
• "I think... because..." formulasini ishlating

<b>Umumiy:</b>
• Tezlikni nazorat qiling
• Filler words: "Well, Actually, You know" ishlating
• Xatoni tuzating: 'Sorry, I mean...' """

    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="tips")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data == "tips_listening")
async def tips_listening(callback: CallbackQuery):
    text = """👂 <b>Listening Tips</b>

• Savollarni oldindan o'qing
• Kalit so'zlarga e'tibor bering
• Yozib olayotganda tinglashni to'xtatmang
• Imlo (spelling) ga e'tibor bering
• Javobni o'zgartirish mumkin

<b>Section 4 eng qiyin:</b>
• Akademik mavzular bo'ladi
• Diqqatni jamlang
• Raqamlar va sanalar muhim"""

    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="tips")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data == "tips_reading")
async def tips_reading(callback: CallbackQuery):
    text = """📖 <b>Reading Tips</b>

• Savollarni avval o'qing, keyin matn
• Skimming va scanning texnikasidan foydalaning
• TRUE/FALSE/NOT GIVEN — "NOT GIVEN" ko'p aldaydi
• Vaqtni taqsimlang: har passage 20 daqiqa
• Javob matndagi so'z bilan bo'lishi kerak

<b>Band 7+ uchun:</b>
• Barcha 40 savolga javob bering
• Taxmin qiling — minus yo'q"""

    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="tips")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
