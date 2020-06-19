# Matcha-version2

# Setup

virtualenv -p python3 magic/

source magic/bin/activate

pip install -r requirements.txt

# Running
export FLASK_APP=run.py

export FLASK_ENV=development

flask run

# Side Note 
Spider man please create a git ignore as follows:

nano or vim .gitignore                //then add the following folders only

__ pycache __                         //without the spaces between the underscores and letters  

magic/                              //or whatever you named your virtual environment

PS... I only want to see the 'app' folder, README.md, run.py, config.py and requirements.txt file, only those 5 things are required, from there on only this README file will guide the person running the app...Please I beg you STOP mixing your virtual environment with the code...the name of the repo is 'mysql-matcha' cd inside 'mysql-matcha' then begin the steps in SETUP till SIDENOTE (YOU SHOULDN'T HAVE bin, include, lib and other environmental stuff mixed in the same directory as the above mentioned 5 files, all these files should be inside 'magic' as in my case), there wont be any disturbance between ur code and the repo code... work cleanly and be neat with your code and structure bafo. from there on you can proceed with what you were doing...