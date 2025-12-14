from flask import Flask, render_template, request, redirect, url_for, session
from math import ceil
from decimal import Decimal, ROUND_HALF_UP

app = Flask(__name__)
app.secret_key = "love_language_super_secret_key"

# ================== DATA PERTANYAAN ==================
questions = [
    ("Saya merasa dihargai ketika mendapat pujian yang tulus.", "G01", "L1", 0.90),
    ("Kata-kata yang mendukung membuat saya merasa dicintai.", "G02", "L1", 0.85),
    ("Ucapan sederhana seperti 'aku bangga padamu' sangat berarti bagi saya.", "G03", "L1", 0.75),
    ("Saya merasa sakit hati jika kata-kata yang diucapkan tidak dijaga.", "G04", "L1", 0.70),
    ("Saya senang ketika seseorang mengucapkan terima kasih atas hal yang saya lakukan.", "G05", "L1", 0.55),
    ("Pesan apresiasi membuat saya merasa lebih dekat.", "G06", "L1", 0.60),
    ("Saya termotivasi ketika diberi semangat verbal.", "G07", "L1", 0.75),
    ("Mendengar perasaan disampaikan langsung membuat saya spesial.", "G08", "L1", 0.50),

    ("Saya merasa dicintai lewat bantuan nyata.", "G09", "L2", 0.90),
    ("Tindakan lebih bermakna dari kata-kata.", "G10", "L2", 0.85),
    ("Bantuan kecil membuat saya dihargai.", "G11", "L2", 0.80),
    ("Inisiatif membantu membuat saya senang.", "G12", "L2", 0.75),
    ("Melihat usaha seseorang terasa bermakna.", "G13", "L2", 0.85),
    ("Saya merasa diperhatikan saat dibantu.", "G14", "L2", 0.60),
    ("Saya mengekspresikan kasih lewat bantuan.", "G15", "L2", 0.80),
    ("Bantuan meringankan beban saya.", "G16", "L2", 0.55),

    ("Saya merasa dicintai lewat hadiah.", "G17", "L3", 0.90),
    ("Hadiah kecil membuat saya tersentuh.", "G18", "L3", 0.85),
    ("Kejutan sederhana memperbaiki hari saya.", "G19", "L3", 0.75),
    ("Hadiah menunjukkan perhatian.", "G20", "L3", 0.65),
    ("Menerima sesuatu yang saya suka berarti.", "G21", "L3", 0.80),
    ("Saya kecewa jika momen hadiah diabaikan.", "G22", "L3", 0.60),
    ("Hadiah simbol kasih sayang.", "G23", "L3", 0.75),
    ("Saya senang kejutan sesuai preferensi.", "G24", "L3", 0.70),

    ("Saya merasa dicintai lewat waktu.", "G25", "L4", 0.90),
    ("Waktu bersama lebih penting.", "G26", "L4", 0.85),
    ("Percakapan mendalam membuat dekat.", "G27", "L4", 0.80),
    ("Saya merasa diabaikan jika tak fokus.", "G28", "L4", 0.75),
    ("Aktivitas sederhana memperkuat hubungan.", "G29", "L4", 0.70),
    ("Waktu khusus membuat saya penting.", "G30", "L4", 0.65),
    ("Kehadiran membuat saya aman.", "G31", "L4", 0.55),
    ("Meluangkan waktu khusus berarti.", "G32", "L4", 0.75),

    ("Saya nyaman dengan sentuhan fisik.", "G33", "L5", 0.90),
    ("Pelukan membuat saya aman.", "G34", "L5", 0.85),
    ("Gestur fisik membuat saya dekat.", "G35", "L5", 0.80),
    ("Saya nyaman menunjukkan kedekatan.", "G36", "L5", 0.75),
    ("Sentuhan lembut berarti bagi saya.", "G37", "L5", 0.70),
    ("Kedekatan fisik membuat terhubung.", "G38", "L5", 0.75),
    ("Kasih lewat sentuhan terasa nyata.", "G39", "L5", 0.65),
    ("Pelukan menenangkan saat sedih.", "G40", "L5", 0.60),
]

# ================== CF USER ==================
user_cf_map = {
    "Tidak": 0.0,
    "Mungkin Tidak": 0.2,
    "Tidak Tahu": 0.5,
    "Mungkin": 0.8,
    "Iya": 1.0
}

PAGE_SIZE = 5

# ================== ROUTES ==================
@app.route("/")
def home():
    session.clear()
    return render_template("home.html")

@app.route("/questions/<int:page>", methods=["GET", "POST"])
def questions_page(page):
    total_q = len(questions)
    total_pages = ceil(total_q / PAGE_SIZE)
    start = (page - 1) * PAGE_SIZE
    end = min(start + PAGE_SIZE, total_q)

    page_items = []
    for i in range(start, end):
        page_items.append({
            "index": i,
            "text": questions[i][0]
        })

    if request.method == "POST":
        answers = session.get("answers", {})
        for item in page_items:
            answers[str(item["index"])] = request.form.get(
                f"q{item['index']}", "Tidak Tahu"
            )
        session["answers"] = answers

        if end >= total_q:
            return redirect(url_for("result"))
        return redirect(url_for("questions_page", page=page + 1))

    return render_template(
        "questions.html",
        page_items=page_items,
        start=start,
        page=page,
        total_pages=total_pages
    )

@app.route("/result")
def result():
    answers = session.get("answers", {})

    # ===== VALIDASI JAWABAN SERAGAM =====
    unique_answers = set(answers.values())
    if len(unique_answers) <= 1:
        return render_template("result_invalid.html")

    # ===== HITUNG CF =====
    cf_cat = {f"L{i}": [] for i in range(1, 6)}

    for idx_str, ans in answers.items():
        idx = int(idx_str)
        _, _, cat, cf_pakar = questions[idx]
        cf_user = user_cf_map.get(ans, 0.5)
        cf_cat[cat].append(cf_user * cf_pakar)

    def cf_combine(lst):
        if not lst:
            return 0
        res = lst[0]
        for cf in lst[1:]:
            res = res + cf * (1 - res)
        return res

    final_cf = {k: cf_combine(v) for k, v in cf_cat.items()}

    # ===== VALIDASI TIDAK ADA DOMINAN =====
    max_cf = max(final_cf.values())
    min_cf = min(final_cf.values())
    if abs(max_cf - min_cf) < 0.05:
        return render_template("result_invalid.html")

    # ===== NORMALISASI =====
    total = sum(final_cf.values())
    perc = {
        k: float(
            (Decimal(str(v / total * 100)))
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        for k, v in final_cf.items()
    }

    names = {
        "L1": "Words of Affirmation",
        "L2": "Acts of Service",
        "L3": "Receiving Gifts",
        "L4": "Quality Time",
        "L5": "Physical Touch"
    }

    descriptions = {
        "L1": "Kamu merasa paling diterima lewat kata-kata.",
        "L2": "Kamu merasa dicintai lewat tindakan nyata.",
        "L3": "Kamu merasa diperhatikan lewat hadiah.",
        "L4": "Kamu merasa dekat lewat waktu berkualitas.",
        "L5": "Kamu merasa terhubung lewat sentuhan fisik."
    }

    dominant_cat = max(perc, key=perc.get)

    return render_template(
        "result.html",
        perc=perc,
        dominant_cat=dominant_cat,
        dominant_name=names[dominant_cat],
        descriptions=descriptions
    )

if __name__ == "__main__":
    app.run(debug=True)
