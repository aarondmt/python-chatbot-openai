from flask import Flask, render_template, request, Response
import os
from openai import OpenAI
import dotenv

app = Flask(__name__)
app.secret_key = "alura"

dotenv.load_dotenv()

client = OpenAI()


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
