# Booknote

Simple books management app based on [flask] microframework.

# Installation & Usage
Simplest way using [virtualenv] assuming dirname == repository name:

    git clone https://github.com/pillserg/promua_test_booknote.git
    virtualenv --no-site-packages .env
    source .env/bin/activate
    pip install -r promua_test_booknote/requirements.txt
    cd promua_test_booknote
    python db_create.py

run tests:

    python tests.py

populate db with demodata (present in repo in dumpdata.csv file). This command can take some time (if you don't have SSD):

    python db_populate.py
    
then run testserver:

    python run.py

    
    
# Development notes
...


[flask]: http://flask.pocoo.org/
[virtualenv]: http://pypi.python.org/pypi/virtualenv