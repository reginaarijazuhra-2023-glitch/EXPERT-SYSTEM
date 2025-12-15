from flask import Flask, render_template, request, redirect, url_for, session
from math import ceil
from decimal import Decimal, getcontext

# =======================
# KONFIGURASI
# =======================
getcontext().prec = 28

app = Flask(__name__)
app.secret_key = "love_language_super_secret_key"

PAGE_SIZE = 5

# =======================
# DATA PERTANYAAN
# =======================
questions = [
    ("Saya merasa dihargai ketika mendapat pujian yang tulus.", "G01", "L1", Decimal("0.90")),
    ("Kata-kata yang mendukung membuat saya merasa dicintai.", "G02", "L1", Decimal("0.85")),
    ("Ucapan sederhana seperti 'aku bangga padamu' sangat berarti bagi saya.", "G03", "L1", Decimal("0.75")),
    ("Saya merasa sakit hati jika kata-kata yang diucapkan tidak dijaga.", "G04", "L1", Decimal("0.70")),
    ("Saya senang ketika seseorang mengucapkan terima kasih atas hal yang saya lakukan.", "G05", "L1", Decimal("0.55")),
    ("Pesan atau chat berisi apresiasi membuat saya merasa lebih dekat.", "G06", "L1", Decimal("0.60")),
    ("Saya termotivasi ketika orang memberi semangat secara verbal.", "G07", "L1", Decimal("0.75")),
    ("Mendengar seseorang menyampaikan perasaan mereka secara langsung membuat saya merasa spesial.", "G08", "L1", Decimal("0.50")),

    ("Saya merasa diperhatikan ketika seseorang membantu menyelesaikan hal yang saya sulitkan.", "G09", "L2", Decimal("0.90")),
    ("Saya merasa dicintai melalui tindakan nyata, bukan hanya kata-kata.", "G10", "L2", Decimal("0.85")),
    ("Bantuan kecil tanpa diminta membuat saya merasa dihargai.", "G11", "L2", Decimal("0.80")),
    ("Saya senang ketika seseorang mengambil inisiatif membantu saya.", "G12", "L2", Decimal("0.75")),
    ("Melihat seseorang melakukan sesuatu untuk saya terasa lebih bermakna daripada ucapan.", "G13", "L2", Decimal("0.85")),
    ("Saya merasa diperhatikan ketika seseorang menyiapkan makanan atau kebutuhan saya.", "G14", "L2", Decimal("0.60")),
    ("Saya biasanya mengekspresikan kasih dengan membantu, bukan berbicara.", "G15", "L2", Decimal("0.80")),
    ("Saya merasa tenang ketika seseorang membantu meringankan beban saya.", "G16", "L2", Decimal("0.55")),

    ("Saya merasa dicintai ketika menerima hadiah yang bermakna.", "G17", "L3", Decimal("0.90")),
    ("Hadiah kecil yang dipilih dengan perhatian membuat saya tersentuh.", "G18", "L3", Decimal("0.85")),
    ("Kejutan sederhana dapat membuat hari saya jauh lebih baik.", "G19", "L3", Decimal("0.75")),
    ("Saya menghargai hadiah karena menunjukkan seseorang memikirkan saya.", "G20", "L3", Decimal("0.65")),
    ("Menerima sesuatu yang saya suka membuat saya merasa diperhatikan.", "G21", "L3", Decimal("0.80")),
    ("Saya kecewa jika momen pemberian hadiah yang penting diabaikan.", "G22", "L3", Decimal("0.60")),
    ("Saya melihat hadiah sebagai simbol perhatian dan kasih sayang.", "G23", "L3", Decimal("0.75")),
    ("Saya senang ketika seseorang mengingat preferensi saya dan memberikannya sebagai kejutan.", "G24", "L3", Decimal("0.70")),

    ("Saya merasa dicintai ketika seseorang memberi perhatian penuh tanpa gangguan.", "G25", "L4", Decimal("0.90")),
    ("Menghabiskan waktu bersama lebih bermakna bagi saya daripada hadiah materi.", "G26", "L4", Decimal("0.85")),
    ("Percakapan yang mendalam membuat saya merasa dekat secara emosional.", "G27", "L4", Decimal("0.80")),
    ("Saya merasa diabaikan jika seseorang hadir secara fisik tetapi fokusnya kemana-mana.", "G28", "L4", Decimal("0.75")),
    ("Aktivitas sederhana bersama seseorang membuat hubungan terasa lebih kuat.", "G29", "L4", Decimal("0.70")),
    ("Waktu khusus yang dijadwalkan bersama membuat saya merasa penting.", "G30", "L4", Decimal("0.65")),
    ("Kehadiran seseorang di samping saya membuat saya merasa aman.", "G31", "L4", Decimal("0.55")),
    ("Saya merasa dihargai ketika seseorang meluangkan waktu khusus hanya untuk saya.", "G32", "L4", Decimal("0.75")),

    ("Saya merasa nyaman ketika duduk berdekatan dengan pasangan.", "G33", "L5", Decimal("0.90")),
    ("Pelukan dari pasangan membuat saya merasa aman.", "G34", "L5", Decimal("0.85")),
    ("Saya menikmati gestur seperti berpegangan tangan.", "G35", "L5", Decimal("0.80")),
    ("Saya tidak keberatan menunjukkan kedekatan di tempat umum.", "G36", "L5", Decimal("0.75")),
    ("Sentuhan lembut membuat saya merasa dihargai.", "G37", "L5", Decimal("0.70")),
    ("Kedekatan fisik membuat saya lebih terhubung.", "G38", "L5", Decimal("0.75")),
    ("Saya merasa diperhatikan lewat kontak fisik.", "G39", "L5", Decimal("0.65")),
    ("Saat sedih, pelukan membantu saya lebih tenang.", "G40", "L5", Decimal("0.60")),
]

