import math

from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "projectguru-secret"

QUESTIONS = [
    {"text": "I often feel stressed by day-to-day responsibilities.", "category": "Stress", "reverse": False},
    {"text": "I feel mentally drained after a normal work or study day.", "category": "Stress", "reverse": False},
    {"text": "I struggle to switch off and relax after work or school.", "category": "Stress", "reverse": False},
    {"text": "I feel worried or uneasy without a clear reason.", "category": "Anxiety", "reverse": False},
    {"text": "I find it hard to calm my mind when things feel intense.", "category": "Anxiety", "reverse": False},
    {"text": "I often feel low, sad, or emotionally flat.", "category": "Depression", "reverse": False},
    {"text": "I have little motivation for activities I usually enjoy.", "category": "Depression", "reverse": False},
    {"text": "My sleep quality has been poor recently.", "category": "Sleep", "reverse": False},
    {"text": "I wake up tired even after enough time in bed.", "category": "Sleep", "reverse": False},
    {"text": "I feel disconnected from other people lately.", "category": "Social", "reverse": False},
    {"text": "I avoid social interactions because I feel overwhelmed.", "category": "Social", "reverse": False},
]

MOOD_EMOJIS = {
    "Great": "😊",
    "Okay": "😐",
    "Low": "😔",
    "Overwhelmed": "😰",
}


def get_age_category(age):
    age = int(age)
    if age < 18:
        return "Youth"
    if age < 35:
        return "Young Adult"
    if age < 60:
        return "Adult"
    return "Senior"


def pct_bar_class(pct):
    if pct < 35:
        return "bg-green"
    if pct < 60:
        return "bg-yellow"
    return "bg-red"


def state_bar_class(state):
    if "Healthy" in state:
        return "bg-green"
    if "Mild" in state:
        return "bg-yellow"
    if "Moderate" in state:
        return "bg-orange"
    if "High" in state:
        return "bg-red"
    return "bg-indigo"


def render_page(content):
    shell = """
    <!doctype html>
    <html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>ProjectGuru</title>
        <style>
            :root { color-scheme: dark; --bg:#07111f; --panel:#112235; --line:#22364c; --text:#eff6ff; --muted:#b8c7db; --green:#22c55e; --yellow:#facc15; --orange:#fb923c; --red:#f87171; --sky:#38bdf8; }
            * { box-sizing: border-box; font-family: Arial, Helvetica, sans-serif; }
            body { margin:0; background:linear-gradient(135deg,#07111f 0%,#0f172a 100%); color:var(--text); }
            a { text-decoration:none; color:inherit; }
            .page { max-width: 1100px; margin: 0 auto; padding: 24px; }
            .hero, .card { background: rgba(17, 34, 53, 0.92); border:1px solid var(--line); border-radius: 18px; box-shadow: 0 18px 36px rgba(0,0,0,0.25); }
            .hero { padding: 28px; margin-bottom: 18px; }
            .title { font-size: 2rem; margin: 0 0 8px; }
            .subtitle { color: var(--muted); line-height: 1.5; }
            .card { padding: 18px; margin-bottom: 16px; }
            .btn { display:inline-block; border-radius: 12px; padding: 10px 14px; border:1px solid var(--line); background:#172c41; color:var(--text); cursor:pointer; }
            .btn-primary { background: linear-gradient(135deg,#2563eb,#38bdf8); border-color: transparent; }
            .btn-secondary { background: #14283a; }
            .form-group { margin-bottom: 14px; }
            .form-label { display:block; margin-bottom:6px; color: var(--muted); font-weight: 700; }
            .form-input { width:100%; border-radius: 10px; border:1px solid var(--line); background:#0b1622; color:var(--text); padding:10px 12px; }
            .radio-group-horizontal, .radio-group-vertical { display:grid; gap:10px; }
            .radio-group-horizontal { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
            .radio-card { display:flex; align-items:center; gap:10px; border:1px solid var(--line); border-radius: 12px; padding: 10px; background:#102032; }
            .radio-card input { accent-color: var(--sky); }
            .badge { display:inline-block; border-radius:999px; padding:4px 8px; font-size:12px; font-weight:700; }
            .badge-sky { background: rgba(56,189,248,0.15); color:#bae6fd; }
            .bar-outer { width:100%; height:8px; background:#183247; border-radius:999px; overflow:hidden; }
            .bar-inner { height:100%; border-radius:999px; }
            .bg-green { background: var(--green); }
            .bg-yellow { background: var(--yellow); }
            .bg-orange { background: var(--orange); }
            .bg-red { background: var(--red); }
            .bg-indigo { background: #818cf8; }
            .metrics { display:grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap:12px; }
            .metric-box { border:1px solid var(--line); border-radius:14px; background:#0d1a29; padding:12px; }
            .metric-label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .12em; }
            .metric-value { font-size: 1.5rem; font-weight: 700; margin-top: 6px; }
            .form-error { color: #fecaca; font-size: 0.95rem; }
        </style>
    </head>
    <body>
        <main class=\"page\">"""
    footer = """
        </main>
    </body>
    </html>
    """
    return render_template_string(shell + content + footer)


