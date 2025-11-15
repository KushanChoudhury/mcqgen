# streamlitapp.py
import streamlit as st
import json
import pandas as pd
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.MCQGenerator import run_pipeline, format_quiz_human
from src.mcqgenerator.logger import logger

st.set_page_config(page_title="MCQ Generator", layout="wide")
st.title("MCQ Generator")

st.markdown(
    "Upload a source file (.pdf or .txt). The app will automatically load your local `response.json` "
    "schema and use it for MCQ generation."
)

RESPONSE_JSON_PATH = "response.json"

try:
    with open(RESPONSE_JSON_PATH, "r", encoding="utf-8") as f:
        RESPONSE_JSON_STRING = f.read()
        json.loads(RESPONSE_JSON_STRING)
except Exception as e:
    st.error(f"Failed to load response.json from {RESPONSE_JSON_PATH}: {e}")
    st.stop()

col_main, col_controls = st.columns([3, 1])

with col_main:
    uploaded_source = st.file_uploader("Source file (.pdf or .txt)", type=["pdf", "txt"])
    run_btn = st.button("Generate MCQs")

with col_controls:
    number = st.number_input("Number of questions", min_value=1, max_value=50, value=5, step=1)
    subject = st.text_input("Subject", value="biology")
    tone = st.selectbox("Tone", ["simple", "academic", "intermediate", "concise"], index=0)
    grade = st.text_input("Grade / audience", value="high-school")


if run_btn:
    if not uploaded_source:
        st.error("Please upload a source file (.pdf or .txt).")
    else:
        try:
            with st.spinner("Reading file..."):
                text = read_file(uploaded_source)

            if not text or not text.strip():
                st.error("Uploaded source file produced no text. Try another file.")
            else:
                with st.spinner("Generating and reviewing MCQs..."):
                    result = run_pipeline(
                        text=text,
                        number=int(number),
                        subject=subject,
                        tone=tone,
                        grade=grade,
                        response_json_string=RESPONSE_JSON_STRING
                    )

                final_quiz = result.get("final_quiz")
                review = result.get("review", {})
                complexity = review.get("complexity_analysis", "")

                st.subheader("Complexity analysis")
                st.write(complexity or "—")

                st.subheader("Quiz (JSON)")
                st.json(final_quiz)

                st.subheader("Human-friendly quiz")
                st.code(format_quiz_human(final_quiz), language="")

                st.subheader("Quiz Table view")
                table_data = get_table_data(json.dumps(final_quiz))
                if table_data:
                    df = pd.DataFrame(table_data)
                    st.dataframe(df)
                else:
                    st.warning("Could not convert quiz to table view.")

        except Exception as e:
            logger.exception("Streamlit MCQ generation failed")
            st.error(f"Error: {e}")
            st.exception(e)
else:
    st.info("Upload a source file and click 'Generate MCQs'. Your local response.json schema will be used automatically.")