# =======================
# MAPPING JAWABAN → CF USER
# =======================
user_cf_map = {
    "Tidak": Decimal("0.0"),
    "Mungkin Tidak": Decimal("0.2"),
    "Tidak Tahu": Decimal("0.5"),
    "Mungkin": Decimal("0.8"),
    "Iya": Decimal("1.0")
}

# =======================
# ROUTES
# =======================
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

    page_items = [{"index": i, "text": questions[i][0]} for i in range(start, end)]
    progress = int(((page - 1) / total_pages) * 100)

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
    page=page,
    page_items=page_items,
    progress=progress,
    start=start,
    answers=session.get("answers", {})
)

@app.route("/restart")
def restart_test():
    session.clear()
    return redirect(url_for("questions_page", page=1))

@app.route("/result")
def result():
    answers = session.get("answers", {})

    # =========================
    # VALIDASI AWAL
    # =========================
    if not answers or len(answers) < len(questions):
        return render_template("result_invalid.html")

    raw_answers = list(answers.values())
    if len(set(raw_answers)) == 1:
        return render_template("result_invalid.html")

    # =========================
    # HITUNG CF
    # =========================
    cf_result = {
        "L1": Decimal("0"),
        "L2": Decimal("0"),
        "L3": Decimal("0"),
        "L4": Decimal("0"),
        "L5": Decimal("0")
    }

    for idx, (_, _, love_code, cf_pakar) in enumerate(questions):
        cf_user = user_cf_map.get(
            answers.get(str(idx), "Tidak Tahu"),
            Decimal("0")
        )
        cf_temp = cf_user * cf_pakar
        cf_result[love_code] = cf_result[love_code] + cf_temp * (1 - cf_result[love_code])

    if all(v == 0 for v in cf_result.values()):
        return render_template("result_invalid.html")

    # =========================
    # NORMALISASI
    # =========================
    total_cf = sum(cf_result.values())
    perc = {
        k: (v / total_cf * 100).quantize(Decimal("0.01"))
        for k, v in cf_result.items()
    }

    # =========================
    # DATA UNTUK TEMPLATE
    # =========================
    names = {
        "L1": "Words of Affirmation",
        "L2": "Acts of Service",
        "L3": "Receiving Gifts",
        "L4": "Quality Time",
        "L5": "Physical Touch"
    }

    descriptions = {
        "L1": "Kamu merasa paling dicintai melalui kata-kata positif, pujian, dan afirmasi yang tulus.",
        "L2": "Kamu merasa dicintai ketika orang lain menunjukkan kasih sayang melalui tindakan nyata.",
        "L3": "Kamu menghargai hadiah sebagai simbol perhatian dan usaha dari orang yang kamu sayangi.",
        "L4": "Kamu merasa paling dicintai saat mendapatkan waktu dan perhatian penuh.",
        "L5": "Kamu merasa dicintai melalui sentuhan fisik seperti pelukan dan kedekatan."
    }

    # =========================
    # TENTUKAN DOMINAN (BISA GANDA)
    # =========================
    max_val = max(perc.values())

    dominant_cats = [
        k for k, v in perc.items()
        if v == max_val
    ]

    # Jika semua sama → invalid
    if len(dominant_cats) == len(perc):
        return render_template("result_invalid.html")

    dominant_names = [names[k] for k in dominant_cats]
    dominant_descriptions = [descriptions[k] for k in dominant_cats]

    # =========================
    # RENDER
    # =========================
    return render_template(
        "result.html",
        dominant_names=dominant_names,
        dominant_cats=dominant_cats,
        dominant_descriptions=dominant_descriptions,
        perc=perc,
        is_multiple=len(dominant_cats) > 1
    )


if __name__ == "__main__":
    app.run(debug=True)
