# 🧮 Daily Math Problem Solver

An AI-powered daily math practice app for students from **Grade 1 to Grade 12**, **Math Olympiad**, and **IIT JEE** aspirants.

## Features

- 📚 **14 levels** — Grade 1 through Grade 12, Math Olympiad, and IIT JEE
- 🎯 **3 difficulty levels** — Easy, Medium, Hard
- 📐 **Topic-specific problems** — curated topics per grade
- 💡 **Hints** — gentle nudges without spoiling the answer
- 🤖 **AI Step-by-step Explanations** — powered by Claude (Anthropic)
- 🔄 **Infinite problems** — generate as many as you want

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/kessousid/daily-math-problem-solver.git
cd daily-math-problem-solver
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Anthropic API key
Create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```
Get your key at [console.anthropic.com](https://console.anthropic.com).

### 4. Run locally
```bash
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub (secrets.toml is gitignored ✅)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Under **Advanced settings → Secrets**, add:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
5. Click **Deploy**

## Tech Stack

- [Streamlit](https://streamlit.io) — UI framework
- [Anthropic Claude](https://anthropic.com) — AI problem generation & explanation

## License

MIT
