import streamlit as st
import anthropic
import re

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
        font-size: 2.4rem; font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.2rem;
    }
    .subtitle { text-align:center; color:#666; font-size:1rem; margin-bottom:1.5rem; }
    .section-label {
        font-size: 0.82rem; font-weight: 700; letter-spacing: 0.08em;
        text-transform: uppercase; margin-bottom: 0.3rem; margin-top: 1rem;
    }
    .label-problem  { color: #667eea; }
    .label-hint     { color: #e6a817; }
    .label-solution { color: #2e7d32; }
    .badge {
        display: inline-block; padding: 0.25rem 0.75rem;
        border-radius: 20px; font-size: 0.78rem; font-weight: 700; margin-right: 0.4rem;
    }
    .badge-easy   { background:#d4edda; color:#155724; }
    .badge-medium { background:#fff3cd; color:#856404; }
    .badge-hard   { background:#f8d7da; color:#721c24; }
    .badge-grade  { background:#cce5ff; color:#004085; }
    .badge-topic  { background:#e2d9f3; color:#4a235a; }
    .paper-header {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: white; border-radius: 12px; padding: 1.5rem 2rem;
        text-align: center; margin-bottom: 1rem;
    }
    .resource-card {
        border: 1px solid #e0e0e0; border-radius: 10px;
        padding: 1rem 1.2rem; margin-bottom: 0.6rem;
        background: #fafafa;
    }
    .stButton > button { border-radius: 8px; font-weight: 600; }
    div[data-testid="stAlert"] { border-radius: 12px; font-size: 1.05rem; line-height: 1.8; }
    .footer {
        text-align: center; color: #aaa; font-size: 0.8rem;
        margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# ── Curriculum ────────────────────────────────────────────────────────────────
GRADE_CURRICULUM = {
    "Grade 1": {
        "Counting & Numbers": ["Counting 1–20", "Counting 1–100", "Number Ordering & Sequencing", "Even & Odd Numbers", "Comparing Numbers (>, <, =)"],
        "Addition": ["Adding Single-digit Numbers", "Number Bonds to 10", "Number Bonds to 20", "Adding with a Number Line", "Word Problems"],
        "Subtraction": ["Subtracting Single-digit Numbers", "Finding the Difference", "Subtraction on a Number Line", "Word Problems"],
        "Shapes & Patterns": ["2D Shapes (Circle, Square, Triangle, Rectangle)", "3D Shapes (Cube, Sphere, Cone, Cylinder)", "Sorting & Classifying Shapes", "Repeating Patterns"],
        "Measurement & Time": ["Comparing Lengths (Longer/Shorter)", "Comparing Weights (Heavier/Lighter)", "Telling Time (O'Clock & Half Past)", "Days of the Week & Months"],
    },
    "Grade 2": {
        "Place Value": ["Tens and Ones", "Hundreds, Tens and Ones", "Expanded Form", "Comparing 3-digit Numbers"],
        "Addition & Subtraction": ["2-digit Addition (No Regrouping)", "2-digit Addition (With Regrouping)", "2-digit Subtraction (No Regrouping)", "2-digit Subtraction (With Regrouping)", "Word Problems"],
        "Multiplication Introduction": ["Equal Groups", "Arrays", "Skip Counting (2s, 5s, 10s)", "Multiplication as Repeated Addition"],
        "Fractions Introduction": ["Halves", "Quarters (Fourths)", "Thirds", "Identifying Fractions of a Shape"],
        "Measurement, Time & Money": ["Measuring Length (cm & m)", "Telling Time (Quarter Past/To)", "Counting Coins", "Simple Money Problems"],
    },
    "Grade 3": {
        "Multiplication": ["Times Tables (2–5)", "Times Tables (6–10)", "Multiplication Properties", "Multiplying by 10 & 100", "Word Problems"],
        "Division": ["Equal Sharing", "Division as Repeated Subtraction", "Division Facts", "Remainders Introduction"],
        "Fractions": ["Equivalent Fractions", "Comparing & Ordering Fractions", "Fractions on a Number Line", "Simple Addition of Like Fractions"],
        "Geometry": ["Perimeter of Polygons", "Area by Counting Squares", "Types of Angles", "Quadrilaterals & Their Properties"],
        "Data & Graphs": ["Tally Charts", "Bar Graphs", "Pictographs", "Reading & Interpreting Data"],
    },
    "Grade 4": {
        "Multi-digit Arithmetic": ["Multi-digit Multiplication", "Long Division (No Remainder)", "Long Division (With Remainder)", "Estimation & Rounding", "Word Problems"],
        "Fractions & Decimals": ["Adding & Subtracting Like Fractions", "Mixed Numbers & Improper Fractions", "Decimal Place Value (Tenths & Hundredths)", "Comparing & Ordering Decimals"],
        "Angles & Geometry": ["Measuring Angles with a Protractor", "Types of Angles (Acute, Obtuse, Reflex)", "Angles on a Straight Line", "Angles in a Triangle"],
        "Area & Perimeter": ["Area of Rectangles & Squares", "Perimeter of Polygons", "Area of Composite Shapes", "Units of Area (cm², m²)"],
        "Factors & Multiples": ["Factors of a Number", "Multiples & LCM", "Prime & Composite Numbers", "Highest Common Factor (HCF)"],
    },
    "Grade 5": {
        "Fractions Operations": ["Adding & Subtracting Unlike Fractions", "Multiplying Fractions", "Dividing Fractions", "Fraction Word Problems", "Mixed Number Operations"],
        "Decimals": ["Adding & Subtracting Decimals", "Multiplying Decimals", "Dividing Decimals", "Rounding & Estimation"],
        "Ratios & Percentages": ["Introduction to Ratios", "Equivalent Ratios", "Percentages (Finding % of a Number)", "Percentage Word Problems"],
        "Geometry & Volume": ["Volume of Cuboids", "Surface Area of Cuboids", "Coordinate Plane (Quadrant I)", "Plotting & Reading Coordinates"],
        "Algebraic Thinking": ["Numerical Expressions & BODMAS", "Simple Algebraic Expressions", "Patterns & Rules", "Introduction to Equations"],
    },
    "Grade 6": {
        "Ratios & Rates": ["Ratios & Equivalent Ratios", "Unit Rates", "Proportions", "Percentage (Increase & Decrease)", "Speed, Distance & Time"],
        "Integers": ["Introduction to Negative Numbers", "Adding Integers", "Subtracting Integers", "Multiplying & Dividing Integers", "Absolute Value"],
        "Expressions & Equations": ["Algebraic Expressions (Simplification)", "Substitution", "One-step Equations", "Two-step Equations", "Inequalities"],
        "Geometry": ["Area of Triangles & Parallelograms", "Area of Trapezoids", "Circumference & Area of Circles", "Nets & Surface Area", "Volume of Prisms"],
        "Statistics": ["Mean, Median, Mode & Range", "Frequency Tables", "Bar Charts & Histograms", "Pie Charts", "Interpreting Data & Outliers"],
    },
    "Grade 7": {
        "Proportional Reasoning": ["Direct Proportion", "Inverse Proportion", "Percentage Problems (Profit & Loss)", "Simple Interest", "Ratio & Proportion Word Problems"],
        "Linear Equations": ["Forming & Solving Linear Equations", "Equations with Variables on Both Sides", "Linear Inequalities", "Word Problems with Linear Equations"],
        "Geometry": ["Angles in Parallel Lines", "Angle Sum of Polygons", "Basic Circle Theorems", "Congruence & Similarity", "Construction & Loci"],
        "Probability": ["Sample Space & Events", "Simple Probability", "Complementary Events", "Experimental vs Theoretical Probability", "Tree Diagrams"],
        "Statistics": ["Box Plots & Stem-and-Leaf Plots", "Scatter Plots & Correlation", "Mean from Grouped Data", "Comparing Two Data Sets"],
    },
    "Grade 8": {
        "Linear Functions": ["Gradient (Slope) of a Line", "Equation of a Line (y = mx + c)", "Graphing Linear Functions", "Parallel & Perpendicular Lines", "Rate of Change"],
        "Systems of Equations": ["Solving by Substitution", "Solving by Elimination", "Graphical Solution", "Word Problems with 2 Unknowns"],
        "Quadratics (Introduction)": ["Expanding Brackets & Identities", "Factoring (Common Factor & Grouping)", "Factoring Trinomials (x² + bx + c)", "Difference of Two Squares"],
        "Pythagorean Theorem": ["Finding the Hypotenuse", "Finding a Missing Side", "Distance Between Two Points", "Applications in 3D"],
        "Exponents & Surds": ["Laws of Exponents", "Negative & Fractional Exponents", "Introduction to Surds (√)", "Simplifying Surds"],
    },
    "Grade 9": {
        "Algebra": ["Polynomials (Addition, Subtraction, Multiplication)", "Polynomial Division & Remainder Theorem", "Rational Expressions", "Factoring (Sum/Difference of Cubes)"],
        "Quadratic Equations": ["Solving by Factoring", "Completing the Square", "Quadratic Formula", "Discriminant & Nature of Roots", "Quadratic Word Problems"],
        "Functions": ["Function Notation & Evaluation", "Domain & Range", "Inverse Functions", "Composite Functions", "Graphing Functions"],
        "Coordinate Geometry": ["Distance & Midpoint Formula", "Equation of a Circle", "Tangent to a Circle", "Collinearity & Area of Triangle"],
        "Statistics & Probability": ["Variance & Standard Deviation", "Normal Distribution (Introduction)", "Conditional Probability", "Permutations", "Combinations"],
    },
    "Grade 10": {
        "Advanced Algebra": ["Exponential & Logarithmic Functions", "Laws of Logarithms", "Exponential Equations", "Absolute Value Equations & Inequalities"],
        "Trigonometry": ["Trigonometric Ratios (sin, cos, tan)", "Sine Rule", "Cosine Rule", "Area of Triangle using Trigonometry", "Angles of Elevation & Depression"],
        "Polynomials": ["Factor Theorem", "Remainder Theorem", "Roots & Coefficients", "Polynomial Long Division"],
        "Coordinate Geometry (Conics)": ["Parabola", "Circle (General & Standard Form)", "Ellipse (Introduction)", "Hyperbola (Introduction)"],
        "Probability": ["Permutations & Combinations", "Binomial Theorem", "Conditional Probability & Bayes' Theorem", "Random Variables & Expected Value"],
    },
    "Grade 11": {
        "Limits & Continuity": ["Concept of a Limit", "Limit Laws & Evaluation", "One-sided Limits", "Limits at Infinity", "Continuity & Discontinuity"],
        "Differentiation": ["Definition of the Derivative", "Power, Product & Quotient Rules", "Chain Rule", "Derivatives of Trig, Exponential & Log Functions", "Implicit Differentiation"],
        "Applications of Derivatives": ["Increasing / Decreasing Functions", "Local Maxima & Minima", "Concavity & Inflection Points", "Optimisation Problems", "Related Rates"],
        "Vectors": ["Vector Operations", "Dot Product", "Cross Product", "Angle Between Vectors", "Vector Equation of a Line"],
        "Complex Numbers": ["Algebra of Complex Numbers", "Argand Plane", "Modulus & Argument", "Polar Form", "De Moivre's Theorem"],
        "Sequences & Series": ["Arithmetic Sequences & Series", "Geometric Sequences & Series", "Sum to Infinity (Geometric)", "Binomial Theorem", "Sigma Notation"],
    },
    "Grade 12": {
        "Integration": ["Indefinite Integrals & Rules", "Integration by Substitution", "Integration by Parts", "Partial Fractions", "Integration of Trigonometric Functions"],
        "Definite Integrals & Applications": ["Definite Integrals & Area Under a Curve", "Area Between Two Curves", "Volume of Revolution", "Fundamental Theorem of Calculus"],
        "Differential Equations": ["Separable Differential Equations", "First-order Linear ODEs", "Homogeneous Differential Equations", "Applications (Growth & Decay)"],
        "Matrices & Determinants": ["Matrix Operations", "Determinant of a 2×2 & 3×3 Matrix", "Inverse of a Matrix", "Solving Linear Systems (Cramer's Rule)"],
        "3D Geometry": ["Direction Cosines & Direction Ratios", "Equation of a Line in 3D", "Equation of a Plane", "Angle Between Lines & Planes", "Distance from a Point to a Plane"],
        "Probability & Statistics": ["Probability Distributions", "Binomial Distribution", "Normal Distribution & Z-scores", "Bayes' Theorem", "Statistical Inference"],
    },
    "Math Olympiad": {
        "Number Theory": ["Divisibility & Remainders", "Prime Numbers & Factorisation", "GCD, LCM & Bezout's Identity", "Modular Arithmetic & Congruences", "Diophantine Equations"],
        "Combinatorics": ["Counting Principles", "Pigeonhole Principle", "Permutations & Combinations (Advanced)", "Inclusion-Exclusion Principle", "Graph Theory (Basic)"],
        "Geometry": ["Triangle Centers", "Circle Theorems & Power of a Point", "Similar & Congruent Triangles (Proofs)", "Ceva's & Menelaus' Theorems", "Projective & Inversive Geometry"],
        "Algebra": ["Functional Equations", "Polynomials & Their Roots", "Vieta's Formulas", "Algebraic Identities", "Sequences & Recurrence Relations"],
        "Inequalities": ["AM–GM Inequality", "Cauchy–Schwarz Inequality", "Jensen's Inequality", "Chebyshev's Sum Inequality", "Power Mean Inequality"],
    },
    "IIT JEE": {
        "Calculus": ["Limits & Continuity", "Differentiation (Rules & Applications)", "Indefinite Integration", "Definite Integration & Properties", "Differential Equations"],
        "Algebra": ["Complex Numbers & Quadratics", "Sequences, Series & Progressions", "Permutations & Combinations", "Binomial Theorem", "Matrices & Determinants"],
        "Coordinate Geometry": ["Straight Lines & Pair of Lines", "Circles & Family of Circles", "Parabola", "Ellipse", "Hyperbola"],
        "Trigonometry": ["Trigonometric Identities & Equations", "Inverse Trigonometric Functions", "Properties of Triangles", "Heights & Distances"],
        "Vectors & 3D Geometry": ["Vector Algebra (Dot & Cross Product)", "3D Lines & Planes", "Direction Cosines & Ratios", "Shortest Distance Between Lines"],
        "Probability & Statistics": ["Classical & Conditional Probability", "Bayes' Theorem", "Binomial & Poisson Distribution", "Mean, Variance & Standard Deviation"],
    },
}

# ── Board exam formats ────────────────────────────────────────────────────────
PAPER_GRADES = [f"Grade {g}" for g in range(6, 13)]

BOARD_FORMATS = {
    "CBSE": {
        "full_name": "Central Board of Secondary Education",
        "Grade 6":  "50 marks, 2 hours. Section A: 12 MCQ (1 mark each). Section B: 8 short answer (2 marks each). Section C: 5 long answer (4 marks each). Section D: 2 HOTS (5 marks each).",
        "Grade 7":  "50 marks, 2 hours. Section A: 12 MCQ (1 mark each). Section B: 8 short answer (2 marks each). Section C: 5 long answer (4 marks each). Section D: 2 HOTS (5 marks each).",
        "Grade 8":  "60 marks, 2.5 hours. Section A: 15 MCQ (1 mark each). Section B: 8 short answer (2 marks each). Section C: 5 long answer (4 marks each). Section D: 2 HOTS (5 marks each).",
        "Grade 9":  "80 marks, 3 hours. Section A: 20 MCQ (1 mark each). Section B: 5 Very Short Answer (2 marks each). Section C: 6 Short Answer (3 marks each). Section D: 4 Long Answer (5 marks each). Section E: 3 Case Study (4 marks each).",
        "Grade 10": "80 marks, 3 hours. Section A: 20 MCQ (1 mark each). Section B: 5 Very Short Answer (2 marks each). Section C: 6 Short Answer (3 marks each). Section D: 4 Long Answer (5 marks each). Section E: 3 Case Study (4 marks each).",
        "Grade 11": "80 marks, 3 hours. Section A: 20 MCQ (1 mark each). Section B: 5 Very Short Answer (2 marks each). Section C: 6 Short Answer (3 marks each). Section D: 4 Long Answer (5 marks each). Section E: 3 Case Study (4 marks each).",
        "Grade 12": "80 marks, 3 hours. Section A: 20 MCQ (1 mark each). Section B: 5 Very Short Answer (2 marks each). Section C: 6 Short Answer (3 marks each). Section D: 4 Long Answer (5 marks each). Section E: 3 Case Study (4 marks each).",
    },
    "ICSE": {
        "full_name": "Indian Certificate of Secondary Education (CISCE)",
        "Grade 6":  "50 marks, 2 hours. Section A (compulsory): short answer and MCQ (25 marks). Section B: attempt any 3 of 5 questions (25 marks).",
        "Grade 7":  "50 marks, 2 hours. Section A (compulsory): short answer and MCQ (25 marks). Section B: attempt any 3 of 5 questions (25 marks).",
        "Grade 8":  "60 marks, 2 hours. Section A (compulsory): 30 marks. Section B: attempt any 3 of 5 questions, 10 marks each.",
        "Grade 9":  "80 marks, 2.5 hours. Section A (compulsory, 40 marks): MCQ and short questions. Section B (40 marks): attempt any 4 of 6 long questions (10 marks each).",
        "Grade 10": "80 marks, 2.5 hours. Section A (compulsory, 40 marks): MCQ and short questions. Section B (40 marks): attempt any 4 of 6 long questions (10 marks each).",
        "Grade 11": "Not applicable for ICSE — use ISC for Grade 11.",
        "Grade 12": "Not applicable for ICSE — use ISC for Grade 12.",
    },
    "ISC": {
        "full_name": "Indian School Certificate (CISCE — Grade 11 & 12)",
        "Grade 6":  "Not applicable — ISC is for Grades 11–12.",
        "Grade 7":  "Not applicable — ISC is for Grades 11–12.",
        "Grade 8":  "Not applicable — ISC is for Grades 11–12.",
        "Grade 9":  "Not applicable — ISC is for Grades 11–12.",
        "Grade 10": "Not applicable — ISC is for Grades 11–12.",
        "Grade 11": "80 marks, 3 hours. Section A (compulsory, 65 marks): Core Mathematics. Section B (15 marks): choose any 2 of 3 questions from optional section.",
        "Grade 12": "80 marks, 3 hours. Section A (compulsory, 65 marks): Algebra, Calculus, Vectors, Probability. Section B (15 marks): attempt any 2 of 3.",
    },
    "Maharashtra State Board": {
        "full_name": "Maharashtra State Board (MSBSHSE)",
        "Grade 6":  "40 marks, 2 hours. Q1 MCQ (8 marks). Q2 Fill-in-the-blanks (8 marks). Q3–Q6 problem solving (6 marks each).",
        "Grade 7":  "40 marks, 2 hours. Q1 MCQ (8 marks). Q2 Fill-in-the-blanks (8 marks). Q3–Q6 problem solving (6 marks each).",
        "Grade 8":  "40 marks, 2 hours. Q1 MCQ (8 marks). Q2 True/False (8 marks). Q3–Q6 problem solving (6 marks each).",
        "Grade 9":  "40 marks, 2 hours per paper (Algebra and Geometry are separate papers). Each: Q1 MCQ (8 marks), Q2–Q5 problem solving.",
        "Grade 10": "40 marks, 2 hours per paper (Algebra and Geometry separate). Q1 MCQ (8 marks). Q2 (4 marks). Q3 (9 marks). Q4 (9 marks). Q5 (10 marks).",
        "Grade 11": "80 marks, 3 hours (Mathematics & Statistics). Q1 MCQ (10 marks). Q2–Q4 short answer. Q5–Q7 long answer.",
        "Grade 12": "80 marks, 3 hours. Paper I (Algebra & Calculus) and Paper II (Statistics, Probability & Geometry) — 80 marks each.",
    },
    "Karnataka State Board": {
        "full_name": "Karnataka KSEEB / SSLC / PUC Board",
        "Grade 6":  "50 marks, 2 hours. MCQ, fill-in-the-blanks, short answer, and long answer sections.",
        "Grade 7":  "50 marks, 2 hours. MCQ, fill-in-the-blanks, short answer, and long answer sections.",
        "Grade 8":  "50 marks, 2 hours. MCQ, fill-in-the-blanks, short answer, and long answer sections.",
        "Grade 9":  "80 marks, 3 hours. MCQ (1 mark), fill-in-the-blanks (1 mark), short answer (2 mark), long answer (3 mark), very long answer (4 mark).",
        "Grade 10": "80 marks, 3 hours (SSLC). Section 1: MCQ (10×1). Section 2: fill-in-blanks (10×1). Section 3: match (5×1). Section 4: SA (5×2). Section 5: LA with diagrams (5×3). Section 6: VLA (4×4).",
        "Grade 11": "100 marks, 3 hours (I PUC). Part A (1 mark each), Part B (2 marks each), Part C (3 marks each), Part D (5 marks each), Part E (10 marks: 6+4).",
        "Grade 12": "100 marks, 3.25 hours (II PUC). Part A (1 mark each), Part B (2 marks each), Part C (3 marks each), Part D (5 marks each), Part E (10 marks: 6+4).",
    },
    "Tamil Nadu State Board": {
        "full_name": "Tamil Nadu State Board (Samacheer Kalvi)",
        "Grade 6":  "100 marks, 3 hours. Section I: MCQ (14×1). Section II: Q&A (10×2). Section III: Q&A (5×5). Section IV: 2 questions (2×8).",
        "Grade 7":  "100 marks, 3 hours. Section I: MCQ (14×1). Section II: Q&A (10×2). Section III: Q&A (5×5). Section IV: 2 questions (2×8).",
        "Grade 8":  "100 marks, 3 hours. Section I: MCQ (15×1). Section II: Q&A (10×2). Section III: Q&A (5×5). Section IV: 2 questions (2×8).",
        "Grade 9":  "100 marks, 3 hours. Section I: MCQ (15×1). Section II: 10×2. Section III: 9×5. Section IV: 2×8.",
        "Grade 10": "100 marks, 3 hours (SSLC). Section I: 15 MCQ (1 mark). Section II: 10 Q (2 marks). Section III: 9 Q (5 marks). Section IV: 2 Q (8 marks).",
        "Grade 11": "90 marks, 3 hours (HSC). Part I: MCQ (1 mark). Part II: 2-mark. Part III: 3-mark. Part IV: 5-mark. Part V: 7-mark.",
        "Grade 12": "90 marks, 3 hours (HSC). Part I: MCQ. Part II: 2-mark. Part III: 3-mark. Part IV: 5-mark. Part V: 7-mark.",
    },
    "UP Board": {
        "full_name": "UP Madhyamik Shiksha Parishad (UPMSP)",
        "Grade 6":  "50 marks, 2 hours. Objective section (MCQ + fill-in) and subjective sections.",
        "Grade 7":  "50 marks, 2 hours. Objective section and subjective problem-solving sections.",
        "Grade 8":  "50 marks, 2 hours. Objective and subjective sections.",
        "Grade 9":  "70 marks written + 30 internal. Section A: objective. Section B: short answer. Section C: long answer.",
        "Grade 10": "70 marks written + 30 internal (High School). Section A: objective (20 marks). Section B: short answer (24 marks). Section C: long answer (26 marks).",
        "Grade 11": "100 marks (Intermediate). Section A: objective. Section B: short answer. Section C: long answer.",
        "Grade 12": "100 marks (Intermediate). Section A: objective. Section B: short answer. Section C: long answer.",
    },
    "West Bengal State Board": {
        "full_name": "West Bengal Board (WBBSE / WBCHSE)",
        "Grade 6":  "50 marks, 2 hours. MCQ, short answer, and long answer sections.",
        "Grade 7":  "50 marks, 2 hours. MCQ, short answer, and long answer sections.",
        "Grade 8":  "60 marks, 2 hours. MCQ, short answer, and long answer sections.",
        "Grade 9":  "90 marks, 3 hours. MCQ (10 marks), SAQ (20 marks), LAQ (60 marks).",
        "Grade 10": "90 marks, 3.15 hours (Madhyamik). MCQ (10 marks), SAQ (20 marks), LAQ (60 marks).",
        "Grade 11": "80 marks, 3 hours (HS). MCQ, short answer, long answer sections.",
        "Grade 12": "80 marks, 3 hours (HS). MCQ, short answer, long answer sections.",
    },
    "IB (HL)": {
        "full_name": "IB Mathematics: Analysis & Approaches Higher Level",
        "Grade 6":  "Not applicable — IB HL is for Grades 11–12.",
        "Grade 7":  "Not applicable — IB HL is for Grades 11–12.",
        "Grade 8":  "Not applicable — IB HL is for Grades 11–12.",
        "Grade 9":  "Not applicable — IB HL is for Grades 11–12.",
        "Grade 10": "Not applicable — IB HL is for Grades 11–12.",
        "Grade 11": "Paper 1 style (no calculator, 120 min): Section A short questions (55 marks) + Section B extended response (55 marks). Paper 2 (calculator, 120 min): same structure.",
        "Grade 12": "Paper 1 (no calc, 120 min, 110 marks) + Paper 2 (calc, 120 min, 110 marks) + Paper 3 (calc, 60 min, 55 marks). Emphasis on rigorous proof.",
    },
    "IB (SL)": {
        "full_name": "IB Mathematics: Analysis & Approaches Standard Level",
        "Grade 6":  "Not applicable — IB SL is for Grades 11–12.",
        "Grade 7":  "Not applicable — IB SL is for Grades 11–12.",
        "Grade 8":  "Not applicable — IB SL is for Grades 11–12.",
        "Grade 9":  "Not applicable — IB SL is for Grades 11–12.",
        "Grade 10": "Not applicable — IB SL is for Grades 11–12.",
        "Grade 11": "Paper 1 style (no calculator, 90 min): Section A short + Section B extended. Paper 2 (calculator, 90 min): same.",
        "Grade 12": "Paper 1 (no calc, 90 min, 80 marks) + Paper 2 (calc, 90 min, 80 marks). Section A short response + Section B extended.",
    },
    "Cambridge IGCSE": {
        "full_name": "Cambridge IGCSE Mathematics (0580)",
        "Grade 6":  "Practice in IGCSE style — shorter structured questions.",
        "Grade 7":  "Practice in IGCSE style — shorter structured questions.",
        "Grade 8":  "Practice in IGCSE style — structured questions.",
        "Grade 9":  "Extended Tier practice: Paper 2 style (90 min, 70 marks) — structured questions, calculator allowed.",
        "Grade 10": "Extended Tier: Paper 2 (90 min, 70 marks, no calculator) + Paper 4 (2.5 hours, 130 marks, calculator). Structured questions.",
        "Grade 11": "Not standard for IGCSE. Use A-Level.",
        "Grade 12": "Not standard for IGCSE. Use A-Level.",
    },
    "Cambridge A-Level": {
        "full_name": "Cambridge International A-Level Mathematics (9709)",
        "Grade 6":  "Not applicable — Cambridge A-Level is for Grades 11–12.",
        "Grade 7":  "Not applicable — Cambridge A-Level is for Grades 11–12.",
        "Grade 8":  "Not applicable — Cambridge A-Level is for Grades 11–12.",
        "Grade 9":  "Not applicable — Cambridge A-Level is for Grades 11–12.",
        "Grade 10": "Not applicable — Cambridge A-Level is for Grades 11–12.",
        "Grade 11": "AS Level (9709): Pure Mathematics Paper 1 (75 marks, 1.75 hours). Short and extended structured questions.",
        "Grade 12": "A-Level (9709): Pure Mathematics 1 & 3 (75 marks each, 1.75h each) + Statistics/Mechanics option. Rigorous proof required.",
    },
}

OFFICIAL_RESOURCES = {
    "CBSE":                  ("https://cbseacademic.nic.in/SQP.html",            "CBSE Academic — Official Sample Papers & Previous Year Question Papers"),
    "ICSE":                  ("https://cisce.org/publications.aspx",             "CISCE — Official Specimen Papers (ICSE & ISC)"),
    "ISC":                   ("https://cisce.org/publications.aspx",             "CISCE — Official ISC Specimen Papers"),
    "Maharashtra State Board": ("https://mahahsscboard.in/",                     "MSBSHSE — Maharashtra Board official papers"),
    "Karnataka State Board": ("https://kseab.karnataka.gov.in/",                 "KSEAB — Karnataka Board official question papers"),
    "Tamil Nadu State Board": ("https://dge.tn.gov.in/",                         "TN DGE — Tamil Nadu Board question papers"),
    "UP Board":              ("https://upmsp.edu.in/",                           "UPMSP — UP Board official papers"),
    "West Bengal State Board": ("https://wbbse.wb.gov.in/",                      "WBBSE — West Bengal Board official papers"),
    "IB (HL)":               ("https://www.ibo.org/programmes/diploma-programme/", "IB — Diploma Programme Mathematics resources"),
    "IB (SL)":               ("https://www.ibo.org/programmes/diploma-programme/", "IB — Diploma Programme Mathematics resources"),
    "Cambridge IGCSE":       ("https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-mathematics-0580/", "Cambridge IGCSE Mathematics (0580) — Past papers"),
    "Cambridge A-Level":     ("https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-mathematics-9709/", "Cambridge A-Level Mathematics (9709) — Past papers"),
}

GRADES = list(GRADE_CURRICULUM.keys())
DIFFICULTIES = ["Easy", "Medium", "Hard"]
DIFFICULTY_EMOJI = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
BOARDS = list(BOARD_FORMATS.keys())
PAPER_YEARS = ["Recent Pattern (2024–25)", "2023–24 Style", "2022–23 Style", "2021–22 Style", "2020–21 Style"]

LATEX_RULES = """
MANDATORY LATEX FORMATTING RULES — no exceptions:
- Use $...$ for ALL inline math: variables, numbers in equations, operators, expressions
- Use $$...$$ for standalone/display equations (on their own line)
- NEVER write mathematics as English words when a symbol exists
  ✗ "x squared plus 3x"       → ✓ $x^2 + 3x$
  ✗ "integral of f(x) dx"    → ✓ $\\int f(x)\\,dx$
  ✗ "square root of 2"       → ✓ $\\sqrt{2}$
  ✗ "sum from i=1 to n"      → ✓ $\\sum_{i=1}^{n}$
  ✗ "pi", "theta"            → ✓ $\\pi$, $\\theta$
  ✗ "infinity"               → ✓ $\\infty$
  ✗ "limit as x→0"           → ✓ $\\lim_{x \\to 0}$
  ✗ "a/b" (plain text)       → ✓ $\\frac{a}{b}$
- Fractions: $\\frac{a}{b}$  Powers: $x^n$  Subscripts: $a_n$
- Greek: $\\alpha$, $\\beta$, $\\gamma$, $\\pi$, $\\theta$, $\\lambda$, $\\sigma$, $\\omega$
- Trig: $\\sin x$, $\\cos x$, $\\tan x$, $\\sec x$, $\\csc x$, $\\cot x$
- Log: $\\log x$, $\\ln x$, $\\log_b x$
- Calculus: $f'(x)$, $\\frac{dy}{dx}$, $\\int_a^b f(x)\\,dx$, $\\lim_{x\\to a}$
- Summation: $\\sum_{i=1}^{n} a_i$   Vectors: $\\vec{v}$, $\\hat{i}$
- Inequalities: $\\leq$, $\\geq$, $\\neq$, $\\approx$, $\\in$, $\\equiv$
- Binomial: $\\binom{n}{k}$   Absolute: $|x|$
- Matrices: $$\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$$
"""

# ── API client ────────────────────────────────────────────────────────────────
def get_client():
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        api_key = None
    if not api_key or api_key.strip() == "sk-ant-your-key-here":
        st.error("**Anthropic API key not set.**\n\nAdd it in Streamlit Cloud → Manage app → Settings → Secrets:\n```\nANTHROPIC_API_KEY = \"sk-ant-...\"\n```", icon="🔑")
        st.stop()
    if not api_key.startswith("sk-ant-"):
        st.error(f"**API key format wrong.** Starts with `{api_key[:10]}...` — should start with `sk-ant-`.", icon="⚠️")
        st.stop()
    return anthropic.Anthropic(api_key=api_key.strip())

# ── Prompts: Daily Practice ───────────────────────────────────────────────────
def build_problem_prompt(grade, difficulty, topic, subtopic):
    jee = " Use JEE Main/Advanced style." if grade == "IIT JEE" else ""
    olp = " Require elegant, non-routine olympiad reasoning." if grade == "Math Olympiad" else ""
    return f"""You are an expert mathematics teacher. Generate ONE self-contained math problem for:
- Level: {grade}{jee}{olp}
- Topic: {topic} → {subtopic}
- Difficulty: {difficulty}

{LATEX_RULES}

Format EXACTLY as:

PROBLEM:
<Complete problem statement. ALL math in LaTeX. Do NOT include the answer.>

HINT:
<One subtle nudge using LaTeX for any math — no giveaways>"""


def build_solution_prompt(grade, difficulty, topic, subtopic, problem):
    jee = " Use JEE-style shortcuts where applicable." if grade == "IIT JEE" else ""
    olp = " Show elegant olympiad reasoning." if grade == "Math Olympiad" else ""
    return f"""You are an expert maths tutor explaining a solution to a {grade} student.{jee}{olp}

Topic: {topic} → {subtopic}
Problem: {problem}

{LATEX_RULES}

Structure your response as:

**Answer:**
<Final answer in LaTeX>

**Step-by-Step Solution:**
<Numbered steps. Every equation and symbol in LaTeX. Explain the WHY of each step.>

**Key Concept:**
<1–2 sentences on the core idea, using LaTeX for math terms.>

**Common Mistakes:**
<1–2 mistakes, showing wrong vs correct expressions in LaTeX.>

Tailor depth and vocabulary to {grade} at {difficulty} level."""

# ── Prompts: Exam Papers ──────────────────────────────────────────────────────
def build_paper_prompt(grade, board, year_style, topics_note):
    fmt = BOARD_FORMATS[board].get(grade, "Standard exam format for the grade.")
    year_note = f" Mirror the style and difficulty level of {year_style} papers." if "Recent" not in year_style else ""
    return f"""You are an expert exam paper setter. Generate a complete mathematics practice paper for:
- Board: {board} ({BOARD_FORMATS[board]['full_name']})
- Grade / Class: {grade}
- Paper style: {year_style}{year_note}
- Topics: {topics_note}

Official format for this board and grade:
{fmt}

{LATEX_RULES}

Generate the full paper with:
1. A proper paper header (Board, Class, Subject, Max Marks, Time Allowed, Date)
2. General instructions to students (as per {board} conventions)
3. All sections exactly as per the format above — correct number of questions per section
4. Each question clearly numbered with marks shown in brackets, e.g. [1 Mark] or [5 Marks]
5. MCQ questions with four options (A), (B), (C), (D)
6. Case-study / application questions with a scenario paragraph followed by sub-parts
7. Space-for-work indications where appropriate

IMPORTANT:
- Do NOT include answers or solutions anywhere in this paper
- Use LaTeX for every mathematical expression (follow rules above strictly)
- Make questions varied: mix computation, proof, application, and reasoning

Output the paper as clean, well-formatted markdown."""


def build_paper_solutions_prompt(paper_text, grade, board):
    return f"""You are an expert mathematics teacher providing a complete marking scheme and solutions for a {board} {grade} paper.

{LATEX_RULES}

PAPER:
{paper_text}

Provide COMPLETE solutions for EVERY question. Format as:

---
## Complete Solutions & Marking Scheme
---

For each question use this structure:
**Q[number]. [question type] — [marks] marks**

*Solution:*
<Step-by-step working with LaTeX. Show all key steps.>

*Answer:* <Final answer in LaTeX>

*Marks Breakdown:* <e.g. 1 mark for setup, 2 marks for working, 1 mark for answer>

For MCQs: State the correct option and give a brief justification with LaTeX.
For Case Study: Solve all sub-parts separately.

Be thorough — students will use this to learn from their mistakes."""

# ── Stream helper ─────────────────────────────────────────────────────────────
def stream_response(client, prompt, placeholder, max_tokens=1800):
    full_text = ""
    try:
        with client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                full_text += text
                placeholder.markdown(full_text + " ▌")
        placeholder.empty()
    except anthropic.AuthenticationError:
        st.error("**Invalid API key.** Go to https://console.anthropic.com/settings/keys, create a new key, and update it in Streamlit Secrets.", icon="🔑")
        st.stop()
    except anthropic.APIStatusError as e:
        st.error(f"**API Error {e.status_code}:** {e.message}", icon="❌")
        st.stop()
    return full_text


def parse_problem(text):
    result = {"problem": text, "hint": ""}
    m = re.search(r"PROBLEM:\s*(.*?)(?=HINT:|$)", text, re.DOTALL | re.IGNORECASE)
    if m:
        result["problem"] = m.group(1).strip()
    m = re.search(r"HINT:\s*(.*?)$", text, re.DOTALL | re.IGNORECASE)
    if m:
        result["hint"] = m.group(1).strip()
    return result

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "problem_data": None, "solution": None,
    "show_hint": False, "show_solution": False, "problem_count": 0,
    "paper_text": None, "paper_solutions": None, "show_paper_solutions": False,
    "paper_meta": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🧮 Daily Math Problem Solver</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">From Grade 1 to IIT JEE & Math Olympiad — powered by AI</div>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_daily, tab_paper, tab_resources = st.tabs(["📝 Daily Practice", "📋 Exam Papers", "🏛️ Past Paper Resources"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Daily Practice
# ══════════════════════════════════════════════════════════════════════════════
with tab_daily:
    with st.sidebar:
        st.header("⚙️ Daily Practice")
        grade = st.selectbox("📚 Grade / Level", GRADES)
        topics = list(GRADE_CURRICULUM[grade].keys())
        topic = st.selectbox("📖 Topic", topics)
        subtopic = st.selectbox("📐 Subtopic", GRADE_CURRICULUM[grade][topic])
        difficulty = st.radio("🎯 Difficulty", DIFFICULTIES, index=1,
                              format_func=lambda d: f"{DIFFICULTY_EMOJI[d]} {d}")
        st.divider()
        generate_btn = st.button("✨ Generate Problem", use_container_width=True, type="primary")
        st.divider()
        st.markdown(f"**Problems solved this session:** {st.session_state.problem_count} 🏆")
        st.markdown("**Tips:**\n- Attempt before looking at hints\n- Understand *why* each step works\n- Increase difficulty once comfortable!")

    if generate_btn:
        st.session_state.show_hint = False
        st.session_state.show_solution = False
        st.session_state.solution = None
        client = get_client()
        with st.spinner("Generating problem…"):
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
            unsafe_allow_html=True,
        )
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
                    sol = stream_response(client,
                          build_solution_prompt(data["grade"], data["difficulty"],
                                                data["topic"], data["subtopic"], data["problem"]), ph)
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
        st.info("👈 **Select your grade, topic, subtopic and difficulty in the sidebar, then click Generate Problem.**", icon="🚀")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 🎓 For All Levels\nGrade 1 counting through IIT JEE and Math Olympiad — every subtopic covered.")
        with c2:
            st.markdown("### 🤖 AI-Powered\nStep-by-step explanations with proper mathematical notation, tailored to your level.")
        with c3:
            st.markdown("### 📈 Build Daily Habits\nOne focused problem per day. Understand it deeply, then move on.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Exam Papers
# ══════════════════════════════════════════════════════════════════════════════
with tab_paper:
    st.subheader("📋 Generate a Full Exam Paper")
    st.caption(
        "AI generates a complete practice paper in the style of your chosen board's official exams. "
        "These are **AI-generated practice papers** — for official previous year papers visit the "
        "**Past Paper Resources** tab."
    )

    # ── Paper config ──────────────────────────────────────────────────────────
    pc1, pc2, pc3 = st.columns([1.2, 1.2, 1.6])
    with pc1:
        p_board = st.selectbox("🏫 Board / Curriculum", BOARDS, key="p_board")
    with pc2:
        p_grade = st.selectbox("📚 Grade", PAPER_GRADES, index=4, key="p_grade")  # default Grade 10
    with pc3:
        p_year = st.selectbox("📅 Paper Style / Year", PAPER_YEARS, key="p_year")

    # Topic coverage
    all_topics = list(GRADE_CURRICULUM.get(p_grade, {}).keys())
    p_topics_choice = st.radio("📖 Topics to Cover", ["All topics for this grade", "Select specific topics"],
                               horizontal=True, key="p_topics_choice")
    if p_topics_choice == "Select specific topics" and all_topics:
        p_topics_selected = st.multiselect("Choose topics", all_topics, default=all_topics[:3], key="p_topics_sel")
        topics_note = ", ".join(p_topics_selected) if p_topics_selected else "All topics"
    else:
        topics_note = "All topics across the full syllabus for this grade"

    # Warn if board not suitable for grade
    board_grade_note = BOARD_FORMATS[p_board].get(p_grade, "")
    if board_grade_note.startswith("Not applicable"):
        st.warning(f"⚠️ {board_grade_note}", icon="ℹ️")

    gen_paper_btn = st.button("📄 Generate Exam Paper", type="primary", use_container_width=False,
                              disabled=board_grade_note.startswith("Not applicable"))

    if gen_paper_btn:
        st.session_state.paper_solutions = None
        st.session_state.show_paper_solutions = False
        client = get_client()
        st.info("⏳ Generating your exam paper — this may take 30–60 seconds for a full paper…", icon="🔄")
        ph = st.empty()
        paper = stream_response(client,
                    build_paper_prompt(p_grade, p_board, p_year, topics_note),
                    ph, max_tokens=4096)
        st.session_state.paper_text = paper
        st.session_state.paper_meta = {"grade": p_grade, "board": p_board, "year": p_year}
        st.rerun()

    # ── Display paper ─────────────────────────────────────────────────────────
    if st.session_state.paper_text:
        meta = st.session_state.paper_meta or {}
        st.markdown(f"""
<div class="paper-header">
    <h3 style="margin:0;color:white;">📄 {meta.get('board','')}&nbsp;&nbsp;|&nbsp;&nbsp;{meta.get('grade','')}</h3>
    <p style="margin:0.3rem 0 0;opacity:0.75;font-size:0.9rem;">{meta.get('year','')} — AI-Generated Practice Paper</p>
</div>
""", unsafe_allow_html=True)

        st.markdown(st.session_state.paper_text)

        st.divider()
        col_sol, col_new = st.columns([1, 1])
        with col_sol:
            if st.button("✅ Generate Complete Solutions & Marking Scheme", type="primary", use_container_width=True):
                st.session_state.show_paper_solutions = True
                if not st.session_state.paper_solutions:
                    client = get_client()
                    st.info("⏳ Generating full solutions — this may take up to 60 seconds…", icon="🔄")
                    ph = st.empty()
                    sols = stream_response(client,
                               build_paper_solutions_prompt(
                                   st.session_state.paper_text,
                                   meta.get("grade", ""), meta.get("board", "")),
                               ph, max_tokens=4096)
                    st.session_state.paper_solutions = sols
                    st.rerun()
        with col_new:
            if st.button("🔄 Generate New Paper (Same Settings)", use_container_width=True):
                st.session_state.paper_text = None
                st.session_state.paper_solutions = None
                st.session_state.show_paper_solutions = False
                st.rerun()

        if st.session_state.show_paper_solutions and st.session_state.paper_solutions:
            st.markdown("---")
            st.markdown('<p class="section-label label-solution">✅ Complete Solutions & Marking Scheme</p>', unsafe_allow_html=True)
            st.success(st.session_state.paper_solutions)
    else:
        st.markdown("""
---
**How it works:**
1. Select your board, grade, and paper style above
2. Click **Generate Exam Paper** — AI writes a full paper following that board's official format
3. Attempt the paper yourself (or give it to a student)
4. Click **Generate Complete Solutions** to reveal the full marking scheme
""")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Past Paper Resources
# ══════════════════════════════════════════════════════════════════════════════
with tab_resources:
    st.subheader("🏛️ Official Past Paper Resources")
    st.caption(
        "The links below take you to official board websites where you can download **real** previous year "
        "question papers and official answer keys. These are not AI-generated."
    )

    # Group boards
    indian_boards = ["CBSE", "ICSE", "ISC", "Maharashtra State Board",
                     "Karnataka State Board", "Tamil Nadu State Board", "UP Board", "West Bengal State Board"]
    international_boards = ["IB (HL)", "IB (SL)", "Cambridge IGCSE", "Cambridge A-Level"]

    col_in, col_int = st.columns(2)

    with col_in:
        st.markdown("#### 🇮🇳 Indian Boards")
        for board in indian_boards:
            url, desc = OFFICIAL_RESOURCES[board]
            st.markdown(f"""
<div class="resource-card">
    <strong>{board}</strong><br>
    <span style="color:#555;font-size:0.9rem;">{desc}</span><br>
    <a href="{url}" target="_blank">🔗 {url}</a>
</div>
""", unsafe_allow_html=True)

    with col_int:
        st.markdown("#### 🌍 International Boards")
        for board in international_boards:
            url, desc = OFFICIAL_RESOURCES[board]
            st.markdown(f"""
<div class="resource-card">
    <strong>{board}</strong><br>
    <span style="color:#555;font-size:0.9rem;">{desc}</span><br>
    <a href="{url}" target="_blank">🔗 {url}</a>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.info(
        "**Tip:** Use the **Exam Papers** tab to generate AI practice papers in the style of any of these boards "
        "while you wait for official papers, or to practise topics not yet covered in the official paper set.",
        icon="💡",
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer">Built with ❤️ using Streamlit & Claude AI</div>', unsafe_allow_html=True)
