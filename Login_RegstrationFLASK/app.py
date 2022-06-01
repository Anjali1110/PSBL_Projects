from operator import add
from flask import Flask, render_template, request, redirect, url_for, session
import re
import pandas as pd
from csv import writer

app = Flask(__name__)
app.secret_key = 'your secret key'

ROOT_FOLDER_PATH = "/Users/anjali/Downloads/NSE/"
df_register_data= pd.DataFrame(columns=['username', 'password', 'email'])

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username=request.form['username']
        password = request.form['password']

        try:
            df_register_data=pd.read_csv("data.csv")
            print(df_register_data.head())
            is_login = df_register_data[(df_register_data['username'] == username) & 
                                    (df_register_data['password'] == password)]

            print("is_login",is_login.head())

            if not is_login.empty:
                session['loggedin'] = True
                session['username'] = username
                msg = 'Logged in successfully !'
                return render_template('index.html', msg = msg)
            else:
                msg='Incorrect username / password !'

        except pd.errors.EmptyDataError:
            print("The CSV file is empty")
            msg = "No Username and Password stored!!"
        else:
            print("Dataframe loaded successfully!!")    
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        is_login = df_register_data[(df_register_data['username'] == username)]
        print("register login",is_login.head())

        if not is_login.empty:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            df_register_data.loc[len(df_register_data.index)] = [username, password, email] 
            msg = 'You have successfully registered !'
            add_df_to_csv(df_register_data,"data.csv")
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template('register.html', msg = msg)

def add_df_to_csv(df, csv):
    with open(csv, 'a') as f:
        df.to_csv(f, header=f.tell()==0, index=False)

if __name__ == "__main__":
    app.run(debug=True,port=5000)

