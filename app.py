import streamlit as st
import anthropic
import re
import json
import base64
import io
import os
import requests as _requests
import streamlit.components.v1 as components
from datetime import date as _date

try:
    from supabase import create_client
    SUPABASE_OK = True
except ImportError:
    SUPABASE_OK = False

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Maths Daily Helper – AI Maths Practice for Grade 1–12, IIT JEE & Olympiad",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GoatCounter Analytics ──────────────────────────────────────────────────────
components.html("""
<script data-goatcounter="https://kessousid.goatcounter.com/count"
        async src="//gc.zgo.at/count.js"></script>
""", height=0)

# ── PWA + SEO ─────────────────────────────────────────────────────────────────
st.markdown("""
<!-- PWA -->
<link rel="manifest" href="/app/static/manifest.json">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Maths Daily Helper">
<meta name="theme-color" content="#8b5cf6">
<link rel="apple-touch-icon" href="/app/static/icon-192.png">
<link rel="icon" type="image/png" sizes="32x32" href="/app/static/icon-32.png">
<link rel="icon" type="image/svg+xml" href="/app/static/logo.svg">

<!-- SEO: Core -->
<meta name="description" content="Free AI-powered maths practice for Grade 1 to Grade 12, IIT JEE, BITSAT, Math Olympiad, SAT and more. Get daily problems, hints, step-by-step solutions and full sample papers — powered by Claude AI.">
<meta name="keywords" content="maths practice, daily maths problems, IIT JEE maths, math olympiad, grade 1 to 12 maths, CBSE maths, ICSE maths, maths helper, AI maths tutor, free maths practice, step by step maths solutions, maths daily helper">
<meta name="author" content="Maths Daily Helper">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://app.mathsdailyhelper.com/">
<link rel="sitemap" type="application/xml" href="/app/static/sitemap.xml">

<!-- SEO: Open Graph (WhatsApp, Facebook previews) -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://app.mathsdailyhelper.com/">
<meta property="og:title" content="Maths Daily Helper – AI Maths Practice for Grade 1–12, IIT JEE & Olympiad">
<meta property="og:description" content="Free AI-powered daily maths practice. Problems, hints & step-by-step solutions for every grade — from Grade 1 to IIT JEE.">
<meta property="og:image" content="https://www.mathsdailyhelper.com/app/static/icon-512.png">

<!-- SEO: Twitter/X card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Maths Daily Helper – AI Maths Practice">
<meta name="twitter:description" content="Free AI-powered daily maths practice for Grade 1–12, IIT JEE & Olympiad.">
<meta name="twitter:image" content="https://www.mathsdailyhelper.com/app/static/icon-512.png">

<!-- SEO: Structured data (Google Education) -->
<script type="application/ld+json">
[
  {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "Maths Daily Helper",
    "url": "https://app.mathsdailyhelper.com",
    "description": "Free AI-powered maths practice for Grade 1 to Grade 12, IIT JEE, BITSAT, Math Olympiad, SAT, AMC and more. Daily problems, hints and step-by-step solutions.",
    "applicationCategory": "EducationApplication",
    "operatingSystem": "All",
    "browserRequirements": "Requires JavaScript",
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    "audience": {"@type": "EducationalAudience", "educationalRole": "student"},
    "featureList": [
      "AI-generated maths problems",
      "Step-by-step solutions",
      "Grade 1 to Grade 12 coverage",
      "IIT JEE preparation",
      "Math Olympiad practice",
      "CBSE and ICSE curriculum",
      "Hints system",
      "Full exam paper generation"
    ]
  },
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Maths Daily Helper",
    "url": "https://app.mathsdailyhelper.com",
    "logo": "https://www.mathsdailyhelper.com/app/static/icon-512.png",
    "sameAs": [
      "https://github.com/kessousid/daily-math-problem-solver"
    ]
  },
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "Is Maths Daily Helper free?",
        "acceptedAnswer": {"@type": "Answer", "text": "Yes, Maths Daily Helper is 100% free — no sign-up, no subscription, no credit card. Every feature including problem generation, hints, step-by-step solutions, and exam paper generation is available at no cost."}
      },
      {
        "@type": "Question",
        "name": "Which grades does Maths Daily Helper cover?",
        "acceptedAnswer": {"@type": "Answer", "text": "It covers Grade 1 through Grade 12, plus IIT JEE, BITSAT, Math Olympiad, SAT, ACT, AMC 8/10/12, AIME, GCSE, A-Level, IB Mathematics, and Cambridge IGCSE."}
      },
      {
        "@type": "Question",
        "name": "Does it support CBSE and ICSE?",
        "acceptedAnswer": {"@type": "Answer", "text": "Yes, Maths Daily Helper supports CBSE and ICSE for all classes from Class 1 to Class 12, including NCERT-aligned practice questions."}
      },
      {
        "@type": "Question",
        "name": "Can I use Maths Daily Helper to prepare for IIT JEE?",
        "acceptedAnswer": {"@type": "Answer", "text": "Yes. Select IIT JEE as your level and choose topics such as calculus, coordinate geometry, complex numbers, or probability. The AI generates JEE-style problems with complete step-by-step solutions."}
      },
      {
        "@type": "Question",
        "name": "Is Maths Daily Helper useful for SAT Math preparation?",
        "acceptedAnswer": {"@type": "Answer", "text": "Yes. Select SAT as your exam level to get algebra, advanced math, problem-solving, and data analysis questions in the SAT format, complete with worked solutions."}
      },
      {
        "@type": "Question",
        "name": "Can I practice Math Olympiad problems on Maths Daily Helper?",
        "acceptedAnswer": {"@type": "Answer", "text": "Yes. Choose Olympiad difficulty to get competition-style problems covering number theory, combinatorics, geometry proofs, and inequalities — suitable for IMO, AMC, AIME, RMO, and similar contests."}
      },
      {
        "@type": "Question",
        "name": "Can I upload a photo of a math problem and get a solution?",
        "acceptedAnswer": {"@type": "Answer", "text": "Yes. Use the Ask a Doubt tab to upload a photo (JPG or PNG) or a PDF of any math problem. The AI reads the image and provides a full step-by-step explanation."}
      },
      {
        "@type": "Question",
        "name": "How does Maths Daily Helper generate problems?",
        "acceptedAnswer": {"@type": "Answer", "text": "Problems are generated by Claude AI (Anthropic), tailored to your selected grade, topic, subtopic and difficulty level. Each problem is unique and freshly generated on demand."}
      },
      {
        "@type": "Question",
        "name": "Does Maths Daily Helper support GCSE and A-Level maths?",
        "acceptedAnswer": {"@type": "Answer", "text": "Yes. UK students can select GCSE or A-Level as their level and practise topics aligned with AQA, Edexcel, and OCR specifications, including pure maths, mechanics, and statistics."}
      },
      {
        "@type": "Question",
        "name": "Can primary school students use Maths Daily Helper?",
        "acceptedAnswer": {"@type": "Answer", "text": "Yes. The tool supports Grade 1 through Grade 5 with age-appropriate problems covering counting, addition, subtraction, multiplication, division, fractions, and basic geometry."}
      }
    ]
  }
]
</script>

<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/app/static/sw.js')
      .catch(err => console.log('SW registration failed:', err));
  });
}
</script>
""", unsafe_allow_html=True)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

