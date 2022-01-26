from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
        return "<p>Hello, World!</p>"


@app.route("/cluster_results")
def get_results():
        return render_template("index.html")
