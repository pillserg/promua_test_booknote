from booknote import app


@app.route('/')
def index():
    return 'Booknote'
