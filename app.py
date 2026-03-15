import streamlit as st
import anthropic
import re
import base64
import io

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# ── Page config ───────────────────────────────────────────────────────────────
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
        font-size:2.4rem; font-weight:800;
        background:linear-gradient(135deg,#667eea,#764ba2);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        text-align:center; margin-bottom:0.2rem;
    }
    .subtitle{text-align:center;color:#666;font-size:1rem;margin-bottom:1.5rem;}
    .section-label{font-size:.82rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin:.8rem 0 .2rem;}
    .label-problem{color:#667eea;} .label-hint{color:#e6a817;} .label-solution{color:#2e7d32;}
    .badge{display:inline-block;padding:.25rem .75rem;border-radius:20px;font-size:.78rem;font-weight:700;margin-right:.4rem;}
    .badge-easy{background:#d4edda;color:#155724;} .badge-medium{background:#fff3cd;color:#856404;}
    .badge-hard{background:#f8d7da;color:#721c24;} .badge-grade{background:#cce5ff;color:#004085;}
    .badge-topic{background:#e2d9f3;color:#4a235a;}
    .paper-header{background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;border-radius:12px;padding:1.5rem 2rem;text-align:center;margin-bottom:1rem;}
    .resource-card{border:1px solid #e0e0e0;border-radius:10px;padding:1rem 1.2rem;margin-bottom:.6rem;background:#fafafa;}
    .stButton>button{border-radius:8px;font-weight:600;}
    div[data-testid="stAlert"]{border-radius:12px;font-size:1.05rem;line-height:1.8;}
    .footer{text-align:center;color:#aaa;font-size:.8rem;margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;}
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# CURRICULUM
# ═════════════════════════════════════════════════════════════════════════════
GRADE_CURRICULUM = {
    "Grade 1": {
        "Counting & Numbers": ["Counting 1–20","Counting 1–100","Number Ordering & Sequencing","Even & Odd Numbers","Comparing Numbers (>, <, =)"],
        "Addition": ["Adding Single-digit Numbers","Number Bonds to 10","Number Bonds to 20","Adding on a Number Line","Word Problems"],
        "Subtraction": ["Subtracting Single-digit Numbers","Finding the Difference","Subtraction on a Number Line","Word Problems"],
        "Shapes & Patterns": ["2D Shapes","3D Shapes","Sorting & Classifying Shapes","Repeating Patterns"],
        "Measurement & Time": ["Comparing Lengths","Comparing Weights","Telling Time (O'Clock & Half Past)","Days & Months"],
    },
    "Grade 2": {
        "Place Value": ["Tens and Ones","Hundreds, Tens and Ones","Expanded Form","Comparing 3-digit Numbers"],
        "Addition & Subtraction": ["2-digit Addition (No Regrouping)","2-digit Addition (With Regrouping)","2-digit Subtraction (No Regrouping)","2-digit Subtraction (With Regrouping)","Word Problems"],
        "Multiplication Introduction": ["Equal Groups","Arrays","Skip Counting (2s, 5s, 10s)","Multiplication as Repeated Addition"],
        "Fractions Introduction": ["Halves","Quarters","Thirds","Identifying Fractions of a Shape"],
        "Measurement, Time & Money": ["Measuring Length (cm & m)","Telling Time (Quarter Past/To)","Counting Coins","Simple Money Problems"],
    },
    "Grade 3": {
        "Multiplication": ["Times Tables (2–5)","Times Tables (6–10)","Multiplication Properties","Multiplying by 10 & 100","Word Problems"],
        "Division": ["Equal Sharing","Division as Repeated Subtraction","Division Facts","Remainders Introduction"],
        "Fractions": ["Equivalent Fractions","Comparing & Ordering Fractions","Fractions on a Number Line","Adding Like Fractions"],
        "Geometry": ["Perimeter","Area by Counting Squares","Types of Angles","Quadrilaterals"],
        "Data & Graphs": ["Tally Charts","Bar Graphs","Pictographs","Reading & Interpreting Data"],
    },
    "Grade 4": {
        "Multi-digit Arithmetic": ["Multi-digit Multiplication","Long Division (No Remainder)","Long Division (With Remainder)","Estimation & Rounding","Word Problems"],
        "Fractions & Decimals": ["Adding & Subtracting Like Fractions","Mixed Numbers & Improper Fractions","Decimal Place Value","Comparing & Ordering Decimals"],
        "Angles & Geometry": ["Measuring Angles with a Protractor","Types of Angles","Angles on a Straight Line","Angles in a Triangle"],
        "Area & Perimeter": ["Area of Rectangles & Squares","Perimeter of Polygons","Composite Shapes","Units of Area"],
        "Factors & Multiples": ["Factors of a Number","Multiples & LCM","Prime & Composite Numbers","Highest Common Factor (HCF)"],
    },
    "Grade 5": {
        "Fractions Operations": ["Adding & Subtracting Unlike Fractions","Multiplying Fractions","Dividing Fractions","Fraction Word Problems","Mixed Number Operations"],
        "Decimals": ["Adding & Subtracting Decimals","Multiplying Decimals","Dividing Decimals","Rounding & Estimation"],
        "Ratios & Percentages": ["Introduction to Ratios","Equivalent Ratios","Percentages (Finding % of a Number)","Percentage Word Problems"],
        "Geometry & Volume": ["Volume of Cuboids","Surface Area of Cuboids","Coordinate Plane (Quadrant I)","Plotting & Reading Coordinates"],
        "Algebraic Thinking": ["Numerical Expressions & BODMAS","Simple Algebraic Expressions","Patterns & Rules","Introduction to Equations"],
    },
    "Grade 6": {
        "Ratios & Rates": ["Ratios & Equivalent Ratios","Unit Rates","Proportions","Percentage (Increase & Decrease)","Speed, Distance & Time"],
        "Integers": ["Introduction to Negative Numbers","Adding Integers","Subtracting Integers","Multiplying & Dividing Integers","Absolute Value"],
        "Expressions & Equations": ["Algebraic Expressions (Simplification)","Substitution","One-step Equations","Two-step Equations","Inequalities"],
        "Geometry": ["Area of Triangles & Parallelograms","Area of Trapezoids","Circumference & Area of Circles","Nets & Surface Area","Volume of Prisms"],
        "Statistics": ["Mean, Median, Mode & Range","Frequency Tables","Bar Charts & Histograms","Pie Charts","Interpreting Data & Outliers"],
    },
    "Grade 7": {
        "Proportional Reasoning": ["Direct Proportion","Inverse Proportion","Percentage Problems (Profit & Loss)","Simple Interest","Ratio Word Problems"],
        "Linear Equations": ["Forming & Solving Linear Equations","Equations with Variables on Both Sides","Linear Inequalities","Word Problems"],
        "Geometry": ["Angles in Parallel Lines","Angle Sum of Polygons","Basic Circle Theorems","Congruence & Similarity","Construction & Loci"],
        "Probability": ["Sample Space & Events","Simple Probability","Complementary Events","Experimental vs Theoretical Probability","Tree Diagrams"],
        "Statistics": ["Box Plots & Stem-and-Leaf Plots","Scatter Plots & Correlation","Mean from Grouped Data","Comparing Two Data Sets"],
    },
    "Grade 8": {
        "Linear Functions": ["Gradient (Slope) of a Line","Equation of a Line (y = mx + c)","Graphing Linear Functions","Parallel & Perpendicular Lines","Rate of Change"],
        "Systems of Equations": ["Solving by Substitution","Solving by Elimination","Graphical Solution","Word Problems with 2 Unknowns"],
        "Quadratics (Introduction)": ["Expanding Brackets & Identities","Factoring (Common Factor)","Factoring Trinomials","Difference of Two Squares"],
        "Pythagorean Theorem": ["Finding the Hypotenuse","Finding a Missing Side","Distance Between Two Points","Applications in 3D"],
        "Exponents & Surds": ["Laws of Exponents","Negative & Fractional Exponents","Introduction to Surds","Simplifying Surds"],
    },
    "Grade 9": {
        "Algebra": ["Polynomials (Add, Subtract, Multiply)","Polynomial Division & Remainder Theorem","Rational Expressions","Factoring Advanced"],
        "Quadratic Equations": ["Solving by Factoring","Completing the Square","Quadratic Formula","Discriminant & Nature of Roots","Word Problems"],
        "Functions": ["Function Notation & Evaluation","Domain & Range","Inverse Functions","Composite Functions","Graphing Functions"],
        "Coordinate Geometry": ["Distance & Midpoint Formula","Equation of a Circle","Tangent to a Circle","Collinearity & Area of Triangle"],
        "Statistics & Probability": ["Variance & Standard Deviation","Normal Distribution (Introduction)","Conditional Probability","Permutations","Combinations"],
    },
    "Grade 10": {
        "Advanced Algebra": ["Exponential & Logarithmic Functions","Laws of Logarithms","Exponential Equations","Absolute Value Equations & Inequalities"],
        "Trigonometry": ["Trigonometric Ratios (sin, cos, tan)","Sine Rule","Cosine Rule","Area of Triangle using Trigonometry","Angles of Elevation & Depression"],
        "Polynomials": ["Factor Theorem","Remainder Theorem","Roots & Coefficients","Polynomial Long Division"],
        "Coordinate Geometry (Conics)": ["Parabola","Circle (General & Standard Form)","Ellipse (Introduction)","Hyperbola (Introduction)"],
        "Probability": ["Permutations & Combinations","Binomial Theorem","Conditional Probability & Bayes' Theorem","Random Variables & Expected Value"],
    },
    "Grade 11": {
        "Limits & Continuity": ["Concept of a Limit","Limit Laws & Evaluation","One-sided Limits","Limits at Infinity","Continuity & Discontinuity"],
        "Differentiation": ["Definition of the Derivative","Power, Product & Quotient Rules","Chain Rule","Derivatives of Trig, Exp & Log Functions","Implicit Differentiation"],
        "Applications of Derivatives": ["Increasing / Decreasing Functions","Local Maxima & Minima","Concavity & Inflection Points","Optimisation Problems","Related Rates"],
        "Vectors": ["Vector Operations","Dot Product","Cross Product","Angle Between Vectors","Vector Equation of a Line"],
        "Complex Numbers": ["Algebra of Complex Numbers","Argand Plane","Modulus & Argument","Polar Form","De Moivre's Theorem"],
        "Sequences & Series": ["Arithmetic Sequences & Series","Geometric Sequences & Series","Sum to Infinity","Binomial Theorem","Sigma Notation"],
    },
    "Grade 12": {
        "Integration": ["Indefinite Integrals & Rules","Integration by Substitution","Integration by Parts","Partial Fractions","Integration of Trig Functions"],
        "Definite Integrals & Applications": ["Definite Integrals & Area Under Curve","Area Between Two Curves","Volume of Revolution","Fundamental Theorem of Calculus"],
        "Differential Equations": ["Separable Differential Equations","First-order Linear ODEs","Homogeneous Differential Equations","Applications (Growth & Decay)"],
        "Matrices & Determinants": ["Matrix Operations","Determinant of a 2×2 & 3×3 Matrix","Inverse of a Matrix","Solving Linear Systems (Cramer's Rule)"],
        "3D Geometry": ["Direction Cosines & Direction Ratios","Equation of a Line in 3D","Equation of a Plane","Angle Between Lines & Planes","Distance from a Point to a Plane"],
        "Probability & Statistics": ["Probability Distributions","Binomial Distribution","Normal Distribution & Z-scores","Bayes' Theorem","Statistical Inference"],
    },
    # ── Indian Competitive Exams ──────────────────────────────────────────────
    "IIT JEE": {
        "Calculus": ["Limits & Continuity","Differentiation (Rules & Applications)","Indefinite Integration","Definite Integration & Properties","Differential Equations"],
        "Algebra": ["Complex Numbers & Quadratics","Sequences, Series & Progressions","Permutations & Combinations","Binomial Theorem","Matrices & Determinants"],
        "Coordinate Geometry": ["Straight Lines & Pair of Lines","Circles & Family of Circles","Parabola","Ellipse","Hyperbola"],
        "Trigonometry": ["Trigonometric Identities & Equations","Inverse Trigonometric Functions","Properties of Triangles","Heights & Distances"],
        "Vectors & 3D Geometry": ["Vector Algebra (Dot & Cross Product)","3D Lines & Planes","Direction Cosines & Ratios","Shortest Distance Between Lines"],
        "Probability & Statistics": ["Classical & Conditional Probability","Bayes' Theorem","Binomial & Poisson Distribution","Mean, Variance & Standard Deviation"],
    },
    "BITSAT (BITS Pilani)": {
        "Algebra & Trigonometry": ["Quadratics & Polynomials","Sequences & Series","Permutations & Combinations","Trigonometric Identities & Equations","Inverse Trigonometry"],
        "Calculus": ["Limits & Continuity","Differentiation","Integration (Indefinite & Definite)","Differential Equations","Applications of Calculus"],
        "Coordinate Geometry": ["Straight Lines","Circles","Conics (Parabola, Ellipse, Hyperbola)","3D Geometry"],
        "Vectors & Matrices": ["Vector Algebra","Dot & Cross Product","Matrix Operations","Determinants & Inverse"],
        "Probability & Statistics": ["Probability","Conditional Probability & Bayes","Binomial Distribution","Mean, Variance"],
    },
    # ── Olympiads ─────────────────────────────────────────────────────────────
    "Math Olympiad (IMO/RMO)": {
        "Number Theory": ["Divisibility & Remainders","Prime Numbers & Factorisation","GCD, LCM & Bezout's Identity","Modular Arithmetic & Congruences","Diophantine Equations"],
        "Combinatorics": ["Counting Principles","Pigeonhole Principle","Permutations & Combinations (Advanced)","Inclusion-Exclusion Principle","Graph Theory (Basic)"],
        "Geometry": ["Triangle Centers","Circle Theorems & Power of a Point","Similar & Congruent Triangles (Proofs)","Ceva's & Menelaus' Theorems","Projective & Inversive Geometry"],
        "Algebra": ["Functional Equations","Polynomials & Their Roots","Vieta's Formulas","Algebraic Identities","Sequences & Recurrence Relations"],
        "Inequalities": ["AM–GM Inequality","Cauchy–Schwarz Inequality","Jensen's Inequality","Chebyshev's Sum Inequality","Power Mean Inequality"],
    },
    # ── USA ───────────────────────────────────────────────────────────────────
    "SAT Math (USA)": {
        "Heart of Algebra": ["Linear Equations & Inequalities","Systems of Linear Equations","Linear Functions","Absolute Value Equations"],
        "Problem Solving & Data Analysis": ["Ratios & Proportions","Percentages","Statistics & Probability","Scatterplots & Data Interpretation"],
        "Advanced Math": ["Quadratic Equations","Polynomial Functions","Exponential Functions","Rational & Radical Equations","Complex Numbers"],
        "Geometry & Trigonometry": ["Area & Volume","Lines, Angles & Triangles","Trigonometric Ratios","Circles"],
    },
    "AMC 10 / AMC 12 (USA)": {
        "Number Theory": ["Divisibility","Primes & Factorisation","Modular Arithmetic","Number Bases","Integer Properties"],
        "Algebra": ["Polynomials","Sequences & Series","Inequalities","Logarithms","Functional Equations"],
        "Geometry": ["Triangles & Circles","Coordinate Geometry","3D Geometry","Trigonometry","Angle Chasing"],
        "Combinatorics & Probability": ["Counting Methods","Permutations & Combinations","Probability","Expected Value","Recursion"],
    },
    "AIME (USA)": {
        "Number Theory": ["Modular Arithmetic","Diophantine Equations","Number Properties","GCD & LCM Applications"],
        "Algebra": ["Polynomials & Roots","Sequences & Series","Logarithms","Inequalities","Functional Equations"],
        "Geometry": ["Classical Euclidean Geometry","Coordinate Geometry","Trigonometry","3D Geometry"],
        "Combinatorics": ["Advanced Counting","Probability","Graph Theory","Recursion & Generating Functions"],
    },
    # ── UK ────────────────────────────────────────────────────────────────────
    "UKMT (UK)": {
        "Number & Algebra": ["Number Properties & Divisibility","Algebraic Manipulation","Sequences & Series","Logarithms & Exponentials"],
        "Geometry": ["Euclidean Geometry","Circle Theorems","Coordinate Geometry","Trigonometry"],
        "Combinatorics & Probability": ["Counting & Combinations","Probability","Pigeonhole Principle","Graph Theory"],
        "Logic & Proof": ["Mathematical Reasoning","Proof by Contradiction","Induction","Problem-Solving Strategies"],
    },
    # ── Singapore ─────────────────────────────────────────────────────────────
    "Singapore A-Level (H2 Math)": {
        "Pure Mathematics": ["Functions & Graphs","Sequences & Series","Vectors","Complex Numbers","Calculus (Differentiation & Integration)"],
        "Statistics": ["Probability","Discrete Random Variables","Normal Distribution","Sampling & Hypothesis Testing","Correlation & Regression"],
    },
    # ── South Korea ───────────────────────────────────────────────────────────
    "South Korea CSAT (수능)": {
        "Algebra & Functions": ["Exponential & Logarithmic Functions","Trigonometric Functions","Sequences & Series","Polynomial Functions"],
        "Calculus": ["Limits & Continuity","Differentiation & Applications","Integration & Applications"],
        "Probability & Statistics": ["Permutations & Combinations","Probability Distributions","Normal Distribution & Estimation"],
        "Geometry & Vectors": ["Plane Curves & Conics","Vectors in 2D & 3D","Space Figures"],
    },
    # ── Australia ─────────────────────────────────────────────────────────────
    "Australia HSC / VCE": {
        "Calculus": ["Limits & Continuity","Differentiation","Integration","Differential Equations"],
        "Algebra & Functions": ["Polynomials","Exponential & Log Functions","Trigonometry","Inverse Functions"],
        "Statistics": ["Probability","Discrete & Continuous Distributions","Statistical Inference","Regression & Correlation"],
        "Vectors & Mechanics": ["Vectors in 2D & 3D","Projectile Motion","Dynamics & Forces"],
    },
    # ── China ─────────────────────────────────────────────────────────────────
    "China Gaokao (高考)": {
        "Algebra & Functions": ["Sets & Logic","Functions (Monotonicity, Inverse)","Exponential & Log Functions","Sequences & Series","Inequalities"],
        "Trigonometry": ["Trigonometric Functions","Sine & Cosine Rules","Triangle Applications","Trigonometric Equations"],
        "Analytic Geometry": ["Straight Lines","Circles","Ellipse","Hyperbola & Parabola"],
        "Calculus": ["Limits","Derivatives & Applications","Definite Integrals & Area"],
        "Statistics & Probability": ["Counting & Combinatorics","Probability","Normal Distribution","Regression & Correlation"],
        "Vectors & Solid Geometry": ["Vectors in 2D & 3D","Solid Geometry Proofs","Spatial Reasoning"],
    },
    # ── Japan ─────────────────────────────────────────────────────────────────
    "Japan Kyotsu-Test (共通テスト)": {
        "Algebra & Functions": ["Quadratics & Higher-degree Functions","Exponential & Logarithmic Functions","Trigonometry","Sequences & Series"],
        "Geometry & Vectors": ["Plane Geometry","Vectors","Complex Numbers (Locus & Argument)"],
        "Calculus": ["Differentiation","Integration","Area & Volume of Revolution"],
        "Statistics & Probability": ["Permutations & Combinations","Probability Distributions","Data Analysis & Inference"],
    },
    # ── Germany ───────────────────────────────────────────────────────────────
    "Germany Abitur": {
        "Analysis (Calculus)": ["Functions & Graphs","Differentiation","Integration","Differential Equations","Exponential & Log Functions"],
        "Analytic Geometry / Linear Algebra": ["Vectors","Lines & Planes in 3D","Matrices","Eigenvalues (Advanced)"],
        "Stochastics (Probability & Statistics)": ["Probability Distributions","Binomial Distribution","Normal Distribution","Hypothesis Testing","Bayesian Methods"],
    },
    # ── France ────────────────────────────────────────────────────────────────
    "France Baccalauréat (Terminale)": {
        "Analysis": ["Limits & Continuity","Derivatives & Applications","Integration","Exponential & Log Functions","Differential Equations"],
        "Algebra & Geometry": ["Complex Numbers","Matrices","Vectors in 3D","Conics"],
        "Probability & Statistics": ["Random Variables","Binomial & Normal Distributions","Statistical Tests","Confidence Intervals"],
    },
}

GRADES = list(GRADE_CURRICULUM.keys())
DIFFICULTIES = ["Easy", "Medium", "Hard"]
DIFFICULTY_EMOJI = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}

# ═════════════════════════════════════════════════════════════════════════════
# BOARD FORMATS & RESOURCES
# ═════════════════════════════════════════════════════════════════════════════
BOARD_FORMATS = {
    "CBSE": {
        "full_name": "Central Board of Secondary Education",
        "Grade 6":  "50 marks, 2 hours. Section A: 12 MCQ (1 mark). Section B: 8 Short Answer (2 marks). Section C: 5 Long Answer (4 marks). Section D: 2 HOTS (5 marks).",
        "Grade 7":  "50 marks, 2 hours. Section A: 12 MCQ (1 mark). Section B: 8 Short Answer (2 marks). Section C: 5 Long Answer (4 marks). Section D: 2 HOTS (5 marks).",
        "Grade 8":  "60 marks, 2.5 hours. Section A: 15 MCQ (1 mark). Section B: 8 Short Answer (2 marks). Section C: 5 Long Answer (4 marks). Section D: 2 HOTS (5 marks).",
        "Grade 9":  "80 marks, 3 hours. Section A: 20 MCQ (1 mark). Section B: 5 VSA (2 marks). Section C: 6 SA (3 marks). Section D: 4 LA (5 marks). Section E: 3 Case Study (4 marks).",
        "Grade 10": "80 marks, 3 hours. Section A: 20 MCQ (1 mark). Section B: 5 VSA (2 marks). Section C: 6 SA (3 marks). Section D: 4 LA (5 marks). Section E: 3 Case Study (4 marks).",
        "Grade 11": "80 marks, 3 hours. Section A: 20 MCQ (1 mark). Section B: 5 VSA (2 marks). Section C: 6 SA (3 marks). Section D: 4 LA (5 marks). Section E: 3 Case Study (4 marks).",
        "Grade 12": "80 marks, 3 hours. Section A: 20 MCQ (1 mark). Section B: 5 VSA (2 marks). Section C: 6 SA (3 marks). Section D: 4 LA (5 marks). Section E: 3 Case Study (4 marks).",
    },
    "ICSE": {
        "full_name": "Indian Certificate of Secondary Education (CISCE)",
        "Grade 6": "50 marks, 2 hours. Section A (compulsory): 25 marks. Section B: attempt any 3 of 5 questions (25 marks).",
        "Grade 7": "50 marks, 2 hours. Section A (compulsory): 25 marks. Section B: attempt any 3 of 5 questions (25 marks).",
        "Grade 8": "60 marks, 2 hours. Section A (compulsory): 30 marks. Section B: attempt any 3 of 5 questions (30 marks).",
        "Grade 9": "80 marks, 2.5 hours. Section A (compulsory, 40 marks). Section B (40 marks): attempt any 4 of 6 long questions (10 marks each).",
        "Grade 10": "80 marks, 2.5 hours. Section A (compulsory, 40 marks). Section B (40 marks): attempt any 4 of 6 long questions (10 marks each).",
        "Grade 11": "Not standard for ICSE — use ISC for Grade 11.",
        "Grade 12": "Not standard for ICSE — use ISC for Grade 12.",
    },
    "ISC": {
        "full_name": "Indian School Certificate (CISCE — Grade 11 & 12)",
        "Grade 6": "Not applicable — ISC is for Grades 11–12.",
        "Grade 7": "Not applicable — ISC is for Grades 11–12.",
        "Grade 8": "Not applicable — ISC is for Grades 11–12.",
        "Grade 9": "Not applicable — ISC is for Grades 11–12.",
        "Grade 10": "Not applicable — ISC is for Grades 11–12.",
        "Grade 11": "80 marks, 3 hours. Section A (compulsory, 65 marks). Section B (15 marks): any 2 of 3.",
        "Grade 12": "80 marks, 3 hours. Section A (compulsory, 65 marks): Algebra, Calculus, Vectors, Probability. Section B (15 marks): any 2 of 3.",
    },
    "Maharashtra State Board": {
        "full_name": "Maharashtra State Board (MSBSHSE)",
        "Grade 6": "40 marks, 2 hours. Q1 MCQ (8). Q2 Fill-in-blanks (8). Q3–Q6 problem solving (6 marks each).",
        "Grade 7": "40 marks, 2 hours. Q1 MCQ (8). Q2 Fill-in-blanks (8). Q3–Q6 problem solving (6 marks each).",
        "Grade 8": "40 marks, 2 hours. Q1 MCQ (8). Q2 True/False (8). Q3–Q6 problem solving (6 marks each).",
        "Grade 9": "40 marks per paper (Algebra and Geometry are separate). Q1 MCQ (8). Q2–Q5 problem solving.",
        "Grade 10": "40 marks per paper (Algebra and Geometry separate). Q1 MCQ (8). Q2 (4). Q3 (9). Q4 (9). Q5 (10).",
        "Grade 11": "80 marks, 3 hours. Q1 MCQ (10). Q2–Q4 short answer. Q5–Q7 long answer.",
        "Grade 12": "80 marks, 3 hours. Paper I (Algebra & Calculus) + Paper II (Statistics & Geometry), 80 marks each.",
    },
    "Karnataka State Board": {
        "full_name": "Karnataka KSEAB / SSLC / PUC Board",
        "Grade 6": "50 marks, 2 hours. MCQ, fill-in-blanks, short answer, long answer.",
        "Grade 7": "50 marks, 2 hours. MCQ, fill-in-blanks, short answer, long answer.",
        "Grade 8": "50 marks, 2 hours. MCQ, fill-in-blanks, short answer, long answer.",
        "Grade 9": "80 marks, 3 hours. MCQ (1 mark), fill-in-blanks (1 mark), short answer (2 marks), long answer (3 marks), very long answer (4 marks).",
        "Grade 10": "80 marks, 3 hours (SSLC). MCQ (10×1), Fill-in-blanks (10×1), Match (5×1), SA (5×2), LA (5×3), VLA (4×4).",
        "Grade 11": "100 marks, 3 hours (I PUC). Part A (1 mark), Part B (2 marks), Part C (3 marks), Part D (5 marks), Part E (10 marks).",
        "Grade 12": "100 marks, 3.25 hours (II PUC). Part A (1 mark), Part B (2 marks), Part C (3 marks), Part D (5 marks), Part E (10 marks).",
    },
    "Tamil Nadu State Board": {
        "full_name": "Tamil Nadu State Board (Samacheer Kalvi)",
        "Grade 6": "100 marks, 3 hours. MCQ (14×1), Q&A (10×2), Q&A (5×5), Essay (2×8).",
        "Grade 7": "100 marks, 3 hours. MCQ (14×1), Q&A (10×2), Q&A (5×5), Essay (2×8).",
        "Grade 8": "100 marks, 3 hours. MCQ (15×1), Q&A (10×2), Q&A (5×5), Essay (2×8).",
        "Grade 9": "100 marks, 3 hours. MCQ (15×1), 2-mark (10), 5-mark (9), 8-mark (2).",
        "Grade 10": "100 marks, 3 hours (SSLC). MCQ (15×1), 2-mark (10), 5-mark (9), 8-mark (2).",
        "Grade 11": "90 marks, 3 hours (HSC). Part I MCQ, Part II 2-mark, Part III 3-mark, Part IV 5-mark, Part V 7-mark.",
        "Grade 12": "90 marks, 3 hours (HSC). Part I MCQ, Part II 2-mark, Part III 3-mark, Part IV 5-mark, Part V 7-mark.",
    },
    "UP Board": {
        "full_name": "UP Madhyamik Shiksha Parishad (UPMSP)",
        "Grade 6": "50 marks, 2 hours. Objective (MCQ + fill-in) and subjective sections.",
        "Grade 7": "50 marks, 2 hours. Objective and subjective problem-solving sections.",
        "Grade 8": "50 marks, 2 hours. Objective and subjective sections.",
        "Grade 9": "70 marks written + 30 internal. Section A: objective. Section B: short answer. Section C: long answer.",
        "Grade 10": "70 marks written + 30 internal (High School). Objective (20), Short answer (24), Long answer (26).",
        "Grade 11": "100 marks (Intermediate). Section A: objective. Section B: short answer. Section C: long answer.",
        "Grade 12": "100 marks (Intermediate). Section A: objective. Section B: short answer. Section C: long answer.",
    },
    "West Bengal State Board": {
        "full_name": "West Bengal Board (WBBSE / WBCHSE)",
        "Grade 6": "50 marks, 2 hours. MCQ, short answer, long answer sections.",
        "Grade 7": "50 marks, 2 hours. MCQ, short answer, long answer sections.",
        "Grade 8": "60 marks, 2 hours. MCQ, short answer, long answer sections.",
        "Grade 9": "90 marks, 3 hours. MCQ (10), SAQ (20), LAQ (60).",
        "Grade 10": "90 marks, 3.15 hours (Madhyamik). MCQ (10), SAQ (20), LAQ (60).",
        "Grade 11": "80 marks, 3 hours (HS). MCQ, short answer, long answer.",
        "Grade 12": "80 marks, 3 hours (HS). MCQ, short answer, long answer.",
    },
    "IB (HL)": {
        "full_name": "IB Mathematics: Analysis & Approaches Higher Level",
        "Grade 6": "Not applicable — IB HL is for Grades 11–12.",
        "Grade 7": "Not applicable — IB HL is for Grades 11–12.",
        "Grade 8": "Not applicable — IB HL is for Grades 11–12.",
        "Grade 9": "Not applicable — IB HL is for Grades 11–12.",
        "Grade 10": "Not applicable — IB HL is for Grades 11–12.",
        "Grade 11": "Paper 1 style (no calculator, 120 min): Section A short (55 marks) + Section B extended (55 marks). Paper 2 (calculator): same structure.",
        "Grade 12": "Paper 1 (no calc, 120 min, 110 marks) + Paper 2 (calc, 120 min, 110 marks) + Paper 3 (calc, 60 min, 55 marks).",
    },
    "IB (SL)": {
        "full_name": "IB Mathematics: Analysis & Approaches Standard Level",
        "Grade 6": "Not applicable — IB SL is for Grades 11–12.",
        "Grade 7": "Not applicable — IB SL is for Grades 11–12.",
        "Grade 8": "Not applicable — IB SL is for Grades 11–12.",
        "Grade 9": "Not applicable — IB SL is for Grades 11–12.",
        "Grade 10": "Not applicable — IB SL is for Grades 11–12.",
        "Grade 11": "Paper 1 (no calculator, 90 min): Section A short + Section B extended. Paper 2 (calculator, 90 min).",
        "Grade 12": "Paper 1 (no calc, 90 min, 80 marks) + Paper 2 (calc, 90 min, 80 marks).",
    },
    "Cambridge IGCSE": {
        "full_name": "Cambridge IGCSE Mathematics (0580)",
        "Grade 6": "Practice in IGCSE Extended style — structured questions.",
        "Grade 7": "Practice in IGCSE Extended style — structured questions.",
        "Grade 8": "Practice in IGCSE Extended style — structured questions.",
        "Grade 9": "Extended Tier: Paper 2 style (90 min, 70 marks) — structured questions, calculator allowed.",
        "Grade 10": "Extended Tier: Paper 2 (90 min, 70 marks, no calculator) + Paper 4 (2.5 hours, 130 marks, calculator).",
        "Grade 11": "Not standard — use Cambridge A-Level.",
        "Grade 12": "Not standard — use Cambridge A-Level.",
    },
    "Cambridge A-Level": {
        "full_name": "Cambridge International A-Level Mathematics (9709)",
        "Grade 6": "Not applicable — Cambridge A-Level is for Grades 11–12.",
        "Grade 7": "Not applicable — Cambridge A-Level is for Grades 11–12.",
        "Grade 8": "Not applicable — Cambridge A-Level is for Grades 11–12.",
        "Grade 9": "Not applicable — Cambridge A-Level is for Grades 11–12.",
        "Grade 10": "Not applicable — Cambridge A-Level is for Grades 11–12.",
        "Grade 11": "AS Level (9709): Pure Mathematics Paper 1 (75 marks, 1.75 hours). Short and extended structured questions.",
        "Grade 12": "A-Level (9709): Pure Mathematics 1 & 3 (75 marks each, 1.75h) + Statistics/Mechanics option.",
    },
}

BOARDS = list(BOARD_FORMATS.keys())
PAPER_GRADES = [f"Grade {g}" for g in range(6, 13)]
PAPER_YEARS = [str(y) for y in range(2024, 2014, -1)]

# Official resource links — homepage level (stable)
OFFICIAL_RESOURCES = {
    "CBSE": {
        "official": ("https://cbse.gov.in", "CBSE official website"),
        "papers":   ("https://cbseacademic.nic.in/SQP.html", "CBSE Academic — Sample Question Papers"),
        "notes":    "Go to Academic → Question Bank / SQP section for year-wise papers.",
    },
    "ICSE": {
        "official": ("https://cisce.org", "CISCE official website"),
        "papers":   ("https://cisce.org/publications.aspx", "CISCE Publications — Specimen Papers"),
        "notes":    "Click Publications → Specimen Question Papers for ICSE/ISC.",
    },
    "ISC": {
        "official": ("https://cisce.org", "CISCE official website"),
        "papers":   ("https://cisce.org/publications.aspx", "CISCE Publications — ISC Specimen Papers"),
        "notes":    "Click Publications → Specimen Question Papers → ISC.",
    },
    "Maharashtra State Board": {
        "official": ("https://mahahsscboard.in", "MSBSHSE official website"),
        "papers":   ("https://mahahsscboard.in", "Maharashtra Board — navigate to Previous Year Papers"),
        "notes":    "Go to Student Section → Previous Year Question Papers.",
    },
    "Karnataka State Board": {
        "official": ("https://kseab.karnataka.gov.in", "KSEAB official website"),
        "papers":   ("https://kseab.karnataka.gov.in", "KSEAB — navigate to Question Papers"),
        "notes":    "Go to Examinations → Model Question Papers or Previous Year Papers.",
    },
    "Tamil Nadu State Board": {
        "official": ("https://dge.tn.gov.in", "Tamil Nadu DGE official website"),
        "papers":   ("https://dge.tn.gov.in", "TN DGE — navigate to Previous Question Papers"),
        "notes":    "Go to Previous Year Question Papers section for SSLC / HSC papers.",
    },
    "UP Board": {
        "official": ("https://upmsp.edu.in", "UPMSP official website"),
        "papers":   ("https://upmsp.edu.in", "UPMSP — navigate to Model Papers"),
        "notes":    "Go to Model Papers or Previous Year Papers section.",
    },
    "West Bengal State Board": {
        "official": ("https://wbbse.wb.gov.in", "WBBSE official website"),
        "papers":   ("https://wbchse.wb.gov.in", "WBCHSE — HS Board (Grades 11–12)"),
        "notes":    "WBBSE (Madhyamik) and WBCHSE (HS) both publish previous year papers on their sites.",
    },
    "IB (HL)": {
        "official": ("https://www.ibo.org", "International Baccalaureate official website"),
        "papers":   ("https://www.ibdocuments.com", "IB Documents — Past Papers Repository"),
        "notes":    "IBO does not publish past papers publicly. Use the IB Documents site or your school's IB resource centre.",
    },
    "IB (SL)": {
        "official": ("https://www.ibo.org", "International Baccalaureate official website"),
        "papers":   ("https://www.ibdocuments.com", "IB Documents — Past Papers Repository"),
        "notes":    "IBO does not publish past papers publicly. Use the IB Documents site or your school's IB resource centre.",
    },
    "Cambridge IGCSE": {
        "official": ("https://www.cambridgeinternational.org", "Cambridge International Education"),
        "papers":   ("https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-mathematics-0580/past-papers/", "Cambridge IGCSE 0580 Past Papers"),
        "notes":    "Click into the link to find year-wise past papers (free after free registration).",
    },
    "Cambridge A-Level": {
        "official": ("https://www.cambridgeinternational.org", "Cambridge International Education"),
        "papers":   ("https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-mathematics-9709/past-papers/", "Cambridge A-Level 9709 Past Papers"),
        "notes":    "Click into the link to find year-wise past papers (free after free registration).",
    },
    "SAT Math (USA)": {
        "official": ("https://satsuite.collegeboard.org", "College Board SAT Suite"),
        "papers":   ("https://satsuite.collegeboard.org/sat/practice-preparation/practice-tests", "SAT Official Practice Tests"),
        "notes":    "8 full official SAT practice tests are available free on the College Board website.",
    },
    "AMC 10 / AMC 12 (USA)": {
        "official": ("https://maa.org/math-competitions", "MAA Math Competitions"),
        "papers":   ("https://artofproblemsolving.com/wiki/index.php/AMC_Problems_and_Solutions", "Art of Problem Solving — AMC Past Problems"),
        "notes":    "AoPS hosts all past AMC 8/10/12/AIME problems with solutions.",
    },
    "AIME (USA)": {
        "official": ("https://maa.org/math-competitions", "MAA Math Competitions"),
        "papers":   ("https://artofproblemsolving.com/wiki/index.php/AIME_Problems_and_Solutions", "Art of Problem Solving — AIME Past Problems"),
        "notes":    "All AIME I and II papers from past years are on AoPS with community solutions.",
    },
    "UKMT (UK)": {
        "official": ("https://www.ukmt.org.uk", "UKMT official website"),
        "papers":   ("https://www.ukmt.org.uk/competition-papers", "UKMT Competition Papers — Past Papers"),
        "notes":    "UKMT publishes Junior, Intermediate and Senior past papers directly on their website.",
    },
    "Singapore A-Level (H2 Math)": {
        "official": ("https://www.seab.gov.sg", "Singapore Examinations and Assessment Board"),
        "papers":   ("https://www.seab.gov.sg/home/examinations/gce-a-level/a-level-past-years-exam-papers", "SEAB — GCE A-Level Past Year Papers"),
        "notes":    "SEAB publishes A-Level past papers. Registration may be required.",
    },
    "South Korea CSAT (수능)": {
        "official": ("https://www.suneung.re.kr", "KICE — Korea Institute for Curriculum and Evaluation"),
        "papers":   ("https://www.suneung.re.kr/main.do", "KICE — Official CSAT Papers"),
        "notes":    "Past CSAT papers are published on the KICE website in Korean. English translated versions are available via search.",
    },
    "Australia HSC / VCE": {
        "official": ("https://educationstandards.nsw.edu.au", "NESA — NSW Education Standards Authority"),
        "papers":   ("https://educationstandards.nsw.edu.au/wps/portal/nesa/11-12/resources/hsc-exam-papers", "NESA — HSC Past Exam Papers"),
        "notes":    "NESA (NSW/HSC) and VCAA (VCE/Victoria) both publish free past papers on their sites.",
    },
    "China Gaokao (高考)": {
        "official": ("https://www.gaokao.cn", "Gaokao.cn — official information portal"),
        "papers":   ("https://www.gaokao.cn", "Navigate to 真题 (Past Papers) section"),
        "notes":    "Past Gaokao papers are available on gaokao.cn and major Chinese education sites.",
    },
    "Japan Kyotsu-Test (共通テスト)": {
        "official": ("https://www.dnc.ac.jp", "National Center for University Entrance Examinations (NCUEE)"),
        "papers":   ("https://www.dnc.ac.jp/kyotsu/kako/", "NCUEE — Past Kyotsu-Test Papers"),
        "notes":    "The NCUEE publishes all past Kyotsu-Test papers (共通テスト) on their website.",
    },
    "Germany Abitur": {
        "official": ("https://www.kmk.org", "Kultusministerkonferenz (KMK)"),
        "papers":   ("https://www.standardsicherung.schulministerium.nrw.de", "NRW Standardsicherung — Abitur Papers (NRW example)"),
        "notes":    "Abitur papers vary by state (Bundesland). Search '[state] Abitur Mathematik Prüfungsaufgaben [year]'.",
    },
    "France Baccalauréat (Terminale)": {
        "official": ("https://www.education.gouv.fr", "Ministère de l'Éducation Nationale"),
        "papers":   ("https://www.sujetdebac.fr", "Sujet de Bac — Past Baccalauréat Papers"),
        "notes":    "Past Bac papers (sujets et corrigés) are freely available on sujetdebac.fr.",
    },
    "Math Olympiad (IMO/RMO)": {
        "official": ("https://www.imo-official.org", "International Mathematical Olympiad — official site"),
        "papers":   ("https://artofproblemsolving.com/wiki/index.php/IMO_Problems_and_Solutions", "AoPS — IMO Past Problems & Solutions"),
        "notes":    "All IMO problems since 1959 are available on the official IMO site and AoPS.",
    },
    "IIT JEE": {
        "official": ("https://jeeadv.ac.in", "JEE Advanced official website"),
        "papers":   ("https://jeeadv.ac.in/pastqp.html", "JEE Advanced — Past Question Papers"),
        "notes":    "JEE Advanced past papers are on jeeadv.ac.in. JEE Main papers are on jeemain.nta.nic.in.",
    },
    "BITSAT (BITS Pilani)": {
        "official": ("https://www.bitsadmission.com", "BITS Pilani Admission — BITSAT"),
        "papers":   ("https://www.bitsadmission.com", "BITSAT — Sample Papers & Practice"),
        "notes":    "BITS Pilani publishes official sample papers on their admission site. Past year papers are available on coaching institute sites.",
    },
}

# All exams/boards with official resources (for Past Resources tab)
ALL_RESOURCE_EXAMS = list(OFFICIAL_RESOURCES.keys())

# ═════════════════════════════════════════════════════════════════════════════
# LATEX RULES
# ═════════════════════════════════════════════════════════════════════════════
LATEX_RULES = """
MANDATORY LATEX FORMATTING — no exceptions:
- $...$ for inline math (all variables, expressions, numbers in equations)
- $$...$$ for display/standalone equations
- NEVER write math as English words:
  ✗ "x squared" → ✓ $x^2$      ✗ "integral of f(x)" → ✓ $\\int f(x)\\,dx$
  ✗ "sqrt of 2" → ✓ $\\sqrt{2}$ ✗ "pi" → ✓ $\\pi$    ✗ "infinity" → ✓ $\\infty$
  ✗ "a/b"      → ✓ $\\frac{a}{b}$   ✗ "limit x→0" → ✓ $\\lim_{x\\to 0}$
- Fractions: $\\frac{a}{b}$   Powers: $x^n$   Subscripts: $a_n$
- Greek: $\\alpha,\\beta,\\gamma,\\pi,\\theta,\\lambda,\\sigma,\\omega$
- Trig: $\\sin x,\\cos x,\\tan x,\\sec x,\\csc x,\\cot x$
- Calculus: $f'(x),\\frac{dy}{dx},\\int_a^b f(x)\\,dx,\\lim_{x\\to a},\\sum_{i=1}^{n}$
- Inequalities: $\\leq,\\geq,\\neq,\\approx,\\in,\\equiv$
- Binomial: $\\binom{n}{k}$   Absolute: $|x|$   Vectors: $\\vec{v},\\hat{i}$
- Matrices: $$\\begin{pmatrix}a&b\\\\c&d\\end{pmatrix}$$
"""

# ═════════════════════════════════════════════════════════════════════════════
# API CLIENT
# ═════════════════════════════════════════════════════════════════════════════
def get_client():
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        api_key = None
    if not api_key or api_key.strip() == "sk-ant-your-key-here":
        st.error("**API key not set.** Add `ANTHROPIC_API_KEY` in Streamlit Cloud → Manage app → Settings → Secrets.", icon="🔑")
        st.stop()
    if not api_key.startswith("sk-ant-"):
        st.error(f"**API key format wrong** — starts with `{api_key[:10]}...`, should start with `sk-ant-`.", icon="⚠️")
        st.stop()
    return anthropic.Anthropic(api_key=api_key.strip())

# ═════════════════════════════════════════════════════════════════════════════
# PROMPTS
# ═════════════════════════════════════════════════════════════════════════════
def build_problem_prompt(grade, difficulty, topic, subtopic):
    extra = ""
    if "JEE" in grade: extra = " Use IIT JEE / JEE Advanced style."
    elif "Olympiad" in grade or "IMO" in grade: extra = " Require elegant, non-routine olympiad reasoning."
    elif "BITSAT" in grade: extra = " Use BITSAT multiple-choice style."
    elif "SAT" in grade: extra = " Use SAT-style question format."
    elif "AMC" in grade or "AIME" in grade: extra = " Use AMC/AIME competition style."
    elif "UKMT" in grade: extra = " Use UKMT competition style."
    return f"""You are an expert maths teacher. Generate ONE self-contained problem for:
Level: {grade}{extra}  |  Topic: {topic} → {subtopic}  |  Difficulty: {difficulty}

{LATEX_RULES}

Format EXACTLY as:
PROBLEM:
<complete problem, ALL math in LaTeX, no answer>

HINT:
<one subtle nudge, LaTeX for any math>"""


def build_solution_prompt(grade, difficulty, topic, subtopic, problem):
    extra = " JEE-style shortcuts where applicable." if "JEE" in grade else ""
    extra += " Elegant olympiad reasoning." if "Olympiad" in grade or "IMO" in grade else ""
    return f"""You are an expert maths tutor.{extra}
Topic: {topic} → {subtopic}  |  Level: {grade}  |  Difficulty: {difficulty}
Problem: {problem}

{LATEX_RULES}

**Answer:** <final answer in LaTeX>
**Step-by-Step Solution:** <numbered steps, every symbol in LaTeX, explain the WHY>
**Key Concept:** <1–2 sentences>
**Common Mistakes:** <1–2 wrong-vs-correct examples in LaTeX>"""


def build_paper_prompt(grade, board, year, topics_note):
    fmt = BOARD_FORMATS[board].get(grade, "Standard exam format for this grade.")
    year_note = f" Mirror the question style and difficulty of {board} {year} papers." if year else ""
    return f"""Generate a complete mathematics practice paper for:
Board: {board} ({BOARD_FORMATS[board]['full_name']})  |  Grade: {grade}  |  Year style: {year}
Topics: {topics_note}
Format: {fmt}{year_note}

{LATEX_RULES}

Include: proper header (Board, Class, Subject, Max Marks, Time, Date), general instructions,
all sections as per format with question numbers and marks in brackets [X Marks],
MCQ with options (A)–(D), case-study with scenario + sub-parts.
Do NOT include answers. Use LaTeX for all math. Output clean markdown."""


def build_paper_solutions_prompt(paper_text, grade, board):
    return f"""Provide COMPLETE solutions and marking scheme for every question in this {board} {grade} paper.

{LATEX_RULES}

PAPER:
{paper_text}

For each question:
**Q[n]. [type] — [marks] marks**
*Solution:* <step-by-step with LaTeX>
*Answer:* <final answer in LaTeX>
*Marks Breakdown:* <e.g. 1M setup + 2M working + 1M answer>

For MCQs: state correct option + brief LaTeX justification.
For Case Study: solve all sub-parts separately."""


def build_doubt_prompt(grade_ctx, question_text, extra_context=""):
    ctx = f" The student is at {grade_ctx} level." if grade_ctx != "Not specified" else ""
    extra = f"\n\nAdditional context: {extra_context}" if extra_context.strip() else ""
    return f"""You are an expert, patient mathematics tutor.{ctx}{extra}

{LATEX_RULES}

Solve or explain the following doubt completely:
{question_text}

Structure your response as:
**Direct Answer / Key Result:**
<Answer with LaTeX>

**Full Explanation:**
<Step-by-step working. Every symbol in LaTeX. Explain WHY each step works.>

**Key Concept:**
<The core mathematical idea being tested.>

If the question has multiple parts, address each part separately."""

# ═════════════════════════════════════════════════════════════════════════════
# STREAM + PARSE HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def stream_response(client, prompt, placeholder, max_tokens=1800, image_data=None, media_type=None):
    content = []
    if image_data:
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}})
    content.append({"type": "text", "text": prompt})
    full_text = ""
    try:
        with client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": content}],
        ) as stream:
            for text in stream.text_stream:
                full_text += text
                placeholder.markdown(full_text + " ▌")
        placeholder.empty()
    except anthropic.AuthenticationError:
        st.error("**Invalid API key.** Create a new key at https://console.anthropic.com/settings/keys and update Streamlit Secrets.", icon="🔑")
        st.stop()
    except anthropic.APIStatusError as e:
        st.error(f"**API Error {e.status_code}:** {e.message}", icon="❌")
        st.stop()
    return full_text


def parse_problem(text):
    result = {"problem": text, "hint": ""}
    m = re.search(r"PROBLEM:\s*(.*?)(?=HINT:|$)", text, re.DOTALL | re.IGNORECASE)
    if m: result["problem"] = m.group(1).strip()
    m = re.search(r"HINT:\s*(.*?)$", text, re.DOTALL | re.IGNORECASE)
    if m: result["hint"] = m.group(1).strip()
    return result


def extract_pdf_text(pdf_bytes):
    if not PDF_SUPPORT:
        return None
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages).strip()
    except Exception:
        return None


def google_search_url(query):
    import urllib.parse
    return f"https://www.google.com/search?q={urllib.parse.quote(query)}"

# ═════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═════════════════════════════════════════════════════════════════════════════
for k, v in {
    "problem_data": None, "solution": None,
    "show_hint": False, "show_solution": False, "problem_count": 0,
    "paper_text": None, "paper_solutions": None, "show_paper_solutions": False, "paper_meta": None,
    "doubt_response": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═════════════════════════════════════════════════════════════════════════════
# HEADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">🧮 Daily Math Problem Solver</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Grade 1 · IIT JEE · SAT · AMC · UKMT · Gaokao · Abitur & more — powered by AI</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TABS
# ═════════════════════════════════════════════════════════════════════════════
tab_daily, tab_paper, tab_resources, tab_doubt = st.tabs([
    "📝 Daily Practice", "📋 Exam Papers", "🏛️ Past Paper Resources", "💬 Ask a Doubt"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DAILY PRACTICE
# ══════════════════════════════════════════════════════════════════════════════
with tab_daily:
    with st.sidebar:
        st.header("⚙️ Daily Practice")
        grade    = st.selectbox("📚 Grade / Level / Exam", GRADES)
        topics   = list(GRADE_CURRICULUM[grade].keys())
        topic    = st.selectbox("📖 Topic", topics)
        subtopic = st.selectbox("📐 Subtopic", GRADE_CURRICULUM[grade][topic])
        difficulty = st.radio("🎯 Difficulty", DIFFICULTIES, index=1,
                              format_func=lambda d: f"{DIFFICULTY_EMOJI[d]} {d}")
        st.divider()
        generate_btn = st.button("✨ Generate Problem", use_container_width=True, type="primary")
        st.divider()
        st.markdown(f"**Problems solved this session:** {st.session_state.problem_count} 🏆")
        st.markdown("**Tips:**\n- Attempt before looking at hints\n- Understand *why* each step works\n- Increase difficulty once comfortable!")

    if generate_btn:
        st.session_state.update(show_hint=False, show_solution=False, solution=None)
        client = get_client()
        ph = st.empty()
        raw = stream_response(client, build_problem_prompt(grade, difficulty, topic, subtopic), ph)
        st.session_state.problem_data = {**parse_problem(raw), "grade": grade,
            "difficulty": difficulty, "topic": topic, "subtopic": subtopic}

    if st.session_state.problem_data:
        data = st.session_state.problem_data
        dc = data["difficulty"].lower()
        st.markdown(
            f'<span class="badge badge-grade">{data["grade"]}</span>'
            f'<span class="badge badge-{dc}">{DIFFICULTY_EMOJI[data["difficulty"]]} {data["difficulty"]}</span>'
            f'<span class="badge badge-topic">📖 {data["topic"]}</span>'
            f'<span class="badge badge-topic">📐 {data["subtopic"]}</span>',
            unsafe_allow_html=True)
        st.markdown('<p class="section-label label-problem">📝 Problem</p>', unsafe_allow_html=True)
        st.info(data["problem"])

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("💡 Show Hint", use_container_width=True):
                st.session_state.show_hint = not st.session_state.show_hint
        with c2:
            if st.button("🔍 Show Solution & Explanation", use_container_width=True, type="primary"):
                st.session_state.show_solution = True
                if not st.session_state.solution:
                    client = get_client()
                    ph = st.empty()
                    sol = stream_response(client, build_solution_prompt(
                        data["grade"], data["difficulty"], data["topic"], data["subtopic"], data["problem"]), ph)
                    st.session_state.solution = sol
                    st.session_state.problem_count += 1
        with c3:
            if st.button("🔄 New Problem (Same Settings)", use_container_width=True):
                st.session_state.update(show_hint=False, show_solution=False, solution=None)
                client = get_client()
                ph = st.empty()
                raw = stream_response(client, build_problem_prompt(
                    data["grade"], data["difficulty"], data["topic"], data["subtopic"]), ph)
                st.session_state.problem_data = {**parse_problem(raw), "grade": data["grade"],
                    "difficulty": data["difficulty"], "topic": data["topic"], "subtopic": data["subtopic"]}
                st.rerun()

        if st.session_state.show_hint and data.get("hint"):
            st.markdown('<p class="section-label label-hint">💡 Hint</p>', unsafe_allow_html=True)
            st.warning(data["hint"])
        if st.session_state.show_solution and st.session_state.solution:
            st.markdown('<p class="section-label label-solution">✅ Solution & Explanation</p>', unsafe_allow_html=True)
            st.success(st.session_state.solution)
    else:
        st.info("👈 **Select your grade/exam, topic, subtopic and difficulty in the sidebar, then click Generate Problem.**", icon="🚀")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 🎓 For All Levels\nGrade 1 through IIT JEE, SAT, AMC, UKMT, Gaokao, Abitur and more.")
        with c2:
            st.markdown("### 🤖 AI-Powered\nProper LaTeX math notation. Step-by-step explanations tailored to your exam.")
        with c3:
            st.markdown("### 📈 Daily Habits\nOne focused subtopic per day. Understand it deeply, then move on.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — EXAM PAPERS
# ══════════════════════════════════════════════════════════════════════════════
with tab_paper:
    st.subheader("📋 Generate a Full Exam Paper")
    st.caption("AI generates a complete practice paper in your chosen board's official format. For real past papers, see the **Past Paper Resources** tab.")

    pc1, pc2, pc3 = st.columns([1.2, 1, 1])
    with pc1: p_board = st.selectbox("🏫 Board / Curriculum", BOARDS, key="p_board")
    with pc2: p_grade = st.selectbox("📚 Grade", PAPER_GRADES, index=4, key="p_grade")
    with pc3: p_year  = st.selectbox("📅 Paper Year / Style", PAPER_YEARS, key="p_year")

    all_topics = list(GRADE_CURRICULUM.get(p_grade, {}).keys())
    p_topics_choice = st.radio("📖 Topics", ["All topics for this grade", "Select specific topics"], horizontal=True)
    if p_topics_choice == "Select specific topics" and all_topics:
        p_sel = st.multiselect("Choose topics", all_topics, default=all_topics[:3])
        topics_note = ", ".join(p_sel) if p_sel else "All topics"
    else:
        topics_note = "Full syllabus for this grade"

    board_grade_note = BOARD_FORMATS[p_board].get(p_grade, "")
    if board_grade_note.startswith("Not applicable") or board_grade_note.startswith("Not standard"):
        st.warning(f"⚠️ {board_grade_note}")

    gen_paper_btn = st.button("📄 Generate Exam Paper", type="primary",
                              disabled=board_grade_note.startswith(("Not applicable", "Not standard")))

    if gen_paper_btn:
        st.session_state.update(paper_solutions=None, show_paper_solutions=False)
        client = get_client()
        st.info("⏳ Generating your paper — this may take up to 60 seconds for a full paper…", icon="🔄")
        ph = st.empty()
        paper = stream_response(client, build_paper_prompt(p_grade, p_board, p_year, topics_note), ph, max_tokens=4096)
        st.session_state.paper_text = paper
        st.session_state.paper_meta = {"grade": p_grade, "board": p_board, "year": p_year}
        st.rerun()

    if st.session_state.paper_text:
        meta = st.session_state.paper_meta or {}
        st.markdown(f"""<div class="paper-header">
            <h3 style="margin:0;color:white;">📄 {meta.get('board','')} &nbsp;|&nbsp; {meta.get('grade','')}</h3>
            <p style="margin:.3rem 0 0;opacity:.75;font-size:.9rem;">{meta.get('year','')} — AI-Generated Practice Paper</p>
        </div>""", unsafe_allow_html=True)
        st.markdown(st.session_state.paper_text)
        st.divider()
        cs1, cs2 = st.columns(2)
        with cs1:
            if st.button("✅ Generate Complete Solutions & Marking Scheme", type="primary", use_container_width=True):
                st.session_state.show_paper_solutions = True
                if not st.session_state.paper_solutions:
                    client = get_client()
                    st.info("⏳ Generating full solutions…", icon="🔄")
                    ph = st.empty()
                    sols = stream_response(client, build_paper_solutions_prompt(
                        st.session_state.paper_text, meta.get("grade",""), meta.get("board","")), ph, max_tokens=4096)
                    st.session_state.paper_solutions = sols
                    st.rerun()
        with cs2:
            if st.button("🔄 Generate New Paper", use_container_width=True):
                st.session_state.update(paper_text=None, paper_solutions=None, show_paper_solutions=False)
                st.rerun()

        if st.session_state.show_paper_solutions and st.session_state.paper_solutions:
            st.markdown('<p class="section-label label-solution">✅ Complete Solutions & Marking Scheme</p>', unsafe_allow_html=True)
            st.success(st.session_state.paper_solutions)
    else:
        st.markdown("""
**How it works:**
1. Select board, grade and year style above
2. Click **Generate Exam Paper** — AI writes a complete paper in that board's official section structure
3. Attempt the paper yourself (or give it to a student)
4. Click **Generate Complete Solutions** to reveal the full marking scheme with step-by-step working
""")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PAST PAPER RESOURCES
# ══════════════════════════════════════════════════════════════════════════════
with tab_resources:
    st.subheader("🏛️ Find Official Past Papers")
    st.caption("Select a board/exam and year to get a direct search link for that paper, plus the official website.")

    r1, r2, r3 = st.columns([1.5, 1, 1])
    with r1: r_board = st.selectbox("🏫 Board / Exam", ALL_RESOURCE_EXAMS, key="r_board")
    with r2:
        r_grade_opts = ["All Grades"] + [f"Grade {g}" for g in range(6, 13)]
        r_grade = st.selectbox("📚 Grade / Class", r_grade_opts, key="r_grade")
    with r3:
        r_year = st.selectbox("📅 Year", PAPER_YEARS, key="r_year")

    # Grade number for search queries
    grade_num = r_grade.replace("Grade ", "") if r_grade != "All Grades" else ""
    grade_label = f"Class {grade_num}" if grade_num else ""

    # Build search query
    search_q = f"{r_board} {grade_label} Mathematics question paper {r_year} PDF".strip()
    search_url = google_search_url(search_q)
    solutions_search_url = google_search_url(f"{r_board} {grade_label} Mathematics {r_year} solutions answer key PDF")

    res = OFFICIAL_RESOURCES.get(r_board, {})
    official_url, official_label = res.get("official", ("#", r_board))
    papers_url, papers_label = res.get("papers", ("#", "Past Papers"))
    notes = res.get("notes", "")

    st.divider()

    # Cards
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
<div class="resource-card">
    <strong>🔍 Search for {r_board} {grade_label} {r_year} Paper</strong><br>
    <span style="color:#555;font-size:.9rem;">Opens a Google search for this specific paper</span><br><br>
    <a href="{search_url}" target="_blank" style="background:#667eea;color:white;padding:.4rem 1rem;border-radius:6px;text-decoration:none;font-weight:600;">
        Search Question Paper →
    </a>
    &nbsp;&nbsp;
    <a href="{solutions_search_url}" target="_blank" style="background:#2e7d32;color:white;padding:.4rem 1rem;border-radius:6px;text-decoration:none;font-weight:600;">
        Search Solutions →
    </a>
</div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
<div class="resource-card">
    <strong>🌐 Official {r_board} Website</strong><br>
    <span style="color:#555;font-size:.9rem;">{official_label}</span><br>
    <a href="{official_url}" target="_blank">🔗 {official_url}</a><br><br>
    <strong>📄 Past Papers Section</strong><br>
    <span style="color:#555;font-size:.9rem;">{papers_label}</span><br>
    <a href="{papers_url}" target="_blank">🔗 {papers_url}</a>
</div>""", unsafe_allow_html=True)

    if notes:
        st.info(f"ℹ️ **Note:** {notes}")

    st.divider()
    st.markdown("#### 🔗 Quick Links — All Boards & Exams")

    # Group display
    groups = {
        "🇮🇳 Indian Boards": ["CBSE","ICSE","ISC","Maharashtra State Board","Karnataka State Board","Tamil Nadu State Board","UP Board","West Bengal State Board"],
        "🇮🇳 Indian Competitive": ["IIT JEE","BITSAT (BITS Pilani)","Math Olympiad (IMO/RMO)"],
        "🇺🇸 USA": ["SAT Math (USA)","AMC 10 / AMC 12 (USA)","AIME (USA)"],
        "🌍 International": ["UKMT (UK)","Singapore A-Level (H2 Math)","South Korea CSAT (수능)","Australia HSC / VCE","China Gaokao (高考)","Japan Kyotsu-Test (共通テスト)","Germany Abitur","France Baccalauréat (Terminale)","IB (HL)","IB (SL)","Cambridge IGCSE","Cambridge A-Level"],
    }
    gcols = st.columns(len(groups))
    for col, (group_name, exams) in zip(gcols, groups.items()):
        with col:
            st.markdown(f"**{group_name}**")
            for exam in exams:
                res_e = OFFICIAL_RESOURCES.get(exam, {})
                url_e, _ = res_e.get("official", ("#", exam))
                st.markdown(f"[{exam}]({url_e})", unsafe_allow_html=False)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ASK A DOUBT
# ══════════════════════════════════════════════════════════════════════════════
with tab_doubt:
    st.subheader("💬 Ask Your Math Doubt")
    st.caption("Type your doubt, or upload a photo/scan/PDF of the problem. AI will explain it step-by-step with proper math notation.")

    d1, d2 = st.columns([1, 2])
    with d1:
        doubt_grade = st.selectbox("Your Grade / Level (context)", ["Not specified"] + GRADES, key="doubt_grade")
    with d2:
        extra_context = st.text_input("Any extra context? (optional)",
            placeholder="e.g. 'I don't understand step 3' or 'Find all real solutions'", key="doubt_ctx")

    input_method = st.radio("📥 How would you like to submit your doubt?",
        ["✏️ Type your question", "📷 Upload an image (photo / scan)", "📄 Upload a PDF"],
        horizontal=True, key="doubt_method")

    prompt_text = None
    image_b64   = None
    image_mime  = None
    ready       = False

    if input_method == "✏️ Type your question":
        typed = st.text_area("Type your math doubt or question here:", height=160, key="doubt_typed",
                             placeholder="e.g. Solve $x^2 - 5x + 6 = 0$, or explain integration by parts…")
        if typed.strip():
            prompt_text = build_doubt_prompt(doubt_grade, typed.strip(), extra_context)
            ready = True

    elif input_method == "📷 Upload an image (photo / scan)":
        uploaded_img = st.file_uploader("Upload image of your question (JPG, PNG):", type=["jpg","jpeg","png"], key="doubt_img")
        if uploaded_img:
            st.image(uploaded_img, caption="Uploaded image", use_container_width=False, width=420)
            img_bytes  = uploaded_img.read()
            image_b64  = base64.b64encode(img_bytes).decode()
            image_mime = uploaded_img.type if uploaded_img.type in ["image/jpeg","image/png","image/gif","image/webp"] else "image/jpeg"
            img_question = "Solve or explain the math problem shown in this image."
            prompt_text  = build_doubt_prompt(doubt_grade, img_question, extra_context)
            ready = True

    elif input_method == "📄 Upload a PDF":
        if not PDF_SUPPORT:
            st.warning("PDF support requires `pdfplumber`. It will be available after the next deployment.", icon="⚠️")
        else:
            uploaded_pdf = st.file_uploader("Upload PDF with your question:", type=["pdf"], key="doubt_pdf")
            if uploaded_pdf:
                pdf_bytes = uploaded_pdf.read()
                pdf_text  = extract_pdf_text(pdf_bytes)
                if pdf_text:
                    st.success(f"✅ Extracted {len(pdf_text)} characters from PDF.", icon="📄")
                    with st.expander("Preview extracted text"):
                        st.text(pdf_text[:1500] + ("…" if len(pdf_text) > 1500 else ""))
                    prompt_text = build_doubt_prompt(doubt_grade, pdf_text, extra_context)
                    ready = True
                else:
                    st.error("Could not extract text from this PDF. Try uploading an image instead.", icon="❌")

    st.divider()
    ask_btn = st.button("🤔 Get AI Explanation", type="primary", disabled=not ready, use_container_width=False)

    if ask_btn and ready and prompt_text:
        st.session_state.doubt_response = None
        client = get_client()
        with st.spinner("Thinking through your doubt…"):
            ph = st.empty()
            response = stream_response(client, prompt_text, ph, max_tokens=2000,
                                       image_data=image_b64, media_type=image_mime)
        st.session_state.doubt_response = response

    if st.session_state.doubt_response:
        st.markdown('<p class="section-label label-solution">✅ AI Explanation</p>', unsafe_allow_html=True)
        st.success(st.session_state.doubt_response)
        if st.button("🔄 Clear & Ask Another", key="doubt_clear"):
            st.session_state.doubt_response = None
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer">Built with ❤️ using Streamlit & Claude AI</div>', unsafe_allow_html=True)
