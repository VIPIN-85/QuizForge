# QuizForge ✦ — Infinite Quiz Studio

**Pick a topic. Tune the difficulty. Keep learning.** A minimalist, customizable quiz game built with Python and Streamlit, with local progress history and a curated question bank.

> Made with love 💙 by VIPIN

## Features
- 12 topics: Python, Computer Science, AI & Machine Learning, Mathematics, Science, World History, Geography, General Knowledge, English, Cybersecurity, Web Development, and Logical Reasoning.
- Difficulty selection, round length, optional answer shuffling, hint toggle, and feedback preferences.
- Round summaries with answer review and JSON export.
- Local SQLite session history and simple lifetime accuracy stats.
- Custom question import using a simple text format.
- Question rotation without repeats until the available pool is exhausted.
- Dark, responsive interface designed for desktop and mobile.
- No account, API key, or external AI service required.

## Quick start — Windows + VS Code

### 1. Install Python
Install Python 3.11 or newer from https://www.python.org/downloads/ . During setup, enable **Add Python to PATH**.

### 2. Extract and open
1. Download `QuizForge.zip` and extract it.
2. Open VS Code.
3. Choose **File → Open Folder** and select the extracted `QuizForge` folder.

### 3. Create a virtual environment
Open **Terminal → New Terminal** in VS Code, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt terminal and run:

```bat
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Launch the app

```bash
streamlit run app.py
```

Your browser should open automatically. If it does not, open the local URL printed in the terminal (usually `http://localhost:8501`).

## Custom question format
Paste one question per line into the optional custom question box:

```text
What is 2 + 2? | 3 | 4 | 5 | 6 | 4 | Adding two and two gives four.
```

Fields: `question | option A | option B | option C | option D | exact correct option text | explanation`

The correct answer must match one of the four option strings exactly. Avoid using `|` inside a field.

## Project structure

```text
QuizForge/
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── quizforge/
│   └── .gitkeep
└── tests/
    └── test_question_bank.py
```

## Python libraries included
- **Streamlit** — interactive application UI.
- **Pandas** — useful for future score analysis and exports.
- **NumPy** — useful for future randomized practice and analytics.
- **Plotly** — useful for future interactive charts.
- **scikit-learn** — optional foundation for future topic/recommendation experiments.
- **pytest** — test runner for question-bank validation.
- **SQLite** (Python standard library) — local session history.
- `json`, `random`, `re`, `dataclasses`, `pathlib`, and `time` — standard-library utilities.

The starter keeps some libraries ready for meaningful next features; it does not pretend every dependency is already used in the core flow.

## Current limits — be honest
- “Infinite” means repeatable sessions and rotating questions, not infinite original facts. The built-in bank is finite; add custom questions or contribute new reviewed questions to grow it.
- The timed challenge currently configures a time-per-question target but does not enforce a countdown. Countdown enforcement is a roadmap item.
- Hints currently use a general reasoning cue rather than a unique per-question hint.
- This is a learning project, not an exam-certification platform. Check facts and explanations before using it for high-stakes assessments.

## Roadmap
- [ ] Add a real countdown timer with auto-submit
- [ ] Expand the question bank with reviewed contributions
- [ ] Add adaptive difficulty based on performance
- [ ] Add spaced-repetition review for missed questions
- [ ] Add question editor and CSV import/export
- [ ] Add per-topic charts with Plotly
- [ ] Add unit tests for session flow and custom imports
- [ ] Add accessible keyboard-first controls and multilingual UI

## License
MIT. See `LICENSE`.

## Contributing
Open an issue for bugs or feature proposals. For question contributions, include a reliable source when the fact may change, one unambiguous answer, plausible distractors, and a concise explanation.
