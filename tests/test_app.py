"""
Regression test suite for Maths Daily Helper (app.py).

Run with:  pytest tests/ -v
"""
import sys
import os
from unittest.mock import MagicMock
from datetime import date, timedelta
import pytest

# ── Mock all heavy/UI dependencies BEFORE importing app ──────────────────────
# This lets us import and call pure functions without a running Streamlit server.

class _FakeSessionState(dict):
    """dict that also supports attribute access, like st.session_state."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return MagicMock()
    def __setattr__(self, key, value):
        self[key] = value

_st = MagicMock()
_st.session_state = _FakeSessionState(
    supabase_user=None,
    problem_count=0,
    streak=0,
    last_solved_date=None,
    show_auth=False,
    sb_client=None,
    active_tab=0,
)
_st.cache_resource = lambda f: f          # decorator passthrough
_st.selectbox = lambda lbl, opts=(), **kw: (list(opts)[0] if opts else "")
_st.radio    = lambda lbl, opts=(), **kw: (list(opts)[0] if opts else "")
_st.multiselect = lambda lbl, opts=(), **kw: []
_st.columns  = lambda n, **kw: [MagicMock()] * (n if isinstance(n, int) else len(n))
_st.tabs     = lambda labels: [MagicMock()] * len(labels)

for _mod in [
    "streamlit",
    "streamlit.components",
    "streamlit.components.v1",
    "anthropic",
    "pdfplumber",
    "supabase",
    "requests",
    "resend",
]:
    sys.modules.setdefault(_mod, MagicMock())

sys.modules["streamlit"] = _st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app  # noqa: E402


# ═════════════════════════════════════════════════════════════════════════════
# detect_question_count
# ═════════════════════════════════════════════════════════════════════════════
class TestDetectQuestionCount:

    def test_q_prefix_style(self):
        text = "\n".join(f"Q{i}. Some question" for i in range(1, 21))
        assert app.detect_question_count(text) == 20

    def test_numbered_dot_style(self):
        text = "\n".join(f"{i}. Some question" for i in range(1, 16))
        assert app.detect_question_count(text) == 15

    def test_question_word_style(self):
        text = "\n".join(f"Question {i}\nSome question text" for i in range(1, 45))
        assert app.detect_question_count(text) == 44

    def test_bold_markdown_style(self):
        text = "\n".join(f"**{i}.** Some question" for i in range(1, 11))
        assert app.detect_question_count(text) == 10

    def test_parenthesis_style(self):
        text = "\n".join(f"({i}) Some question" for i in range(1, 26))
        assert app.detect_question_count(text) == 25

    def test_empty_returns_fallback(self):
        assert app.detect_question_count("") == 45

    def test_plain_text_no_numbers_returns_fallback(self):
        assert app.detect_question_count("Here is some text with no question numbers.") == 45

    def test_cap_at_100(self):
        text = "\n".join(f"Q{i}. question" for i in range(1, 150))
        assert app.detect_question_count(text) == 100

    def test_sat_44_questions(self):
        text = "\n".join(f"Question {i}\nAnswer choices here" for i in range(1, 45))
        assert app.detect_question_count(text) == 44

    def test_mixed_formats_takes_max(self):
        # Paper has both Q1 and numbered lines — should return the higher
        text = "Q1. first\nQ2. second\n10. tenth"
        assert app.detect_question_count(text) == 10

    def test_jee_90_questions(self):
        text = "\n".join(f"Q{i}. Some question" for i in range(1, 91))
        assert app.detect_question_count(text) == 90


# ═════════════════════════════════════════════════════════════════════════════
# parse_problem
# ═════════════════════════════════════════════════════════════════════════════
class TestParseProblem:

    def test_extracts_problem_and_hint(self):
        text = "PROBLEM:\nSolve x^2 = 4\nHINT:\nThink about square roots"
        result = app.parse_problem(text)
        assert "Solve x^2 = 4" in result["problem"]
        assert "square roots" in result["hint"]

    def test_no_hint_section(self):
        text = "PROBLEM:\nSolve x^2 = 4"
        result = app.parse_problem(text)
        assert "Solve x^2 = 4" in result["problem"]
        assert result["hint"] == ""

    def test_fallback_returns_full_text(self):
        text = "Some random text without markers"
        result = app.parse_problem(text)
        assert result["problem"] == text

    def test_case_insensitive_markers(self):
        text = "problem:\nThe question\nhint:\nThe hint"
        result = app.parse_problem(text)
        assert "The question" in result["problem"]
        assert "The hint" in result["hint"]


# ═════════════════════════════════════════════════════════════════════════════
# build_verify_prompt
# ═════════════════════════════════════════════════════════════════════════════
class TestBuildVerifyPrompt:

    def setup_method(self):
        self.prompt = app.build_verify_prompt(
            "Solve x² + 5x + 6 = 0",
            "x = -2 and x = -3"
        )

    def test_contains_five_steps(self):
        for step in ["STEP 1", "STEP 2", "STEP 3", "STEP 4", "STEP 5"]:
            assert step in self.prompt

    def test_result_keyword_present(self):
        assert "RESULT: CORRECT" in self.prompt
        assert "RESULT: INCORRECT" in self.prompt

    def test_contains_problem_text(self):
        assert "x² + 5x + 6 = 0" in self.prompt

    def test_contains_student_answer(self):
        assert "x = -2 and x = -3" in self.prompt

    def test_instructs_independent_solve_first(self):
        # Step 1 must appear before Step 3 (where student answer is compared)
        assert self.prompt.index("STEP 1") < self.prompt.index("STEP 3")


# ═════════════════════════════════════════════════════════════════════════════
# build_paper_grading_prompt
# ═════════════════════════════════════════════════════════════════════════════
class TestBuildPaperGradingPrompt:

    def setup_method(self):
        self.paper = "Q1. What is 2+2?\n(A) 3  (B) 4  (C) 5  (D) 6\n\nQ2. Solve x+1=3"
        self.answers = {1: "B", 2: "x=2"}
        self.prompt = app.build_paper_grading_prompt(
            self.paper, self.answers, "Grade 8", "CBSE"
        )

    def test_contains_paper_text(self):
        assert "What is 2+2?" in self.prompt

    def test_contains_student_answers(self):
        assert "Q1: B" in self.prompt
        assert "Q2: x=2" in self.prompt

    def test_contains_step_by_step_solve(self):
        prompt_lower = self.prompt.lower()
        assert "independently" in prompt_lower or "solve" in prompt_lower

    def test_mcq_letter_matching_instruction(self):
        prompt_lower = self.prompt.lower()
        assert "letter" in prompt_lower or "a/b/c/d" in prompt_lower

    def test_total_score_format_present(self):
        assert "TOTAL SCORE" in self.prompt

    def test_exam_context_in_prompt(self):
        assert "CBSE" in self.prompt
        assert "Grade 8" in self.prompt

    def test_empty_answers_excluded(self):
        answers_with_blank = {1: "B", 2: "", 3: "  "}
        prompt = app.build_paper_grading_prompt(
            self.paper, answers_with_blank, "Grade 8", "CBSE"
        )
        assert "Q1: B" in prompt
        assert "Q2:" not in prompt
        assert "Q3:" not in prompt

    def test_no_board_competitive_exam(self):
        prompt = app.build_paper_grading_prompt(
            self.paper, self.answers, "IIT JEE", None
        )
        assert "IIT JEE" in prompt

    def test_proof_question_handling_mentioned(self):
        prompt_lower = self.prompt.lower()
        assert "prove" in prompt_lower or "proof" in prompt_lower or "subjective" in prompt_lower


# ═════════════════════════════════════════════════════════════════════════════
# build_problem_prompt
# ═════════════════════════════════════════════════════════════════════════════
class TestBuildProblemPrompt:

    def test_contains_grade_topic_difficulty(self):
        p = app.build_problem_prompt("Grade 10", "Hard", "Algebra", "Quadratics")
        assert "Grade 10" in p
        assert "Algebra" in p
        assert "Quadratics" in p
        assert "Hard" in p

    def test_format_markers_present(self):
        p = app.build_problem_prompt("Grade 10", "Medium", "Geometry", "Triangles")
        assert "PROBLEM:" in p
        assert "HINT:" in p

    def test_jee_gets_jee_style(self):
        p = app.build_problem_prompt("IIT JEE", "Hard", "Calculus", "Integration")
        assert "JEE" in p

    def test_sat_gets_sat_style(self):
        p = app.build_problem_prompt("SAT", "Medium", "Algebra", "Linear Equations")
        assert "SAT" in p

    def test_gre_gets_gre_style(self):
        p = app.build_problem_prompt("GRE Quantitative", "Medium", "Statistics", "Mean")
        assert "GRE" in p

    def test_gmat_gets_gmat_style(self):
        p = app.build_problem_prompt("GMAT Quantitative", "Medium", "Algebra", "Ratios")
        assert "GMAT" in p

    def test_olympiad_gets_olympiad_style(self):
        p = app.build_problem_prompt("Math Olympiad (IMO)", "Olympiad", "Number Theory", "Primes")
        assert "olympiad" in p.lower() or "olympiad" in p.lower()


# ═════════════════════════════════════════════════════════════════════════════
# RESULT line parsing  (replicates logic in the Check Answer handler)
# ═════════════════════════════════════════════════════════════════════════════
class TestResultParsing:

    def _parse(self, text):
        """Mirror the RESULT-scanning logic used in the app (exact line match)."""
        for line in text.splitlines():
            stripped = line.strip()
            if stripped == "RESULT: CORRECT":
                return True
            if stripped == "RESULT: INCORRECT":
                return False
        return None  # not found

    def test_correct_at_end(self):
        assert self._parse("STEP 1...\nSTEP 5\nRESULT: CORRECT") is True

    def test_incorrect_at_end(self):
        assert self._parse("Some explanation.\nRESULT: INCORRECT") is False

    def test_correct_mid_response(self):
        assert self._parse("RESULT: CORRECT\nExtra notes here") is True

    def test_no_result_line_returns_none(self):
        assert self._parse("Looks correct to me. Well done.") is None

    def test_partial_match_does_not_trigger(self):
        # "RESULT: CORRECTLY" should not trigger CORRECT
        assert self._parse("RESULT: CORRECTLY answered") is None

    def test_incorrect_before_correct_reads_first(self):
        # First matching line wins
        response = "RESULT: INCORRECT\nRESULT: CORRECT"
        assert self._parse(response) is False


# ═════════════════════════════════════════════════════════════════════════════
# Streak logic  (replicates logic in handle_correct_answer)
# ═════════════════════════════════════════════════════════════════════════════
class TestStreakLogic:

    def _apply(self, last_date, current_streak, today=None):
        today = today or date.today()
        if last_date == today:
            new_streak = current_streak
        elif last_date and (today - last_date).days == 1:
            new_streak = current_streak + 1
        else:
            new_streak = 1
        return new_streak

    def test_first_solve_sets_streak_to_1(self):
        assert self._apply(None, 0) == 1

    def test_consecutive_day_increments(self):
        yesterday = date.today() - timedelta(days=1)
        assert self._apply(yesterday, 5) == 6

    def test_two_day_gap_resets_to_1(self):
        two_days_ago = date.today() - timedelta(days=2)
        assert self._apply(two_days_ago, 10) == 1

    def test_week_gap_resets_to_1(self):
        week_ago = date.today() - timedelta(days=7)
        assert self._apply(week_ago, 20) == 1

    def test_same_day_does_not_increment(self):
        today = date.today()
        assert self._apply(today, 7) == 7

    def test_streak_of_1_goes_to_2_next_day(self):
        yesterday = date.today() - timedelta(days=1)
        assert self._apply(yesterday, 1) == 2


# ═════════════════════════════════════════════════════════════════════════════
# Grade / curriculum data integrity
# ═════════════════════════════════════════════════════════════════════════════
class TestCurriculumData:

    def test_all_grades_have_topics(self):
        for grade, topics in app.GRADE_CURRICULUM.items():
            assert len(topics) > 0, f"{grade} has no topics"

    def test_all_topics_have_subtopics(self):
        for grade, topics in app.GRADE_CURRICULUM.items():
            for topic, subtopics in topics.items():
                assert len(subtopics) > 0, f"{grade} > {topic} has no subtopics"

    def test_gre_present(self):
        assert any("GRE" in g for g in app.GRADE_CURRICULUM)

    def test_gmat_present(self):
        assert any("GMAT" in g for g in app.GRADE_CURRICULUM)

    def test_sat_present(self):
        assert any("SAT" in g for g in app.GRADES)

    def test_iit_jee_present(self):
        assert any("JEE" in g for g in app.GRADES)
