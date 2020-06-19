# Matcha-version2

# Setup

virtualenv -p python3 magic/
source magic/bin/activate
pip install -r requirements.txt

# Running
export FLASK_APP=run.py
export FLASK_ENV=development
flask run