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
    .section-label {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
        margin-top: 1rem;
    }
    .label-problem  { color: #667eea; }
    .label-hint     { color: #e6a817; }
    .label-solution { color: #2e7d32; }
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
    div[data-testid="stAlert"] {
        border-radius: 12px;
        font-size: 1.05rem;
        line-height: 1.8;
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

# ── Curriculum ─────────────────────────────────────────────────────────────────
# Structure: Grade → Topic → [Subtopics]
GRADE_CURRICULUM = {
    "Grade 1": {
        "Counting & Numbers": [
            "Counting 1–20", "Counting 1–100", "Number Ordering & Sequencing",
            "Even & Odd Numbers", "Comparing Numbers (>, <, =)",
        ],
        "Addition": [
            "Adding Single-digit Numbers", "Number Bonds to 10",
            "Number Bonds to 20", "Adding with a Number Line", "Word Problems",
        ],
        "Subtraction": [
            "Subtracting Single-digit Numbers", "Finding the Difference",
            "Subtraction on a Number Line", "Word Problems",
        ],
        "Shapes & Patterns": [
            "2D Shapes (Circle, Square, Triangle, Rectangle)",
            "3D Shapes (Cube, Sphere, Cone, Cylinder)",
            "Sorting & Classifying Shapes", "Repeating Patterns",
        ],
        "Measurement & Time": [
            "Comparing Lengths (Longer / Shorter)", "Comparing Weights (Heavier / Lighter)",
            "Telling Time (O'Clock & Half Past)", "Days of the Week & Months",
        ],
    },

    "Grade 2": {
        "Place Value": [
            "Tens and Ones", "Hundreds, Tens and Ones",
            "Expanded Form", "Comparing 3-digit Numbers",
        ],
        "Addition & Subtraction": [
            "2-digit Addition (No Regrouping)", "2-digit Addition (With Regrouping)",
            "2-digit Subtraction (No Regrouping)", "2-digit Subtraction (With Regrouping)",
            "Word Problems",
        ],
        "Multiplication Introduction": [
            "Equal Groups", "Arrays", "Skip Counting (2s, 5s, 10s)",
            "Multiplication as Repeated Addition",
        ],
        "Fractions Introduction": [
            "Halves", "Quarters (Fourths)", "Thirds",
            "Identifying Fractions of a Shape",
        ],
        "Measurement, Time & Money": [
            "Measuring Length (cm & m)", "Telling Time (Quarter Past / To)",
            "Counting Coins", "Simple Money Problems",
        ],
    },

    "Grade 3": {
        "Multiplication": [
            "Times Tables (2–5)", "Times Tables (6–10)", "Multiplication Properties",
            "Multiplying by 10 & 100", "Word Problems",
        ],
        "Division": [
            "Equal Sharing", "Division as Repeated Subtraction",
            "Division Facts (Related to Times Tables)", "Remainders Introduction",
        ],
        "Fractions": [
            "Equivalent Fractions", "Comparing & Ordering Fractions",
            "Fractions on a Number Line", "Simple Addition of Like Fractions",
        ],
        "Geometry": [
            "Perimeter of Polygons", "Area by Counting Squares",
            "Types of Angles", "Quadrilaterals & Their Properties",
        ],
        "Data & Graphs": [
            "Tally Charts", "Bar Graphs", "Pictographs", "Reading & Interpreting Data",
        ],
    },

    "Grade 4": {
        "Multi-digit Arithmetic": [
            "Multi-digit Multiplication", "Long Division (No Remainder)",
            "Long Division (With Remainder)", "Estimation & Rounding", "Word Problems",
        ],
        "Fractions & Decimals": [
            "Adding & Subtracting Like Fractions", "Mixed Numbers & Improper Fractions",
            "Decimal Place Value (Tenths & Hundredths)",
            "Comparing & Ordering Decimals",
        ],
        "Angles & Geometry": [
            "Measuring Angles with a Protractor", "Types of Angles (Acute, Obtuse, Reflex)",
            "Angles on a Straight Line", "Angles in a Triangle",
        ],
        "Area & Perimeter": [
            "Area of Rectangles & Squares", "Perimeter of Polygons",
            "Area of Composite Shapes", "Units of Area (cm², m²)",
        ],
        "Factors & Multiples": [
            "Factors of a Number", "Multiples & LCM",
            "Prime & Composite Numbers", "Highest Common Factor (HCF)",
        ],
    },

    "Grade 5": {
        "Fractions Operations": [
            "Adding & Subtracting Unlike Fractions", "Multiplying Fractions",
            "Dividing Fractions", "Fraction Word Problems", "Mixed Number Operations",
        ],
        "Decimals": [
            "Adding & Subtracting Decimals", "Multiplying Decimals",
            "Dividing Decimals", "Rounding & Estimation",
        ],
        "Ratios & Percentages": [
            "Introduction to Ratios", "Equivalent Ratios",
            "Percentages (Finding % of a Number)", "Percentage Word Problems",
        ],
        "Geometry & Volume": [
            "Volume of Cuboids", "Surface Area of Cuboids",
            "Coordinate Plane (Quadrant I)", "Plotting & Reading Coordinates",
        ],
        "Algebraic Thinking": [
            "Numerical Expressions & Order of Operations (BODMAS)",
            "Simple Algebraic Expressions", "Patterns & Rules",
            "Introduction to Equations",
        ],
    },

    "Grade 6": {
        "Ratios & Rates": [
            "Ratios & Equivalent Ratios", "Unit Rates", "Proportions",
            "Percentage (Increase & Decrease)", "Speed, Distance & Time",
        ],
        "Integers": [
            "Introduction to Negative Numbers", "Adding Integers",
            "Subtracting Integers", "Multiplying & Dividing Integers",
            "Absolute Value",
        ],
        "Expressions & Equations": [
            "Algebraic Expressions (Simplification)", "Substitution",
            "One-step Equations", "Two-step Equations", "Inequalities",
        ],
        "Geometry": [
            "Area of Triangles & Parallelograms", "Area of Trapezoids",
            "Circumference & Area of Circles", "Nets & Surface Area",
            "Volume of Prisms",
        ],
        "Statistics": [
            "Mean, Median, Mode & Range", "Frequency Tables",
            "Bar Charts & Histograms", "Pie Charts",
            "Interpreting Data & Outliers",
        ],
    },

    "Grade 7": {
        "Proportional Reasoning": [
            "Direct Proportion", "Inverse Proportion",
            "Percentage Problems (Profit & Loss)", "Simple Interest",
            "Ratio & Proportion Word Problems",
        ],
        "Linear Equations": [
            "Forming & Solving Linear Equations", "Equations with Variables on Both Sides",
            "Linear Inequalities", "Word Problems with Linear Equations",
        ],
        "Geometry": [
            "Angles in Parallel Lines (Alternate, Corresponding, Co-interior)",
            "Angle Sum of Polygons", "Circle Theorems (Basic)",
            "Congruence & Similarity", "Construction & Loci",
        ],
        "Probability": [
            "Sample Space & Events", "Simple Probability",
            "Complementary Events", "Experimental vs Theoretical Probability",
            "Tree Diagrams",
        ],
        "Statistics": [
            "Box Plots & Stem-and-Leaf Plots", "Scatter Plots & Correlation",
            "Mean from Grouped Data", "Comparing Two Data Sets",
        ],
    },

    "Grade 8": {
        "Linear Functions": [
            "Gradient (Slope) of a Line", "Equation of a Line (y = mx + c)",
            "Graphing Linear Functions", "Parallel & Perpendicular Lines",
            "Rate of Change",
        ],
        "Systems of Equations": [
            "Solving by Substitution", "Solving by Elimination",
            "Graphical Solution", "Word Problems with 2 Unknowns",
        ],
        "Quadratics (Introduction)": [
            "Expanding Brackets & Identities", "Factoring (Common Factor & Grouping)",
            "Factoring Trinomials (x² + bx + c)", "Difference of Two Squares",
        ],
        "Pythagorean Theorem": [
            "Finding the Hypotenuse", "Finding a Missing Side",
            "Distance Between Two Points", "Applications in 3D",
        ],
        "Exponents & Surds": [
            "Laws of Exponents", "Negative & Fractional Exponents",
            "Introduction to Surds (√)", "Simplifying Surds",
        ],
    },

    "Grade 9": {
        "Algebra": [
            "Polynomials (Addition, Subtraction, Multiplication)",
            "Polynomial Division & Remainder Theorem",
            "Rational Expressions (Simplification)", "Factoring Advanced (Sum/Difference of Cubes)",
        ],
        "Quadratic Equations": [
            "Solving by Factoring", "Completing the Square",
            "Quadratic Formula", "Discriminant & Nature of Roots",
            "Quadratic Word Problems",
        ],
        "Functions": [
            "Function Notation & Evaluation", "Domain & Range",
            "Inverse Functions", "Composite Functions",
            "Graphing Functions (Parabolas, Cubics)",
        ],
        "Coordinate Geometry": [
            "Distance & Midpoint Formula", "Equation of a Circle",
            "Tangent to a Circle", "Collinearity & Area of Triangle",
        ],
        "Statistics & Probability": [
            "Measures of Dispersion (Variance & Standard Deviation)",
            "Normal Distribution (Introduction)", "Conditional Probability",
            "Permutations", "Combinations",
        ],
    },

    "Grade 10": {
        "Advanced Algebra": [
            "Exponential & Logarithmic Functions",
            "Laws of Logarithms", "Exponential Equations",
            "Absolute Value Equations & Inequalities",
        ],
        "Trigonometry": [
            "Trigonometric Ratios (sin, cos, tan)", "Sine Rule",
            "Cosine Rule", "Area of Triangle using Trigonometry",
            "Angles of Elevation & Depression",
        ],
        "Polynomials": [
            "Factor Theorem", "Remainder Theorem",
            "Roots & Coefficients of Polynomials", "Polynomial Long Division",
        ],
        "Coordinate Geometry (Conics)": [
            "Parabola (y = ax² + bx + c)", "Circle (General & Standard Form)",
            "Ellipse (Introduction)", "Hyperbola (Introduction)",
        ],
        "Probability": [
            "Permutations & Combinations", "Binomial Theorem",
            "Conditional Probability & Bayes' Theorem",
            "Random Variables & Expected Value",
        ],
    },

    "Grade 11": {
        "Limits & Continuity": [
            "Concept of a Limit", "Limit Laws & Evaluation",
            "One-sided Limits", "Limits at Infinity",
            "Continuity & Discontinuity",
        ],
        "Differentiation": [
            "Definition of the Derivative", "Power, Product & Quotient Rules",
            "Chain Rule", "Derivatives of Trig, Exponential & Log Functions",
            "Implicit Differentiation",
        ],
        "Applications of Derivatives": [
            "Increasing / Decreasing Functions", "Local Maxima & Minima",
            "Concavity & Inflection Points", "Optimisation Problems",
            "Related Rates",
        ],
        "Vectors": [
            "Vector Operations (Addition, Subtraction, Scalar Multiplication)",
            "Dot Product", "Cross Product", "Angle Between Vectors",
            "Vector Equation of a Line",
        ],
        "Complex Numbers": [
            "Algebra of Complex Numbers", "Argand Plane",
            "Modulus & Argument", "Polar Form",
            "De Moivre's Theorem",
        ],
        "Sequences & Series": [
            "Arithmetic Sequences & Series", "Geometric Sequences & Series",
            "Sum to Infinity (Geometric)", "Binomial Theorem",
            "Sigma Notation",
        ],
    },

    "Grade 12": {
        "Integration": [
            "Indefinite Integrals & Rules", "Integration by Substitution",
            "Integration by Parts", "Partial Fractions",
            "Integration of Trigonometric Functions",
        ],
        "Definite Integrals & Applications": [
            "Definite Integrals & Area Under a Curve", "Area Between Two Curves",
            "Volume of Revolution", "Fundamental Theorem of Calculus",
        ],
        "Differential Equations": [
            "Separable Differential Equations", "First-order Linear ODEs",
            "Homogeneous Differential Equations", "Applications (Growth & Decay)",
        ],
        "Matrices & Determinants": [
            "Matrix Operations (Addition, Multiplication)", "Determinant of a 2×2 & 3×3 Matrix",
            "Inverse of a Matrix", "Solving Linear Systems using Matrices (Cramer's Rule)",
        ],
        "3D Geometry": [
            "Direction Cosines & Direction Ratios", "Equation of a Line in 3D",
            "Equation of a Plane", "Angle Between Lines & Planes",
            "Distance from a Point to a Plane",
        ],
        "Probability & Statistics": [
            "Probability Distributions (Discrete & Continuous)",
            "Binomial Distribution", "Normal Distribution & Z-scores",
            "Bayes' Theorem", "Statistical Inference (Introduction)",
        ],
    },

    "Math Olympiad": {
        "Number Theory": [
            "Divisibility & Remainders", "Prime Numbers & Factorisation",
            "GCD, LCM & Bezout's Identity", "Modular Arithmetic & Congruences",
            "Diophantine Equations",
        ],
        "Combinatorics": [
            "Counting Principles (Addition & Multiplication)", "Pigeonhole Principle",
            "Permutations & Combinations (Advanced)", "Inclusion-Exclusion Principle",
            "Graph Theory (Basic — Paths, Trees, Colouring)",
        ],
        "Geometry": [
            "Triangle Centers (Centroid, Incenter, Circumcenter, Orthocenter)",
            "Circle Theorems & Power of a Point",
            "Similar & Congruent Triangles (Advanced Proofs)",
            "Trigonometric Cevians (Ceva's Theorem, Menelaus)",
            "Projective & Inversive Geometry",
        ],
        "Algebra": [
            "Functional Equations", "Polynomials & Their Roots",
            "Vieta's Formulas", "Algebraic Identities & Manipulations",
            "Sequences & Recurrence Relations",
        ],
        "Inequalities": [
            "AM–GM Inequality", "Cauchy–Schwarz Inequality",
            "Jensen's Inequality", "Chebyshev's Sum Inequality",
            "Power Mean Inequality",
        ],
    },

    "IIT JEE": {
        "Calculus": [
            "Limits & Continuity", "Differentiation (Rules & Applications)",
            "Indefinite Integration", "Definite Integration & Properties",
            "Differential Equations",
        ],
        "Algebra": [
            "Complex Numbers & Quadratics", "Sequences, Series & Progressions",
            "Permutations & Combinations", "Binomial Theorem",
            "Matrices & Determinants",
        ],
        "Coordinate Geometry": [
            "Straight Lines & Pair of Lines", "Circles & Family of Circles",
            "Parabola", "Ellipse", "Hyperbola",
        ],
        "Trigonometry": [
            "Trigonometric Identities & Equations",
            "Inverse Trigonometric Functions",
            "Properties of Triangles (Sine & Cosine Rule, R & r)",
            "Heights & Distances",
        ],
        "Vectors & 3D Geometry": [
            "Vector Algebra (Dot & Cross Product)", "3D Lines & Planes",
            "Direction Cosines & Ratios", "Shortest Distance Between Lines",
        ],
        "Probability & Statistics": [
            "Classical & Conditional Probability", "Bayes' Theorem",
            "Binomial & Poisson Distribution", "Mean, Variance & Standard Deviation",
        ],
    },
}

GRADES = list(GRADE_CURRICULUM.keys())
DIFFICULTIES = ["Easy", "Medium", "Hard"]
DIFFICULTY_EMOJI = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}

LATEX_RULES = """
MANDATORY LATEX FORMATTING RULES — no exceptions:
- Use $...$ for ALL inline math: variables, numbers in equations, operators, expressions
- Use $$...$$ for standalone/display equations (on their own line)
- NEVER write mathematics as English words when a symbol exists
  ✗ WRONG: "x squared plus 3x"         ✓ RIGHT: $x^2 + 3x$
  ✗ WRONG: "integral of f(x) dx"       ✓ RIGHT: $\\int f(x)\\,dx$
  ✗ WRONG: "square root of 2"          ✓ RIGHT: $\\sqrt{2}$
  ✗ WRONG: "sum from i=1 to n"         ✓ RIGHT: $\\sum_{i=1}^{n}$
  ✗ WRONG: "pi", "theta", "alpha"      ✓ RIGHT: $\\pi$, $\\theta$, $\\alpha$
  ✗ WRONG: "infinity"                  ✓ RIGHT: $\\infty$
  ✗ WRONG: "limit as x approaches 0"   ✓ RIGHT: $\\lim_{x \\to 0}$
  ✗ WRONG: "a/b"                       ✓ RIGHT: $\\frac{a}{b}$
- Fractions: $\\frac{numerator}{denominator}$
- Powers: $x^{n}$, $e^{2x}$   Subscripts: $a_n$, $x_1$
- Greek letters: $\\alpha$, $\\beta$, $\\gamma$, $\\delta$, $\\lambda$, $\\mu$, $\\sigma$, $\\omega$, $\\pi$, $\\theta$
- Trig: $\\sin x$, $\\cos x$, $\\tan x$, $\\sec x$, $\\csc x$, $\\cot x$
- Log/ln: $\\log x$, $\\ln x$, $\\log_b x$
- Vectors: $\\vec{v}$, $\\hat{i}$
- Derivatives: $f'(x)$, $\\frac{dy}{dx}$, $\\frac{d^2y}{dx^2}$
- Integrals: $\\int_a^b f(x)\\,dx$, $\\oint$
- Summation: $\\sum_{i=1}^{n} a_i$   Products: $\\prod_{i=1}^{n}$
- Limits: $\\lim_{x \\to a}$, $\\lim_{x \\to \\infty}$
- Inequalities: $\\leq$, $\\geq$, $\\neq$, $\\approx$, $\\in$, $\\subset$, $\\equiv$
- Absolute value: $|x|$   Binomial: $\\binom{n}{k}$
- Matrices: $$\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$$
- Partial derivatives: $\\frac{\\partial f}{\\partial x}$
"""

# ── API client ────────────────────────────────────────────────────────────────
def get_client():
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        api_key = None
    if not api_key or api_key.strip() == "sk-ant-your-key-here":
        st.error(
            "**Anthropic API key not found or not set.**\n\n"
            "In Streamlit Cloud go to **Manage app → Settings → Secrets** and add:\n"
            "```\nANTHROPIC_API_KEY = \"sk-ant-api03-...\"\n```\n"
            "Get your key at https://console.anthropic.com/settings/keys",
            icon="🔑",
        )
        st.stop()
    if not api_key.startswith("sk-ant-"):
        st.error(
            "**API key format looks wrong.**\n\n"
            f"Your key starts with `{api_key[:10]}...` but it should start with `sk-ant-`.\n\n"
            "Please copy the full key from https://console.anthropic.com/settings/keys",
            icon="⚠️",
        )
        st.stop()
    return anthropic.Anthropic(api_key=api_key.strip())


# ── Prompts ───────────────────────────────────────────────────────────────────
def build_problem_prompt(grade: str, difficulty: str, topic: str, subtopic: str) -> str:
    jee_note = (
        " This is for IIT JEE preparation — use JEE Main/Advanced style problems."
        if grade == "IIT JEE" else ""
    )
    olympiad_note = (
        " This is for Math Olympiad — the problem must require elegant, non-routine reasoning."
        if grade == "Math Olympiad" else ""
    )
    return f"""You are an expert mathematics teacher. Generate a single, self-contained math problem for:
- Level: {grade}{jee_note}{olympiad_note}
- Topic: {topic}
- Subtopic: {subtopic}
- Difficulty: {difficulty}

{LATEX_RULES}

Format your response EXACTLY as follows (use these exact headers):

PROBLEM:
<Complete problem statement using LaTeX for ALL math. Do NOT include the answer.>

HINT:
<One subtle hint using LaTeX for any math — nudges without giving away the answer>

Keep the problem clear and perfectly appropriate for {grade} level. Do not include the solution."""


def build_solution_prompt(grade: str, difficulty: str, topic: str, subtopic: str, problem: str) -> str:
    jee_note = " Use JEE-style approach with shortcuts where applicable." if grade == "IIT JEE" else ""
    olympiad_note = " Show elegant olympiad-style reasoning." if grade == "Math Olympiad" else ""
    return f"""You are an expert mathematics tutor explaining a solution to a {grade} student.{jee_note}{olympiad_note}

Topic: {topic} → {subtopic}
Problem:
{problem}

{LATEX_RULES}

Provide a COMPLETE step-by-step solution structured as:

**Answer:**
<Final answer using LaTeX>

**Step-by-Step Solution:**
<Numbered steps. Every equation, expression, or symbol MUST use LaTeX. Explain the WHY of each step.>

**Key Concept:**
<1–2 sentences on the core mathematical idea. Use LaTeX for any terms.>

**Common Mistakes:**
<1–2 mistakes students commonly make, showing wrong vs correct expressions in LaTeX.>

Tailor depth and vocabulary to a {grade} student at {difficulty} difficulty."""


def parse_problem(text: str) -> dict:
    result = {"problem": text, "hint": ""}
    m = re.search(r"PROBLEM:\s*(.*?)(?=HINT:|$)", text, re.DOTALL | re.IGNORECASE)
    if m:
        result["problem"] = m.group(1).strip()
    m = re.search(r"HINT:\s*(.*?)$", text, re.DOTALL | re.IGNORECASE)
    if m:
        result["hint"] = m.group(1).strip()
    return result


def stream_response(client, prompt: str, placeholder):
    full_text = ""
    try:
        with client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=1800,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                full_text += text
                placeholder.markdown(full_text + " ▌")
        placeholder.empty()
    except anthropic.AuthenticationError:
        st.error(
            "**Invalid API key.** Your key was found but rejected by Anthropic.\n\n"
            "1. Go to https://console.anthropic.com/settings/keys\n"
            "2. Delete the old key and create a **new** one\n"
            "3. Copy the **full** key (100+ characters)\n"
            "4. Update it in Streamlit Cloud → **Manage app → Settings → Secrets**",
            icon="🔑",
        )
        st.stop()
    except anthropic.APIStatusError as e:
        st.error(f"**API Error {e.status_code}:** {e.message}", icon="❌")
        st.stop()
    return full_text


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in {
    "problem_data": None,
    "solution": None,
    "show_hint": False,
    "show_solution": False,
    "problem_count": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🧮 Daily Math Problem Solver</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">From Grade 1 to IIT JEE & Math Olympiad — powered by AI</div>',
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    grade = st.selectbox("📚 Grade / Level", GRADES, index=0)

    topics = list(GRADE_CURRICULUM[grade].keys())
    topic = st.selectbox("📖 Topic", topics)

    subtopics = GRADE_CURRICULUM[grade][topic]
    subtopic = st.selectbox("📐 Subtopic", subtopics)

    difficulty = st.radio(
        "🎯 Difficulty",
        DIFFICULTIES,
        index=1,
        format_func=lambda d: f"{DIFFICULTY_EMOJI[d]} {d}",
    )

    st.divider()
    generate_btn = st.button("✨ Generate Problem", use_container_width=True, type="primary")
    st.divider()

    st.markdown(f"**Problems solved this session:** {st.session_state.problem_count} 🏆")
    st.markdown("""
**Tips:**
- Attempt the problem before using hints
- Understand *why* each step works, not just *what* it is
- Challenge yourself: increase difficulty once comfortable!
""")

# ── Generate ──────────────────────────────────────────────────────────────────
if generate_btn:
    st.session_state.show_hint = False
    st.session_state.show_solution = False
    st.session_state.solution = None

    client = get_client()
    prompt = build_problem_prompt(grade, difficulty, topic, subtopic)

    with st.spinner("Generating your problem..."):
        placeholder = st.empty()
        raw = stream_response(client, prompt, placeholder)

    st.session_state.problem_data = {
        **parse_problem(raw),
        "grade": grade, "difficulty": difficulty,
        "topic": topic, "subtopic": subtopic,
    }

# ── Display ───────────────────────────────────────────────────────────────────
if st.session_state.problem_data:
    data = st.session_state.problem_data
    diff_class = data["difficulty"].lower()

    # Badges
    st.markdown(
        f'<span class="badge badge-grade">{data["grade"]}</span>'
        f'<span class="badge badge-{diff_class}">{DIFFICULTY_EMOJI[data["difficulty"]]} {data["difficulty"]}</span>'
        f'<span class="badge badge-topic">📖 {data["topic"]}</span>'
        f'<span class="badge badge-topic">📐 {data["subtopic"]}</span>',
        unsafe_allow_html=True,
    )

    # Problem
    st.markdown('<p class="section-label label-problem">📝 Problem</p>', unsafe_allow_html=True)
    st.info(data["problem"])

    # Buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💡 Show Hint", use_container_width=True):
            st.session_state.show_hint = not st.session_state.show_hint

    with col2:
        if st.button("🔍 Show Solution & Explanation", use_container_width=True, type="primary"):
            st.session_state.show_solution = True
            if not st.session_state.solution:
                client = get_client()
                sol_prompt = build_solution_prompt(
                    data["grade"], data["difficulty"],
                    data["topic"], data["subtopic"], data["problem"]
                )
                sol_placeholder = st.empty()
                solution_text = stream_response(client, sol_prompt, sol_placeholder)
                st.session_state.solution = solution_text
                st.session_state.problem_count += 1

    with col3:
        if st.button("🔄 New Problem (Same Settings)", use_container_width=True):
            st.session_state.show_hint = False
            st.session_state.show_solution = False
            st.session_state.solution = None
            client = get_client()
            prompt = build_problem_prompt(
                data["grade"], data["difficulty"], data["topic"], data["subtopic"]
            )
            with st.spinner("Generating..."):
                placeholder = st.empty()
                raw = stream_response(client, prompt, placeholder)
            st.session_state.problem_data = {
                **parse_problem(raw),
                "grade": data["grade"], "difficulty": data["difficulty"],
                "topic": data["topic"], "subtopic": data["subtopic"],
            }
            st.rerun()

    # Hint
    if st.session_state.show_hint and data.get("hint"):
        st.markdown('<p class="section-label label-hint">💡 Hint</p>', unsafe_allow_html=True)
        st.warning(data["hint"])

    # Solution
    if st.session_state.show_solution and st.session_state.solution:
        st.markdown('<p class="section-label label-solution">✅ Solution & Explanation</p>', unsafe_allow_html=True)
        st.success(st.session_state.solution)

else:
    # Welcome screen
    st.info(
        "👈 **Select your grade, topic, subtopic, and difficulty from the sidebar, "
        "then click 'Generate Problem' to get started!**",
        icon="🚀",
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
### 🎓 For All Levels
Grade 1 basic counting through IIT JEE and Math Olympiad — every subtopic covered.
        """)
    with col2:
        st.markdown("""
### 🤖 AI-Powered
Step-by-step explanations with proper mathematical notation, tailored to your level.
        """)
    with col3:
        st.markdown("""
### 📈 Build Daily Habits
One focused problem per day. Pick a subtopic, understand it deeply, move on.
        """)

st.markdown('<div class="footer">Built with ❤️ using Streamlit & Claude AI</div>', unsafe_allow_html=True)
