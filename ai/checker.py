from openai import AsyncOpenAI
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def check_writing(topic: str, essay: str) -> dict:
    prompt = f"""You are an expert IELTS examiner. Evaluate the following IELTS Writing Task 2 essay.

Topic: {topic}

Essay:
{essay}

Provide a detailed evaluation in this exact JSON format:
{{
    "band_score": <number between 1-9>,
    "task_achievement": <score 1-9>,
    "coherence_cohesion": <score 1-9>,
    "lexical_resource": <score 1-9>,
    "grammatical_range": <score 1-9>,
    "overall_feedback": "<2-3 sentences general feedback>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>"],
    "corrected_sentences": ["<example corrected sentence if any>"]
}}

Be strict and accurate like a real IELTS examiner."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    import json
    result = json.loads(response.choices[0].message.content)
    return result


async def format_feedback(result: dict) -> str:
    band = result.get("band_score", 0)
    ta = result.get("task_achievement", 0)
    cc = result.get("coherence_cohesion", 0)
    lr = result.get("lexical_resource", 0)
    gr = result.get("grammatical_range", 0)
    feedback = result.get("overall_feedback", "")
    strengths = result.get("strengths", [])
    improvements = result.get("improvements", [])

    # Band emoji
    if band >= 7:
        emoji = "🏆"
    elif band >= 6:
        emoji = "✅"
    elif band >= 5:
        emoji = "📈"
    else:
        emoji = "📚"

    text = f"""{emoji} <b>IELTS Writing Natija</b>

<b>Overall Band Score: {band}/9</b>

📊 <b>Batafsil Baholar:</b>
• Task Achievement: {ta}/9
• Coherence & Cohesion: {cc}/9
• Lexical Resource: {lr}/9
• Grammatical Range: {gr}/9

💬 <b>Umumiy Fikr:</b>
{feedback}

✅ <b>Kuchli tomonlar:</b>
"""
    for s in strengths:
        text += f"• {s}\n"

    text += "\n🔧 <b>Yaxshilash kerak:</b>\n"
    for i in improvements:
        text += f"• {i}\n"

    return text
