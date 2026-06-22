import sqlite3
from flask import Flask, render_template, request



import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




app = Flask(__name__)


def get_connection():
    conn = sqlite3.connect("ifa.db")
    conn.row_factory = sqlite3.Row
    return conn


def search_plants(keyword):

    conn = get_connection()
    cursor = conn.cursor()

    keyword = f"%{keyword}%"

    cursor.execute("""
        SELECT *
        FROM plants
        WHERE chinese_name LIKE ?
           OR english_name LIKE ?
           OR latin_name LIKE ?
        ORDER BY chinese_name
    """, (
        keyword,
        keyword,
        keyword
    ))

    plants = cursor.fetchall()

    conn.close()

    return plants


def get_random_plant():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM plants
        WHERE chinese_name IS NOT NULL
          AND chinese_name != ''
          AND english_name IS NOT NULL
          AND english_name != ''
          AND latin_name IS NOT NULL
          AND latin_name != ''
        ORDER BY RANDOM()
        LIMIT 1
    """)

    plant = cursor.fetchone()
    conn.close()
    return plant


def get_plant_by_id(plant_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM plants
        WHERE id = ?
    """, (plant_id,))

    plant = cursor.fetchone()
    conn.close()
    return plant


def get_plant_detail(plant_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM plants
        WHERE id = ?
    """, (plant_id,))

    plant = cursor.fetchone()

    conn.close()

    return plant

def get_level(total):
    if total < 20:
        return "🌱 新手學習者"
    elif total < 100:
        return "🌿 持續成長"
    elif total < 300:
        return "🌳 進階學習者"
    else:
        return "🏆 IFA衝刺高手"


def generate_ai_latin_helper(plant):
    return f"""
【AI功能展示版】

植物：
{plant["chinese_name"]}

英文名：
{plant["english_name"]}

拉丁名：
{plant["latin_name"]}

OpenAI API 尚未啟用。

未來將自動產生：

【拉丁文字根解析】
分析拉丁學名中的字根、詞源或可能含義。

【德式拉丁文發音】
產生台灣學生容易閱讀的德式拉丁文發音提示。

【記憶口訣】
根據字根與植物特色，產生幫助記憶的句子。

【考試重點】
整理 IFA 考試複習時需要注意的重點。
"""


def generate_openai_memory_tip(plant):
    prompt = f"""
你是一位芳療植物拉丁文學習助理。
請用繁體中文，幫考生記憶以下植物拉丁學名。

中文名：{plant["chinese_name"]}
英文名：{plant["english_name"]}
拉丁名：{plant["latin_name"]}
屬名：{plant["genus"]}
種名：{plant["species"]}

請輸出：
1. 拉丁名拆解
2. 字根或可能意思
3. 記憶口訣
4. 考試提醒

如果詞源不確定，請寫「可能與……有關」，不要硬編。
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        return response.output_text

    except Exception as e:
        return f"AI 暫時無法產生內容：{str(e)}"





def get_cached_ai(plant_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ai_explanation
        FROM ai_cache
        WHERE plant_id = ?
    """, (plant_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row["ai_explanation"]

    return None


def save_ai_cache(plant_id, ai_explanation):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO ai_cache (
            plant_id,
            ai_explanation
        )
        VALUES (?, ?)
    """, (
        plant_id,
        ai_explanation
    ))

    conn.commit()
    conn.close()



def save_attempt(plant_id, user_answer, correct_answer, is_correct):
    conn = get_connection()
    cursor = conn.cursor()

    user_id = 1

    cursor.execute("""
        INSERT INTO attempts (
            plant_id,
            user_answer,
            correct_answer,
            is_correct,
            user_id
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        plant_id,
        user_answer,
        correct_answer,
        is_correct,
        user_id
    ))

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_connection()
    cursor = conn.cursor()

    user_id = 1

    cursor.execute("""
        SELECT COUNT(*)
        FROM plants
    """)
    plant_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM attempts
        WHERE user_id = ?
    """, (user_id,))
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM attempts
        WHERE user_id = ?
          AND is_correct = 1
    """, (user_id,))
    correct = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT plant_id)
        FROM attempts
        WHERE user_id = ?
          AND is_correct = 1
    """, (user_id,))
    learned_count = cursor.fetchone()[0]

    if total > 0:
        accuracy = round(correct / total * 100, 2)
    else:
        accuracy = 0

    if plant_count > 0:
        progress = round(learned_count / plant_count * 100, 2)
    else:
        progress = 0

    level = get_level(total)

    conn.close()

    return render_template(
        "index.html",
        plant_count=plant_count,
        total=total,
        accuracy=accuracy,
        level=level,
        learned_count=learned_count,
        progress=progress
    )


