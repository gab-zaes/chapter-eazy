import sys
import re
import sqlite3
from flask import Flask, flash, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, romans


# Configure application 
app = Flask(__name__)



# Configure filter for roman algorisms
app.jinja_env.filters["romans"] = romans

# use filesystem instead of cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Ensure responses arent cached
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Landing Page"""
    try:
        state = session["user_id"]
    except KeyError:
        return render_template("index.html", value=133)
    redirect("/writer")
    


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        # check the form content
        if password == request.form.get("check-password") and re.search(r"^[\w\.]+@\w+\.\w+$", email) and username and password:
            
            # Start database
            con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
            # Create cursor
            db = con.cursor()

            # check if username is already in db
            if db.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone() != None:
                return apology("Username is not available")
            elif db.execute("SELECT email FROM users WHERE email = ?", (email,)).fetchone() != None:
                return apology("Email is not available")

            # insert information into db
            db.execute("INSERT INTO users(username, email, hash) VALUES (?, ?, ?)", (username, email, generate_password_hash(password)))
            con.commit()
            con.close()
            
            # call login 
            login()
            return redirect("/write")
        return apology("Error! Invalid input")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Start user session"""

    #Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)

        if not request.form.get("password"):
            return apology("must providee password", 403)

        # Start database
        con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
        # Create cursor
        db = con.cursor()

        # Get hash in db for that username (1 row as an iterable should be the returned value)
        res = db.execute("SELECT user_id, hash FROM users WHERE username = ?", (request.form.get("username"),))

        # rows is a list of tuples [(user_id, hash)]
        rows = res.fetchall()
        
        # If password dont match or there is no username, than return apology
        if len(rows) != 1 or not check_password_hash(rows[0][1], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Start user session
        session["user_id"] = rows[0][0]

        con.close()

        return redirect("/write")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Terminates user session"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/write", methods=["GET", "POST"])
@login_required
def write():
    """Handles the written information, loading and saving to the database."""
    chapter_titles = []
    chapter_count = 0

    if request.method == "POST":
        # Save to database logic
        ...
    # Load information from database
    ...
    # then render the page

    # Start database
    con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
    # Create cursor
    db = con.cursor()
    
    username = db.execute("SELECT username FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()[0]
    con.close()
    
    return render_template("write.html", username=username, chapter_count=chapter_count, chapter_titles=chapter_titles)


@app.route("/new_book", methods=["POST"])
@login_required
def new_book():
    """Creates a new book given its title"""
    title = request.form.get("book_title")
    return redirect("/new_chapter")


@app.route("/new_chapter", methods=["POST"])
@login_required
def new_chapter():
    """Create new chapter in database given its title"""
    ...
    return redirect("/write")


@app.route("/export", methods=["GET", "POST"])
@login_required
def export():
    """Gives options to export"""
    if request.method == "POST":
        # Export logic based on user input
        ...
    # Load information from db
    return render_template("export.html", ...)


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Manages account and password"""
    if request.method == "POST":
        # Check password change
        ...
    return render_template("account.html")


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    """Deletes the user in database"""
    # check for password again
    ...
    flash("You have deleted your account.")
    return redirect("logout")