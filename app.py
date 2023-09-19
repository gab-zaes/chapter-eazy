import sys
import re
import sqlite3
import random
import os
from datetime import datetime
from flask import Flask, flash, render_template, request, redirect, session, send_file, url_for, send_from_directory
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, romans, erase
from finalformat import Chapter, Book, consolidate_pdf

REGULAR_SIZE = (125, 180)
date_time = datetime.now()

# Configure application 
app = Flask(__name__)

# Configure filter for roman algorisms
app.jinja_env.filters["romans"] = romans

UPLOAD_FOLDER = "./download/"

# use filesystem instead of cookies
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
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
    return redirect("/write")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    #Forget any user_id
    session.clear()

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
    # First we call save
    save()

    # con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
    # db = con.cursor()


    # con.commit()
    # con.close()
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/write")
@login_required
def write():
    """Handles the written information, loading and saving to the database."""
    # Start database
    con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
    # Create cursor
    db = con.cursor()
    chapters = []

    # Load information from database
    try:
        current_title, current_chapter = db.execute("SELECT title, chapter_name FROM active WHERE user_id = ?", (session["user_id"],)).fetchone()
    except (ValueError, TypeError):
        current_title = ""
        current_chapter = ""
        current_index = 1
    print(current_title, current_chapter)
        

    # then render the page

    rows = db.execute("SELECT chapter_name FROM books WHERE user_id = ? AND title = ? ORDER BY chapter_index ASC", (session["user_id"], current_title)).fetchall()
    chapters = [row[0] for row in rows]
    if chapters is None:
        chapters = []
    username = db.execute("SELECT username FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()[0]
    if current_chapter:
        chapter_body = db.execute("SELECT chapter_body FROM books WHERE chapter_name = ?", (current_chapter,)).fetchone()[0]
        current_index = 1 + chapters.index(current_chapter)
    else:
        # if there is no chapters yet
        current_index = 1
        chapter_body = "    "

    if chapter_body is None:
        chapter_body = "    "

    chapter_count = len(chapters)

    con.commit()
    con.close()

    return render_template("write.html", 
        username=username, 
        chapters=chapters, 
        chapter_body=chapter_body, 
        current_title=current_title, 
        current_chapter=current_chapter,
        current_index=current_index,
        chapter_count=chapter_count,
    )


@app.route("/save", methods=["POST"])
@login_required
def save():
    """Saves progress to database"""
    con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
    db = con.cursor()

    # hidden fields sent through request along with the body of text
    t = (request.form.get("chapter_body"), session["user_id"], request.form.get("book_title"), request.form.get("chapter_name"),)
    db.execute("UPDATE books SET chapter_body = ? WHERE user_id = ? AND title = ? AND chapter_name = ?", t)

    con.commit()
    con.close()
    flash(random.choice(["Saved!", "One Save to Rule then All", "Progress Saved", "Keep Saving", "Checkpoint", "Coffee Time!"]), "save")
    return redirect("/write")


@app.route("/new_chapter", methods=["POST"])
@login_required
def new_chapter():
    """Create new chapter in database given its title"""
    con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
    db = con.cursor()

    try:
        index = db.execute("SELECT chapter_index FROM books WHERE user_id = ? AND title = ? ORDER BY chapter_index DESC", (session["user_id"], request.form.get("book_title"))).fetchone()[0]
        index += 1
    except TypeError:
        index = 1

    # title must be either prompted by user in first access or stored in a hidden field in /write
    save_data = (session["user_id"], request.form.get("book_title"), request.form.get("chapter_name"), index, request.form.get("chapter_body"),)

    # save new chapter to database in the books Table
    db.execute("INSERT INTO books(user_id, title, chapter_name, chapter_index, chapter_body) VALUES (?, ?, ?, ?, ?)", save_data)
    db.execute("REPLACE INTO active(user_id, title, chapter_name) VALUES(?, ?, ?)", (session["user_id"], request.form.get("book_title"), request.form.get("chapter_name"),))
    con.commit()
    con.close()
    flash("Chapter created!", "save")
    
    return redirect("/write")


@app.route("/change_order", methods=["POST"])
@login_required
def change_order():
    """Changes the order of the Chapters"""
    # Start database
    con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
    # Create cursor
    db = con.cursor()

    try:
        old = int(request.form.get("old_index"))
        new = int(request.form.get("new_index"))
        current_title = request.form.get("current_title")
    except ValueError:
        flash("invalid input", "warning")
        return write

    rows = db.execute("SELECT chapter_name FROM books WHERE user_id = ? AND title = ? ORDER BY chapter_index ASC", (session["user_id"], current_title)).fetchall()
    chapters = [row[0] for row in rows]

    if new > len(chapters) or old > len(chapters) or new < 1 or old < 1:
        return write()
    else:
        tmp = chapters.pop(old - 1)
        chapters.insert(new - 1, tmp)
    # change positions in database
    for i, chapter in enumerate(chapters):
        res = db.execute("UPDATE books SET chapter_index = ? WHERE chapter_name = ? AND user_id = ?", (i + 1, chapter, session["user_id"]))

    con.commit()
    con.close()
    return redirect("/write")


@app.route("/set_chapter", methods=["POST"])
@login_required
def set_chapter():
    """Set the active chapter when the user clicks on it"""
    con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
    db = con.cursor()

    chapter_index = request.form.get("chapter_index")
    # book title must be a hidden field
    title = request.form.get("book_title")
    chapter_name = db.execute("SELECT chapter_name FROM books WHERE user_id = ? AND chapter_index = ?", (session["user_id"], chapter_index)).fetchone()[0]
    db.execute("UPDATE active SET chapter_name = ? WHERE user_id = ?", (chapter_name, session["user_id"]))

    con.commit()
    con.close()

    return redirect("/write")


@app.route("/export", methods=["GET", "POST"])
@login_required
def export():
    """Downloads the current book in md or pdf"""
    con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
    db = con.cursor()

    username = db.execute("SELECT username FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()[0]
    email = db.execute("SELECT email FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()[0]

    # current title for printing
    current_title = db.execute("SELECT title FROM active WHERE user_id = ?", (session["user_id"],)).fetchone()[0]
    if request.method == "POST":
        chapters = db.execute(
            "SELECT chapter_name, chapter_body FROM books WHERE user_id = ? AND title = ? ORDER BY chapter_index ASC", 
            (session["user_id"], current_title))

        if request.form.get("format") == "md":
            # open current_title.md file in temporary folder
            filename = username + current_title + ".md"

            path = app.config["UPLOAD_FOLDER"] + filename
            with open(path, "w") as file:
                # write to the file iterating over chapters
                for chapter, body in chapters:
                    print(chapter, body)
                    file.write("# " + chapter + "\n\n")
                    try:
                        file.writelines(body + "\n\n")
                    except TypeError:
                        file.write("\n")
            
            return download(request.form.get("format"))

        elif request.form.get("format") == "pdf":
            # call finalformat classes and functions
            filename = username + current_title + ".pdf"
            path = app.config["UPLOAD_FOLDER"] + filename
            index = []
            for chapter, body in chapters:
                index.append(Chapter(chapter, body))

            meta = {
                "title": current_title,
                "author": request.form.get("author"),
                "date": f"{date_time.day}/{date_time.month}/{date_time.year}",
                "contact": email,
                "license": f"All rights regarding the text presented here are reserved to {request.form.get('author')}",
                "quote": request.form.get("quote"),
                "bio": request.form.get("bio")
            }

            # create book instance
            book = Book(index, "0", "0", REGULAR_SIZE, **meta)

            if consolidate_pdf(book, path, "L"):
                return download(request.form.get("format"))

    con.commit()
    con.close()
    return render_template("export.html", current_title=current_title, username=username)


@app.route("/download/", methods=["GET"])
@login_required
def download(format):
    con = sqlite3.connect("chaptereasy.db", check_same_thread=False)
    db = con.cursor()

    current_title = db.execute("SELECT title FROM active WHERE user_id = ?", (session["user_id"],)).fetchone()[0]
    username = db.execute("SELECT username FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()[0]

    con.commit()
    con.close()

    match format:
        case "md":
            files = os.listdir("./download")
            for f in files:
                if f == f"{username}{current_title}.md":
                    filename = f.replace(username, "")
                    path = os.path.join(app.root_path, (app.config["UPLOAD_FOLDER"] + f).replace("./", ""))
                    # path = "temp/" + username + filename
                    # path = os.path.join(app.root_path.replace(" ", "%20"), path)
                    break

        case "pdf":
            files = os.listdir("./download")
            for f in files:
                if f == f"{username}{current_title}.pdf":
                    filename = f.replace(username, "")
                    path = os.path.join(app.root_path, (app.config["UPLOAD_FOLDER"] + f).replace("./", ""))
                    # path = "temp/" + username + filename
                    # path = os.path.join(app.root_path.replace(" ", "%20"), path)
                    break
            

    return send_file(path, as_attachment=True, download_name=filename), erase(path)
    


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