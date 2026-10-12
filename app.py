from __future__ import annotations

import json
import random
import re
import sqlite3
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "quizforge_history.sqlite3"
st.set_page_config(page_title="QuizForge — Infinite Quiz Studio", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--ink:#edf0f7;--muted:#9aa5b8;--line:#283246;--panel:#111827;--panel2:#151f30;--blue:#91adff;--mint:#91e5c5}
html,body,[class*="css"]{font-family:'Manrope',sans-serif}
.stApp{background:radial-gradient(ellipse at 15% 0%,#192642 0%,transparent 34%),#0a0f19;color:var(--ink)}
.block-container{max-width:1420px;padding-top:1.7rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.04em!important}
h1{font-weight:800!important}
div[data-testid="stMetric"]{background:linear-gradient(145deg,#151f30,#101725);border:1px solid #29364d;border-radius:16px;padding:17px 18px}
div[data-testid="stMetricLabel"]{color:#9aa8bf}
div[data-testid="stMetricValue"]{color:#f3f6ff}
.stButton>button{border-radius:11px;border:1px solid #35445f;min-height:2.7rem;font-weight:700;background:#172338;color:#edf2ff}
.stButton>button:hover{border-color:#91adff;color:#fff;background:#1d2d49}
.stButton>button[kind="primary"]{background:#a9bdff;color:#101729;border-color:#a9bdff}
.stTextInput input,.stNumberInput input,.stSelectbox div[data-baseweb="select"],.stTextArea textarea{background:#0c1422;border-color:#2b3850;border-radius:10px;color:#f1f4fb}
div[data-testid="stExpander"]{border:1px solid #29364b;border-radius:12px;background:#101827}
div[data-testid="stAlert"]{border-radius:12px}
div[data-testid="stProgressBar"]>div>div{background:linear-gradient(90deg,#8ba8ff,#8fe2c2)}
.qcard{border:1px solid #2a374e;background:linear-gradient(145deg,#141e2e,#101724);border-radius:17px;padding:22px 24px;margin:10px 0 15px}
.eyebrow{font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:.14em;font-size:.72rem;color:#9db5ff}
.qtext{font-size:1.28rem;font-weight:750;line-height:1.48;margin:.65rem 0 1rem;color:#f2f5fc}
.muted{color:#9aa8bf}
.smallmono{font-family:'DM Mono',monospace;font-size:.74rem;color:#9aa8bf}
.brandmark{display:inline-flex;align-items:center;gap:10px;border:1px solid #2b3951;background:#111a29;padding:8px 12px;border-radius:12px}
.brandicon{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:9px;background:#a9bdff;color:#101729;font-weight:900}
hr{border-color:#263249}
footer{visibility:hidden}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

TOPICS: dict[str, dict[str, Any]] = {
    "Python": {"description": "Core Python, collections, functions, files and practical debugging.", "tags": ["python", "programming", "coding"]},
    "Computer Science": {"description": "Algorithms, data structures, operating systems and networking.", "tags": ["computer science", "cs", "programming"]},
    "AI & Machine Learning": {"description": "ML foundations, neural networks, computer vision and responsible AI.", "tags": ["ai", "machine learning", "ml", "technology"]},
    "Mathematics": {"description": "Arithmetic, algebra, geometry, probability and logical reasoning.", "tags": ["math", "mathematics", "algebra"]},
    "Science": {"description": "Physics, chemistry, biology and the scientific method.", "tags": ["science", "physics", "chemistry", "biology"]},
    "World History": {"description": "Civilizations, turning points, chronology and historical context.", "tags": ["history", "world history"]},
    "Geography": {"description": "Landforms, climate, maps, countries and human geography.", "tags": ["geography", "earth"]},
    "General Knowledge": {"description": "Stable facts across culture, institutions, nature and society.", "tags": ["general knowledge", "gk", "trivia"]},
    "English": {"description": "Grammar, vocabulary, usage, literary terms and clear writing.", "tags": ["english", "grammar", "vocabulary"]},
    "Cybersecurity": {"description": "Defensive security, privacy, networks and secure software habits.", "tags": ["security", "cybersecurity", "privacy"]},
    "Web Development": {"description": "HTML, CSS, JavaScript, HTTP and browser fundamentals.", "tags": ["web", "html", "css", "javascript"]},
    "Logical Reasoning": {"description": "Patterns, deductions, sequences and structured problem-solving.", "tags": ["logic", "reasoning", "aptitude"]},
}

@dataclass
class Question:
    topic: str
    difficulty: str
    prompt: str
    options: list[str]
    answer: str
    explanation: str
    source: str = "QuizForge built-in question bank"

# Hand-written seed questions. Quiz generation samples without repeating until the selected topic/difficulty pool is exhausted.
BANK: list[Question] = [
Question("Python","Beginner","Which Python type is designed to store an ordered, mutable sequence?",["tuple","list","frozenset","str"],"list","A list preserves item order and supports item assignment and methods such as append()."),
Question("Python","Beginner","What does len({'a': 1, 'b': 2}) return?",["1","2","3","An error"],"2","len() on a dictionary returns the number of keys."),
Question("Python","Beginner","Which keyword begins a function definition in Python?",["func","define","def","function"],"def","Python uses def to define a function."),
Question("Python","Intermediate","What is the result of [x*x for x in range(4) if x % 2 == 0]?",["[0, 1, 4, 9]","[0, 4]","[1, 9]","[2, 4]"],"[0, 4]","The comprehension keeps even x values, 0 and 2, and squares them."),
Question("Python","Intermediate","Which statement about a Python set is true?",["It preserves duplicate values","Its elements must be hashable","It supports integer indexing","It always preserves insertion order as its contract"],"Its elements must be hashable","Set elements must be hashable so membership can be managed efficiently."),
Question("Python","Advanced","What is the main purpose of a context manager used with the with statement?",["To make every operation asynchronous","To manage setup and cleanup around a block","To suppress every exception","To turn a function into a generator"],"To manage setup and cleanup around a block","Context managers use the context management protocol to reliably manage resources or other state."),
Question("Computer Science","Beginner","Which data structure follows FIFO order?",["Stack","Queue","Heap","Graph"],"Queue","FIFO means first in, first out, which is the queue discipline."),
Question("Computer Science","Intermediate","Binary search on a sorted array has what worst-case time complexity?",["O(1)","O(log n)","O(n)","O(n log n)"],"O(log n)","Each comparison halves the remaining search interval."),
Question("Computer Science","Intermediate","Which structure is most directly suited to representing pairwise connections between entities?",["Graph","Stack","Scalar","Queue"],"Graph","Graphs model vertices and edges between them."),
Question("Computer Science","Advanced","A hash table has n items and severe collisions. What can its worst-case lookup time become?",["O(1) guaranteed","O(log log n)","O(n)","O(n²) always"],"O(n)","With all keys colliding, lookup may inspect a linear number of entries."),
Question("AI & Machine Learning","Beginner","In supervised learning, training examples usually include what?",["Only unlabeled inputs","Inputs paired with target labels","Only random noise","No data"],"Inputs paired with target labels","Supervised methods learn from examples that include target outputs or labels."),
Question("AI & Machine Learning","Intermediate","What is overfitting?",["A model performs well on training data but generalizes poorly","A model cannot fit training data at all","A dataset has no labels","A model uses too little memory"],"A model performs well on training data but generalizes poorly","Overfitting captures training-specific patterns that do not transfer reliably to unseen data."),
Question("AI & Machine Learning","Intermediate","Why keep a test set separate from training data?",["To increase training-set size","To estimate performance on unseen data","To guarantee 100% accuracy","To remove all bias automatically"],"To estimate performance on unseen data","A held-out test set gives a less biased final estimate when not used for model selection."),
Question("AI & Machine Learning","Advanced","For an imbalanced binary classification task, why might precision-recall metrics be informative?",["They reveal the trade-off between positive predictive value and sensitivity","They guarantee calibrated probabilities","They replace the need for labels","They always equal accuracy"],"They reveal the trade-off between positive predictive value and sensitivity","Precision and recall expose different aspects of positive-class performance, particularly when classes are imbalanced."),
Question("Mathematics","Beginner","What is 15% of 240?",["24","30","36","42"],"36","0.15 × 240 = 36."),
Question("Mathematics","Beginner","Solve: 3x + 5 = 20.",["x = 3","x = 5","x = 8","x = 15"],"x = 5","Subtract 5 to get 3x = 15, then divide by 3."),
Question("Mathematics","Intermediate","A fair six-sided die is rolled once. What is the probability of getting an even number?",["1/6","1/3","1/2","2/3"],"1/2","Three of the six outcomes, 2, 4, and 6, are even."),
Question("Mathematics","Intermediate","What is the slope of the line through (2, 3) and (6, 11)?",["1","2","4","8"],"2","Slope = (11 − 3) / (6 − 2) = 8 / 4 = 2."),
Question("Mathematics","Advanced","If f(x)=x²−4x, at what x-value does f reach its minimum?",["−2","0","2","4"],"2","For ax²+bx+c with a positive, the vertex is at x=−b/(2a)=4/2=2."),
Question("Science","Beginner","Which cell structure is the main site of aerobic respiration in eukaryotic cells?",["Ribosome","Mitochondrion","Golgi apparatus","Cell wall"],"Mitochondrion","Mitochondria host most ATP-producing stages of aerobic respiration in eukaryotic cells."),
Question("Science","Beginner","At standard atmospheric pressure, pure water freezes at what temperature on the Celsius scale?",["0°C","10°C","32°C","100°C"],"0°C","The freezing point of pure water is 0°C at standard atmospheric pressure."),
Question("Science","Intermediate","Which particle has a negative electric charge?",["Proton","Neutron","Electron","Alpha particle"],"Electron","An electron carries a negative elementary charge."),
Question("Science","Intermediate","Which relationship is expressed by Newton's second law for constant mass?",["F = ma","E = mc²","V = IR²","P = m/v"],"F = ma","The net force equals mass multiplied by acceleration."),
Question("Science","Advanced","Which molecule carries genetic information in most living organisms?",["ATP","DNA","Glucose","Hemoglobin"],"DNA","DNA stores hereditary information in most organisms; some viruses use RNA."),
Question("World History","Beginner","The ancient Olympic Games originated in which civilization?",["Ancient Greek","Ancient Roman","Ancient Egyptian","Ancient Persian"],"Ancient Greek","The ancient games were held at Olympia in Greece."),
Question("World History","Intermediate","The printing press associated with Johannes Gutenberg spread in which European century?",["12th century","14th century","15th century","18th century"],"15th century","Gutenberg's movable-type printing work is associated with mid-15th-century Europe."),
Question("World History","Intermediate","The Magna Carta was sealed in England in which year?",["1066","1215","1492","1688"],"1215","King John sealed Magna Carta in 1215."),
Question("World History","Advanced","Which development most directly helped accelerate industrialization in 18th-century Britain?",["Mechanized production and expanding use of steam power","The invention of the internet","The end of all international trade","The replacement of factories by household-only production"],"Mechanized production and expanding use of steam power","Mechanization, energy changes, capital, and institutions all contributed to Britain's Industrial Revolution."),
Question("Geography","Beginner","Which is the largest ocean on Earth by area?",["Atlantic Ocean","Indian Ocean","Arctic Ocean","Pacific Ocean"],"Pacific Ocean","The Pacific is the largest ocean by surface area."),
Question("Geography","Beginner","What do contour lines on a topographic map usually connect?",["Places of equal elevation","Places with equal population","Roads with the same name","Countries with shared borders"],"Places of equal elevation","Contour lines connect points at the same elevation."),
Question("Geography","Intermediate","Which atmospheric layer contains most of Earth's weather?",["Stratosphere","Troposphere","Mesosphere","Thermosphere"],"Troposphere","Most clouds and weather occur in the troposphere."),
Question("Geography","Advanced","Why are many major deserts found around 30° north and south latitude?",["Descending dry air in subtropical high-pressure belts","The strongest daily tides occur there","Earth's magnetic field blocks clouds there","All ocean currents stop at those latitudes"],"Descending dry air in subtropical high-pressure belts","Hadley-cell circulation produces subsiding, warming air that inhibits cloud formation in many subtropical regions."),
Question("General Knowledge","Beginner","How many sides does a hexagon have?",["Five","Six","Seven","Eight"],"Six","A hexagon is a six-sided polygon."),
Question("General Knowledge","Intermediate","What is the SI base unit of electric current?",["Volt","Ohm","Ampere","Watt"],"Ampere","The ampere is the SI base unit for electric current."),
Question("General Knowledge","Intermediate","Which organization publishes the annual Human Development Report?",["UNDP","WTO","OPEC","Interpol"],"UNDP","The United Nations Development Programme publishes the Human Development Report."),
Question("General Knowledge","Advanced","Which principle is central to the scientific method?",["Claims should be testable against evidence","A hypothesis must never be revised","A single observation proves every universal claim","Authority replaces reproducibility"],"Claims should be testable against evidence","Scientific claims should be open to empirical testing and revision in light of evidence."),
Question("English","Beginner","Choose the grammatically correct sentence.",["She go to school daily.","She goes to school daily.","She going to school daily.","She gone to school daily."],"She goes to school daily.","The third-person singular subject 'she' takes 'goes' in the simple present."),
Question("English","Intermediate","Which word is closest in meaning to 'meticulous'?",["Careless","Precise and attentive","Impatient","Uncertain"],"Precise and attentive","Meticulous describes careful attention to detail."),
Question("English","Intermediate","In the sentence 'The old bridge groaned in the wind,' which device gives a nonhuman thing a human-like action?",["Hyperbole","Personification","Alliteration","Euphemism"],"Personification","The bridge is described as groaning, a human-like action."),
Question("English","Advanced","Which sentence uses a semicolon most appropriately?",["I packed; my bag and shoes.","The sky darkened; rain soon followed.","Because; it was late, we left.","She likes; reading novels."],"The sky darkened; rain soon followed.","A semicolon can connect closely related independent clauses."),
Question("Cybersecurity","Beginner","What is the safest response to an unexpected email asking for your password?",["Reply with the password","Use the email link immediately","Verify through a trusted channel and never share the password","Forward it to everyone"],"Verify through a trusted channel and never share the password","Unexpected credential requests are a phishing warning sign; verify independently."),
Question("Cybersecurity","Intermediate","What does multi-factor authentication add?",["A second independent verification factor","A guarantee against every attack","A public password list","Automatic encryption of every file"],"A second independent verification factor","MFA requires two or more factor types, reducing risk if one credential is compromised."),
Question("Cybersecurity","Intermediate","Why should software dependencies be updated responsibly?",["Updates can fix known vulnerabilities, but should be tested","Every update is guaranteed harmless","Updates eliminate the need for backups","Only the visual appearance changes"],"Updates can fix known vulnerabilities, but should be tested","Updates often patch vulnerabilities; testing helps catch compatibility regressions."),
Question("Cybersecurity","Advanced","What is the principle of least privilege?",["Give every account administrator rights","Grant only permissions needed for the task","Disable all authentication","Reuse one account for every person"],"Grant only permissions needed for the task","Least privilege limits the access available if an account or process is compromised."),
Question("Web Development","Beginner","Which HTML element is intended for the main heading of a page?",["<h1>","<head>","<meta>","<footer>"],"<h1>","The h1 element represents the highest-level heading in the page content."),
Question("Web Development","Beginner","Which CSS property changes text color?",["font-style","background-color","color","text-decoration"],"color","The color property sets an element's foreground text color."),
Question("Web Development","Intermediate","What does HTTP status code 404 conventionally indicate?",["Request succeeded","Resource was not found","Server redirected permanently","Client is authenticated"],"Resource was not found","404 is the standard Not Found response status."),
Question("Web Development","Advanced","Why is escaping or safely encoding untrusted text important when rendering HTML?",["It helps prevent untrusted text from being interpreted as executable markup","It makes every page load offline","It encrypts all network traffic","It guarantees correct business logic"],"It helps prevent untrusted text from being interpreted as executable markup","Context-appropriate output encoding helps mitigate injection issues such as cross-site scripting."),
Question("Logical Reasoning","Beginner","What number comes next: 2, 4, 8, 16, …?",["18","24","30","32"],"32","Each term doubles, so 16 × 2 = 32."),
Question("Logical Reasoning","Intermediate","All zargs are mips. No mips are lums. Which conclusion must follow?",["Some zargs are lums","No zargs are lums","All lums are zargs","All mips are zargs"],"No zargs are lums","Since every zarg belongs to the set of mips and no mip is a lum, no zarg can be a lum."),
Question("Logical Reasoning","Intermediate","A code uses A=1, B=2, …, Z=26. What is the sum for CAT?",["22","24","26","28"],"24","C=3, A=1, T=20; the sum is 3+1+20=24."),
Question("Logical Reasoning","Advanced","Three boxes are labeled APPLES, ORANGES, and MIXED. Every label is wrong. You may take one fruit from one box to identify all boxes. From which labeled box should you draw?",["APPLES","ORANGES","MIXED","Any box works equally well"],"MIXED","Because all labels are wrong, the box labeled MIXED cannot be mixed. One fruit reveals its single-fruit contents, after which the other two boxes can be deduced."),
]

def init_db() -> None:
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, played_at REAL NOT NULL,
            topic TEXT NOT NULL, difficulty TEXT NOT NULL, correct INTEGER NOT NULL,
            total INTEGER NOT NULL, seconds REAL NOT NULL
        )""")

def history() -> list[tuple]:
    init_db()
    with sqlite3.connect(DB_PATH) as con:
        return con.execute("SELECT played_at, topic, difficulty, correct, total, seconds FROM attempts ORDER BY id DESC LIMIT 500").fetchall()

def save_attempt(topic: str, difficulty: str, correct: int, total: int, seconds: float) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as con:
        con.execute("INSERT INTO attempts(played_at,topic,difficulty,correct,total,seconds) VALUES(?,?,?,?,?,?)",
                    (time.time(), topic, difficulty, correct, total, seconds))

def generate_questions(topic: str, difficulty: str, count: int, used: set[str], custom_text: str = "") -> list[Question]:
    pool = [q for q in BANK if (topic == "Mixed topics" or q.topic == topic) and (difficulty == "Any" or q.difficulty == difficulty)]
    pool = [q for q in pool if q.prompt not in used]
    random.shuffle(pool)
    result = pool[:count]
    if custom_text.strip():
        result.extend(parse_custom_questions(custom_text, topic, difficulty, used, max(0, count-len(result))))
    return result[:count]

def parse_custom_questions(text: str, topic: str, difficulty: str, used: set[str], limit: int) -> list[Question]:
    """Optional custom question import format: question | option A | option B | option C | option D | answer | explanation"""
    result = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7 or parts[0] in used:
            continue
        prompt, *rest = parts
        options = rest[:4]
        answer, explanation = rest[4:6]
        if answer not in options:
            continue
        result.append(Question(topic if topic != "Mixed topics" else "Custom", difficulty if difficulty != "Any" else "Custom", prompt, options, answer, explanation, "User-imported"))
        if len(result) >= limit:
            break
    return result

def reset_round() -> None:
    for key in ["round_questions", "round_index", "round_answers", "round_started", "round_finished", "round_saved"]:
        st.session_state.pop(key, None)

init_db()
if "used_questions" not in st.session_state:
    st.session_state.used_questions = set()
if "total_answered" not in st.session_state:
    st.session_state.total_answered = 0
if "total_correct" not in st.session_state:
    st.session_state.total_correct = 0

with st.sidebar:
    st.markdown("## ✦ QuizForge")
    st.caption("INFINITE QUIZ STUDIO")
    st.markdown("---")
    st.markdown("### Build your session")
    topic = st.selectbox("Topic", ["Mixed topics", *TOPICS.keys()], index=0)
    if topic != "Mixed topics":
        st.caption(TOPICS[topic]["description"])
    difficulty = st.select_slider("Difficulty", options=["Beginner", "Intermediate", "Advanced"], value="Intermediate")
    question_count = st.slider("Questions per round", 3, 20, 10)
    timer_mode = st.selectbox("Pace", ["Relaxed", "Timed challenge"])
    seconds_per_question = st.slider("Seconds per question", 10, 120, 30, step=5, disabled=timer_mode != "Timed challenge")
    shuffle_options = st.toggle("Shuffle answer options", value=True)
    show_hints = st.toggle("Show optional hints", value=True)
    instant_feedback = st.toggle("Explain after each answer", value=True)
    st.markdown("---")
    st.markdown("### Your controls")
    if st.button("↻ Reset used-question history", use_container_width=True):
        st.session_state.used_questions = set()
        st.success("Question rotation reset. You can replay the available bank.")
    st.caption("Questions rotate without repeats until the selected pool is exhausted. This starter uses a curated local bank; it does not invent unlimited new facts.")

st.markdown('<div class="brandmark"><span class="brandicon">✦</span><span><b>QUIZFORGE</b><br><span class="smallmono">INFINITE QUIZ STUDIO</span></span></div>', unsafe_allow_html=True)
st.title("Your curiosity. No finish line.")
st.markdown('<p class="muted">Pick a topic, tune the challenge, and keep learning. Minimal interface, meaningful feedback, and your progress stored locally.</p>', unsafe_allow_html=True)

h = history()
answered = st.session_state.total_answered
accuracy = round(100 * st.session_state.total_correct / answered) if answered else 0
c1,c2,c3,c4 = st.columns(4)
c1.metric("Questions answered", answered)
c2.metric("Accuracy", f"{accuracy}%")
c3.metric("Topics available", len(TOPICS))
c4.metric("Saved sessions", len(h))

st.markdown("---")
left, right = st.columns([1.6,1], gap="large")
with left:
    st.subheader("Start a round")
    st.write("Choose a subject in the sidebar. Each round gives you a fresh selection from the question bank.")
    available = [q for q in BANK if (topic == "Mixed topics" or q.topic == topic) and (difficulty == "Any" or q.difficulty == difficulty) and q.prompt not in st.session_state.used_questions]
    if not available:
        st.warning("You've exhausted this topic and difficulty pool. Reset used-question history or change the filters.")
    else:
        st.caption(f"{len(available)} unseen questions available for the current selection.")
    custom = st.text_area("Optional: add your own questions", placeholder="One per line: question | option A | option B | option C | option D | correct option text | explanation", height=100)
    with st.expander("See import format example"):
        st.code("What is 2 + 2? | 3 | 4 | 5 | 6 | 4 | Adding two and two gives four.", language="text")
    if st.button("✦ Forge a new round", type="primary", use_container_width=True, disabled=(not available and not custom.strip())):
        reset_round()
        qs = generate_questions(topic, difficulty, question_count, st.session_state.used_questions, custom)
        if qs:
            if shuffle_options:
                for q in qs:
                    # Preserve correctness while randomizing choices.
                    random.shuffle(q.options)
            st.session_state.round_questions = [asdict(q) for q in qs]
            st.session_state.round_index = 0
            st.session_state.round_answers = []
            st.session_state.round_started = time.time()
            st.session_state.round_finished = False
            st.session_state.round_saved = False
            st.rerun()
        else:
            st.warning("No valid questions available. Try another topic or check your custom-question format.")
with right:
    st.subheader("Your learning rhythm")
    if answered:
        st.progress(accuracy/100, text=f"{accuracy}% lifetime accuracy")
        st.write(f"You've answered **{answered}** questions so far, with **{st.session_state.total_correct}** correct.")
    else:
        st.info("Your stats begin with your first answer. Progress is stored in a local SQLite file on this computer.")
    st.markdown("#### Included topics")
    st.markdown(" · ".join(TOPICS.keys()))
    st.markdown("#### Design principles")
    st.markdown("- No account or API key\n- No external AI calls\n- Explanations with each answer\n- Local progress history\n- Question rotation without repeats")

if "round_questions" in st.session_state:
    qs = st.session_state.round_questions
    idx = st.session_state.round_index
    if idx < len(qs):
        q = qs[idx]
        st.markdown("---")
        st.markdown(f'<div class="eyebrow">ROUND IN PROGRESS · QUESTION {idx+1} OF {len(qs)}</div>', unsafe_allow_html=True)
        st.progress(idx/len(qs), text=f"{idx} of {len(qs)} completed")
        pending = st.session_state.get("pending_feedback")
        if pending is not None:
            if pending["correct"]:
                st.success("Correct — nicely done.")
            else:
                st.error(f"Not quite. The answer is: {pending['answer']}")
            if instant_feedback:
                st.info(pending["explanation"])
            if st.button("Continue to next question →", type="primary", use_container_width=True):
                st.session_state.round_index += 1
                st.session_state.pending_feedback = None
                st.rerun()
        else:
            st.markdown(f'<div class="qcard"><div class="eyebrow">{q["topic"]} / {q["difficulty"]}</div><div class="qtext">{q["prompt"]}</div></div>', unsafe_allow_html=True)
            if timer_mode == "Timed challenge":
                st.caption(f"Challenge setting: {seconds_per_question} seconds per question. This starter provides a timed mode setting; strict per-question countdown enforcement is not enabled yet.")
            if show_hints:
                with st.expander("Need a hint?"):
                    st.write("Break the question into its key concept, then eliminate choices that do not fit. (A more specific hint can be added to each question in future versions.)")
            answer_key = f"answer_{idx}"
            choice = st.radio("Choose one answer", q["options"], key=answer_key, index=None)
            col_a,col_b = st.columns([1,1])
            with col_a:
                if st.button("Submit answer →", type="primary", use_container_width=True, disabled=not choice):
                    correct = choice == q["answer"]
                    st.session_state.round_answers.append({"prompt":q["prompt"],"topic":q["topic"],"chosen":choice,"answer":q["answer"],"correct":correct,"explanation":q["explanation"]})
                    st.session_state.used_questions.add(q["prompt"])
                    st.session_state.total_answered += 1
                    st.session_state.total_correct += int(correct)
                    st.session_state.pending_feedback = {"correct":correct,"choice":choice,"answer":q["answer"],"explanation":q["explanation"]}
                    st.rerun()
            with col_b:
                if st.button("End round", use_container_width=True):
                    st.session_state.round_index = len(qs)
                    st.session_state.pending_feedback = None
                    st.rerun()
    else:
        answers = st.session_state.round_answers
        correct_n = sum(a["correct"] for a in answers)
        total_n = len(answers)
        st.markdown("---")
        st.subheader("Round complete ✦")
        st.markdown(f"### {correct_n} / {total_n} correct")
        if total_n:
            st.progress(correct_n/total_n, text=f"{round(100*correct_n/total_n)}% round accuracy")
        if not st.session_state.get("round_saved", False):
            save_attempt(topic, difficulty, correct_n, total_n, time.time()-st.session_state.round_started)
            st.session_state.round_saved = True
        with st.expander("Review answers", expanded=True):
            for i,a in enumerate(answers,1):
                st.markdown(f"**{i}. {a['prompt']}**")
                st.write(("✓" if a["correct"] else "✗") + f" Your answer: {a['chosen']}")
                if not a["correct"]:
                    st.write(f"Correct answer: **{a['answer']}**")
                st.caption(a["explanation"])
        col1,col2=st.columns(2)
        with col1:
            if st.button("↻ Forge another round",type="primary",use_container_width=True):
                reset_round()
                st.rerun()
        with col2:
            report = {"app":"QuizForge","topic":topic,"difficulty":difficulty,"correct":correct_n,"total":total_n,"answers":answers}
            st.download_button("Export round as JSON",json.dumps(report,indent=2),file_name="quizforge-round.json",mime="application/json",use_container_width=True)

st.markdown("---")
with st.expander("Recent session history"):
    rows = history()
    if rows:
        for played, t, d, c, n, secs in rows[:20]:
            st.write(f"**{time.strftime('%d %b %Y · %H:%M', time.localtime(played))}** · {t} · {d} · {c}/{n} · {round(secs)} sec")
    else:
        st.caption("No sessions saved yet.")
st.markdown("<div style='text-align:center;padding:30px 0 8px;color:#9aa5b8'>Made with love 💙 by <b style='color:#edf0f7'>VIPIN</b></div>", unsafe_allow_html=True)
