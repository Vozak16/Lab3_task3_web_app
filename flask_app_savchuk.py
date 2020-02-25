from flask import Flask, render_template, request
from locations_friends import main
from urllib.error import HTTPError


app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    try:
        user = request.form["username"]
        print(user)
        if user == '':
            return render_template("failure.html")

        contex = {"my_map": main(user)}
        return render_template("friend_locations_map.html", **contex)
    except HTTPError:
        return render_template("failure.html")


if __name__ == "__main__":
    app.run(port=5001)

