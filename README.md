# AI: Personalized Data Analyst

An AI-powered data analytics platform that turns plain English into live charts, 
insights and decisions — no code required.

🔗 **Live Demo:** [ai-personalized-data-analyst.streamlit.app](https://ai-personalized-data-analyst.streamlit.app/)

---

## What it does

Upload any CSV or Excel file and ask questions like:
- *"Show total sales by region as a bar chart"*
- *"Which products have the highest return rates?"*
- *"What happens if marketing spend increases by 20%?"*

The AI converts your question into Pandas code, executes it in a safe sandbox, 
and visualizes the result automatically using Plotly.

---

## Features

| Feature | Description |
|---|---|
| 📊 Data Explorer | Ask questions in plain English, get instant charts + AI insights |
| 💬 Chat Analyst | Conversational follow-up questions with memory |
| 🔍 Anomaly Detector | Detect outliers using IQR and Isolation Forest side by side |
| 🔮 What-If Simulator | Adjust any column by % and see ripple effects on correlated columns |
| 🗄️ SQL Mode | See the SQL equivalent of every Pandas query generated |
| 📂 Multi-file Support | Upload multiple files, join them on common columns, cross-query |

---

## Tech Stack

- **LLM** — Groq LLaMA 3.3 70B (fast inference)
- **Frontend** — Streamlit
- **Data** — Pandas, NumPy
- **Charts** — Plotly
- **ML** — scikit-learn (Isolation Forest)
- **Language** — Python 3.11

---

## Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/piyushparanjape98/AI-Personalized-Data-Analyst.git
cd AI-Personalized-Data-Analyst
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

Create a file `lumin/.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key at [console.groq.com](https://console.groq.com)

**5. Run the app**
```bash
cd lumin
streamlit run app.py
```

---

## Project Structure
```
AI-Personalized-Data-Analyst/
├── lumin/
│   ├── app.py                  # Main app entry point
│   ├── modules/
│   │   ├── nl_query.py         # NL → Pandas code generation
│   │   ├── visualizer.py       # Auto chart rendering
│   │   ├── chat_memory.py      # Conversational analyst
│   │   ├── anomaly_detector.py # IQR + Isolation Forest
│   │   ├── what_if.py          # What-If simulator
│   │   ├── insight_engine.py   # AI insight generation
│   │   └── data_loader.py      # File loading + schema
│   ├── prompts/
│   │   └── templates.py        # All LLM prompt templates
│   ├── ui/
│   │   ├── styles.py           # CSS theme
│   │   └── components.py       # Reusable UI components
│   └── .env                    # API key (not committed)
└── requirements.txt
```

---

## How it works

The system never asks the LLM to do math directly — LLMs hallucinate on calculations.

Instead:
1. User asks a question in plain English
2. LLM generates Pandas/SQL code to answer it
3. Code runs in a sandboxed environment
4. Result is visualized automatically

This combines the linguistic power of AI with the computational precision of Python.

---

## Deploy your own

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set main file to `lumin/app.py`
4. Add your `GROQ_API_KEY` in Advanced Settings → Secrets
5. Deploy

---

Built by [Piyush Paranjape](https://github.com/piyushparanjape98)
