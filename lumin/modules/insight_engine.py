import streamlit as st
import re
from prompts.templates import insight_prompt, why_what_next_prompt
from modules.nl_query import ask_groq

def generate_insight(question, result_df, schema):
    prompt = insight_prompt(question, str(result_df), schema)
    with st.spinner("Generating AI Insight..."):
        insight = ask_groq(prompt)
    if insight:
        st.success(f"📌 **AI Insight**\n\n{insight}")

def generate_why_what_next(question, result_df, schema):
    prompt = why_what_next_prompt(question, str(result_df), schema)
    with st.spinner("Analyzing why and what next..."):
        response = ask_groq(prompt)
    
    with st.expander("🧠 Why did this happen? What should I explore next?"):
        if response:
            lines = response.split('\n')
            explanation = []
            questions = []
            for line in lines:
                if re.match(r'^\d+\.', line.strip()):
                    questions.append(re.sub(r'^\d+\.\s*', '', line.strip()))
                else:
                    if line.strip():
                        explanation.append(line)
            
            st.write(" ".join(explanation))
            
            st.write("**Suggested follow-up questions:**")
            for q in questions[:3]:
                if st.button(q, key=f"btn_{q}"):
                    st.session_state["pending_question"] = q
                    st.rerun()