<style>
/* ── Base ── */
html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif !important;
}
.stApp {
    background: #0d0d1f;
    background-image:
        radial-gradient(ellipse at 15% 40%, rgba(139,92,246,0.18) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 15%, rgba(236,72,153,0.12) 0%, transparent 55%),
        radial-gradient(ellipse at 60% 85%, rgba(6,182,212,0.10) 0%, transparent 55%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,10,40,0.98) 0%, rgba(20,15,55,0.98) 100%) !important;
    border-right: 1px solid rgba(139,92,246,0.25) !important;
}
section[data-testid="stSidebar"] * { font-family: 'Space Grotesk', sans-serif !important; }
section[data-testid="stSidebar"] label { color: rgba(226,232,240,0.7) !important; font-size: 0.8rem !important; font-weight: 600 !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu { display: none !important; }
footer { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar collapse button: hide ligature text, show unicode arrow ── */
[data-testid="collapsedControl"] span,
[data-testid="stSidebarCollapseButton"] span {
    font-size: 0 !important;
    color: transparent !important;
}
[data-testid="collapsedControl"] span::before,
[data-testid="stSidebarCollapseButton"] span::before {
    content: "◀";
    font-size: 18px !important;
    color: rgba(139, 92, 246, 0.8) !important;
}
/* ── Ensure sidebar button text is always visible ── */
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span {
    font-size: inherit !important;
    color: inherit !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    padding: 5px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: rgba(226,232,240,0.55) !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.25s ease !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: rgba(226,232,240,0.9) !important;
    background: rgba(139,92,246,0.12) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(139,92,246,0.4) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 0.55rem 1.4rem !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.25s ease !important;
    background: rgba(139,92,246,0.15) !important;
    color: #c4b5fd !important;
    border: 1px solid rgba(139,92,246,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    background: rgba(139,92,246,0.28) !important;
    border-color: rgba(139,92,246,0.6) !important;
    box-shadow: 0 8px 25px rgba(139,92,246,0.35) !important;
    color: #ede9fe !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #8b5cf6, #ec4899) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(139,92,246,0.45) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #7c3aed, #db2777) !important;
    box-shadow: 0 8px 30px rgba(139,92,246,0.6) !important;
    color: #ffffff !important;
}

/* ── Inputs & selects ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.stSelectbox > div > div:hover,
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(139,92,246,0.5) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.15) !important;
}

/* ── Radio buttons ── */
.stRadio > div { gap: 0.5rem !important; }
.stRadio > div > label {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.2s !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}
.stRadio > div > label:hover { border-color: rgba(139,92,246,0.4) !important; background: rgba(139,92,246,0.08) !important; }

/* ── Alert boxes (problem / hint / solution) ── */
div[data-testid="stAlert"] {
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-radius: 18px !important;
    font-size: 1.06rem !important;
    line-height: 1.85 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    border-width: 1px !important;
}

/* ── Multiselect ── */
.stMultiSelect > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── Custom classes ── */
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa 0%, #ec4899 50%, #38bdf8 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.3rem;
    animation: gradientShift 4s ease infinite;
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.hero-sub {
    text-align: center;
    color: rgba(226,232,240,0.5);
    font-size: 1rem;
    font-weight: 500;
    margin-bottom: 1.8rem;
    font-family: 'Space Grotesk', sans-serif;
}
.section-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    margin: 1rem 0 0.3rem; display: flex; align-items: center; gap: 6px;
}
.label-problem { color: #a78bfa; }
.label-hint    { color: #fbbf24; }
.label-solution{ color: #34d399; }

.badge {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 100px;
    font-size: 0.72rem; font-weight: 700;
    margin-right: 0.35rem;
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: 0.03em;
}
.badge-easy   { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-medium { background: rgba(251,191,36,0.15);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
.badge-hard   { background: rgba(248,113,113,0.15); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }
.badge-grade  { background: rgba(167,139,250,0.15); color: #a78bfa; border: 1px solid rgba(167,139,250,0.3); }
.badge-topic  { background: rgba(56,189,248,0.15);  color: #38bdf8; border: 1px solid rgba(56,189,248,0.3); }

.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.8rem 1rem;
    text-align: center;
    font-family: 'Space Grotesk', sans-serif;
}
.stat-number {
    font-size: 1.8rem; font-weight: 800;
    background: linear-gradient(135deg,#a78bfa,#ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.stat-label { font-size: 0.72rem; color: rgba(226,232,240,0.45); font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px; }

.rank-pill {
    display: inline-block;
    background: linear-gradient(135deg, rgba(139,92,246,0.25), rgba(236,72,153,0.25));
    border: 1px solid rgba(139,92,246,0.4);
    border-radius: 100px;
    padding: 0.3rem 1rem;
    font-size: 0.82rem; font-weight: 700;
    color: #c4b5fd;
    font-family: 'Space Grotesk', sans-serif;
}
.feature-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.6rem 1.4rem;
    text-align: center;
    transition: transform 0.3s, border-color 0.3s;
    font-family: 'Space Grotesk', sans-serif;
}
.feature-card:hover { transform: translateY(-4px); border-color: rgba(139,92,246,0.35); }
.feature-icon { font-size: 2.2rem; margin-bottom: 0.6rem; }
.feature-title { font-size: 1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.4rem; }
.feature-desc { font-size: 0.85rem; color: rgba(226,232,240,0.5); line-height: 1.5; }

.paper-header {
    background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(236,72,153,0.15));
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 18px;
    padding: 1.5rem 2rem;
    text-align: center;
    margin-bottom: 1.2rem;
    font-family: 'Space Grotesk', sans-serif;
}

.upload-zone {
    border: 2px dashed rgba(139,92,246,0.35);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    background: rgba(139,92,246,0.05);
    font-family: 'Space Grotesk', sans-serif;
}

.footer {
    text-align: center;
    color: rgba(226,232,240,0.25);
    font-size: 0.78rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-family: 'Space Grotesk', sans-serif;
}

/* ── Registration banner ── */
.reg-banner-wrap {
    overflow: hidden;
    background: linear-gradient(90deg, #7c3aed, #db2777, #7c3aed);
    background-size: 200% 100%;
    animation: bannerShift 6s linear infinite;
    border-radius: 10px;
    margin-bottom: 1rem;
    padding: 0.6rem 0;
}
@keyframes bannerShift {
    0%   { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}
.reg-banner-track {
    display: inline-block;
    white-space: nowrap;
    animation: marquee 22s linear infinite;
}
@keyframes marquee {
    0%   { transform: translateX(100vw); }
    100% { transform: translateX(-100%); }
}
.reg-banner-track span {
    font-size: 0.88rem;
    font-weight: 600;
    color: #fff;
    letter-spacing: 0.03em;
    padding: 0 2rem;
}

/* ── Auth gate card ── */
.auth-gate {
    max-width: 420px;
    margin: 3rem auto;
    background: rgba(139,92,246,0.08);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 18px;
    padding: 2rem 2rem 1.5rem;
    text-align: center;
}
.auth-gate h3 {
    color: #e2e8f0;
    margin-bottom: 0.3rem;
    font-size: 1.25rem;
}
.auth-gate p {
    color: rgba(226,232,240,0.55);
    font-size: 0.88rem;
    margin-bottom: 1.2rem;
}
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
    "IIT JEE Mains": {
        "Calculus": ["Limits & Continuity","Differentiation (Rules & Applications)","Indefinite Integration","Definite Integration & Properties","Differential Equations"],
        "Algebra": ["Complex Numbers & Quadratics","Sequences, Series & Progressions","Permutations & Combinations","Binomial Theorem","Matrices & Determinants"],
        "Coordinate Geometry": ["Straight Lines & Pair of Lines","Circles & Family of Circles","Parabola","Ellipse","Hyperbola"],
        "Trigonometry": ["Trigonometric Identities & Equations","Inverse Trigonometric Functions","Properties of Triangles","Heights & Distances"],
        "Vectors & 3D Geometry": ["Vector Algebra (Dot & Cross Product)","3D Lines & Planes","Direction Cosines & Ratios","Shortest Distance Between Lines"],
        "Probability & Statistics": ["Classical & Conditional Probability","Bayes' Theorem","Binomial & Poisson Distribution","Mean, Variance & Standard Deviation"],
    },
    "IIT JEE Advanced": {
        "Calculus": ["Limits & Continuity (Advanced)","Differentiation & Applications","Indefinite & Definite Integration","Differential Equations","Area Under Curves"],
        "Algebra": ["Complex Numbers","Quadratics & Higher-Degree Polynomials","Sequences & Series","Permutations & Combinations","Binomial Theorem","Matrices & Determinants"],
        "Coordinate Geometry": ["Straight Lines & Pair of Lines","Circles","Parabola","Ellipse","Hyperbola","3D Geometry"],
        "Trigonometry": ["Trigonometric Equations & Identities","Inverse Trigonometric Functions","Properties of Triangles"],
        "Vectors & 3D Geometry": ["Vector Algebra","3D Lines & Planes","Direction Cosines","Shortest Distance"],
        "Probability & Statistics": ["Probability (Classical & Conditional)","Bayes' Theorem","Probability Distributions"],
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
    "GCSE": {
        "Number": ["Number Properties & Calculations","Fractions, Decimals & Percentages","Ratio & Proportion","Powers & Roots","Standard Form"],
        "Algebra": ["Expressions & Formulae","Linear Equations & Inequalities","Quadratic Equations","Sequences","Graphs of Functions"],
        "Geometry & Measures": ["Angles & Properties of Shapes","Area & Volume","Transformations","Pythagoras & Trigonometry","Vectors"],
        "Probability & Statistics": ["Basic Probability","Representing Data","Averages & Spread","Cumulative Frequency","Scatter Graphs"],
    },
    "A-Level": {
        "Pure Mathematics": ["Algebra & Functions","Coordinate Geometry","Sequences & Series","Trigonometry","Exponentials & Logarithms","Differentiation","Integration","Numerical Methods","Vectors"],
        "Mechanics": ["Kinematics","Forces & Newton's Laws","Moments","Projectiles","Friction"],
        "Statistics": ["Statistical Sampling","Data Presentation","Probability","Statistical Distributions","Hypothesis Testing"],
        "Further Pure (A2)": ["Complex Numbers","Matrices","Further Algebra","Differential Equations","Polar Coordinates","Hyperbolic Functions"],
    },
    "Cambridge IGCSE": {
        "Number": ["Number & Calculation","Fractions & Percentages","Ratio, Rate & Proportion","Standard Form","Surds & Indices"],
        "Algebra & Graphs": ["Algebraic Manipulation","Linear & Quadratic Equations","Inequalities","Functions & Graphs","Sequences"],
        "Coordinate Geometry": ["Straight Lines","Gradient & Equation of a Line","Parallel & Perpendicular Lines"],
        "Geometry & Trigonometry": ["Angles & Polygons","Circles & Theorems","Trigonometry (SOHCAHTOA)","Sine & Cosine Rule","Vectors"],
        "Mensuration": ["Perimeter, Area & Volume","Arc Length & Sector Area"],
        "Statistics & Probability": ["Statistical Diagrams","Averages","Probability (Tree & Venn Diagrams)"],
    },
    "Cambridge A-Level": {
        "Pure Mathematics 1": ["Quadratics","Functions","Coordinate Geometry","Circular Measure","Trigonometry","Series","Differentiation","Integration"],
        "Pure Mathematics 3": ["Algebra","Logarithms","Trigonometry (Advanced)","Differentiation (Implicit, Parametric)","Integration Techniques","Differential Equations","Vectors","Complex Numbers"],
        "Statistics": ["Representation of Data","Probability","Discrete Random Variables","Normal Distribution","Hypothesis Testing","Regression & Correlation"],
        "Mechanics": ["Velocity & Acceleration","Kinematics","Forces","Newton's Laws","Energy, Work & Power"],
    },
    "IB HL": {
        "Algebra": ["Sequences & Series","Exponents & Logarithms","Binomial Theorem","Proof & Induction","Complex Numbers","Systems of Equations"],
        "Functions": ["Function Concepts","Transformations","Rational & Inverse Functions","Polynomial Functions","Exponential & Logarithmic Functions"],
        "Geometry & Trigonometry": ["3D Geometry","Trigonometric Functions & Identities","Vectors in 2D & 3D","Circle Theorems"],
        "Statistics & Probability": ["Descriptive Statistics","Probability","Discrete Distributions","Continuous Distributions","Hypothesis Testing"],
        "Calculus": ["Limits","Differentiation","Applications of Differentiation","Integration","Differential Equations"],
    },
    "IB SL": {
        "Algebra": ["Sequences & Series","Exponents & Logarithms","Financial Mathematics","Binomial Theorem"],
        "Functions": ["Function Concepts","Transformations","Quadratic & Exponential Functions","Logarithmic Functions"],
        "Geometry & Trigonometry": ["2D Trigonometry","3D Geometry","Sine & Cosine Rules","Vectors (2D)"],
        "Statistics & Probability": ["Descriptive Statistics","Probability","Binomial Distribution","Normal Distribution"],
        "Calculus": ["Differentiation","Applications of Differentiation","Integration & Applications"],
    },
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
    # ── Graduate / Professional ───────────────────────────────────────────────
    "GRE Quantitative (USA)": {
        "Arithmetic": ["Integer Properties","Fractions & Decimals","Exponents & Roots","Percentages","Ratio & Proportion","Number Lines"],
        "Algebra": ["Algebraic Expressions & Equations","Linear Equations & Inequalities","Quadratic Equations","Functions & Graphs","Coordinate Geometry","Systems of Equations"],
        "Geometry": ["Lines, Angles & Triangles","Quadrilaterals & Polygons","Circles","3D Figures","Pythagorean Theorem","Perimeter, Area & Volume"],
        "Data Analysis": ["Mean, Median & Mode","Standard Deviation & Range","Interpreting Tables & Graphs","Probability","Counting Methods","Data Interpretation"],
        "Quantitative Comparison": ["Comparing Quantities","Number Properties","Algebraic Comparisons","Geometric Comparisons"],
    },
    "GMAT Quantitative (USA)": {
        "Problem Solving": ["Arithmetic & Number Properties","Algebra & Linear Equations","Geometry","Percentages, Ratios & Proportions","Word Problems & Applied Math"],
        "Data Sufficiency": ["Number Properties","Algebra","Geometry","Statistics","Ratio & Percentage","Logical Reasoning with Data"],
        "Integrated Reasoning": ["Data Interpretation","Multi-source Reasoning","Table Analysis","Graphics Interpretation"],
    },
}

GRADES = list(GRADE_CURRICULUM.keys())

# Exams where Board/Curriculum and Paper Year/Style are not applicable
NO_BOARD_EXAMS = {k for k in GRADE_CURRICULUM if not k.startswith("Grade")}
PAPER_GRADES = [f"Grade {g}" for g in range(6, 13)] + [k for k in GRADE_CURRICULUM if not k.startswith("Grade")]

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
PAPER_YEARS = [str(y) for y in range(2024, 2014, -1)]


# ═════════════════════════════════════════════════════════════════════════════
# LATEX RULES
# ═════════════════════════════════════════════════════════════════════════════
LATEX_RULES = """
MANDATORY LATEX FORMATTING — no exceptions:
- $...$ for inline math (all variables, expressions, numbers in equations)
- $$...$$ for display/standalone equations — MANDATORY for ALL multi-line environments:
  $$\\begin{cases}...\\end{cases}$$  $$\\begin{pmatrix}...\\end{pmatrix}$$
  $$\\begin{align}...\\end{align}$$  $$\\begin{bmatrix}...\\end{bmatrix}$$
  NEVER wrap these inside single $...$, always use $$...$$
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
    import os
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or api_key.strip() == "sk-ant-your-key-here":
        st.error("**API key not set.** Add `ANTHROPIC_API_KEY` as an environment variable.", icon="🔑")
        st.stop()
    if not api_key.startswith("sk-ant-"):
        st.error(f"**API key format wrong** — starts with `{api_key[:10]}...`, should start with `sk-ant-`.", icon="⚠️")
        st.stop()
    return anthropic.Anthropic(api_key=api_key.strip())

# ═════════════════════════════════════════════════════════════════════════════
# SUPABASE — optional, gracefully degrades if not configured
# ═════════════════════════════════════════════════════════════════════════════
def get_supabase():
    if not SUPABASE_OK:
        return None
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        return None
    # Reuse the same client instance within a browser session so the
    # auth session (set after sign_in_with_password) is preserved across reruns.
    if "sb_client" not in st.session_state:
        try:
            st.session_state.sb_client = create_client(url, key)
        except Exception:
            return None
    return st.session_state.sb_client

def sb_load_stats(user_id):
    sb = get_supabase()
    if not sb or not user_id:
        return None
    try:
        r = sb.table("user_stats").select("*").eq("id", user_id).single().execute()
        return r.data
    except Exception:
        return None

def sb_save_stats(user_id, problems_solved, streak, last_solved_date):
    sb = get_supabase()
    if not sb or not user_id:
        return
    try:
        sb.table("user_stats").upsert({
            "id": user_id,
            "problems_solved": problems_solved,
            "streak": streak,
            "last_solved_date": str(last_solved_date) if last_solved_date else None,
        }).execute()
    except Exception:
        pass

def sb_save_problem(user_id, entry):
    """Persist one solved problem to Supabase (requires solved_problems table)."""
    sb = get_supabase()
    if not sb or not user_id:
        return
    try:
        sb.table("solved_problems").insert({
            "user_id":    user_id,
            "grade":      entry.get("grade", ""),
            "topic":      entry.get("topic", ""),
            "subtopic":   entry.get("subtopic", ""),
            "difficulty": entry.get("difficulty", ""),
            "problem":    entry.get("problem", ""),
            "solved_at":  entry.get("solved_at", ""),
        }).execute()
    except Exception:
        pass  # table may not exist yet; silent fail

def sb_load_problems(user_id):
    """Load all solved problems for a user from Supabase (newest first)."""
    sb = get_supabase()
    if not sb or not user_id:
        return []
    try:
        r = sb.table("solved_problems").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return r.data or []
    except Exception:
        return []

def sb_sign_up(email, password):
    sb = get_supabase()
    if not sb:
        return None, "Supabase not configured"
    try:
        r = sb.auth.sign_up({"email": email, "password": password})
        if r.user:
            return r.user, None
        return None, "Sign-up failed"
    except Exception as e:
        return None, str(e)

def sb_sign_in(email, password):
    sb = get_supabase()
    if not sb:
        return None, "Supabase not configured"
    try:
        r = sb.auth.sign_in_with_password({"email": email, "password": password})
        if r.user:
            return r.user, None
        return None, "Invalid email or password"
    except Exception as e:
        return None, str(e)

def get_supabase_admin():
    """Admin Supabase client using service role key — bypasses RLS for admin queries."""
    if not SUPABASE_OK:
        return None
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None

def sb_log_paper(user_id, user_email, grade, board):
    """Log a paper generation event to paper_usage table."""
    sb = get_supabase()
    if not sb:
        return
    try:
        sb.table("paper_usage").insert({
            "user_id":    user_id,
            "user_email": user_email or "anonymous",
            "grade":      grade or "",
            "board":      board or "",
        }).execute()
    except Exception:
        pass

def sb_check_paper_today(user_id):
    """Return True if this logged-in user has already generated a paper today."""
    if not user_id:
        return False
    sb = get_supabase()
    if not sb:
        return False
    try:
        today = _date.today().isoformat()
        r = (sb.table("paper_usage")
               .select("id")
               .eq("user_id", user_id)
               .gte("created_at", today)
               .execute())
        return len(r.data or []) > 0
    except Exception:
        return False

def sb_get_admin_stats():
    """Fetch all usage data for the admin dashboard (uses service role key)."""
    sb = get_supabase_admin()
    if not sb:
        return None
    try:
        papers_r = (sb.table("paper_usage")
                      .select("*")
                      .order("created_at", desc=True)
                      .execute())
        # auth.users is only accessible via the admin REST endpoint
        import json as _json
        import urllib.request as _urllib
        url  = os.environ.get("SUPABASE_URL", "").rstrip("/")
        skey = os.environ.get("SUPABASE_SERVICE_KEY", "")
        req  = _urllib.Request(
            f"{url}/auth/v1/admin/users?per_page=1000",
            headers={"apikey": skey, "Authorization": f"Bearer {skey}"},
        )
        with _urllib.urlopen(req) as resp:
            auth_data = _json.loads(resp.read())
        auth_users = auth_data.get("users", [])
        return {
            "papers":      papers_r.data or [],
            "total_users": len(auth_users),
            "users":       auth_users,
        }
    except Exception as e:
        return {"error": str(e)}

def handle_correct_answer():
    """Increment solved count and update streak, then sync to Supabase."""
    today = _date.today()
    last  = st.session_state.last_solved_date

    if last == today:
        pass  # already counted today
    elif last and (today - last).days == 1:
        st.session_state.streak += 1
    else:
        st.session_state.streak = 1

    st.session_state.last_solved_date = today
    st.session_state.problem_count   += 1

    # Snapshot problem into session history (newest first)
    _pd = st.session_state.get("problem_data") or {}
    if _pd.get("problem"):
        st.session_state.solved_history.insert(0, {
            "grade":      _pd.get("grade", ""),
            "topic":      _pd.get("topic", ""),
            "subtopic":   _pd.get("subtopic", ""),
            "difficulty": _pd.get("difficulty", ""),
            "problem":    _pd.get("problem", ""),
            "solved_at":  str(today),
        })

    user = st.session_state.get("supabase_user")
    if user:
        sb_save_stats(user["id"],
                      st.session_state.problem_count,
                      st.session_state.streak,
                      today)
        _pd2 = st.session_state.get("problem_data") or {}
        if _pd2.get("problem"):
            sb_save_problem(user["id"], {
                "grade":      _pd2.get("grade", ""),
                "topic":      _pd2.get("topic", ""),
                "subtopic":   _pd2.get("subtopic", ""),
                "difficulty": _pd2.get("difficulty", ""),
                "problem":    _pd2.get("problem", ""),
                "solved_at":  str(today),
            })

# ═════════════════════════════════════════════════════════════════════════════
# PROMPTS
# ═════════════════════════════════════════════════════════════════════════════
def build_problem_prompt(grade, difficulty, topic, subtopic):
    extra = ""
    if "JEE Mains" in grade: extra = " Use JEE Mains style: single-correct MCQ with options (A)–(D), moderate-to-hard difficulty."
    elif "JEE Advanced" in grade: extra = " Use JEE Advanced style: multi-correct or integer-type question, high difficulty requiring deep reasoning."
    elif "JEE" in grade: extra = " Use IIT JEE / JEE Advanced style."
    elif "Olympiad" in grade or "IMO" in grade: extra = " Require elegant, non-routine olympiad reasoning."
    elif "BITSAT" in grade: extra = " Use BITSAT multiple-choice style."
    elif "SAT" in grade: extra = " Use SAT-style question format."
    elif "AMC" in grade or "AIME" in grade: extra = " Use AMC/AIME competition style."
    elif "UKMT" in grade: extra = " Use UKMT competition style."
    elif "GRE" in grade: extra = " Use GRE Quantitative Reasoning style, including quantitative comparison and data interpretation question types."
    elif "GMAT" in grade: extra = " Use GMAT Quantitative style, including problem solving and data sufficiency question types."
    elif grade == "GCSE": extra = " Use GCSE style: structured question with parts (a), (b), mark allocations in brackets."
    elif grade == "A-Level": extra = " Use A-Level style: multi-part structured question with show-that and hence parts where appropriate."
    elif "Cambridge IGCSE" in grade: extra = " Use Cambridge IGCSE (0580) Extended style: structured question with clear working expected."
    elif "Cambridge A-Level" in grade: extra = " Use Cambridge International A-Level (9709) style: multi-part structured question."
    elif grade == "IB HL": extra = " Use IB Mathematics HL style: multi-part question, expect rigorous working and exact answers."
    elif grade == "IB SL": extra = " Use IB Mathematics SL style: structured multi-part question with GDC allowed."
    return f"""You are an expert maths teacher. Generate ONE self-contained problem for:
Level: {grade}{extra}  |  Topic: {topic} → {subtopic}  |  Difficulty: {difficulty}

{LATEX_RULES}

Format EXACTLY as:
PROBLEM:
<complete problem, ALL math in LaTeX, no answer>

HINT:
<one subtle nudge, LaTeX for any math>"""


def build_solution_prompt(grade, difficulty, topic, subtopic, problem):
    extra = " JEE Mains-style concise solution with key steps." if "JEE Mains" in grade else ""
    extra += " JEE Advanced-style rigorous multi-step solution." if "JEE Advanced" in grade else ""
    extra += " JEE-style shortcuts where applicable." if "JEE" in grade and "Mains" not in grade and "Advanced" not in grade else ""
    extra += " Elegant olympiad reasoning." if "Olympiad" in grade or "IMO" in grade else ""
    extra += " GRE-style clear concise explanation." if "GRE" in grade else ""
    extra += " GMAT-style explanation including data sufficiency logic where applicable." if "GMAT" in grade else ""
    extra += " GCSE-style answer with clear method marks and structured working." if grade == "GCSE" else ""
    extra += " A-Level style solution showing all required steps." if grade == "A-Level" else ""
    extra += " Cambridge IGCSE style — show all working clearly." if "Cambridge IGCSE" in grade else ""
    extra += " Cambridge A-Level style — structured solution with method shown." if "Cambridge A-Level" in grade else ""
    extra += " IB HL style — precise working, exact answers, reference to syllabus concepts." if grade == "IB HL" else ""
    extra += " IB SL style — clear working, GDC answers acceptable where appropriate." if grade == "IB SL" else ""
    return f"""You are an expert maths tutor.{extra}
Topic: {topic} → {subtopic}  |  Level: {grade}  |  Difficulty: {difficulty}
Problem: {problem}

{LATEX_RULES}

**Answer:** <final answer in LaTeX>
**Step-by-Step Solution:** <numbered steps, every symbol in LaTeX, explain the WHY>
**Key Concept:** <1–2 sentences>
**Common Mistakes:** <1–2 wrong-vs-correct examples in LaTeX>"""


def build_verify_prompt(problem, user_answer):
    return f"""You are a strict maths examiner. Follow these steps exactly.

STEP 1 — Solve the problem yourself independently. Do NOT look at the student's answer yet.
Problem: {problem}
Compute the correct answer carefully, showing each step.

STEP 2 — Write the correct answer clearly: "Correct answer: ..."

STEP 3 — Now compare with the student's answer: {user_answer}
Is it numerically/mathematically equivalent to your answer in Step 2?
Accept equivalent forms (2/4 = 1/2, x=3 or x = 3, 0.5 and 1/2) but reject any wrong value.

STEP 4 — Write your feedback: 1–2 sentences. Use LaTeX for all math.
If correct: confirm and name the key concept.
If incorrect: give a small nudge without revealing the answer.

STEP 5 — Final verdict. The VERY LAST LINE of your response must be exactly one of:
RESULT: CORRECT
RESULT: INCORRECT"""


def build_paper_prompt(grade, board, year, topics_note, jee_type=None):
    if board:
        fmt = BOARD_FORMATS[board].get(grade, "Standard exam format for this grade.")
        year_note = f" Mirror the question style and difficulty of {board} {year} papers." if year else ""
        header = f"Board: {board} ({BOARD_FORMATS[board]['full_name']})  |  Grade: {grade}  |  Year style: {year}"
        format_line = f"Format: {fmt}{year_note}"
        include_note = ("Include: proper header (Board, Class, Subject, Max Marks, Time, Date), general instructions, "
                        "all sections as per format with question numbers and marks in brackets [X Marks], "
                        "MCQ with options (A)–(D), case-study with scenario + sub-parts.")
    elif jee_type == "JEE Mains":
        header = "Exam: JEE Mains — Mathematics Section"
        format_line = (
            "Format: JEE Mains Mathematics section. 30 questions total, 100 marks, 1 hour.\n"
            "Section A (Q1–Q20): 20 Single-Correct MCQ — +4 marks correct, −1 mark incorrect, 0 unattempted.\n"
            "Section B (Q21–Q30): 10 Numerical Value questions — attempt any 5, +4 marks correct, no negative marking.\n"
            "Difficulty: moderate to hard, NCERT-based with application. Do NOT include Physics or Chemistry."
        )
        include_note = (
            "Include:\n"
            "- Header: JEE Mains | Mathematics | Maximum Marks: 100 | Duration: 1 Hour\n"
            "- Marking scheme instructions (MCQ: +4/−1, Numerical: +4/no negative, attempt any 5 of Section B)\n"
            "- Section A heading, then Q1–Q20 as MCQ with options (A)(B)(C)(D), each labelled [4 Marks]\n"
            "- Section B heading, then Q21–Q30 as Numerical Value questions, each labelled [4 Marks]\n"
            "- Do NOT add topic sub-headers before individual questions — just Q[n]. then the question"
        )
    elif jee_type == "JEE Advanced":
        header = "Exam: IIT JEE Advanced"
        format_line = ("Format: Realistic JEE Advanced paper (Paper 1). 3 sections, 3 hours. "
                       "Section 1: 6 single-correct MCQ (3 marks, -1 negative). "
                       "Section 2: 8 multi-correct MCQ (4 marks, partial marking, -2 negative). "
                       "Section 3: 6 integer type — answer is a non-negative integer (3 marks, no negative). "
                       "Difficulty: high, requires deep conceptual understanding and multi-step reasoning.")
        include_note = ("Include: proper JEE Advanced header, detailed instructions for each section type, "
                        "question numbers and marks in brackets [X Marks], MCQ with options (A)–(D).")
    else:
        exam_label = grade
        header = f"Exam: {exam_label}"
        format_line = (f"Format: Generate a realistic full-length {exam_label} practice paper with the actual exam's "
                       "section structure, question types, marks, and time allocation.")
        include_note = ("Include: proper exam header (Exam name, Section, Total Marks, Time), instructions, "
                        "all question types typical of this exam with marks in brackets [X Marks]. "
                        "For GRE include Quantitative Comparison and Problem Solving sections. "
                        "For GMAT include Problem Solving and Data Sufficiency sections. "
                        "CRITICAL: Number every question sequentially as **Problem 1.**, **Problem 2.**, **Problem 3.** etc. "
                        "(or **Q1.**, **Q2.** for MCQ-style exams). Never use sub-labels or skip numbers. "
                        "Each question must start on its own line with this bold label.")
    return f"""Generate a complete mathematics practice paper for:
{header}
Topics: {topics_note}
{format_line}

{LATEX_RULES}

{include_note}
Do NOT include answers inside the paper. Use LaTeX for all math. Output clean markdown.

After the complete paper, output this exact block (on new lines, no extra text around it):
##ANSWER_KEY_START##
Q1: (A)
Q2: (B)
Q3: 42
(one line per question — MCQ: letter in parentheses e.g. (A); numerical: the number; proof/show/derive: write proof)
##ANSWER_KEY_END##"""



def detect_question_count(paper_text):
    """Scan paper text to find the highest question number."""
    all_nums = []
    # Q1, Q.1, Question 1, Problem 1 (competition/AIME/AMC style)
    all_nums += re.findall(r'\b(?:Q\.?\s*|Question\s*|Problem\s*)(\d+)\b', paper_text, re.IGNORECASE)
    # Lines starting with a number: "1.", "1)", "(1)", "**1.**", "**1)"
    all_nums += re.findall(r'^\s*\*{0,2}\(?\s*(\d+)\s*[.)]\*{0,2}', paper_text, re.MULTILINE)
    # Bold problem/question lines at line start: **Problem 1.** or **Q 1.**
    all_nums += re.findall(r'^\s*\*+\s*(?:Problem|Question|Q\.?)\s*(\d+)', paper_text, re.MULTILINE | re.IGNORECASE)
    if all_nums:
        return min(max(int(m) for m in all_nums), 100)
    return 45  # fallback




def parse_and_strip_answer_key(paper_text):
    """Extract ##ANSWER_KEY_START## … ##ANSWER_KEY_END## block from paper.
    Returns (clean_paper, answer_key_text)."""
    m = re.search(
        r'##ANSWER_KEY_START##\s*(.*?)\s*##ANSWER_KEY_END##',
        paper_text, re.DOTALL | re.IGNORECASE,
    )
    if m:
        answer_key = m.group(1).strip()
        clean_paper = paper_text[:m.start()].rstrip()
        return clean_paper, answer_key
    return paper_text, ""


def parse_total_marks(paper_text):
    """Extract declared maximum marks from the paper header."""
    m = re.search(r'(?:Maximum|Max\.?|Total)\s*Marks\s*[:\-–]?\s*(\d+)', paper_text, re.IGNORECASE)
    return int(m.group(1)) if m else None


def _norm_answer(ans):
    """Normalise an answer string for comparison: strip spaces, parens, dots; uppercase."""
    return re.sub(r'[\s().*/]', '', ans).upper()


def grade_with_answer_key(paper_text, answers_dict, answer_key_text, q_marks_override=None):
    """
    Grade entirely in Python using the embedded answer key.
    No AI involved — zero revision risk.
    Returns verdict text in the same format as the grading prompt expects,
    or None if the answer key is empty/unparseable.
    q_marks_override: dict {q_num: marks} from solutions (overrides paper-text detection).
    """
    # ── Parse answer key: "Q1: (A) [4]", "Q1: (A)", "Q2: 42", etc.
    #    Marks may be embedded as trailing [N] in the key line.
    key = {}
    key_marks = {}  # marks extracted directly from answer key lines
    for m in re.finditer(r'Q(\d+)\s*:\s*([^\n]+)', answer_key_text or ""):
        q_num = int(m.group(1))
        raw = m.group(2).strip()
        # Check for embedded marks: "... [4]" at end of line
        mk_m = re.search(r'\[(\d+)\]\s*$', raw)
        if mk_m:
            key_marks[q_num] = int(mk_m.group(1))
            raw = raw[:mk_m.start()].strip()
        key[q_num] = raw

    if not key:
        return None  # No key — fall back to Claude

    # ── Build q_marks: key_marks first, then paper-text, then override
    q_marks = dict(key_marks)  # start with embedded marks (most reliable)

    # Paper-text: "[4 Marks]" near question heading — wider 250-char window
    for m in re.finditer(
        r'\bQ\.?\s*(\d+)\b[^\n]{0,250}\[(\d+)\s*[Mm]arks?\]',
        paper_text, re.IGNORECASE
    ):
        q_num = int(m.group(1))
        if q_num not in q_marks:  # don't overwrite embedded marks
            q_marks[q_num] = int(m.group(2))

    # Fallback global marks: multiple patterns
    fallback_marks = 1
    for _pat in [
        r'\+\s*(\d+)\s*[Mm]arks?\s*(?:for\s*)?correct',          # "+4 marks for correct"
        r'(?:correct|right)\s+answer[^\n]{0,30}[+＋]\s*(\d+)',    # "correct answer +4"
        r'each\s+(?:question|carries?|worth)\s+(\d+)\s*[Mm]arks?', # "each carries 4 marks"
        r'(\d+)\s*[Mm]arks?\s*(?:for\s*)?(?:each\s*)?correct',    # "4 marks for correct"
        r'[Mm]arks?\s*per\s*[Qq]uestion\s*[:\-]?\s*(\d+)',        # "marks per question: 4"
        r'\(\s*(\d+)\s*[Mm]arks?\s*(?:each)?\s*\)',               # "(4 marks each)"
    ]:
        _fm = re.search(_pat, paper_text, re.IGNORECASE)
        if _fm:
            fallback_marks = int(_fm.group(1))
            break
    if fallback_marks == 1 and q_marks:
        fallback_marks = max(set(q_marks.values()), key=list(q_marks.values()).count)

    # Override dict (from solutions, passed in) — fills gaps not covered above
    if q_marks_override:
        for q, m in q_marks_override.items():
            if q not in q_marks:
                q_marks[q] = m
        if fallback_marks == 1:
            _ov = list(q_marks_override.values())
            if _ov:
                fallback_marks = max(set(_ov), key=_ov.count)

    # ── Detect negative marking from paper text (generic)
    neg_mark = 0
    _neg_m = re.search(
        r'(?:'
        r'[−\-]\s*(\d+)\s*(?:mark|marks)\s*(?:for\s+)?(?:wrong|incorrect|each\s+wrong)'  # "-1 marks for wrong"
        r'|(?:wrong|incorrect)[^\n]{0,40}[−\-]\s*(\d+)'                                   # "incorrect answer -1"
        r'|\+\s*\d+\s*[,/]\s*[−\-]\s*(\d+)'                                               # "+4/-1" or "+4, -1"
        r')',
        paper_text, re.IGNORECASE
    )
    if _neg_m:
        _neg_val = int(next(g for g in _neg_m.groups() if g is not None))
        neg_mark = -_neg_val

    total_q = max(key.keys())
    lines = []

    for q in range(1, total_q + 1):
        correct_raw = key.get(q, "")
        student_raw = answers_dict.get(q, "").strip()
        marks       = q_marks.get(q, fallback_marks)
        correct_norm = _norm_answer(correct_raw)
        student_norm = _norm_answer(student_raw)

        if correct_raw.lower().strip() in ("proof", "prove", "show", "derive"):
            lines.append(f"📝 **Q{q}** Proof/subjective — not auto-graded")
        elif not student_raw:
            lines.append(f"⬜ **Q{q}** Not attempted — 0/{marks}")
        elif correct_norm == student_norm:
            lines.append(f"✅ **Q{q}** Correct — {marks}/{marks} | Ans: {correct_raw}")
        else:
            scored = neg_mark if neg_mark else 0
            lines.append(
                f"❌ **Q{q}** Incorrect — {scored}/{marks} | "
                f"Correct: {correct_raw} | Student gave: {student_raw}"
            )

    return "\n\n".join(lines)


def parse_key_from_solutions(solutions_text):
    """
    Extract answer key and marks from the ##ANSWER_KEY_START## block that
    build_paper_solutions_prompt asks Claude to append.
    Falls back to scanning for Answer: lines if the block is absent.
    Returns (key_dict {q_num: answer_str}, marks_dict {q_num: int}).
    """
    key = {}
    marks = {}

    # ── Primary: parse the explicit structured block ──────────────────────
    block_m = re.search(
        r'##ANSWER_KEY_START##\s*(.*?)\s*##ANSWER_KEY_END##',
        solutions_text, re.DOTALL | re.IGNORECASE
    )
    if block_m:
        for line in block_m.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith('('):   # skip comment lines
                continue
            m = re.match(r'Q(\d+)\s*:\s*(.+)', line, re.IGNORECASE)
            if not m:
                continue
            q_num = int(m.group(1))
            rest  = m.group(2).strip()
            # Extract trailing [marks]
            mk_m = re.search(r'\[(\d+)\]\s*$', rest)
            if mk_m:
                marks[q_num] = int(mk_m.group(1))
                rest = rest[:mk_m.start()].strip()
            key[q_num] = rest
        if key:
            return key, marks   # block found and parsed — done

    # ── Fallback: scan each question chunk for "Answer:" line ─────────────
    chunks = re.split(r'\n(?=\*{0,2}(?:#+\s*)?Q\.?\s*\d+[.\)\s])', solutions_text)
    for chunk in chunks:
        qm = re.match(r'\*{0,2}(?:#+\s*)?Q\.?\s*(\d+)', chunk.strip())
        if not qm:
            continue
        q_num = int(qm.group(1))
        mm = re.search(r'(?:[—–\-]\s*(\d+)\s*[Mm]arks?|\[(\d+)\s*[Mm]arks?\])', chunk[:300])
        if mm:
            marks[q_num] = int(mm.group(1) or mm.group(2))
        all_ans = re.findall(
            r'\*{0,2}(?:Correct\s+)?Answer[:\s]+\*{0,2}\s*\**\s*([A-D\(\[][^\n✓\*]{0,25})',
            chunk, re.IGNORECASE
        )
        if all_ans:
            raw = all_ans[-1].strip().rstrip('✓ .,*)')
            raw = re.sub(r'\s+.*$', '', raw)
            if raw:
                key[q_num] = raw
    return key, marks


def build_extract_key_prompt(solutions_text):
    """Extract the final answer for every question directly from the solutions text.
    Guarantees grading matches exactly what is displayed to the student."""
    return f"""Below are complete step-by-step solutions to a math exam.
Read each solution carefully and extract the FINAL answer stated at the end of each solution.

SOLUTIONS:
{solutions_text}

Output ONLY one line per question in this exact format — nothing else:
Q1: (A) [4]
Q2: 42 [4]
Q3: proof [5]

Rules:
- MCQ: the correct option letter in parentheses e.g. (A) (B) (C) (D)
- Numerical: the exact number as stated in the solution
- Proof/show/derive: write proof
- [N]: marks for that question as stated in the solution
- Copy the answer EXACTLY as it appears in the solution — do not re-solve
- Output ONLY these lines, no other text"""


def build_paper_grading_prompt(paper_text, answers_dict, answer_key, grade, board):
    exam_ref = f"{board} {grade}" if board else grade
    answers_formatted = "\n".join(
        f"Q{q}: {a.strip()}" for q, a in sorted(answers_dict.items()) if a.strip()
    ) or "No answers provided."

    return f"""You are a strict {exam_ref} examiner. You have a pre-verified answer key — do NOT re-solve anything. Compare each student answer to the answer key.

ANSWER KEY (authoritative — trust completely):
{answer_key}

STUDENT ANSWERS:
{answers_formatted}

EXAM PAPER (for marks/context only):
{paper_text}

MARKING SCHEME: Read the marking instructions from the paper header/instructions above and apply them exactly.
- If the paper specifies negative marking (e.g. -1 for wrong MCQ), apply it: wrong answer scores negative marks.
- If the paper specifies partial marking, apply it.
- If no special scheme is stated, correct = full marks, wrong/unattempted = 0.
- Use the marks shown in brackets [X Marks] beside each question for [max].

GRADING RULES:
1. MCQ: accept bare A/B/C/D as equivalent to (A)/(B)/(C)/(D).
2. Numerical: require EXACT match.
3. No student answer + proof/show/derive question → 📝 Proof.
4. No student answer + all other types → ⬜ Not attempted.
5. Output a verdict for EVERY question in the paper.

OUTPUT FORMAT — one line per question:
✅ **Q[n]** Correct — [scored]/[max] | Ans: [correct answer] | [≤8 word feedback]
❌ **Q[n]** Incorrect — [scored]/[max] | Correct: [answer] | Student gave: [answer] | [≤8 word feedback]
📝 **Q[n]** Proof/subjective — not auto-graded
⬜ **Q[n]** Not attempted — 0/[max]

CRITICAL: Exactly ONE line per question. Never revise. Do NOT output a TOTAL SCORE.
Use LaTeX for all math."""


def fix_grading_score(score_text, total_marks=None):
    """
    Post-process Claude's raw grading output:
    1. Fix merged-line duplicates: "❌ Qn … ✅ Qn" on one line → keep ✅ part.
    2. Fix separate-line duplicates: keep the LAST verdict per question.
    3. Strip any TOTAL SCORE Claude may have written anyway.
    4. Compute and append the correct score entirely in Python.
    """
    VERDICT_LINE = re.compile(
        r'^([✅❌📝⬜])[ \t]+\*{0,2}Q(\d+)\*{0,2}[^\n]*$',
        re.MULTILINE,
    )

    # ── 1. Merged-line: ❌/📝/⬜ Qn … ✅ Qn on same line → keep ✅ part only
    score_text = re.sub(
        r'[❌📝⬜][ \t]+\*{0,2}Q(\d+)\*{0,2}[^✅❌📝⬜\n]*'
        r'✅([ \t]+\*{0,2}Q\1\*{0,2}[^\n]*)',
        r'✅\2',
        score_text,
    )

    # ── 2. Separate-line duplicates: delete earlier occurrences, keep last
    seen = {}
    to_remove = []
    for m in VERDICT_LINE.finditer(score_text):
        q = m.group(2)
        if q in seen:
            to_remove.append(seen[q])
        seen[q] = m

    for m in sorted(to_remove, key=lambda x: x.start(), reverse=True):
        end = m.end() + (1 if m.end() < len(score_text) and score_text[m.end()] == '\n' else 0)
        score_text = score_text[:m.start()] + score_text[end:]

    # ── 3. Strip any TOTAL SCORE block Claude wrote (we replace it below)
    score_text = re.sub(
        r'\n*-{3,}\n\*{0,2}TOTAL SCORE:.*',
        '',
        score_text,
        flags=re.DOTALL,
    )
    score_text = re.sub(
        r'\n*\*{0,2}TOTAL SCORE:.*',
        '',
        score_text,
        flags=re.DOTALL,
    )

    # ── 4. Compute score from the clean verdict lines
    total_scored = total_possible_from_verdicts = correct = attempted = 0
    for m in VERDICT_LINE.finditer(score_text):
        line = m.group(0)
        # Marks pattern: handles negatives like -1/4
        mk = re.search(r'[—–]\s*(-?\d+)\s*/\s*(\d+)', line)
        if not mk:
            mk = re.search(r'\s(-?\d+)\s*/\s*(\d+)', line)
        if mk:
            total_scored              += int(mk.group(1))
            total_possible_from_verdicts += int(mk.group(2))
        if m.group(1) == '✅':
            correct += 1;  attempted += 1
        elif m.group(1) == '❌':
            attempted += 1

    # Use declared exam total marks if available (e.g. 100 for JEE Mains),
    # otherwise fall back to sum of question marks
    total_possible = total_marks if total_marks else total_possible_from_verdicts

    # ── 5. Ensure blank line before every verdict line so markdown renders them
    #       as separate items, not one flowing paragraph
    score_text = re.sub(
        r'([^\n])\n([✅❌📝⬜])',
        r'\1\n\n\2',
        score_text,
    )

    score_text = score_text.rstrip()
    score_text += (
        f"\n\n---\n**TOTAL SCORE: {total_scored} / {total_possible}**\n\n"
        f"Student attempted **{attempted}** question(s) — "
        f"**{correct} correct** / {attempted - correct} incorrect "
        f"(scored **{total_scored}** out of **{total_possible}** marks)."
    )
    return score_text


def build_paper_solutions_prompt(paper_text, grade, board):
    exam_ref = f"{board} {grade}" if board else grade
    return f"""Provide COMPLETE solutions and marking scheme for every question in this {exam_ref} paper.

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
def render_math_markdown(text, height=6000):
    """Render markdown+LaTeX using MathJax in an iframe.
    Protects math from markdown mangling before passing to marked.js."""
    json_text = json.dumps(text)
    # JS regexes built as plain strings to avoid Python invalid-escape warnings
    re_display  = r"/\$\$([\s\S]*?)\$\$/g"
    re_inline   = r"/\$([^\n\$]+?)\$/g"
    re_bracket  = r"/\\\[([\s\S]*?)\\\]/g"
    re_paren    = r"/\\\(([\s\S]*?)\\\)/g"
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<script src='https://cdn.jsdelivr.net/npm/marked@9/marked.min.js'></script>"
        "<script>"
        "MathJax = {"
        "  tex: { inlineMath: [['$','$']], displayMath: [['$$','$$']], processEscapes: true },"
        "  options: { skipHtmlTags: ['script','noscript','style','textarea','pre'] }"
        "};"
        "</script>"
        "<script async src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js'></script>"
        "<style>"
        "body { font-family: 'Segoe UI', Arial, sans-serif; padding: 1.2rem 1.8rem; background: #ffffff; color: #1a1a2e; line-height: 1.8; }"
        "h1,h2,h3,h4 { color: #1e293b; margin: 1.1rem 0 .5rem; font-weight: 700; }"
        "h1 { font-size: 1.3rem; border-bottom: 2px solid #8b5cf6; padding-bottom: .4rem; }"
        "h2 { font-size: 1.1rem; color: #4c1d95; }"
        "h3 { font-size: 1rem; color: #5b21b6; }"
        "hr { border: none; border-top: 2px solid #e2e8f0; margin: 1rem 0; }"
        "strong { font-weight: 700; color: #0f172a; } p { margin: .4rem 0; }"
        "li { margin: .3rem 0; } ol,ul { padding-left: 1.4rem; }"
        "mjx-container { font-size: 1.05em !important; }"
        "</style></head><body>"
        f"<script type='application/json' id='d'>{json_text}</script>"
        "<div id='c'></div>"
        "<script>"
        "var raw = JSON.parse(document.getElementById('d').textContent);"
        "var store = {}, n = 0;"
        "function protect(t) {"
        f"  t = t.replace({re_bracket}, function(m) {{ var k='XX'+n+++'XX'; store[k]=m; return k; }});"
        f"  t = t.replace({re_paren},   function(m) {{ var k='XX'+n+++'XX'; store[k]=m; return k; }});"
        f"  t = t.replace({re_display}, function(m) {{ var k='XX'+n+++'XX'; store[k]=m; return k; }});"
        f"  t = t.replace({re_inline},  function(m) {{ var k='XX'+n+++'XX'; store[k]=m; return k; }});"
        "  return t;"
        "}"
        "function restore(h) {"
        "  for (var k in store) h = h.split(k).join(store[k]);"
        "  return h;"
        "}"
        "document.getElementById('c').innerHTML = restore(marked.parse(protect(raw)));"
        "function typeset() {"
        "  if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([document.getElementById('c')]);"
        "  else setTimeout(typeset, 400);"
        "}"
        "typeset();"
        "</script></body></html>"
    )
    components.html(html, height=height, scrolling=True)

def render_math_box(text, box_type="info", height=None):
    """Render markdown+LaTeX in a styled dark-theme box using MathJax.
    Avoids Streamlit's built-in KaTeX which mangles $currency$ as math delimiters."""
    styles = {
        "info":    {"bg": "#0a1929", "border": "#1e88e5", "color": "#90caf9"},
        "warning": {"bg": "#1a1200", "border": "#fb8c00", "color": "#ffe082"},
        "success": {"bg": "#071a0e", "border": "#43a047", "color": "#a5d6a7"},
    }
    s = styles.get(box_type, styles["info"])
    estimated_h = max(180, min(1600, len(text) // 3 + 200)) if height is None else height
    json_text = json.dumps(text)
    re_display = r"/\$\$([\s\S]*?)\$\$/g"
    re_inline  = r"/\$([^\n\$]+?)\$/g"
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<script src='https://cdn.jsdelivr.net/npm/marked@9/marked.min.js'></script>"
        "<script>"
        "MathJax = {"
        "  tex: { inlineMath: [['$','$']], displayMath: [['$$','$$']], processEscapes: true },"
        "  options: { skipHtmlTags: ['script','noscript','style','textarea','pre'] }"
        "};"
        "</script>"
        "<script async src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js'></script>"
        "<style>"
        f"body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0.85rem 1.1rem;"
        f"  background: {s['bg']}; border-left: 4px solid {s['border']}; border-radius: 4px;"
        f"  color: {s['color']}; line-height: 1.75; font-size: 0.97rem; }}"
        "p { margin: 0.25rem 0; } strong { font-weight: 600; }"
        "ol, ul { margin: 0.4rem 0; padding-left: 1.4rem; }"
        "</style></head><body>"
        f"<script type='application/json' id='d'>{json_text}</script>"
        "<div id='c'></div>"
        "<script>"
        "var raw = JSON.parse(document.getElementById('d').textContent);"
        "var store = {}, n = 0;"
        "function protect(t) {"
        f"  t = t.replace({re_display}, function(m) {{ var k='XX'+n+++'XX'; store[k]=m; return k; }});"
        f"  t = t.replace({re_inline},  function(m) {{ var k='XX'+n+++'XX'; store[k]=m; return k; }});"
        "  return t;"
        "}"
        "function restore(h) {"
        "  for (var k in store) h = h.split(k).join(store[k]);"
        "  return h;"
        "}"
        "document.getElementById('c').innerHTML = restore(marked.parse(protect(raw)));"
        "function typeset() {"
        "  if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([document.getElementById('c')]);"
        "  else setTimeout(typeset, 400);"
        "}"
        "typeset();"
        "</script></body></html>"
    )
    components.html(html, height=estimated_h, scrolling=True)


def stream_response(client, prompt, placeholder, max_tokens=1800, image_data=None, media_type=None, model="claude-haiku-4-5-20251001"):
    content = []
    if image_data:
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}})
    content.append({"type": "text", "text": prompt})
    full_text = ""
    try:
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=(
                "IMPORTANT: For ALL mathematical expressions without exception, "
                "use ONLY these LaTeX delimiters: $...$ for inline math and $$...$$ "
                r"for display/block math. Never use \(...\) or \[...\] or any other delimiter style."
            ),
            messages=[{"role": "user", "content": content}],
        ) as stream:
            for text in stream.text_stream:
                full_text += text
                placeholder.text(full_text + " ▌")  # plain text avoids partial-LaTeX render errors
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


# ═════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═════════════════════════════════════════════════════════════════════════════
for k, v in {
    "problem_data": None, "solution": None,
    "show_hint": False, "show_solution": False, "problem_count": 0,
    "paper_text": None, "paper_solutions": None, "show_paper_solutions": False, "paper_meta": None, "paper_answer_key": None, "paper_q_marks": None,
    "doubt_response": None, "active_tab": 0,
    # answer verification
    "answer_result": None, "answer_feedback": "",
    # streak
    "streak": 0, "last_solved_date": None,
    # optional user profile
    "supabase_user": None,
    # full paper answers
    "paper_score": None,
    # solved history (current session)
    "solved_history": [], "show_history": False,
    # paper daily-limit tracking
    "paper_generated_this_session": False,
    # admin auth
    "admin_authenticated": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# On load: if user signed in last session, restore stats from Supabase
if st.session_state.supabase_user and st.session_state.problem_count == 0:
    _stats = sb_load_stats(st.session_state.supabase_user["id"])
    if _stats:
        st.session_state.problem_count    = _stats.get("problems_solved", 0)
        st.session_state.streak           = _stats.get("streak", 0)
        _ld = _stats.get("last_solved_date")
        st.session_state.last_solved_date = _date.fromisoformat(_ld) if _ld else None

# ═════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD  (accessed via ?admin=true in the URL)
# ═════════════════════════════════════════════════════════════════════════════
_qp = st.query_params
if _qp.get("admin") == "true":
    _admin_pwd_env = (
        os.environ.get("ADMIN_PASSWORD")
        or (st.secrets.get("ADMIN_PASSWORD") if hasattr(st, "secrets") else "")
        or ""
    )
    st.title("🔐 Maths Daily Helper — Admin")

    if not st.session_state.admin_authenticated:
        _pwd = st.text_input("Admin password", type="password")
        if st.button("Login", type="primary"):
            if _pwd and _pwd == _admin_pwd_env:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.stop()

    # ── Authenticated admin view ──────────────────────────────────────────────
    if st.button("🚪 Sign Out of Admin"):
        st.session_state.admin_authenticated = False
        st.rerun()

    _stats = sb_get_admin_stats()
    if _stats is None:
        st.error("SUPABASE_SERVICE_KEY not configured. Add it to Railway env vars.")
    elif "error" in _stats:
        st.error(f"Supabase error: {_stats['error']}")
    else:
        _papers = _stats["papers"]
        _today  = _date.today().isoformat()
        _papers_today = [p for p in _papers if (p.get("created_at") or "")[:10] == _today]

        # ── Top metrics ──────────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👥 Registered Users", _stats["total_users"])
        c2.metric("📄 Total Papers Generated", len(_papers))
        c3.metric("📅 Papers Today", len(_papers_today))
        _unique_users = len({p["user_email"] for p in _papers if p.get("user_email") and p["user_email"] != "anonymous"})
        c4.metric("🧑‍🎓 Unique Generating Users", _unique_users)

        st.divider()

        # ── Papers by grade ──────────────────────────────────────────────────
        if _papers:
            from collections import Counter
            _grade_counts = Counter(p.get("grade", "Unknown") for p in _papers)
            st.subheader("📊 Papers by Grade / Exam")
            _gc_sorted = sorted(_grade_counts.items(), key=lambda x: -x[1])
            _gc_labels = [g for g, _ in _gc_sorted]
            _gc_vals   = [v for _, v in _gc_sorted]
            st.bar_chart(dict(zip(_gc_labels, _gc_vals)))

        st.divider()

        # ── Registered users ─────────────────────────────────────────────────
        st.subheader("👥 Registered Users")
        _users = _stats.get("users", [])
        if _users:
            _user_rows = []
            for u in _users:
                _user_rows.append({
                    "Email":           u.get("email", "—"),
                    "Signed Up":       (u.get("created_at") or "")[:16].replace("T", " "),
                    "Last Sign In":    (u.get("last_sign_in_at") or "—")[:16].replace("T", " "),
                    "Email Confirmed": "Yes" if u.get("email_confirmed_at") else "No",
                })
            st.dataframe(_user_rows, use_container_width=True)
        else:
            st.info("No registered users yet.")

        st.divider()

        # ── Recent paper log ─────────────────────────────────────────────────
        st.subheader("📋 Recent Paper Generations")
        if _papers:
            _rows = []
            for p in _papers[:200]:
                _rows.append({
                    "Email":      p.get("user_email", "—"),
                    "Grade/Exam": p.get("grade", "—"),
                    "Board":      p.get("board", "—"),
                    "Generated":  (p.get("created_at") or "")[:16].replace("T", " "),
                })
            st.dataframe(_rows, use_container_width=True)
        else:
            st.info("No papers generated yet.")

    st.stop()  # Do not render the rest of the app for admin view

# ═════════════════════════════════════════════════════════════════════════════
# HEADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin-bottom:0.2rem;">
  <div style="width:56px;height:56px;border-radius:14px;box-shadow:0 4px 24px rgba(139,92,246,0.4);overflow:hidden;flex-shrink:0;">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="56" height="56">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#8b5cf6"/>
          <stop offset="60%" stop-color="#6d28d9"/>
          <stop offset="100%" stop-color="#4338ca"/>
        </linearGradient>
        <linearGradient id="bolt" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#fde68a"/>
          <stop offset="100%" stop-color="#f59e0b"/>
        </linearGradient>
      </defs>
      <rect width="512" height="512" rx="110" fill="url(#bg)"/>
      <path d="M 72 390 L 72 135 L 256 295 L 440 135 L 440 390"
            stroke="white" stroke-width="58"
            stroke-linejoin="round" stroke-linecap="round" fill="none" opacity="0.95"/>
      <polygon points="300,68 248,218 286,218 232,420 392,204 348,204 396,68"
               fill="url(#bolt)"/>
    </svg>
  </div>
  <div>
    <div class="hero-title" style="margin-bottom:0;">Maths Daily Helper</div>
    <div class="hero-sub" style="margin-top:2px;">Grade 1 → IIT JEE · SAT · AMC · Olympiad · Gaokao · Abitur & more</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════════
# CONTACT EMAIL
# ═════════════════════════════════════════════════════════════════════════════
def send_contact_email(name, email, topic, issue_type, message):
    try:
        api_key = os.environ.get("RESEND_API_KEY", "")
        if not api_key:
            return False, "Email service not configured."
        body = (
            f"Name:       {name}\n"
            f"Email:      {email}\n"
            f"Topic:      {topic}\n"
            f"Issue Type: {issue_type}\n\n"
            f"Message:\n{message}"
        )
        resp = _requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "from": "Maths Daily Helper <support@mathsdailyhelper.com>",
                "to": ["support@mathsdailyhelper.com"],
                "reply_to": email,
                "subject": f"[{issue_type}] {topic} — from {name}",
                "text": body,
            },
            timeout=15,
        )
        if resp.status_code in (200, 201):
            return True, "Sent"
        return False, resp.text
    except Exception as e:
        return False, str(e)

# SIDEBAR (global — always visible)
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
        # Rank logic
        n = st.session_state.problem_count
        if n == 0:    rank, rank_emoji = "Newcomer", "🌱"
        elif n < 5:   rank, rank_emoji = "Rookie",   "🔥"
        elif n < 15:  rank, rank_emoji = "Grinder",  "⚡"
        elif n < 30:  rank, rank_emoji = "Big Brain", "🧠"
        else:          rank, rank_emoji = "Legend",   "👑"

        _streak = st.session_state.streak
        _streak_display = f"🔥{_streak}" if _streak > 0 else "—"
        _user   = st.session_state.get("supabase_user")
        _user_label = (f"<div style='font-size:0.75rem;color:#a78bfa;margin-top:0.3rem;'>👤 {_user['email']}</div>"
                       if _user else "<span></span>")
        st.markdown(
            f"<div style='text-align:center;padding:1rem 0 0.5rem;'>"
            f"<div style='font-size:2rem;'>{rank_emoji}</div>"
            f"<div class='rank-pill'>{rank}</div>"
            f"{_user_label}"
            f"<div style='margin-top:0.8rem;display:flex;gap:8px;justify-content:center;'>"
            f"<div class='stat-card' style='flex:1;'><div class='stat-number'>{_streak_display}</div><div class='stat-label'>streak</div></div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
        # Solved count as a clickable button
        _history_label = f"{'📂' if st.session_state.show_history else '📋'} {n} solved"
        if st.button(_history_label, use_container_width=True, key="btn_history",
                     help="Click to view your solved problems"):
            st.session_state.show_history = not st.session_state.show_history
            st.rerun()
        # ── Optional user profile ─────────────────────────────────────────────
        st.divider()
        _sb_user = st.session_state.get("supabase_user")
        if _sb_user:
            st.markdown(f"<div style='color:#a78bfa;font-size:0.85rem;margin-bottom:0.4rem;'>👤 {_sb_user['email']}</div>", unsafe_allow_html=True)
            if st.button("Sign Out", use_container_width=True):
                st.session_state.supabase_user = None
                st.session_state.problem_count = 0
                st.session_state.streak = 0
                st.session_state.last_solved_date = None
                st.session_state.pop("sb_client", None)
                st.rerun()
        else:
            if get_supabase():
                if "show_auth" not in st.session_state:
                    st.session_state.show_auth = False
                st.markdown("<div style='font-size:0.78rem;color:rgba(226,232,240,0.45);margin-bottom:0.4rem;'>Sign in to save your streak &amp; progress across sessions</div>", unsafe_allow_html=True)
                if st.button("👤 Sign In / Create Account", use_container_width=True, key="btn_show_auth"):
                    st.session_state.show_auth = not st.session_state.show_auth
                    st.rerun()
                if st.session_state.show_auth:
                    _auth_tab = st.radio("", ["Sign In", "Create Account"], horizontal=True, key="auth_mode", label_visibility="collapsed")
                    _email    = st.text_input("Email", key="auth_email")
                    _pw       = st.text_input("Password", type="password", key="auth_pw")
                    if _auth_tab == "Sign In":
                        if st.button("Sign In", use_container_width=True, key="btn_signin"):
                            if _email and _pw:
                                _u, _err = sb_sign_in(_email, _pw)
                                if _u:
                                    st.session_state.supabase_user = {"id": _u.id, "email": _u.email}
                                    st.session_state.show_auth = False
                                    _stats = sb_load_stats(_u.id)
                                    if _stats:
                                        st.session_state.problem_count    = _stats.get("problems_solved", 0)
                                        st.session_state.streak           = _stats.get("streak", 0)
                                        _ld = _stats.get("last_solved_date")
                                        st.session_state.last_solved_date = _date.fromisoformat(_ld) if _ld else None
                                    st.rerun()
                                else:
                                    st.error(_err)
                    else:
                        if st.button("Create Account", use_container_width=True, key="btn_signup"):
                            if _email and _pw:
                                _u, _err = sb_sign_up(_email, _pw)
                                if _u:
                                    st.session_state.supabase_user = {"id": _u.id, "email": _u.email}
                                    st.session_state.show_auth = False
                                    st.rerun()
                                else:
                                    st.error(_err)

        st.divider()
        grade    = st.selectbox("📚 Level / Exam", GRADES)
        topics   = list(GRADE_CURRICULUM[grade].keys())
        topic    = st.selectbox("📖 Topic", topics)
        subtopic = st.selectbox("📐 Subtopic", GRADE_CURRICULUM[grade][topic])
        difficulty = st.radio("🎯 How spicy?", DIFFICULTIES, index=1,
                              format_func=lambda d: f"{DIFFICULTY_EMOJI[d]} {d}")
        st.divider()
        generate_btn = st.button("🚀 Drop a Problem", use_container_width=True, type="primary")
        if generate_btn:
            st.session_state.active_tab = 0
        st.divider()
        st.markdown("<div style='color:rgba(226,232,240,0.4);font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;'>Pro Tips</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:rgba(226,232,240,0.55);font-size:0.82rem;line-height:1.7;'>🎯 Always try before hitting hint<br>🧠 Understand the <em>why</em>, not just the answer<br>📈 Level up difficulty once you're comfortable</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("<div style='color:rgba(226,232,240,0.4);font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;'>📬 Contact Us</div>", unsafe_allow_html=True)

        with st.form("contact_form", clear_on_submit=False):
            c_name  = st.text_input("Your Name")
            c_email = st.text_input("Your Email")
            c_topic = st.selectbox("Topic", [
                "General Query", "Bug Report", "Feature Request",
                "Content Issue", "Billing / Subscription", "Other"
            ])
            c_issue = st.selectbox("Type of Issue", [
                "Question", "Problem not loading", "Wrong answer / solution",
                "Missing topic", "App crash", "Suggestion", "Other"
            ])
            c_msg      = st.text_area("Message", height=100)
            submitted  = st.form_submit_button("Send Message", use_container_width=True, type="primary")
            if submitted:
                if not c_name.strip() or not c_email.strip() or not c_msg.strip():
                    st.warning("Please fill in Name, Email and Message.")
                else:
                    with st.spinner("Sending…"):
                        ok, info = send_contact_email(
                            c_name.strip(), c_email.strip(), c_topic, c_issue, c_msg.strip()
                        )
                    if ok:
                        st.success("✅ Sent! We'll get back to you soon.")
                    else:
                        st.error(f"Could not send: {info}")

# ── Registration banner (shown to guests) ─────────────────────────────────────
if not st.session_state.supabase_user:
    _msg = ("🎓 Registration is now required to use Maths Daily Helper &nbsp;·&nbsp; "
            "Create your free account in seconds &nbsp;·&nbsp; "
            "Save your streak, track your progress &nbsp;·&nbsp; "
            "Sign in via the sidebar → &nbsp;·&nbsp; "
            "🎓 Registration is now required to use Maths Daily Helper &nbsp;·&nbsp; "
            "Create your free account — it's completely free!")
    st.markdown(
        f'<div class="reg-banner-wrap"><div class="reg-banner-track"><span>{_msg}</span></div></div>',
        unsafe_allow_html=True,
    )

# ═════════════════════════════════════════════════════════════════════════════
# CUSTOM TABS
# ═════════════════════════════════════════════════════════════════════════════
_tab_labels = ["⚡ Daily Drop", "📋 Full Paper", "💬 Ask Anything"]
_tcols = st.columns(3)
for _i, (_col, _label) in enumerate(zip(_tcols, _tab_labels)):
    with _col:
        if st.button(_label, use_container_width=True,
                     type="primary" if st.session_state.active_tab == _i else "secondary",
                     key=f"tab_btn_{_i}"):
            st.session_state.active_tab = _i
            if _i != 0:  # leaving Daily Drop — close history panel
                st.session_state.show_history = False
            st.rerun()
st.divider()

# ── Auth gate — require login for all features ─────────────────────────────────
if not st.session_state.supabase_user:
    st.markdown("""
    <div class="auth-gate">
      <h3>🔐 Sign in to continue</h3>
      <p>Maths Daily Helper now requires a free account.<br>
         Use the <strong>Sign In / Create Account</strong> button in the sidebar to get started.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# ── Solved History Panel ──────────────────────────────────────────────────────
if st.session_state.show_history and st.session_state.active_tab == 0:
    _sb_user = st.session_state.get("supabase_user")

    # Prefer Supabase history (all sessions) when logged in
    if _sb_user:
        _history = sb_load_problems(_sb_user["id"])
        st.markdown(f"<h3 style='color:#c4b5fd;margin-bottom:0.5rem;'>📋 All Solved Problems ({len(_history)})</h3>", unsafe_allow_html=True)
        st.caption("Showing your complete history across all sessions.")
    else:
        _history = st.session_state.solved_history
        st.markdown(f"<h3 style='color:#c4b5fd;margin-bottom:0.5rem;'>📋 Solved Problems ({len(_history)})</h3>", unsafe_allow_html=True)
        st.caption("Showing this session only. Sign in to save and view your full history across sessions.")

    if not _history:
        st.info("No problems solved yet. Solve one to see it here! 🚀")
    else:
        for _i, _entry in enumerate(_history):
            _diff_emoji = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴", "Olympiad": "🏆"}.get(_entry.get("difficulty", ""), "⚪")
            with st.expander(
                f"{_diff_emoji} #{len(_history) - _i} · {_entry.get('grade','')} · {_entry.get('topic','')} · {_entry.get('difficulty','')} · {_entry.get('solved_at','')}",
                expanded=False
            ):
                render_math_box(_entry.get("problem", ""), "info")
    st.divider()

# TAB 1 — DAILY PRACTICE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == 0:
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
        render_math_box(data["problem"], "info")

        # ── Answer input + Math keyboard ──────────────────────────────────────
        st.markdown('<p class="section-label label-hint">✏️ Your Answer</p>', unsafe_allow_html=True)

        # Math symbol keyboard
        with st.expander("🔢 Math Keyboard — click to insert symbols", expanded=False):
            st.markdown("<div style='font-size:0.78rem;color:rgba(226,232,240,0.45);margin-bottom:0.5rem;'>Click any symbol to append it to your answer</div>", unsafe_allow_html=True)
            KB_ROWS = [
                ["π", "∞", "√", "∛", "²", "³", "±", "×", "÷", "≠"],
                ["≤", "≥", "≈", "∈", "∉", "⊂", "∪", "∩", "Σ", "∫"],
                ["α", "β", "γ", "θ", "λ", "σ", "Δ", "∂", "∝", "∴"],
                ["(", ")", "[", "]", "{", "}", "^", "_", "/", "|"],
            ]
            for row in KB_ROWS:
                cols = st.columns(len(row))
                for i, sym in enumerate(row):
                    if cols[i].button(sym, key=f"kb_{sym}", use_container_width=True):
                        current = st.session_state.get("answer_input", "")
                        st.session_state["answer_input"] = current + sym

        user_answer = st.text_input(
            "Type your answer here:",
            key="answer_input",
            placeholder="e.g.  x = 3,  √5,  π/2,  12.5 …",
        )

        cb1, cb2 = st.columns([1, 2])
        with cb1:
            check_btn = st.button("✅ Check Answer", type="primary", use_container_width=True)
        with cb2:
            if st.session_state.answer_result == "correct":
                st.success("🎉 Correct! Well done.")
            elif st.session_state.answer_result == "incorrect":
                st.error("❌ Not quite — try again or use a hint.")

        if check_btn and not user_answer.strip():
            st.warning("Please enter your answer first.", icon="✏️")
        if check_btn and user_answer.strip():
            st.session_state.answer_result   = None
            st.session_state.answer_feedback = ""
            client = get_client()
            with st.spinner("Checking your answer…"):
                ph = st.empty()
                verdict = stream_response(client,
                    build_verify_prompt(data["problem"], user_answer.strip()), ph, max_tokens=600)
            st.session_state.answer_feedback = verdict
            # Find RESULT line anywhere in the response (Claude may reason before concluding)
            _result = "incorrect"
            for _line in verdict.strip().split("\n"):
                _l = _line.strip()
                if _l == "RESULT: CORRECT":
                    _result = "correct"
                    break
                elif _l == "RESULT: INCORRECT":
                    _result = "incorrect"
                    break
            st.session_state.answer_result = _result
            if _result == "correct" and not st.session_state.show_solution:
                handle_correct_answer()
                st.balloons()
            st.rerun()

        if st.session_state.answer_feedback:
            # Show feedback: remove RESULT line and Step headers, keep explanation only
            fb_lines = [l for l in st.session_state.answer_feedback.split("\n")
                        if not l.strip().startswith("RESULT:")
                        and not l.strip().startswith("STEP ")
                        and not l.strip().startswith("Correct answer:")]
            fb_body = "\n".join(fb_lines).strip()
            if fb_body:
                box_t = "success" if st.session_state.answer_result == "correct" else "warning"
                render_math_box(fb_body, box_t)

        st.divider()

        # ── Hint / Solution / Next buttons ────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("💡 Give Me a Nudge", use_container_width=True):
                st.session_state.show_hint = not st.session_state.show_hint
        with c2:
            if st.button("🧠 Reveal the W", use_container_width=True, type="primary"):
                st.session_state.show_solution = True
                if not st.session_state.solution:
                    client = get_client()
                    ph = st.empty()
                    sol = stream_response(client, build_solution_prompt(
                        data["grade"], data["difficulty"], data["topic"], data["subtopic"], data["problem"]), ph)
                    st.session_state.solution = sol
                    # only increment if not already counted via answer check
                    if st.session_state.answer_result != "correct":
                        handle_correct_answer()
                    st.balloons()
        with c3:
            if st.button("🔄 Next One", use_container_width=True):
                st.session_state.update(
                    show_hint=False, show_solution=False, solution=None,
                    answer_result=None, answer_feedback="", answer_input="",
                )
                client = get_client()
                ph = st.empty()
                raw = stream_response(client, build_problem_prompt(
                    data["grade"], data["difficulty"], data["topic"], data["subtopic"]), ph)
                st.session_state.problem_data = {**parse_problem(raw), "grade": data["grade"],
                    "difficulty": data["difficulty"], "topic": data["topic"], "subtopic": data["subtopic"]}
                st.rerun()

        if st.session_state.show_hint and data.get("hint"):
            st.markdown('<p class="section-label label-hint">💡 Hint</p>', unsafe_allow_html=True)
            render_math_box(data["hint"], "warning")
        if st.session_state.show_solution and st.session_state.solution:
            st.markdown('<p class="section-label label-solution">✅ Solution & Explanation</p>', unsafe_allow_html=True)
            render_math_box(st.session_state.solution, "success")
    else:
        st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;">
    <div style="font-size:1.15rem;font-weight:600;color:rgba(226,232,240,0.6);margin-bottom:0.3rem;">ready to big brain it?</div>
    <div style="font-size:0.9rem;color:rgba(226,232,240,0.35);">pick your level on the left and hit 🚀</div>
</div>
""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""<div class="feature-card">
<div class="feature-icon">🎓</div>
<div class="feature-title">Every Level</div>
<div class="feature-desc">Grade 1 → IIT JEE · SAT · AMC · Gaokao · Abitur · Olympiad and more</div>
</div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""<div class="feature-card">
<div class="feature-icon">🤖</div>
<div class="feature-title">AI Explanations</div>
<div class="feature-desc">Step-by-step solutions with proper maths notation, tailored to your exact exam</div>
</div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""<div class="feature-card">
<div class="feature-icon">🔥</div>
<div class="feature-title">Build Streaks</div>
<div class="feature-desc">One focused subtopic a day. Stack knowledge, not just answers. Rank up 👑</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — EXAM PAPERS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 1:
    st.markdown("<div style='font-size:1.5rem;font-weight:800;color:#e2e8f0;margin-bottom:0.2rem;'>📋 Full Send a Paper</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:rgba(226,232,240,0.45);font-size:0.88rem;margin-bottom:1.2rem;'>AI builds a complete exam paper in your board's official format. Attempt it, then reveal the full marking scheme.</div>", unsafe_allow_html=True)

    p_grade = st.selectbox("📚 Grade / Exam", PAPER_GRADES, index=4, key="p_grade")
    is_competitive = p_grade in NO_BOARD_EXAMS

    # JEE Mains vs Advanced sub-option
    jee_type = None
    if "IIT JEE" in p_grade:
        if "Mains" in p_grade:
            jee_type = "JEE Mains"
        elif "Advanced" in p_grade:
            jee_type = "JEE Advanced"
        else:
            jee_type = st.radio("📝 Paper Type", ["JEE Mains", "JEE Advanced"], horizontal=True, key="jee_type")

    if not is_competitive:
        pc1, pc2 = st.columns([1.2, 1])
        with pc1: p_board = st.selectbox("🏫 Board / Curriculum", BOARDS, key="p_board")
        with pc2: p_year  = st.selectbox("📅 Paper Year / Style", PAPER_YEARS, key="p_year")
    else:
        p_board = None
        p_year  = None

    all_topics = list(GRADE_CURRICULUM.get(p_grade, {}).keys())
    p_topics_choice = st.radio("📖 Topics", ["All topics for this exam", "Select specific topics"], horizontal=True)
    if p_topics_choice == "Select specific topics" and all_topics:
        p_sel = st.multiselect("Choose topics", all_topics, default=all_topics[:3])
        topics_note = ", ".join(p_sel) if p_sel else "All topics"
    else:
        topics_note = "Full syllabus for this exam"

    if not is_competitive:
        board_grade_note = BOARD_FORMATS[p_board].get(p_grade, "")
        if board_grade_note.startswith("Not applicable") or board_grade_note.startswith("Not standard"):
            st.warning(f"⚠️ {board_grade_note}")
        paper_disabled = board_grade_note.startswith(("Not applicable", "Not standard"))
    else:
        paper_disabled = False

    # ── Daily paper limit ─────────────────────────────────────────────────────
    _current_user = st.session_state.supabase_user
    # TODO: re-enable daily limit after testing
    _limit_reached = False

    gen_paper_btn = st.button("📄 Generate Exam Paper", type="primary",
                               disabled=paper_disabled)

    if gen_paper_btn:
        st.session_state.update(paper_solutions=None, show_paper_solutions=False, paper_answer_key=None, paper_q_marks=None)
        client = get_client()

        st.info("⏳ Generating your paper — this may take up to 30 seconds…", icon="🔄")
        ph = st.empty()
        paper = stream_response(client, build_paper_prompt(p_grade, p_board, p_year, topics_note, jee_type), ph, max_tokens=8192)

        # Parse and strip the embedded answer key (never shown to student)
        paper_clean, answer_key = parse_and_strip_answer_key(paper)
        st.session_state.paper_text = paper_clean
        st.session_state.paper_answer_key = answer_key
        st.session_state.paper_meta = {"grade": p_grade, "board": p_board, "year": p_year, "jee_type": jee_type}

        # Silently generate complete solutions in background to build reliable answer key
        try:
            # Step 1: generate solutions for display
            with st.spinner("📖 Generating complete solutions…"):
                sols_ph = st.empty()
                sols = stream_response(client, build_paper_solutions_prompt(
                    paper_clean, p_grade, p_board), sols_ph, max_tokens=8192)
                sols_ph.empty()
            st.session_state.paper_solutions = sols

            # Step 2: extract answer key FROM the solutions — not re-solving,
            # so grading is guaranteed to match what the student sees
            with st.spinner("🔑 Extracting answer key from solutions…"):
                key_ph = st.empty()
                key_raw = stream_response(client, build_extract_key_prompt(sols),
                                          key_ph, max_tokens=1024)
                key_ph.empty()
            # Parse "Q1: (A) [4]" lines directly — no regex heroics needed
            _key_lines_out = []
            _marks_dict = {}
            for _line in key_raw.splitlines():
                _line = _line.strip()
                _km = re.match(r'Q(\d+)\s*:\s*(.+)', _line, re.IGNORECASE)
                if not _km:
                    continue
                _qn, _rest = int(_km.group(1)), _km.group(2).strip()
                _mm = re.search(r'\[(\d+)\]\s*$', _rest)
                if _mm:
                    _marks_dict[_qn] = int(_mm.group(1))
                    _rest = _rest[:_mm.start()].strip()
                _key_lines_out.append(f"Q{_qn}: {_rest} [{_marks_dict[_qn]}]" if _qn in _marks_dict else f"Q{_qn}: {_rest}")
            if _key_lines_out:
                st.session_state.paper_answer_key = "\n".join(_key_lines_out)
            if _marks_dict:
                st.session_state.paper_q_marks = _marks_dict
        except Exception:
            pass  # answer key from embedded block is still available as fallback

        # Log usage and mark limit
        _uid   = _current_user["id"]    if _current_user else None
        _email = _current_user["email"] if _current_user else None
        sb_log_paper(_uid, _email, p_grade, p_board)
        if not _current_user:
            st.session_state.paper_generated_this_session = True

        st.rerun()

    if st.session_state.paper_text:
        meta = st.session_state.paper_meta or {}
        board_label = f"{meta.get('board','')} &nbsp;|&nbsp; " if meta.get('board') else ""
        jee_label   = f" — {meta.get('jee_type','')}" if meta.get('jee_type') else ""
        year_label  = f"{meta.get('year','')} — " if meta.get('year') else ""
        st.markdown(f"""<div class="paper-header">
            <h3 style="margin:0;color:white;">📄 {board_label}{meta.get('grade','')}{jee_label}</h3>
            <p style="margin:.3rem 0 0;opacity:.75;font-size:.9rem;">{year_label}AI-Generated Practice Paper</p>
        </div>""", unsafe_allow_html=True)
        render_math_markdown(st.session_state.paper_text)
        st.divider()

        # ── Answer Entry ──────────────────────────────────────────────────────
        q_count = detect_question_count(st.session_state.paper_text)

        with st.expander(f"✏️ Enter Your Answers ({q_count} questions detected)", expanded=False):
            st.caption("MCQ: type A / B / C / D. Numerical: type the value. Leave blank to skip.")

            # Numbered answer inputs — 3 per row
            for _row_start in range(1, q_count + 1, 3):
                _cols = st.columns(3)
                for _ci, _qi in enumerate(range(_row_start, min(_row_start + 3, q_count + 1))):
                    with _cols[_ci]:
                        st.text_input(f"Q{_qi}", key=f"paper_ans_{_qi}",
                                      placeholder=f"Answer for Q{_qi}")

            # ── Math Symbol Keyboard (optional) ───────────────────────────
            with st.expander("🔢 Math Symbol Keyboard (optional — for Olympiad / advanced answers)", expanded=False):
                st.caption("Click a symbol to add it to the scratch pad, then copy-paste into your answer box.")
                if "math_scratch" not in st.session_state:
                    st.session_state.math_scratch = ""

                _sym_rows = [
                    ["π", "∞", "√", "∛", "²", "³", "±", "×", "÷"],
                    ["≠", "≤", "≥", "≈", "∈", "∉", "⊂", "∪", "∩"],
                    ["Σ", "∫", "∂", "∝", "∴", "α", "β", "γ", "θ"],
                    ["λ", "σ", "Δ", "μ", "φ", "ψ", "ω", "ε", "η"],
                ]
                for _sym_row in _sym_rows:
                    _sym_cols = st.columns(len(_sym_row))
                    for _sci, _sym in enumerate(_sym_row):
                        with _sym_cols[_sci]:
                            if st.button(_sym, key=f"sym_{_sym}", use_container_width=True):
                                st.session_state.math_scratch += _sym
                                st.rerun()

                _scratch_col, _sclear_col = st.columns([4, 1])
                with _scratch_col:
                    st.text_input("Scratch pad", key="math_scratch",
                                  placeholder="Symbols appear here — copy and paste into your answer box")
                with _sclear_col:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Clear", key="sym_clear", use_container_width=True):
                        st.session_state.math_scratch = ""
                        st.rerun()

            st.markdown("---")
            if st.button("🗑️ Clear Answers", use_container_width=True):
                for _qi in range(1, q_count + 1):
                    st.session_state[f"paper_ans_{_qi}"] = ""
                st.session_state.paper_score = None
                st.session_state.show_paper_solutions = False
                st.rerun()

        # ── Single submit button (outside expander for visibility) ──────────
        _sub_col, _new_col = st.columns([2, 1])
        with _sub_col:
            submit_btn = st.button("📊 Submit to get score and Complete solution",
                                   type="primary", use_container_width=True)
        with _new_col:
            if st.button("🔄 Generate New Paper", use_container_width=True):
                st.session_state.update(paper_text=None, paper_solutions=None,
                                        show_paper_solutions=False, paper_score=None,
                                        paper_answer_key=None, paper_q_marks=None)
                for _qi in range(1, 41):
                    st.session_state.pop(f"paper_ans_{_qi}", None)
                st.rerun()

        if submit_btn:
            _answers = {_qi: st.session_state.get(f"paper_ans_{_qi}", "")
                        for _qi in range(1, q_count + 1)}
            _filled  = sum(1 for v in _answers.values() if v.strip())
            if _filled == 0:
                st.warning("Please enter at least one answer before submitting.", icon="✏️")
            else:
                st.session_state.paper_score = None
                _answer_key  = st.session_state.get("paper_answer_key") or ""
                _total_marks = parse_total_marks(st.session_state.paper_text)

                score_text = grade_with_answer_key(
                    st.session_state.paper_text, _answers, _answer_key,
                    q_marks_override=st.session_state.get("paper_q_marks")
                )

                if score_text is None:
                    # Answer key missing — fall back to Claude
                    client = get_client()
                    st.info(f"⏳ Grading {_filled} answer(s)…", icon="🔄")
                    ph = st.empty()
                    score_text = stream_response(
                        client,
                        build_paper_grading_prompt(
                            st.session_state.paper_text, _answers,
                            _answer_key,
                            meta.get("grade", ""), meta.get("board", "")
                        ),
                        ph,
                        max_tokens=4096,
                        model="claude-sonnet-4-6",
                    )

                st.session_state.paper_score = fix_grading_score(score_text, total_marks=_total_marks)
                st.session_state.show_paper_solutions = True  # always reveal solutions on submit
                st.rerun()

        if st.session_state.show_paper_solutions and st.session_state.paper_solutions:
            st.markdown('<p class="section-label label-solution">✅ Complete Solutions & Marking Scheme</p>', unsafe_allow_html=True)
            render_math_markdown(st.session_state.paper_solutions)

        if st.session_state.paper_score:
            st.markdown('<p class="section-label label-solution">📊 Your Score & Feedback</p>',
                        unsafe_allow_html=True)
            render_math_markdown(st.session_state.paper_score)
    else:
        st.markdown("""
**How it works:**
1. Select board, grade and year style above
2. Click **Generate Exam Paper** — AI writes a complete paper in that board's official section structure
3. Attempt the paper yourself (or give it to a student)
4. Click **Generate Complete Solutions** to reveal the full marking scheme with step-by-step working
""")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ASK A DOUBT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 2:
    st.markdown("<div style='font-size:1.5rem;font-weight:800;color:#e2e8f0;margin-bottom:0.2rem;'>💬 Ask Anything</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:rgba(226,232,240,0.45);font-size:0.88rem;margin-bottom:1.2rem;'>No cap — type, snap, or upload whatever's confusing you. AI breaks it down step by step.</div>", unsafe_allow_html=True)

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
    ask_btn = st.button("🤔 Get AI Explanation", type="primary", use_container_width=False)

    if ask_btn and not ready:
        st.warning("Please enter a question, upload an image, or upload a PDF first.", icon="⚠️")
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
        render_math_box(st.session_state.doubt_response, "success")
        if st.button("🔄 Clear & Ask Another", key="doubt_clear"):
            st.session_state.doubt_response = None
            st.rerun()

# ── SEO Content Section ───────────────────────────────────────────────────────
st.markdown("""
<section id="seo-content" style="
    margin: 3rem auto 2rem auto;
    max-width: 960px;
    padding: 0 1.5rem;
    color: rgba(226,232,240,0.75);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.92rem;
    line-height: 1.8;
">

<hr style="border:none; border-top:1px solid rgba(139,92,246,0.2); margin-bottom:2.5rem;">

<!-- Who is it for -->
<h2 style="color:#c4b5fd; font-size:1.3rem; margin-bottom:0.75rem;">Free AI Math Practice for Every Student, Everywhere</h2>
<p>
Maths Daily Helper is a free AI-powered math practice tool built for students at every level — from
<strong>Grade 1 primary school</strong> all the way through <strong>Grade 12</strong> and competitive exams.
Whether you need daily arithmetic drills, algebra practice, geometry help, calculus problems, or full-length
exam papers, the tool generates fresh questions instantly and explains every solution step by step.
It works for students in <strong>India, the United States, the United Kingdom, Canada, Australia</strong>,
and anywhere else in the world.
</p>

<!-- Exam & curriculum grid -->
<h2 style="color:#c4b5fd; font-size:1.3rem; margin-top:2rem; margin-bottom:1rem;">Exams &amp; Curricula Supported</h2>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:1rem; margin-bottom:1.5rem;">

  <div style="background:rgba(139,92,246,0.08); border:1px solid rgba(139,92,246,0.18); border-radius:12px; padding:1rem;">
    <strong style="color:#e2e8f0;">India</strong>
    <ul style="margin:0.5rem 0 0 1rem; padding:0;">
      <li>CBSE Class 1–12</li>
      <li>ICSE / ISC</li>
      <li>IIT JEE Main &amp; Advanced</li>
      <li>BITSAT</li>
      <li>WBJEE, MHT CET, KCET</li>
      <li>NTSE, KVPY Maths</li>
      <li>Indian Mathematical Olympiad (IMO / RMO / INMO)</li>
    </ul>
  </div>

  <div style="background:rgba(139,92,246,0.08); border:1px solid rgba(139,92,246,0.18); border-radius:12px; padding:1rem;">
    <strong style="color:#e2e8f0;">United States</strong>
    <ul style="margin:0.5rem 0 0 1rem; padding:0;">
      <li>SAT Math (College Board)</li>
      <li>ACT Mathematics</li>
      <li>AMC 8, AMC 10, AMC 12</li>
      <li>AIME</li>
      <li>MATHCOUNTS</li>
      <li>AP Calculus AB / BC</li>
      <li>AP Statistics</li>
      <li>Common Core Grade 1–12</li>
    </ul>
  </div>

  <div style="background:rgba(139,92,246,0.08); border:1px solid rgba(139,92,246,0.18); border-radius:12px; padding:1rem;">
    <strong style="color:#e2e8f0;">United Kingdom</strong>
    <ul style="margin:0.5rem 0 0 1rem; padding:0;">
      <li>GCSE Maths (AQA, Edexcel, OCR)</li>
      <li>A-Level Maths &amp; Further Maths</li>
      <li>UK Junior / Intermediate / Senior Math Challenge</li>
      <li>UK Math Olympiad</li>
      <li>Key Stage 1, 2, 3, 4</li>
    </ul>
  </div>

  <div style="background:rgba(139,92,246,0.08); border:1px solid rgba(139,92,246,0.18); border-radius:12px; padding:1rem;">
    <strong style="color:#e2e8f0;">International</strong>
    <ul style="margin:0.5rem 0 0 1rem; padding:0;">
      <li>IB Mathematics (SL &amp; HL)</li>
      <li>Cambridge IGCSE &amp; A-Level</li>
      <li>International Math Olympiad (IMO)</li>
      <li>Australian AMC &amp; HSC</li>
      <li>Canadian Gauss, Cayley &amp; Fermat contests</li>
      <li>Singapore O-Level &amp; A-Level</li>
    </ul>
  </div>

</div>

<!-- Topics -->
<h2 style="color:#c4b5fd; font-size:1.3rem; margin-top:2rem; margin-bottom:0.75rem;">Math Topics Covered</h2>
<p>
The tool covers the full school and competitive mathematics curriculum:
<strong>Number sense &amp; arithmetic</strong> (Grade 1–5),
<strong>fractions, decimals &amp; percentages</strong>,
<strong>algebra</strong> (linear equations, quadratics, polynomials, functions),
<strong>geometry</strong> (2D shapes, triangles, circles, coordinate geometry, 3D solids),
<strong>trigonometry</strong> (ratios, identities, inverse functions),
<strong>calculus</strong> (limits, differentiation, integration, differential equations),
<strong>statistics &amp; probability</strong>,
<strong>number theory</strong> (primes, divisibility, modular arithmetic),
<strong>combinatorics &amp; permutations</strong>,
<strong>matrices &amp; vectors</strong>,
<strong>complex numbers</strong>,
and <strong>olympiad problem-solving</strong> (inequalities, functional equations, graph theory).
</p>

<!-- How it works -->
<h2 style="color:#c4b5fd; font-size:1.3rem; margin-top:2rem; margin-bottom:0.75rem;">How It Works</h2>
<p>
Select your grade level, choose a topic and subtopic, pick a difficulty (Easy, Medium, Hard, or Olympiad),
and click <em>Generate Problem</em>. Maths Daily Helper instantly creates a unique math problem tailored to
your selection. Stuck? Request a hint. Ready to check? Get a full step-by-step solution with explanations.
You can also generate complete <strong>sample exam papers</strong> (10–30 questions) for timed practice,
or upload a photo or PDF of a question you're struggling with and get an AI explanation instantly.
</p>

<!-- FAQ -->
<h2 style="color:#c4b5fd; font-size:1.3rem; margin-top:2rem; margin-bottom:1rem;">Frequently Asked Questions</h2>

<details style="margin-bottom:0.75rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:0.75rem 1rem;">
  <summary style="cursor:pointer; font-weight:600; color:#e2e8f0;">Is Maths Daily Helper completely free?</summary>
  <p style="margin:0.5rem 0 0 0;">Yes. Maths Daily Helper is 100% free — no sign-up, no subscription, no credit card. Every feature including problem generation, hints, step-by-step solutions, and exam paper generation is available at no cost.</p>
</details>

<details style="margin-bottom:0.75rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:0.75rem 1rem;">
  <summary style="cursor:pointer; font-weight:600; color:#e2e8f0;">Which grade levels does it support?</summary>
  <p style="margin:0.5rem 0 0 0;">Grade 1 through Grade 12, plus university-entry and competitive exam levels including IIT JEE, SAT, GCSE, A-Level, IB, and Math Olympiad.</p>
</details>

<details style="margin-bottom:0.75rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:0.75rem 1rem;">
  <summary style="cursor:pointer; font-weight:600; color:#e2e8f0;">Can I use it to prepare for IIT JEE?</summary>
  <p style="margin:0.5rem 0 0 0;">Yes. Select IIT JEE as your level and choose topics such as calculus, coordinate geometry, complex numbers, or probability. The AI generates JEE-style problems at the right difficulty with complete solutions.</p>
</details>

<details style="margin-bottom:0.75rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:0.75rem 1rem;">
  <summary style="cursor:pointer; font-weight:600; color:#e2e8f0;">Is it useful for SAT Math preparation?</summary>
  <p style="margin:0.5rem 0 0 0;">Absolutely. Select SAT as your exam level to get algebra, advanced math, problem-solving, and data analysis questions in the SAT format, complete with worked solutions.</p>
</details>

<details style="margin-bottom:0.75rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:0.75rem 1rem;">
  <summary style="cursor:pointer; font-weight:600; color:#e2e8f0;">Does it support CBSE and ICSE syllabuses?</summary>
  <p style="margin:0.5rem 0 0 0;">Yes. Problems follow the CBSE and ICSE curriculum for each class. You can also use it for NCERT-aligned practice across all classes from Class 1 to Class 12.</p>
</details>

<details style="margin-bottom:0.75rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:0.75rem 1rem;">
  <summary style="cursor:pointer; font-weight:600; color:#e2e8f0;">Can I practice Math Olympiad problems?</summary>
  <p style="margin:0.5rem 0 0 0;">Yes. Choose Olympiad difficulty to get competition-style problems covering number theory, combinatorics, geometry proofs, and inequalities — suitable for IMO, AMC, AIME, RMO, and similar contests.</p>
</details>

<details style="margin-bottom:0.75rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:0.75rem 1rem;">
  <summary style="cursor:pointer; font-weight:600; color:#e2e8f0;">Can I upload a photo of a math problem?</summary>
  <p style="margin:0.5rem 0 0 0;">Yes. Use the "Ask a Doubt" tab to upload a photo (JPG or PNG) or a PDF of any math problem. The AI will read the image and provide a full step-by-step explanation.</p>
</details>

<details style="margin-bottom:0.75rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:0.75rem 1rem;">
  <summary style="cursor:pointer; font-weight:600; color:#e2e8f0;">What AI powers Maths Daily Helper?</summary>
  <p style="margin:0.5rem 0 0 0;">Problems and solutions are generated by Claude AI, built by Anthropic. Claude is known for strong mathematical reasoning and clear, structured explanations.</p>
</details>

</section>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">built with ⚡ by mathdrop · powered by claude ai · made for the curious ones'
    ' &nbsp;·&nbsp; <a href="/?admin=true" style="color:rgba(226,232,240,0.15);text-decoration:none;">admin</a>'
    '</div>',
    unsafe_allow_html=True
)