@app.route("/")
def index():
    content = """
    <section class=\"hero\">
        <h1 class=\"title\">ProjectGuru</h1>
        <p class=\"subtitle\">A simple mental wellness intake, quiz, and results experience. Start by entering your profile details.</p>
        <p><a class=\"btn btn-primary\" href=\"/intake\">Start Assessment</a></p>
    </section>
    """
    return render_page(content)


@app.route("/intake", methods=["GET", "POST"])
def intake():
    errors = {}
    profile = session.get("profile", {})
    name = profile.get("name", "")
    age = profile.get("age", "")
    gender = profile.get("gender", "")
    situation = profile.get("situation", "Student")
    mood = profile.get("mood", "")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age_str = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        situation = request.form.get("situation", "Student").strip()
        mood = request.form.get("mood", "").strip()

        if not age_str.isdigit() or not (5 <= int(age_str) <= 100):
            errors["age"] = "Please enter a valid age between 5 and 100."
        if not gender:
            errors["gender"] = "Please select a gender."
        if not mood:
            errors["mood"] = "Please select your current mood."

        if not errors:
            session["profile"] = {"name": name, "age": int(age_str), "gender": gender, "situation": situation, "mood": mood}
            session["answers"] = {}
            session.modified = True
            return redirect(url_for("quiz", qnum=0))

    age_str = str(age) if age != "" else ""
    content = f"""
    <section class=\"hero\"><h1 class=\"title\">Your Profile</h1><p class=\"subtitle\">Complete the intake section to personalize the assessment.</p></section>
    <section class=\"card\">
        <form method=\"POST\" action=\"/intake\">
            <div class=\"form-group\"><label class=\"form-label\" for=\"name\">Full Name (optional)</label><input class=\"form-input\" type=\"text\" id=\"name\" name=\"name\" value=\"{name}\" placeholder=\"Enter name...\"></div>
            <div class=\"form-group\"><label class=\"form-label\" for=\"age\">Age (required)</label><input class=\"form-input\" type=\"number\" id=\"age\" name=\"age\" value=\"{age_str}\" placeholder=\"Enter age (5 - 100)...\">{"<span class='form-error'>⚠️ " + errors['age'] + "</span>" if 'age' in errors else ""}</div>
            <div class=\"form-group\"><label class=\"form-label\">Gender (required)</label><div class=\"radio-group-horizontal\"><label class=\"radio-card\"><input type=\"radio\" name=\"gender\" value=\"Male\" {('checked' if gender == 'Male' else '')}> <span>Male</span></label><label class=\"radio-card\"><input type=\"radio\" name=\"gender\" value=\"Female\" {('checked' if gender == 'Female' else '')}> <span>Female</span></label><label class=\"radio-card\"><input type=\"radio\" name=\"gender\" value=\"Prefer Not To Say\" {('checked' if gender == 'Prefer Not To Say' else '')}> <span>Prefer Not To Say</span></label></div>{"<span class='form-error'>⚠️ " + errors['gender'] + "</span>" if 'gender' in errors else ""}</div>
            <div class=\"form-group\"><label class=\"form-label\" for=\"situation\">Current Life Situation</label><select class=\"form-input\" id=\"situation\" name=\"situation\"><option value=\"Student\" {('selected' if situation == 'Student' else '')}>Student</option><option value=\"Working Professional\" {('selected' if situation == 'Working Professional' else '')}>Working Professional</option><option value=\"Homemaker\" {('selected' if situation == 'Homemaker' else '')}>Homemaker</option><option value=\"Unemployed\" {('selected' if situation == 'Unemployed' else '')}>Unemployed</option><option value=\"Retired\" {('selected' if situation == 'Retired' else '')}>Retired</option><option value=\"Other\" {('selected' if situation == 'Other' else '')}>Other</option></select></div>
            <div class=\"form-group\"><label class=\"form-label\">Current Mood right now (required)</label><div class=\"radio-group-horizontal\"><label class=\"radio-card\"><input type=\"radio\" name=\"mood\" value=\"Great\" {('checked' if mood == 'Great' else '')}> <span>😊 Great</span></label><label class=\"radio-card\"><input type=\"radio\" name=\"mood\" value=\"Okay\" {('checked' if mood == 'Okay' else '')}> <span>😐 Okay</span></label><label class=\"radio-card\"><input type=\"radio\" name=\"mood\" value=\"Low\" {('checked' if mood == 'Low' else '')}> <span>😔 Low</span></label><label class=\"radio-card\"><input type=\"radio\" name=\"mood\" value=\"Overwhelmed\" {('checked' if mood == 'Overwhelmed' else '')}> <span>😰 Overwhelmed</span></label></div>{"<span class='form-error'>⚠️ " + errors['mood'] + "</span>" if 'mood' in errors else ""}</div>
            <div class=\"form-group\"><button type=\"submit\" class=\"btn btn-primary\">Start Assessment →</button></div>
        </form>
    </section>
    """
    return render_page(content)


