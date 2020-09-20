from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testing'

app.config['MONGO_dbname'] = 'UserDB'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'

mongo = PyMongo(app)

@app.route("/")
@app.route("/main")
def main():
    return render_template('index.html')


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        signup_user = users.find_one({'userid': request.form['userid']})

        if signup_user:
            flash(request.form['userid'] + ' userid is already exist')
            return redirect(url_for('signup'))

        hashed = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        users.insert({'userid': request.form['userid'], 'password': hashed, 'name': request.form['name']})
        session['userid'] = request.form['userid']
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/index')
def index():
    if 'userid' in session:
        users = mongo.db.users
        user_list = [p['userid'] for p in users.find()]
        return render_template('index.html', userid=session['userid'], user_list=user_list)

    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        users = mongo.db.users
        signin_user = users.find_one({'userid': request.form['userid']})

        if signin_user:
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), signin_user['password']):
                session['userid'] = request.form['userid']
                return redirect(url_for('index'))

        flash('userid and password combination is wrong')
        return render_template('signup.html')
    return render_template('signin.html')


@app.route('/delete', methods=['POST'])
def delete_user():
    users = mongo.db.users
    users.delete_one({'userid': request.form['user']})
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('userid', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
    app.run()
