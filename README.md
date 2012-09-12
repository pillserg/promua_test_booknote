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

populate db with demodata:

    python db_populate.py
    
# Development notes
...


[flask]: http://flask.pocoo.org/
[virtualenv]: http://pypi.python.org/pypi/virtualenv