from flask import Flask, render_template, request, session, redirect, send_file
import subprocess
import os
import uuid

app = Flask(__name__)
app.secret_key = "bro_code_secret"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session['user'] = request.form["username"]
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/", methods=["GET", "POST"])
def index():
    if 'user' not in session:
        return redirect("/login")

    output = ""
    code = ""
    theme = "vs-dark"
    mode = "roast"

    if request.method == "POST":
        code = request.form.get("code", "")
        theme = "vs" if request.form.get("theme_toggle") and request.form.get("theme") == "vs-dark" else "vs-dark"
        mode = "roast" if request.form.get("mode") == "roast" else "normal"
        action = request.form.get("action", "run")

        filename = f"temp_{uuid.uuid4().hex}.py"

        with open(filename, "w") as f:
            f.write(code)

        if action == "download":
            return send_file(filename, as_attachment=True)

        elif action == "save":
            output = f"🔗 Saved! Share this code file: {filename}"

        else:
            try:
                result = subprocess.run(["python", filename], capture_output=True, text=True, timeout=5)
                output = result.stdout + ("\n⚠️ " + result.stderr if result.stderr else "")
                if mode == "roast" and result.returncode != 0:
                    output += "\n\n🔥 Bro, tujhse na ho payega!"
            except subprocess.TimeoutExpired:
                output = "⏰ Execution timed out!"
            except Exception as e:
                output = f"❌ Error: {str(e)}"

        try:
            os.remove(filename)
        except:
            pass

    return render_template("index.html", output=output, code=code, theme=theme, mode=mode)

if __name__ == "__main__":
    app.run(debug=True)