@app.route("/search", methods=["GET", "POST"])
def search():

    plants = []

    if request.method == "POST":

        keyword = request.form["keyword"]

        plants = search_plants(keyword)

    return render_template(
        "search.html",
        plants=plants
    )

@app.route("/plant/<int:plant_id>", methods=["GET", "POST"])
def plant_detail(plant_id):

    plant = get_plant_detail(plant_id)
    ai_memory = None

    if request.method == "POST":

        cached = get_cached_ai(plant["id"])

        if cached:
            ai_memory = cached
        else:
            ai_memory = generate_openai_memory_tip(plant)
            save_ai_cache(plant["id"], ai_memory)

    return render_template(
        "plant_detail.html",
        plant=plant,
        ai_memory=ai_memory
    )

@app.route("/practice", methods=["GET", "POST"])
def practice():
    result = ""
    old_plant = None
    ai_explanation = None

    if request.method == "POST":
        plant_id = request.form["plant_id"]
        user_answer = request.form["answer"].strip()

        old_plant = get_plant_by_id(plant_id)
        correct_answer = old_plant["latin_name"]

        if user_answer.lower() == correct_answer.lower():
            result = "✅ 答對了！"
            is_correct = 1
        else:
            result = f"❌ 答錯了！正確答案是：{correct_answer}"
            is_correct = 0

        save_attempt(
            plant_id,
            user_answer,
            correct_answer,
            is_correct
        )

        ai_explanation = generate_ai_latin_helper(old_plant)

    plant = get_random_plant()

    return render_template(
        "practice.html",
        plant=plant,
        old_plant=old_plant,
        result=result,
        ai_explanation=ai_explanation
    )


@app.route("/stats")
def stats():
    conn = get_connection()
    cursor = conn.cursor()

    user_id = 1

    cursor.execute("""
        SELECT COUNT(*)
        FROM attempts
        WHERE user_id = ?
    """, (user_id,))
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM attempts
        WHERE user_id = ?
          AND is_correct = 1
    """, (user_id,))
    correct = cursor.fetchone()[0]

    wrong = total - correct

    if total > 0:
        accuracy = round(correct / total * 100, 2)
    else:
        accuracy = 0

    level = get_level(total)

    cursor.execute("""
        SELECT
            p.chinese_name,
            p.english_name,
            p.latin_name,
            COUNT(*) AS wrong_count
        FROM attempts a
        JOIN plants p
        ON a.plant_id = p.id
        WHERE a.user_id = ?
          AND a.is_correct = 0
        GROUP BY a.plant_id
        ORDER BY wrong_count DESC
        LIMIT 10
    """, (user_id,))
    wrong_plants = cursor.fetchall()

    cursor.execute("""
        SELECT
            p.chinese_name,
            p.english_name,
            p.latin_name,
            a.is_correct,
            a.created_at
        FROM attempts a
        JOIN plants p
        ON a.plant_id = p.id
        WHERE a.user_id = ?
        ORDER BY a.id DESC
        LIMIT 10
    """, (user_id,))
    recent_attempts = cursor.fetchall()

    conn.close()

    return render_template(
        "stats.html",
        total=total,
        correct=correct,
        wrong=wrong,
        accuracy=accuracy,
        level=level,
        wrong_plants=wrong_plants,
        recent_attempts=recent_attempts
    )


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)