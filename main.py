from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")

app.run(debug=True)



# npx tailwindcss -i ./static/src/input.css -o ./static/css/main.css -- watch | Run this command every time you start.