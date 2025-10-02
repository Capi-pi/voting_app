import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from generate_ids import load_ids

# ------------- Generate unique ids -------------------
generated_ids = load_ids("ids.csv")

# -------------- Load .env variables ---------------
load_dotenv()

# ------set up and configuration-------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change_this_secret_in_prod")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///votes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- Model of vote ---
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(128), nullable=False)
    post = db.Column(db.String(64), nullable=False)
    candidate = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    __table_args__ = (db.UniqueConstraint('student_id', 'post', name='u_student_post'),)

# --- Posts and Candidates ---
POSTS = [
    "présidente",
    "vice_président(e)",
    "responsable_organisation",
    "adjoint_organisation",
    "secrétaire",
    "adjoint_secrétaire",
    "responsable_communication",
    "adjoint_communication",
    "responsable_trésorerie",
    "adjoint_trésorerie",
    "responsable_relations_extérieures",
    "adjoint_relations_extérieures",
    "responsable_sport",
    "adjoint_sport"
]

CANDIDATS = {
    "présidente": [
        {"value": "ngone", "label": "Ngoné Anne Pouye 2A", "image": "../static/images/president/ngone.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "nekhou", "label": "Aminata Nekhou 2B", "image": "../static/images/president/nekhou.jpeg"},
    ],
    "vice_président(e)": [
        {"value": "alioune", "label": "Alioune Ibrahima Dieng 1B", "image": "../static/images/vice_president/alioune.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "awa", "label": "Ndeye Awa Mar 1A", "image": "../static/images/vice_president/awa.jpeg"},
    ],
    "responsable_organisation": [
        {"value": "salimata", "label": "Mame Salimata Gueye 2A", "image": "../static/images/responsable_organisation/salimata.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "arame", "label": "Arame Diagne 2B", "image": "../static/images/responsable_organisation/arame.jpeg"},
    ],
    "adjoint_organisation": [
        {"value": "aida", "label": "Aida Niang 1A", "image": "../static/images/adjoint_organisation/aida.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "maroufa", "label": "Maroufa 1B", "image": "../static/images/adjoint_organisation/maroufa.jpeg"},
    ],
    "secrétaire": [
        {"value": "fatou", "label": "Fatou Kiné Basse 2A", "image": "../static/images/secretaire/fatou.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "roseline", "label": "Roseline Wonou 2B", "image": "../static/images/secretaire/roseline.jpeg"},
    ],
    "adjoint_secrétaire": [
        {"value": "assietou", "label": "Ndeye Assietou Diouf 1A", "image": "../static/images/adjoint_secretaire/assietou.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "bakary", "label": "Bakary 1B", "image": "../static/images/adjoint_secretaire/bakary.jpeg"},
    ],
    "responsable_communication": [
        {"value": "yaye", "label": "Yaye Aminatou Ndiaye 2A", "image": "../static/images/responsable_communication/yaye.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
    ],
    "adjoint_communication": [
        {"value": "adama", "label": "Adama Gueye 1A", "image": "../static/images/adjoint_communication/adama.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "aby", "label": "Aby Dieye Fall 1B", "image": "../static/images/adjoint_communication/aby.jpeg"},
    ],
    "responsable_trésorerie": [
        {"value": "marieme", "label": "Marieme Seck Fall 2A", "image": "../static/images/responsable_tresorerie/marieme.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "diari", "label": "Diari Koursoum Wane 2B", "image": "../static/images/responsable_tresorerie/diari.jpeg"},
    ],
    "adjoint_trésorerie": [
        {"value": "marietou", "label": "Mariétou SALL 1B", "image": "../static/images/adjoint_tresorerie/marietou.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
    ],
    "responsable_relations_extérieures": [
        {"value": "seyni", "label": "Ndeye Fatou Seyni Ndaw 2A", "image": "../static/images/responsable_relations_exterieures/seyni.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "badara", "label": "Alioune Badara Niang 2B", "image": "../static/images/responsable_relations_exterieures/badara.jpeg"},
    ],
    "adjoint_relations_extérieures": [
        {"value": "zeynab", "label": "Zeynab 1B", "image": "../static/images/adjoint_relations_exterieures/zeynab.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "oceanne", "label": "Océanne Grâce Esther Ouattara 1A", "image": "../static/images/adjoint_relations_exterieures/oceanne.jpeg"}
    ],
    "responsable_sport": [
        {"value": "babacar", "label": "Mbaye Babacar Ndiaye Faye 2A", "image": "../static/images/responsable_sport/babacar.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
    ],
    "adjoint_sport": [
        {"value": "radji", "label": "Radji Mohanad 1B", "image": "../static/images/adjoint_sport/radji.jpeg"},
        {"value": "vote-blanc", "label": "Vote Blanc", "image": "../static/images/vote-blanc.png"},
        {"value": "lamine", "label": "Lamine Gueye 1B", "image": "../static/images/adjoint_sport/lamine.jpeg"},
    ],
}



# --- DB init + WAL ---
with app.app_context():
    db.create_all()
    # Improve concurrent writes in SQLite
    try:
        db.session.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass

# --- Helpers ---
def require_login():
    if "student_id" not in session:
        return False
    return True

def require_admin():
    return session.get("is_admin", False)

# --- Routes ---
@app.route("/", methods=["GET"])
def root():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    # GET -> render login, POST -> set session student_id and redirect to /vote
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        if not student_id:
            return render_template("login.html", error="Identifiant requis")
        elif student_id not in generated_ids:
            return render_template("login.html", error="Identifiant incorrect")
        session.clear()
        session["student_id"] = student_id
        return redirect(url_for("vote"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/vote")
def vote():
    # Page unique qui héberge le JS et le flow client-side
    if not require_login():
        return redirect(url_for("login"))
    return render_template("vote.html", posts=POSTS, candidats=CANDIDATS)

@app.route("/confirm")
def confirm():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("confirm.html")

# API: poster un vote pour un post donné (JSON)
@app.route("/api/vote", methods=["POST"])
def api_vote():
    if not require_login():
        return jsonify({"ok": False, "error": "not_logged"}), 401

    data = request.get_json() or {}
    post = data.get("post")
    candidate = data.get("candidate")
    student_id = session["student_id"]

    if post not in POSTS or not candidate:
        return jsonify({"ok": False, "error": "bad_request"}), 400

    v = Vote(student_id=student_id, post=post, candidate=candidate)
    try:
        db.session.add(v)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"ok": False, "error": "already_voted"}), 409

    # déterminer le post suivant
    idx = POSTS.index(post)
    if idx + 1 < len(POSTS):
        next_post = POSTS[idx+1]
        return jsonify({"ok": True, "next": next_post})
    else:
        return jsonify({"ok": True, "done": True})

# Admin login
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd and pwd == os.environ.get("ADMIN_PASSWORD", "adminpass"):
            session["is_admin"] = True
            return redirect(url_for("admin"))
        return render_template("admin_login.html", error="Mauvais mot de passe")
    return render_template("admin_login.html")

@app.route("/admin")
def admin():
    if not require_admin():
        return redirect(url_for("admin_login"))
    # Résultats agrégés
    rows = db.session.query(Vote.post, Vote.candidate, db.func.count(Vote.id)).group_by(Vote.post, Vote.candidate).all()
    # transform to dict {post: [(candidate, count), ...], ...}
    results = {}
    for post, candidate, count in rows:
        results.setdefault(post, []).append((candidate, count))
    votes = Vote.query.order_by(Vote.timestamp.desc()).all()
    return render_template("admin.html", results=results, votes=votes)

""" @app.route("/admin")
def admin():
    if not require_admin():
        return redirect(url_for("admin_login"))

    # Résultats agrégés (post, candidate, count)
    rows = db.session.query(Vote.post, Vote.candidate, db.func.count(Vote.id)) \
                    .group_by(Vote.post, Vote.candidate).all()

    # transform to dict {post: [(candidate, count), ...], ...}
    results = {}
    for post, candidate, count in rows:
        results.setdefault(post, []).append((candidate, int(count)))

    # Préparer une version sérialisable pour JS: {post: [{candidate, count}, ...], ...}
    results_js = {}
    for post, rows in results.items():
        results_js[post] = [{"candidate": cand, "count": cnt} for (cand, cnt) in rows]

    votes = Vote.query.order_by(Vote.timestamp.desc()).all()
    return render_template("admin.html",
                           results=results,
                           votes=votes,
                           results_js=results_js) """


# Export CSV simple
@app.route("/export_csv")
def export_csv():
    if not require_admin():
        return redirect(url_for("admin_login"))
    import csv
    from io import StringIO
    si = StringIO()
    w = csv.writer(si)
    w.writerow(["student_id","post","candidate","timestamp"])
    for v in Vote.query.order_by(Vote.timestamp):
        w.writerow([v.student_id, v.post, v.candidate, v.timestamp])
    output = si.getvalue()
    return app.response_class(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=votes.csv"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