@app.route("/quiz/<int:qnum>", methods=["GET", "POST"])
def quiz(qnum):
    if "profile" not in session:
        return redirect(url_for("intake"))
    if qnum < 0 or qnum >= len(QUESTIONS):
        return redirect(url_for("intake"))

    question = QUESTIONS[qnum]
    saved_answer = session.get("answers", {}).get(str(qnum))
    error = ""

    if request.method == "POST":
        answer_str = request.form.get("answer")
        if answer_str is None:
            error = "Please select an option to continue."
        else:
            answers = dict(session.get("answers", {}))
            answers[str(qnum)] = int(answer_str)
            session["answers"] = answers
            session.modified = True
            if qnum == len(QUESTIONS) - 1:
                return redirect(url_for("results"))
            return redirect(url_for("quiz", qnum=qnum + 1))

    options = [(0, "Never"), (1, "Rarely"), (2, "Sometimes"), (3, "Often"), (4, "Always")]
    if question.get("reverse"):
        options = [(0, "Always"), (1, "Often"), (2, "Sometimes"), (3, "Rarely"), (4, "Never")]

    radio_choices_html = "".join(
        f"<label class=\"radio-card\"><input type=\"radio\" name=\"answer\" value=\"{score}\" {'checked' if saved_answer == score else ''}> <span>{label}</span></label>"
        for score, label in options
    )

    back_url = url_for("quiz", qnum=qnum - 1) if qnum > 0 else url_for("intake")
    content = f"""
    <section class=\"hero\"><h1 class=\"title\">Question {qnum + 1} of {len(QUESTIONS)}</h1><p class=\"subtitle\">{question['text']}</p></section>
    <section class=\"card\"><form method=\"POST\" action=\"/quiz/{qnum}\"><div class=\"radio-group-vertical\">{radio_choices_html}</div>{f"<p class='form-error'>⚠️ {error}</p>" if error else ""}<div style=\"display:flex; justify-content:space-between; gap:12px; margin-top:14px;\"><a class=\"btn btn-secondary\" href=\"{back_url}\">← Back</a><button class=\"btn btn-primary\" type=\"submit\">{'View Results' if qnum == len(QUESTIONS)-1 else 'Next Question →'}</button></div></form></section>
    """
    return render_page(content)


