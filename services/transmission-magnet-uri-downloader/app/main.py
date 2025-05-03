import requests
import json

from flask import Flask, jsonify, request
from flask_cors import CORS

from lib.transmission import TransmissionRequest as tr

import os

app = Flask(__name__)
CORS(app)

@app.route("/magnet", methods=["POST"])
def add_magnet():
    
    d = request.json
    print("got d %s", d )
    if not d or d.get("magnet") is None:
        return "", 201
    
    t = tr()
    t.torrent_add(d.get("magnet"))
    return "", 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", default=4000))    
