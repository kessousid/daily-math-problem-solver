import streamlit as st
import anthropic
import re

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Daily Math Problem Solver",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .problem-box {
        background: linear-gradient(135deg, #f5f7fa, #e8ecf1);
        border-left: 5px solid #667eea;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        font-size: 1.15rem;
        line-height: 1.8;
        margin: 1rem 0;
    }
    .solution-box {
        background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
        border-left: 5px solid #4caf50;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
    }
    .hint-box {
        background: linear-gradient(135deg, #fff8e1, #fffde7);
        border-left: 5px solid #ffc107;
        border-radius: 12px;
        padding: 1.2rem 1.8rem;
        margin: 1rem 0;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-right: 0.4rem;
    }
    .badge-easy   { background:#d4edda; color:#155724; }
    .badge-medium { background:#fff3cd; color:#856404; }
    .badge-hard   { background:#f8d7da; color:#721c24; }
    .badge-grade  { background:#cce5ff; color:#004085; }
    .badge-topic  { background:#e2d9f3; color:#4a235a; }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
GRADES = [
    "Grade 1", "Grade 2", "Grade 3", "Grade 4",
    "Grade 5", "Grade 6", "Grade 7", "Grade 8",
    "Grade 9", "Grade 10", "Grade 11", "Grade 12",
    "Math Olympiad", "IIT JEE",
]

DIFFICULTIES = ["Easy", "Medium", "Hard"]

GRADE_TOPICS = {
    "Grade 1":  ["Counting & Numbers", "Addition", "Subtraction", "Shapes", "Measurement"],
    "Grade 2":  ["Place Value", "Addition & Subtraction", "Multiplication Intro", "Fractions Intro", "Time & Money"],
    "Grade 3":  ["Multiplication", "Division", "Fractions", "Geometry", "Data & Graphs"],
    "Grade 4":  ["Multi-digit Arithmetic", "Fractions & Decimals", "Angles", "Area & Perimeter", "Factors & Multiples"],
    "Grade 5":  ["Fractions Operations", "Decimals", "Volume", "Coordinate Plane", "Algebraic Thinking"],
    "Grade 6":  ["Ratios & Rates", "Integers", "Expressions & Equations", "Geometry", "Statistics"],
    "Grade 7":  ["Proportional Reasoning", "Linear Equations", "Geometry", "Probability", "Statistics"],
    "Grade 8":  ["Linear Functions", "Systems of Equations", "Pythagorean Theorem", "Transformations", "Statistics"],
    "Grade 9":  ["Algebra I", "Quadratics", "Functions", "Statistics", "Geometry"],
    "Grade 10": ["Algebra II", "Trigonometry", "Coordinate Geometry", "Probability", "Polynomials"],
    "Grade 11": ["Calculus Intro", "Vectors", "Complex Numbers", "Sequences & Series", "Statistics"],
    "Grade 12": ["Calculus", "Matrices", "Probability & Statistics", "Differential Equations Intro", "3D Geometry"],
    "Math Olympiad": ["Number Theory", "Combinatorics", "Geometry", "Algebra", "Inequalities"],
    "IIT JEE":  ["Calculus", "Algebra", "Coordinate Geometry", "Trigonometry", "Vectors & 3D"],
}

DIFFICULTY_EMOJI = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}

# ── API client ────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        api_key = None
    if not api_key:
        st.error(
            "**Anthropic API key not found.**\n\n"
            "Add it to `.streamlit/secrets.toml`:\n```\nANTHROPIC_API_KEY = 'sk-ant-...'\n```\n"
            "or set the `ANTHROPIC_API_KEY` environment variable.",
            icon="🔑",
        )
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

# ── Helpers ───────────────────────────────────────────────────────────────────
def build_problem_prompt(grade: str, difficulty: str, topic: str) -> str:
    jee_note = (
        " This is for IIT JEE preparation — use JEE Main/Advanced style and difficulty."
        if grade == "IIT JEE" else ""
    )
    olympiad_note = (
        " This is for Math Olympiad — the problem should require elegant, non-routine reasoning."
        if grade == "Math Olympiad" else ""
    )
    return f"""You are an expert mathematics teacher. Generate a single, self-contained math problem for:
- Level: {grade}{jee_note}{olympiad_note}
- Topic: {topic}
- Difficulty: {difficulty}

Format your response EXACTLY as follows (use these exact section headers):

PROBLEM:
<Write the complete problem statement here. Use plain text with LaTeX math notation where needed, e.g. $x^2 + 3x + 2 = 0$. Do NOT include the answer.>

TOPIC TAG:
<One short topic label, e.g. "Quadratic Equations">

HINT:
<One subtle hint that nudges without giving away the answer>

Keep the problem clear, unambiguous, and appropriate for the level. Do not include the solution."""


def build_solution_prompt(grade: str, difficulty: str, problem: str) -> str:
    jee_note = " Use JEE-style approach with shortcuts where applicable." if grade == "IIT JEE" else ""
    olympiad_note = " Show the elegant olympiad-style reasoning." if grade == "Math Olympiad" else ""
    return f"""You are an expert, patient mathematics tutor explaining a solution to a {grade} student.{jee_note}{olympiad_note}

Problem:
{problem}

Provide a COMPLETE step-by-step solution. Structure it as:

ANSWER:
<Give the final answer first, clearly>

STEP-BY-STEP SOLUTION:
<Numbered steps, each explaining the WHY behind the step. Use LaTeX math notation e.g. $expression$.>

KEY CONCEPT:
<In 1-2 sentences, state the core mathematical idea this problem tests>

COMMON MISTAKES:
<List 1-2 common mistakes students make on this type of problem>

Tailor the depth and vocabulary to a {grade} student at {difficulty} level."""


def parse_problem(text: str) -> dict:
    result = {"problem": text, "topic_tag": "", "hint": ""}
    m = re.search(r"PROBLEM:\s*(.*?)(?=TOPIC TAG:|HINT:|$)", text, re.DOTALL | re.IGNORECASE)
    if m:
        result["problem"] = m.group(1).strip()
    m = re.search(r"TOPIC TAG:\s*(.*?)(?=HINT:|$)", text, re.DOTALL | re.IGNORECASE)
    if m:
        result["topic_tag"] = m.group(1).strip()
    m = re.search(r"HINT:\s*(.*?)$", text, re.DOTALL | re.IGNORECASE)
    if m:
        result["hint"] = m.group(1).strip()
    return result


def stream_response(client, prompt: str, placeholder):
    full_text = ""
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            full_text += text
            placeholder.markdown(full_text + "▌")
    placeholder.markdown(full_text)
    return full_text


# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "problem_data": None,
    "solution": None,
    "show_hint": False,
    "show_solution": False,
    "problem_count": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Layout ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🧮 Daily Math Problem Solver</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">From Grade 1 to IIT JEE & Math Olympiad — powered by AI</div>',
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    grade = st.selectbox("📚 Select Grade / Level", GRADES, index=0)
    topics = GRADE_TOPICS.get(grade, ["General"])
    topic = st.selectbox("📐 Topic", topics)
    difficulty = st.radio(
        "🎯 Difficulty",
        DIFFICULTIES,
        index=1,
        format_func=lambda d: f"{DIFFICULTY_EMOJI[d]} {d}",
    )
    st.divider()
    generate_btn = st.button("✨ Generate New Problem", use_container_width=True, type="primary")
    st.divider()
    st.markdown(f"**Problems solved this session:** {st.session_state.problem_count} 🏆")
    st.markdown("""
---
**Tips:**
- Try solving before peeking at hints
- Use the AI explanation to understand *why*, not just *what*
- Challenge yourself: try a harder difficulty next!
""")

# ── Main area ─────────────────────────────────────────────────────────────────
if generate_btn:
    st.session_state.show_hint = False
    st.session_state.show_solution = False
    st.session_state.solution = None

    client = get_client()
    prompt = build_problem_prompt(grade, difficulty, topic)

    with st.spinner("Generating your problem..."):
        placeholder = st.empty()
        raw = stream_response(client, prompt, placeholder)
        placeholder.empty()

    st.session_state.problem_data = {
        **parse_problem(raw),
        "grade": grade,
        "difficulty": difficulty,
        "topic": topic,
    }

if st.session_state.problem_data:
    data = st.session_state.problem_data
    diff_class = data["difficulty"].lower()
    topic_tag = data["topic_tag"] or data["topic"]

    # Badges
    st.markdown(
        f'<span class="badge badge-grade">{data["grade"]}</span>'
        f'<span class="badge badge-{diff_class}">{DIFFICULTY_EMOJI[data["difficulty"]]} {data["difficulty"]}</span>'
        f'<span class="badge badge-topic">📐 {topic_tag}</span>',
        unsafe_allow_html=True,
    )

    # Problem box
    st.markdown(
        f'<div class="problem-box">{data["problem"]}</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("💡 Show Hint", use_container_width=True):
            st.session_state.show_hint = not st.session_state.show_hint

    with col2:
        if st.button("🔍 Show Solution & AI Explanation", use_container_width=True, type="primary"):
            st.session_state.show_solution = True
            if not st.session_state.solution:
                client = get_client()
                sol_prompt = build_solution_prompt(
                    data["grade"], data["difficulty"], data["problem"]
                )
                sol_placeholder = st.empty()
                solution_text = stream_response(client, sol_prompt, sol_placeholder)
                sol_placeholder.empty()
                st.session_state.solution = solution_text
                st.session_state.problem_count += 1

    with col3:
        if st.button("🔄 New Problem (Same Settings)", use_container_width=True):
            st.session_state.show_hint = False
            st.session_state.show_solution = False
            st.session_state.solution = None
            client = get_client()
            prompt = build_problem_prompt(data["grade"], data["difficulty"], data["topic"])
            with st.spinner("Generating..."):
                placeholder = st.empty()
                raw = stream_response(client, prompt, placeholder)
                placeholder.empty()
            st.session_state.problem_data = {
                **parse_problem(raw),
                "grade": data["grade"],
                "difficulty": data["difficulty"],
                "topic": data["topic"],
            }
            st.rerun()

    # Hint
    if st.session_state.show_hint and data.get("hint"):
        st.markdown(
            f'<div class="hint-box"><strong>💡 Hint:</strong><br>{data["hint"]}</div>',
            unsafe_allow_html=True,
        )

    # Solution
    if st.session_state.show_solution and st.session_state.solution:
        st.markdown(
            f'<div class="solution-box">{st.session_state.solution}</div>',
            unsafe_allow_html=True,
        )

else:
    # Welcome screen
    st.info(
        "👈 **Select your grade, topic, and difficulty from the sidebar, then click "
        "'Generate New Problem' to get started!**",
        icon="🚀",
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
### 🎓 For All Levels
From basic counting (Grade 1) to advanced Calculus & Olympiad problems.
        """)
    with col2:
        st.markdown("""
### 🤖 AI-Powered
Step-by-step explanations tailored to your grade — understand the *why*, not just the answer.
        """)
    with col3:
        st.markdown("""
### 📈 Build Daily Habits
One problem a day keeps exam anxiety away. Track your streak this session!
        """)

st.markdown('<div class="footer">Built with ❤️ using Streamlit & Claude AI</div>', unsafe_allow_html=True)
