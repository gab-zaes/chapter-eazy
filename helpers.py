from functools import wraps
from flask import session, redirect, flash, render_template
from roman import toRoman



def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please login first", "warning")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def romans(n: int):
    return toRoman(n)


def apology(message, code=400):
    return render_template("apology.html", code=code, message=message), code