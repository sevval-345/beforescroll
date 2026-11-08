"""Panel + canlı model API.  Çalıştırma: python app.py  ->  http://localhost:8000"""
from flask import Flask, jsonify, request

from beforescroll.service import Engine

app = Flask(__name__, static_folder="web", static_url_path="")
print("Model eğitiliyor (ilk açılışta birkaç saniye sürer)...")
eng = Engine()


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/state")
def state():
    return jsonify(eng.state())


@app.post("/api/tasks")
def tasks():
    b = request.get_json(force=True)
    return jsonify(eng.set_task(int(b["i"]), b["done"]))


@app.post("/api/checkin")
def checkin():
    return jsonify(eng.checkin(bool(request.get_json(force=True)["ok"])))


@app.post("/api/ask")
def ask():
    return jsonify(answer=eng.ask(request.get_json(force=True).get("q", "")))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)