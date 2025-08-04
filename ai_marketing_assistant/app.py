from flask import Flask, render_template, request
from ai_engine import generate_marketing_content

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["idea"]
        result = generate_marketing_content(user_input)
        return render_template("result.html", idea=user_input, result=result)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
