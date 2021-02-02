from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime
import os
import sqlite3

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

### USER LOGIN/LOGOUT/REGISTER/UPDATE ###
#####################################################################################
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        f = request.form
        un = f.get('username')
        pw = f.get('password')

        # Ensure username was submitted
        if not un:
            fail = True;
            return render_template("login.html", fail=fail, msg="Must provide a username")

        # Ensure password was submitted
        elif not pw:
            fail = True;
            return render_template("login.html", fail=fail, msg="Must provide a password")

        # Query database to see if username exists and that correct password passed
        with sqlite3.connect("preper.db") as con:  
            cur = con.cursor()   
            cur.execute("SELECT * FROM users WHERE username = :username",
                        {'username': un})
            row = cur.fetchone()    

            if not row or not check_password_hash(row[2], pw):
                fail = True
                return render_template("login.html", fail=fail, msg="Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = row[0]
        session["un"] = row[1]

        # Redirect user to home page
        return redirect(url_for("mainDash", user=session['un']))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        f = request.form
        un = f.get('username')
        pw = f.get('password')
        confirm = f.get('confirmation')

        # Ensure username was submitted
        if not un:
            fail = 1
            return render_template("register.html", fail=fail, msg="Please enter a username")

        # Ensure password was submitted
        elif not pw or not confirm:
            fail = 1
            return render_template("register.html", fail=fail, msg="Please enter a password")

        elif pw != confirm:
            fail = 1
            return render_template("register.html", fail=fail, msg="Passwords did not match")

        # Query database for username to ensure that username does not already exist
        with sqlite3.connect("preper.db") as con:  
            cur = con.cursor()   
            cur.execute("SELECT * FROM users WHERE username = :username",
                        {'username': un})
            row = cur.fetchone()    

            if row:
                fail = 1
                return render_template("register.html", fail=fail, msg="Username already exists")

            # new user registration successful: hash password and insert new user into database
            cur.execute("INSERT INTO users (username, password) VALUES (:username, :hashed_password)",
                    {'username':un,
                    'hashed_password':generate_password_hash(pw)})

            con.commit()

        # Redirect user to home page
        return render_template("login.html", msg="Registration successful! Please log in")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/account", methods=["GET"])
@login_required
def redirectAccount():
    return redirect(url_for("userAccount", user=session['un']))

@app.route("/<user>/account", methods=["GET"])
@login_required
def userAccount(user):
    return render_template("account.html", user=user, user_id=session['user_id'])

@app.route("/<user>/account/<msg>", methods=["GET"])
@login_required
def accountMSG(user, msg):
    return render_template("account.html", user=user, user_id=session['user_id'], msg=msg)

@app.route("/updateUsername", methods=["POST"])
@login_required
def updateUsername():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        f = request.form
        uid = f.get('userID')
        newName = f.get('newName')

        # Query database for username to ensure that username does not already exist
        with sqlite3.connect("preper.db") as con:  
            cur = con.cursor()   
            cur.execute("SELECT * FROM users WHERE username = :username",
                        {'username': newName})
            row = cur.fetchone()    

            # username already exists
            if row:
                return redirect(url_for("accountMSG", user=session['un'], msg="UAE"))
                con.close()

            # username does not exist update username
            cur.execute("UPDATE users SET username=:un WHERE id=:uid",
                    {'un': newName,
                    'uid':uid})

            con.commit()

        #update session 
        session["un"] = newName

        # Redirect user to home page
        return redirect(url_for("accountMSG", user=session['un'], msg="US"))
        con.close()

@app.route("/updatePassword", methods=["POST"])
@login_required
def updatePassword():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        f = request.form
        uid = f.get('userID')
        newPass = f.get('newPass')
        confirmPass = f.get('confirmPass')

        if newPass != confirmPass:
            return redirect(url_for("accountMSG", user=session['un'], msg="NM"))

        # Query database for username to ensure that username does not already exist
        with sqlite3.connect("preper.db") as con:  
            cur = con.cursor()   
            
            # update password
            cur.execute("UPDATE users SET password=:pw WHERE id=:uid",
                    {'pw': generate_password_hash(newPass),
                    'uid':uid})

            con.commit()

        # Redirect user to home page
        return redirect(url_for("accountMSG", user=session['un'], msg="US"))
        con.close()

@app.route("/deleteAccount", methods=["POST"])
@login_required
def delAccount():
    if request.method == "POST":
        try:
            f = request.form
            uid = f.get("userID")
            print(uid)
            with sqlite3.connect("preper.db") as con:
                cur = con.cursor()
                cur.execute("SELECT project_id FROM projects WHERE user_id = :uid", {'uid': uid})
                projects = cur.fetchall()
                for project in projects:
                    cur.execute("DELETE FROM tasks WHERE project_id = :id", {'id': project[0]})
                    cur.execute("DELETE FROM projects WHERE project_id = :id", {'id': project[0]})
                cur.execute("DELETE FROM users WHERE id = :id", {'id': uid})
                con.commit()
            msg="Account Deleted :("
        except:
            con.rollback()
            msg = "Unable to delete project!"
        finally:
            # Forget any user_id
            session.clear()
            return render_template("login.html", fail=True, msg=msg)
            con.close()

#####################################################################################

@app.route("/dash-main", methods=["GET"])
@login_required
def redirectDash():
    return redirect(url_for("mainDash", user=session['un']))

@app.route("/<user>/dash-main", methods=["GET"])
@login_required
def mainDash(user):

    # Query database for user projects
    with sqlite3.connect("preper.db") as con:  
        cur = con.cursor()   
        cur.execute("SELECT project_id, project_title, created, dueDate FROM projects WHERE user_id = :user_id",
                    {'user_id': session['user_id']})
        projects = cur.fetchall()       

    return render_template("dash-main.html", user=session['un'], projects=projects, now=datetime.now())

### dash for individual projects ###
@app.route("/<user>/<project_id>/<project>/dash", methods=["GET"])
@login_required
def dash(user, project_id, project):

    # Query database for user tasks associated with project
    with sqlite3.connect("preper.db") as con:  
        cur = con.cursor()   
        cur.execute("SELECT id, task_title, task_description, time_estimate, time_actual, task_status FROM tasks WHERE project_id = :pid", {'pid': project_id})
        tasks = cur.fetchall()
        cur.execute("SELECT content FROM notes WHERE project_id = :pid", {'pid': project_id})
        note = cur.fetchone()

    return render_template("dash.html", tasks=tasks, project=project_id, title=project, note=note)

@app.route("/tasks", methods=["GET"])
@login_required
def redirectTasks():
    return redirect(url_for("tasks", user=session['un']))

@app.route("/<user>/tasks", methods=["GET"])
@login_required
def tasks(user):

    # Query database for user tasks
    with sqlite3.connect("preper.db") as con:  
        cur = con.cursor()   
        cur.execute("SELECT tasks.id, tasks.task_title, tasks.task_description, tasks.time_estimate, tasks.time_actual, tasks.task_status, projects.project_id, projects.project_title FROM tasks JOIN projects ON tasks.project_id = projects.project_id JOIN users ON projects.user_id = users.id WHERE users.username = :user", {'user': user})
        tasks = cur.fetchall()
        cur.execute("SELECT projects.project_id, projects.project_title FROM projects JOIN users on projects.user_id = users.id WHERE users.username = :user", {'user': user})       
        projects = cur.fetchall()

    return render_template("tasks.html", user=user, tasks=tasks, projects=projects)

#####################################################################################

### CRUD projects ###
#####################################################################################
@app.route("/addProject", methods=["POST"])
@login_required
def addProject():
    msg = ""
    if request.method == "POST":
        try:
            f = request.form
            title = f.get("projectName")
            created = f.get("createDate")
            dueDate = f.get("dueDate")
            with sqlite3.connect("preper.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO projects (project_title, user_id, created, dueDate) VALUES (:title, :user_id, :created, :dueDate)",
                            {'title': title,
                            'user_id': session["user_id"],
                            'created': created,
                            'dueDate': dueDate})
                con.commit()
                msg = "Added {} to your projects!".format(title)
        except:
            con.rollback()
            msg = "Unable to create project!"
        finally:
            return redirect(url_for("mainDash", user=session['un']))
            con.close()

@app.route("/deleteProject", methods=['POST'])
@login_required
def deleteProject():
    msg=""
    if request.method == "POST":
        try:
            pid = request.form.get("projectID")
            with sqlite3.connect("preper.db") as con:
                cur = con.cursor()
                cur.execute("DELETE FROM projects WHERE project_id = :pid", {'pid': pid})
                con.commit()
                msg = "Deleted {}!".format(title)
        except:
            con.rollback()
            msg = "Unable to delete project!"
        finally:
            return redirect(url_for("mainDash", user=session['un']))
            con.close()

@app.route("/editProject", methods=['POST'])
@login_required
def editProject():
    msg=""
    if request.method == "POST":
        try:
            f = request.form
            newTitle = f.get("newName")
            newDue = f.get("newDue")
            pid = f.get("projectID")
            with sqlite3.connect("preper.db") as con:
                cur = con.cursor()
                cur.execute("UPDATE projects SET project_title = :ptitle, dueDate = :pdue WHERE project_id = :pid", 
                            {'ptitle': newTitle,
                            'pdue': newDue,
                            'pid': pid})
                con.commit()
                msg = "Edited {}!".format(title)
        except:
            con.rollback()
            msg = "Unable to edit project!"
        finally:
            return redirect(url_for("mainDash", user=session['un']))
            con.close()

@app.route("/addDueDate", methods=['POST'])
@login_required
def addDueDate():
    msg=""
    if request.method == "POST":
        try:
            f = request.form
            newDue = f.get("addDue")
            pid = f.get("projectID")
            with sqlite3.connect("preper.db") as con:
                cur = con.cursor()
                cur.execute("UPDATE projects SET dueDate = :pdue WHERE project_id = :pid", 
                            {'pdue': newDue,
                            'pid': pid})
                con.commit()
                msg = "Added due for {}!".format(title)
        except:
            con.rollback()
            msg = "Unable to add due date!"
        finally:
            return redirect(url_for("mainDash", user=session['un']))
            con.close()
#####################################################################################

### CRUD tasks ###
#####################################################################################
@app.route("/addTask", methods=['POST'])
@login_required
def addTask():
    msg=""
    where=""
    if request.method == "POST":
        try:
            f = request.form
            taskName = f.get("taskName")
            D = f.get('taskDays', type=int)
            H = f.get('taskHrs', type=int)
            M = f.get('taskMins', type=int) 
            taskTimeEst = 0
            if D: taskTimeEst += D
            if H: taskTimeEst += H
            if M: taskTimeEst += M
            taskD =f.get('taskDescription')
            if not taskD: taskD = "Click the edit button to add a task description!"
            pid = f.get('projectID')
            print(pid)
            createDate = f.get('createDate')
            where = f.get('where')
            pt = f.get('project')
            with sqlite3.connect("preper.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO tasks (task_title, task_description, time_estimate, created, project_id, task_status) VALUES (:tn, :td, :te, :c, :pid, :s)",
                            {'tn': taskName,
                            'td': taskD,
                            'te': taskTimeEst,
                            'c': createDate,
                            'pid': pid,
                            's': 0})
                con.commit()
                msg = "Added task {}!".format(taskName)
            print('made it')
        except:
            con.rollback()
            msg = "Unable to add task!"
        finally:
            if where:
                return redirect(url_for(where, user=session['un'], project_id=pid, project=pt))
            return redirect(url_for("mainDash", user=session['un']))
            con.close()

@app.route("/editTask", methods=['POST'])
@login_required
def editTask():
    msg=""
    if request.method == "POST":
        try:
            f = request.form
            taskTitle = f.get("taskName")
            taskStatus = f.get("taskStatus")
            D = f.get('taskDays', type=int)
            H = f.get('taskHrs', type=int)
            M = f.get('taskMins', type=int) 
            taskTimeEst = 0
            if D: taskTimeEst += D
            if H: taskTimeEst += H
            if M: taskTimeEst += M           
            taskD =f.get('taskDescription')         
            pid = f.get('projectID')
            tid = f.get('taskID')
            where = f.get('where')
            pt = f.get('project')
            with sqlite3.connect("preper.db") as con:
                cur = con.cursor()
                cur.execute("UPDATE tasks SET task_title = :t, task_description = :d, time_estimate = :est, task_status = :status WHERE id = :tid", 
                            {'t': taskTitle,
                            'd': taskD,
                            'est': taskTimeEst,
                            'status': taskStatus,
                            'tid': tid})
                con.commit()
                msg = "Edited {}!".format(taskTitle)
        except:
            con.rollback()
            msg = "Unable to edit task!"
        finally:
            if where:
                return redirect(url_for(where, user=session['un'], project_id=pid, project=pt))
            con.close()

@app.route("/deleteTask", methods=['POST'])
@login_required
def deleteTask():
    msg=""
    if request.method == "POST":
        try:
            f = request.form
            pid = f.get("projectID")
            tid = f.get("taskID")
            where = f.get("where")
            pt = f.get("project")
            with sqlite3.connect("preper.db") as con:
                cur = con.cursor()
                cur.execute("DELETE FROM tasks WHERE id = :tid", {'tid': tid})
                con.commit()
                msg = "Deleted Task!"
        except:
            con.rollback()
            msg = "Unable to delete task!"
        finally:
            if where:
                return redirect(url_for(where, user=session['un'], project_id=pid, project=pt))
            con.close()
#####################################################################################

### CRUD tasks ###
#####################################################################################
@app.route("/saveNotes", methods=['POST'])
@login_required
def saveNotes():
    if request.method == "POST":
        try:
            f = request.form
            pid = f.get("projectID")
            pt = f.get('projectTitle')
            content = f.get("noteContent")
            with sqlite3.connect("preper.db") as con:
                cur = con.cursor()
                
                # query to for project note to check if it exists
                cur.execute("SELECT id FROM notes WHERE project_id = :pid", {'pid': pid})
                row = cur.fetchone()
                
                # note already exists update note with new content
                if row:
                    cur.execute("UPDATE notes SET content = :content WHERE project_id = :pid", {'content': content, 'pid': pid})
                
                # if note does not exist create note
                else: 
                    cur.execute("INSERT INTO notes (content, project_id) VALUES (:c, :p)", {'c': content, 'p': pid})
                
                con.commit()
                msg = "Note Saved!"
        except:
            con.rollback()
            msg = "Unable to save note!"
        finally:
            return redirect(url_for("dash", user=session['un'], project_id=pid, project=pt))
            con.close()

### Error Handling ###
#####################################################################################
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html")

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)