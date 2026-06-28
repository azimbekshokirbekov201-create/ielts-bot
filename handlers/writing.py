from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database as db
from ai.checker import check_writing, format_feedback

router = Router()

# Writing topics
WRITING_TOPICS = [
    "Some people think that the best way to reduce crime is to give longer prison sentences. Others, however, believe there are better alternative ways of reducing crime. Discuss both views and give your own opinion.",
    "In many countries, the number of animals and plants is declining. Why do you think this is happening? How can this issue be addressed?",
    "Some people believe that it is best to accept a bad situation, such as an unsatisfactory job or shortage of money. Others argue that it is better to try and improve such situations. Discuss both views and give your own opinion.",
    "The internet has transformed the way information is shared and consumed, but it has also created problems that did not exist before. What are the most serious problems associated with the internet and what solutions can you suggest?",
    "Some people think that modern technology is making people more sociable, while others think it is making them less sociable. Discuss both views and give your own opinion.",
    "Many people believe that social networking sites have had a huge negative impact on both individuals and society. To what extent do you agree?",
    "In some countries, young people are encouraged to work or travel for a year between finishing high school and starting university. Discuss the advantages and disadvantages for young people who decide to do this.",
    "Some people think that a sense of competition in children should be encouraged. Others believe that children who are taught to co-operate rather than compete become more useful adults. Discuss both views and give your own opinion.",
]

# Premium limit
FREE_WRITING_LIMIT = 3

class WritingStates(StatesGroup):
    waiting_for_essay = State()

@router.callback_query(F.data == "writing")
async def writing_menu(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    premium = await db.is_premium(callback.from_user.id)

    writing_count = user[6] if user else 0

    if not premium and writing_count >= FREE_WRITING_LIMIT:
        builder = InlineKeyboardBuilder()
        builder.button(text="💎 Premium olish", callback_data="premium")
        builder.button(text="🔙 Orqaga", callback_data="menu")
        builder.adjust(1)

        await callback.message.edit_text(
            f"❌ <b>Bepul limit tugadi!</b>\n\n"
            f"Siz {FREE_WRITING_LIMIT} ta bepul writing tekshiruvidan foydalandingiz.\n\n"
            f"💎 <b>Premium</b> oling va cheksiz tekshiring!",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        return

    import random
    topic = random.choice(WRITING_TOPICS)

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Boshqa topik", callback_data="writing")
    builder.button(text="🔙 Orqaga", callback_data="menu")
    builder.adjust(1)

    await callback.message.edit_text(
        f"✍️ <b>Writing Task 2</b>\n\n"
        f"📝 <b>Topik:</b>\n{topic}\n\n"
        f"📌 <b>Ko'rsatmalar:</b>\n"
        f"• Kamida 250 so'z yozing\n"
        f"• Vaqt: 40 daqiqa\n"
        f"• Essayingizni yozib, shu chatga yuboring\n\n"
        f"✏️ Yozishni boshlang!",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    # Store topic in FSM
    # We need state here, but callback doesn't have state directly
    # Will handle via message handler below

@router.callback_query(F.data == "writing_start")
async def writing_start(callback: CallbackQuery, state: FSMContext):
    import random
    topic = random.choice(WRITING_TOPICS)

    await state.set_state(WritingStates.waiting_for_essay)
    await state.update_data(topic=topic)

    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data="cancel_writing")
    builder.adjust(1)

    await callback.message.answer(
        f"✍️ <b>Writing Task 2</b>\n\n"
        f"📝 <b>Topik:</b>\n{topic}\n\n"
        f"📌 <b>Ko'rsatmalar:</b>\n"
        f"• Kamida 250 so'z yozing\n"
        f"• Vaqt: 40 daqiqa\n\n"
        f"✏️ Essayingizni yozing va yuboring:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "writing_new")
async def writing_new(callback: CallbackQuery, state: FSMContext):
    await writing_start(callback, state)

@router.callback_query(F.data == "cancel_writing")
async def cancel_writing(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    from handlers.start import main_menu
    await callback.message.edit_text(
        "❌ Writing bekor qilindi.\n\n🏠 Asosiy menyu:",
        reply_markup=main_menu()
    )

@router.message(WritingStates.waiting_for_essay)
async def process_essay(message: Message, state: FSMContext):
    essay = message.text

    # Check word count
    word_count = len(essay.split())
    if word_count < 50:
        await message.answer(
            f"⚠️ Essay juda qisqa ({word_count} so'z).\n"
            f"Kamida 250 so'z yozing!"
        )
        return

    data = await state.get_data()
    topic = data.get("topic", "General IELTS Writing Task 2")

    # Show loading message
    loading_msg = await message.answer(
        "⏳ <b>Essayingiz tekshirilmoqda...</b>\n\n"
        "🤖 AI tahlil qilmoqda, biroz kuting...",
        parse_mode="HTML"
    )

    try:
        result = await check_writing(topic, essay)
        feedback_text = await format_feedback(result)
        band_score = result.get("band_score", 0)

        # Save to DB
        await db.save_writing(
            telegram_id=message.from_user.id,
            topic=topic,
            essay=essay,
            feedback=feedback_text,
            band_score=band_score
        )

        # Delete loading message
        await loading_msg.delete()

        # Send feedback
        builder = InlineKeyboardBuilder()
        builder.button(text="✍️ Yana yozish", callback_data="writing_new")
        builder.button(text="📊 Natijalarim", callback_data="progress")
        builder.button(text="🏠 Menyu", callback_data="menu")
        builder.adjust(2)

        await message.answer(
            feedback_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

        await state.clear()

    except Exception as e:
        await loading_msg.delete()
        await message.answer(
            "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
        )
        await state.clear()
