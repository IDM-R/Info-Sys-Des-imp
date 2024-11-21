from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Welcome to Flask World!'


@app.route('/hello')
def hello_wprld():
    return 'Welcome to Flask World!!!!!'
    
from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = b'random string...'

member_data = {}

message_data = []

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html',\
        title='Sign in to Nebula',\
        message='Nebulaへようこそ', )


@app.route('/', methods=['POST'])
def form():
    msg = request.form.get('comment')
    message_data.append((session['id'], msg))
    if len(message_data) > 25:
        message_data.pop(0)
    return redirect('/')

# login page access
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html',\
    title='Login',\
    err=False,\
    message='IDとパスワードを入力:',\
    id='')

# login form sended.
@app.route('/login', methods=['POST'])
def login_post():
    global member_data
    id = request.form.get('id')
    pswd = request.form.get('pass')
    if id in member_data:
        if pswd == member_data[id]:
            session['login'] = True
        else:
            session['login'] = False
    else:
        member_data[id] = pswd
        session['login'] = True
    session['id'] = id
    if session['login']:
        return redirect('/')
    else:
        return render_template('login.html',\
        title='Login',\
        err=False,\
        message='パスワードが違います!',\
        id=id)

# logout
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('id', None)
    session.pop('login')
    return redirect('/login')



if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost')