import os
import ast
import pandas as pd
import numpy as np
from io import BytesIO
from flask import Blueprint, request, jsonify, session
from supabase import create_client
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression

from .gemini_client import ask_gemini


# ===========================
# 🔧 ENV SETUP
# ===========================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "uploads")

supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


# ===========================
# 💬 BLUEPRINT
# ===========================

chat_bp = Blueprint("chat", __name__)


# ===========================
# 🧠 DATA CONTEXT BUILDER
# ===========================

def build_dataset_context(df):
    try:
        summary = df.describe(include='all').fillna("").to_string()

        top_categories = ""
        if "Category" in df.columns and "Revenue" in df.columns:
            top_categories = df.groupby("Category")["Revenue"].sum()\
                .sort_values(ascending=False).head().to_string()

        sample_data = df.head(5).to_string()

        return f"""
DATASET OVERVIEW:
- Rows: {len(df)}
- Columns: {list(df.columns)}

STATISTICAL SUMMARY:
{summary}

TOP CATEGORY REVENUE:
{top_categories}

SAMPLE DATA:
{sample_data}
"""
    except:
        return "Dataset context unavailable."


# ===========================
# 💬 CHAT API
# ===========================

@chat_bp.route("/ask", methods=["POST"])
def chat_api():

    # ===========================
    # 🔹 DATASET CHECK
    # ===========================
    if "dataset_key" not in session:
        return jsonify({"error": "No dataset uploaded"}), 400

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    user_question = data["message"]
    context = data.get("context")
    lower_q = user_question.lower()

    # ===========================
    # 🔹 LOAD DATASET
    # ===========================
    try:
        file_data = supabase_admin.storage.from_(SUPABASE_BUCKET).download(
            session["dataset_key"]
        )
        df = pd.read_csv(BytesIO(file_data))
    except Exception as e:
        return jsonify({"error": f"Dataset loading failed: {str(e)}"}), 500

    schema_info = {
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict()
    }

    dataset_context = build_dataset_context(df)

    # ===========================
    # 🔥 INSIGHTS PAGE MODE
    # ===========================
    if context == "insights_page":

        visual_summary = session.get("insight_visuals", [])
        red_flags = session.get("red_flag_visuals", [])

        visual_text = "\n".join([
            f"- {v.get('explanation','')} (Severity: {v.get('severity','')})"
            for v in visual_summary if isinstance(v, dict)
        ])

        red_flag_text = "\n".join([
            f"- {r.get('explanation','')} (Severity: {r.get('severity','')})"
            for r in red_flags if isinstance(r, dict)
        ])

        explanation_prompt = f"""
You are an expert data analyst.

{dataset_context}

INSIGHT SUMMARY:
{visual_text}

RED FLAGS:
{red_flag_text}

User Question:
{user_question}

Instructions:
- Explain using both dataset and insights
- Mention risk or trend if relevant
- Be clear and specific
- 2–4 lines only
- No code
"""

        answer = ask_gemini(explanation_prompt) or "Insight indicates variability or dominance patterns affecting performance."

        return jsonify({"answer": answer})

    # ===========================
    # 🔹 DETECT ANALYTICAL QUERY
    # ===========================

    analysis_keywords = [
        "total", "sum", "average", "mean", "max", "min",
        "count", "how many", "forecast", "predict",
        "compare", "growth", "trend",
        "highest", "lowest", "top", "bottom",
        "percentage", "distribution"
    ]

    is_analytical = any(word in lower_q for word in analysis_keywords)

    # ===========================
    # 🧠 EXPLANATION MODE
    # ===========================

    if not is_analytical:

        prompt = f"""
You are a smart business data analyst.

{dataset_context}

User Question:
{user_question}

Instructions:
- Answer using dataset
- Give insights, not generic answer
- Mention values if possible
- 2–4 lines
- No code
"""

        answer = ask_gemini(prompt) or "This reflects trends or performance differences within the dataset."

        return jsonify({"answer": answer})

    # ===========================
    # 🔬 ANALYTICAL MODE (CODE GEN)
    # ===========================

    planning_prompt = f"""
You are a Python data analyst.

DATASET INFO:
Columns: {schema_info['columns']}

{dataset_context}

User Question:
{user_question}

Instructions:
- Generate ONLY Python code
- Use dataframe 'df'
- Store final answer in variable 'result'
- No print statements
"""

    code = ask_gemini(planning_prompt)

    if not code:
        return jsonify({"error": "Failed to generate analysis code"}), 500

    if "```" in code:
        code = code.split("```")[1]

    code = code.replace("python", "").strip()

    try:
        ast.parse(code)
    except:
        return jsonify({"error": "Invalid code generated"}), 500

    try:
        local_vars = {}
        exec(code, {"df": df, "pd": pd, "np": np, "LinearRegression": LinearRegression}, local_vars)

        result = local_vars.get("result")

        if result is None:
            return jsonify({"error": "No result generated"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # ===========================
    # 📊 FORMAT RESULT
    # ===========================

    if isinstance(result, pd.DataFrame):
        result_text = result.head(20).to_string(index=False)
    elif isinstance(result, pd.Series):
        result_text = result.to_string()
    else:
        result_text = str(result)

    # ===========================
    # 🧠 FINAL EXPLANATION
    # ===========================

    explanation_prompt = f"""
You are a business analyst.

User Question:
{user_question}

Computed Result:
{result_text}

Explain:
- What this means
- Why it matters
- Give insight

Keep it short (2–3 lines).
"""

    final_answer = ask_gemini(explanation_prompt) or f"The result is {result_text}"

    return jsonify({"answer": final_answer})