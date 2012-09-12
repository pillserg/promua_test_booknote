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

populate db with demodata (present in repo in dumpdata.csv file). This command can take some time (if you don't have SSD :) ):

    python db_populate.py
    
then run testserver:

    python run.py

# Development notes
*   Комментарии на английском - привычка, тяжело избавится.
*   регистронезависимый like со sqlite и юникодом так и не нашел, так что там страшненький костыль 
*   try-except - как-то и не нашлось где впихнуть
*   js-validation
*   ...

# Possible improvments
Что хотелось бы добавить, но времени не хватает:

*   добавление авторов из формы добавления книги
*   inline редактирование книг и авторов
*   нормальный поиск типа whoosh или сорла
*   собрать все менеджмент скрипты в один мейкфайл
*   пройтись по коду еще на свежую голову )
*   больше тестов
*   ...
 
# improvments beyond test assignment
*   добавить timestamp и fk на юзера от книжек и авторов
*   user permissions (редактирование только своих книг)
*   ...


[flask]: http://flask.pocoo.org/
[virtualenv]: http://pypi.python.org/pypi/virtualenv