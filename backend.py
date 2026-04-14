from flask import Flask, request, jsonify, Response
import re
import json
import os

app = Flask(__name__)

SQL_FILE = "eczane.sql"


# -----------------------------
# SQL PARSER (mytable)
# -----------------------------
def load_eczane():
    data = []

    if not os.path.exists(SQL_FILE):
        return data

    with open(SQL_FILE, "r", encoding="utf-8", errors="ignore") as f:
        sql = f.read()

    # INSERT satırlarını yakala
    inserts = re.findall(r"INSERT INTO mytable.*?VALUES\s*\((.*?)\);", sql)

    for row in inserts:
        parts = []
        current = ""
        in_q = False

        for ch in row:
            if ch == "'" and not in_q:
                in_q = True
            elif ch == "'" and in_q:
                in_q = False

            if ch == "," and not in_q:
                parts.append(current.strip().strip("'"))
                current = ""
            else:
                current += ch

        parts.append(current.strip().strip("'"))

        if len(parts) >= 4:
            data.append({
                "eczane": parts[0],
                "ad": parts[1],
                "adres": parts[2],
                "telefon": parts[3]
            })

    return data


DB = load_eczane()
print(f"Yüklendi: {len(DB)} eczane")


# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    return Response(
        json.dumps({"status": "ok", "count": len(DB)}, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


# -----------------------------
# ECZANE API
# -----------------------------
@app.route("/eczane", methods=["GET"])
def eczane():

    ad = request.args.get("ad")
    ilce = request.args.get("ilce")
    adres = request.args.get("adres")

    result = DB

    if ad:
        result = [x for x in result if ad.lower() in x["ad"].lower()]

    if ilce:
        result = [x for x in result if ilce.lower() in x["adres"].lower()]

    if adres:
        result = [x for x in result if adres.lower() in x["adres"].lower()]

    return Response(
        json.dumps({
            "count": len(result),
            "data": result[:100]
        }, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


# -----------------------------
# RUN (Render uyumlu)
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
