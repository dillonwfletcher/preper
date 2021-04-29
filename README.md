## preper

preper is a project/task management web application

## instructions for testing on your machine
clone this repo
create and activate virtual environment in repo (optional but recommended)
* follow this resource if you don't know how: https://python.land/virtual-environments/virtualenv

download requirements
* python3 (need this before you can use python venv)
* flask (in venv)
* flask_session (in venv)
* sqlite3 (in venv)

start flask app locally
* in command line
  * export FLASK_APP=application.py
  * flask run
  
flask app should now be running on local IP 127.0.0.1 port 5000
* go to http://127.0.0.1:5000/ in your browser

should be good to go! create an account and test out the app
any accounts/project/tasks/notes you create with be stored locally on your machine in preper.db other people wont be able to see them









