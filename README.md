# Matcha-version2

# Setup

virtualenv -p python3 magic/

source magic/bin/activate

pip install -r requirements.txt

# Running

export FLASK_APP=run.py

export FLASK_ENV=development

flask run

Open your web browser on localhost

# Troubleshooting
In the unfortunate event that you receive a "Access denied for user 'root@localhost' error" perform the following:

$ sudo mysql
> use mysql

> update user set plugin='' where user='root';

> flush privileges

> exit or ctrl+D

That should resolve the error.

# 500 Users
To create 500 dummy user accounts (NOTE: the script can only be successfully executed if at least one user was created manually within the app):

$ sudo mysql < populate_db.sql 