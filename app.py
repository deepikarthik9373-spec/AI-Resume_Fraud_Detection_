from flask import Flask, render_template, request
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def calculate_fraud_score(text):
    score = 0

    suspicious_words = [
        "fake", "fraud", "scam", "urgent",
        "verify immediately", "guaranteed",
        "100% job", "pay money", "payment required",
        "fake experience", "forged", "duplicate",
        "certificate available", "guaranteed placement"
    ]

    text_lower = text.lower()

    for word in suspicious_words:
        if word in text_lower:
            score += 8

    # Suspicious email patterns
    if re.search(r"example\.com|test@gmail\.com", text_lower):
        score += 10

    # Too many numbers may indicate suspicious/inconsistent data
    numbers = re.findall(r"\d+", text)
    if len(numbers) > 15:
        score += 5

    # Keep score between 0 and 100
    score = min(score, 100)

    if score >= 50:
        result = "High Fraud Risk"
    elif score >= 25:
        result = "Suspicious Resume"
    else:
        result = "Low Fraud Risk"

    return score, result


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return "No resume selected"

    resume = request.files["resume"]

    if resume.filename == "":
        return "Please select a resume"

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        resume.filename
    )

    resume.save(file_path)

    # Read resume text
    text = ""

    try:
        from pypdf import PdfReader

        reader = PdfReader(file_path)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

    except Exception as e:
        print("PDF reading error:", e)

    # Calculate fraud score
    score, result = calculate_fraud_score(text)

    return render_template(
        "result.html",
        filename=resume.filename,
        score=score,
        result=result
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)