@app.route("/results")
def results():
    profile = session.get("profile")
    answers = session.get("answers")
    if not profile or not answers or len(answers) < len(QUESTIONS):
        return redirect(url_for("index"))

    stress_val = sum(int(answers.get(str(i), 0)) for i in (0, 1, 2))
    anxiety_val = sum(int(answers.get(str(i), 0)) for i in (3, 4))
    depression_val = sum(int(answers.get(str(i), 0)) for i in (5, 6))
    sleep_val = sum(int(answers.get(str(i), 0)) for i in (7, 8))
    social_val = sum(int(answers.get(str(i), 0)) for i in (9, 10))

    stress_pct = round((stress_val / 12.0) * 100)
    anxiety_pct = round((anxiety_val / 8.0) * 100)
    depression_pct = round((depression_val / 8.0) * 100)
    sleep_pct = round((sleep_val / 8.0) * 100)
    social_pct = round((social_val / 8.0) * 100)

    category_scores = {"Stress": stress_pct, "Anxiety": anxiety_pct, "Depression": depression_pct, "Sleep": sleep_pct, "Social": social_pct}
    avg_risk = sum(category_scores.values()) / 5.0
    wellness_score = max(0, min(100, round(100.0 - avg_risk)))

    age = profile["age"]
    age_cat = get_age_category(age)
    name = profile["name"] or "there"
    gender = profile["gender"]
    situation = profile["situation"]
    mood = MOOD_EMOJIS.get(profile["mood"], profile["mood"])

    priors = {"Healthy": 0.35, "Mild Stress": 0.30, "Moderate Stress": 0.20, "High Stress": 0.10, "Burnout Risk": 0.05}
    centers = {"Healthy": 10, "Mild Stress": 30, "Moderate Stress": 50, "High Stress": 70, "Burnout Risk": 90}
    sigma = 15.0
    posteriors = {}
    total = 0.0
    for state, prior in priors.items():
        likelihood = math.exp(-((avg_risk - centers[state]) ** 2) / (2 * (sigma ** 2)))
        unnorm = prior * likelihood
        posteriors[state] = unnorm
        total += unnorm
    normalized = {k: round((v / total) * 100, 1) for k, v in posteriors.items()} if total else {k: 0.0 for k in priors}
    diff = round(100.0 - sum(normalized.values()), 1)
    if diff:
        max_state = max(normalized, key=normalized.get)
        normalized[max_state] = round(normalized[max_state] + diff, 1)
    today_state = max(normalized, key=normalized.get)

    reasons = []
    if stress_pct >= 60:
        reasons.append("High stress responses detected across multiple questions")
    if sleep_pct >= 50:
        reasons.append("Poor sleep quality signals detected")
    if social_pct >= 50:
        reasons.append("Reduced social engagement observed")
    if anxiety_pct >= 50:
        reasons.append("Anxiety indicators above baseline threshold")
    if depression_pct >= 50:
        reasons.append("Low mood or anhedonia signals present")
    if not reasons:
        reasons.append("Overall scores indicate a well-balanced mental state")

    top_remedies = ["Meditation", "Walking", "Deep Breathing"]
    primary_issue = "Stress" if stress_pct >= anxiety_pct else "Anxiety"
    goal = "Calm" if primary_issue == "Stress" else "Relaxed"

    category_rows = "".join(
        f"<div class='metric-box'><div class='metric-label'>{label}</div><div class='metric-value'>{pct}%</div><div class='bar-outer'><div class='bar-inner {pct_bar_class(pct)}' style='width:{pct}%'></div></div></div>"
        for label, pct in category_scores.items()
    )

    content = f"""
    <section class=\"hero\"><h1 class=\"title\">Hello, {name}!</h1><p class=\"subtitle\">Your mental wellness summary is ready. Here are the results based on your responses.</p></section>
    <section class=\"card\"><div class=\"badge badge-sky\">{age_cat} Badge</div><div class=\"metrics\" style=\"margin-top:12px;\"><div class=\"metric-box\"><div class=\"metric-label\">Age</div><div class=\"metric-value\">{age}</div></div><div class=\"metric-box\"><div class=\"metric-label\">Gender</div><div class=\"metric-value\">{gender}</div></div><div class=\"metric-box\"><div class=\"metric-label\">Situation</div><div class=\"metric-value\">{situation}</div></div><div class=\"metric-box\"><div class=\"metric-label\">Mood</div><div class=\"metric-value\">{mood}</div></div></div></section>
    <section class=\"card\"><h2 style=\"margin-top:0;\">Assessment Summary</h2><div class=\"metric-box\"><div class=\"metric-label\">Overall Wellness Baseline</div><div class=\"metric-value\">{wellness_score}%</div><div class=\"bar-outer\"><div class=\"bar-inner bg-green\" style=\"width:{wellness_score}%\"></div></div></div><div class=\"metrics\" style=\"margin-top:12px;\">{category_rows}</div></section>
    <section class=\"card\"><h2 style=\"margin-top:0;\">Bayesian State</h2><p class=\"subtitle\">Today's most likely state is <strong>{today_state}</strong>.</p>{''.join(f'<div class=\"metric-box\" style=\"margin-top:8px;\"><div class=\"metric-label\">{state}</div><div class=\"metric-value\">{pct}%</div><div class=\"bar-outer\"><div class=\"bar-inner {state_bar_class(state)}\" style=\"width:{pct}%\"></div></div></div>' for state, pct in normalized.items())}</section>
    <section class=\"card\"><h2 style=\"margin-top:0;\">Why this result?</h2><ul>{''.join(f'<li>{r}</li>' for r in reasons)}</ul></section>
    <section class=\"card\"><h2 style=\"margin-top:0;\">Recommended Plan</h2><p class=\"subtitle\">Primary concern: {primary_issue}. Target goal: {goal}.</p><p>Try {', '.join(top_remedies)} for your next routine.</p></section>
    <section class=\"card\"><a class=\"btn btn-secondary\" href=\"/intake\">Start Over</a></section>
    """
    return render_page(content)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
