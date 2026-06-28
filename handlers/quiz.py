from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random
import database as db

router = Router()

QUIZ_QUESTIONS = [
    {
        "question": "Choose the correct word: The government has introduced new _____ to reduce pollution.",
        "options": ["politics", "policies", "polices", "policy"],
        "answer": "policies",
        "explanation": "'Policies' = siyosatlar (ko'plik). 'Policy' = siyosat (birlik). 'Politics' = siyosat (fan sifatida)."
    },
    {
        "question": "Choose the correct form: She _____ to university since 2020.",
        "options": ["goes", "went", "has been going", "had gone"],
        "answer": "has been going",
        "explanation": "'Since 2020' bilan Present Perfect Continuous ishlatiladi."
    },
    {
        "question": "Which word means 'to make something better'?",
        "options": ["deteriorate", "enhance", "diminish", "neglect"],
        "answer": "enhance",
        "explanation": "'Enhance' = yaxshilamoq, kuchaytirmoq. IELTS Writing da ko'p ishlatiladi."
    },
    {
        "question": "Complete: 'Despite _____ hard, he failed the exam.'",
        "options": ["study", "studied", "studying", "to study"],
        "answer": "studying",
        "explanation": "'Despite' dan keyin -ing shakli keladi: Despite + Ving"
    },
    {
        "question": "Which is correct?",
        "options": [
            "The informations are wrong.",
            "The information is wrong.",
            "The information are wrong.",
            "The informations is wrong."
        ],
        "answer": "The information is wrong.",
        "explanation": "'Information' — sanalmaydigan ot (uncountable noun), shuning uchun 'is' ishlatiladi, ko'plik qo'shimchasi qo'shilmaydi."
    },
    {
        "question": "IELTS Writing Task 2 da minimum necha so'z yozish kerak?",
        "options": ["150", "200", "250", "300"],
        "answer": "250",
        "explanation": "Task 2 da minimum 250 so'z talab qilinadi. Kamroq yozsangiz band score pasayadi."
    },
    {
        "question": "Which linking word shows CONTRAST?",
        "options": ["Furthermore", "Therefore", "However", "Similarly"],
        "answer": "However",
        "explanation": "'However' = lekin, ammo — qarshi fikr bildiradi. 'Furthermore' = qo'shimcha, 'Therefore' = shuning uchun."
    },
    {
        "question": "Choose the academic word: 'The study _____ that exercise improves mental health.'",
        "options": ["says", "tells", "indicates", "speaks"],
        "answer": "indicates",
        "explanation": "'Indicates' = ko'rsatadi, anglatadi — akademik writing da professional ko'rinadi."
    },
    {
        "question": "IELTS Speaking imtihoni necha qismdan iborat?",
        "options": ["2", "3", "4", "5"],
        "answer": "3",
        "explanation": "Part 1: Tanishuv (4-5 daqiqa), Part 2: Cue card (3-4 daqiqa), Part 3: Muhokama (4-5 daqiqa)"
    },
    {
        "question": "Which sentence is grammatically correct?",
        "options": [
            "Each of the students have their own book.",
            "Each of the students has their own book.",
            "Each of the students has its own book.",
            "Each of the students have its own book."
        ],
        "answer": "Each of the students has their own book.",
        "explanation": "'Each' yagona son (singular) — 'has' ishlatiladi. 'Their' = zamonaviy ingliz tilida gender-neutral sifatida qabul qilingan."
    },
]

class QuizStates(StatesGroup):
    answering = State()

@router.callback_query(F.data == "quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    question_data = random.choice(QUIZ_QUESTIONS)
    options = question_data["options"].copy()
    random.shuffle(options)

    await state.set_state(QuizStates.answering)
    await state.update_data(
        question=question_data["question"],
        correct=question_data["answer"],
        explanation=question_data["explanation"]
    )

    builder = InlineKeyboardBuilder()
    for option in options:
        builder.button(text=option, callback_data=f"answer_{option[:30]}")
    builder.button(text="⏭ O'tkazib yuborish", callback_data="skip_quiz")
    builder.adjust(1)

    await callback.message.edit_text(
        f"🎯 <b>Kunlik Quiz</b>\n\n"
        f"❓ <b>{question_data['question']}</b>\n\n"
        f"Javobni tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("answer_"))
async def check_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await callback.answer("Quiz tugagan!")
        return

    user_answer = callback.data.replace("answer_", "")
    correct_answer = data.get("correct", "")
    explanation = data.get("explanation", "")

    # Find full option text
    full_answer = user_answer
    for q in QUIZ_QUESTIONS:
        for opt in q["options"]:
            if opt.startswith(user_answer) or user_answer == opt[:30]:
                full_answer = opt
                break

    is_correct = full_answer == correct_answer or user_answer == correct_answer[:30]

    if is_correct:
        result_text = f"✅ <b>To'g'ri!</b>"
        # Update score
        async with __import__('aiosqlite').connect('ielts_bot.db') as db_conn:
            await db_conn.execute(
                "UPDATE users SET quiz_score = quiz_score + 1 WHERE telegram_id = ?",
                (callback.from_user.id,)
            )
            await db_conn.commit()
    else:
        result_text = f"❌ <b>Noto'g'ri!</b>\n\n✅ To'g'ri javob: <b>{correct_answer}</b>"

    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Keyingi savol", callback_data="quiz")
    builder.button(text="🏠 Menyu", callback_data="menu")
    builder.adjust(1)

    await callback.message.edit_text(
        f"{result_text}\n\n"
        f"💡 <b>Izoh:</b>\n{explanation}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    await state.clear()

@router.callback_query(F.data == "skip_quiz")
async def skip_quiz(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Boshqa savol", callback_data="quiz")
    builder.button(text="🏠 Menyu", callback_data="menu")
    builder.adjust(1)

    await callback.message.edit_text(
        "⏭ Savol o'tkazildi.",
        reply_markup=builder.as_markup()
    )
