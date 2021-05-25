from flask import Flask, render_template, request, redirect, url_for, session, flash
import re
import MySQLdb.cursors
from flask_mysqldb import MySQL
import pymysql
import smtplib
from flask_mail import Mail, Message




app = Flask(__name__)
  
app.secret_key = 'kolaaa'


app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'hdG3JcxRPV'
app.config['MYSQL_PASSWORD'] = 'yV3zZaKLa5'
app.config['MYSQL_DB'] = 'hdG3JcxRPV'
mysql = MySQL(app)

con = pymysql.connect(host='remotemysql.com',
        user='hdG3JcxRPV',
        password='yV3zZaKLa5',
        db='hdG3JcxRPV',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

        

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods =['GET', 'POST'])
#users login
def login():
    global userid
    msg = ''
   
  
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password ))
        account = cursor.fetchone()
        print (account)
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid=  account[0]
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            
            msg = 'Logged in successfully !'
            return redirect(url_for('dashboard', msg=msg))
        elif  request.form['username'] == 'admin' or request.form['password'] == 'admin':
            return redirect(url_for('admin_panel'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

#users registeration
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
        account = cursor.fetchone()
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, email,password))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

#users dashboard
@app.route('/dashboard', methods =['GET'])
def dashboard():
    
    print(session["username"],session['id'])
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM pay WHERE username = % s', (session['username'],))
    account = cursor.fetchone()
    print(account)

    
    return render_template('dashboard.html',account = account)



#contact our services
@app.route('/contact')
def contact():

    return render_template('contact.html')
#logout
@app.route('/logout')
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('login.html')

#admin_panel
@app.route('/admin_panel')
def admin_panel():
    con = pymysql.connect(host='remotemysql.com',
        user='hdG3JcxRPV',
        password='yV3zZaKLa5',
        db='hdG3JcxRPV',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

    try:

        with con.cursor() as cur:

            cur.execute('SELECT * FROM pay')

            data = cur.fetchall()

            for row in data:
                print(row['id'], row['name'])

    finally:
        con.close()
        return render_template('admin_panel.html', pay = data)
 
@app.route('/add_contact', methods=['POST'])
#add user payement details
def add_pay():
    con = pymysql.connect(host='remotemysql.com',
            user='hdG3JcxRPV',
            password='yV3zZaKLa5',
            db='hdG3JcxRPV',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)

    try:

        with con.cursor() as cur:
            if request.method == 'POST':
                username = request.form['username']
                products = request.form['products']
                cost = request.form['cost']
                duedate = request.form['duedate']
                payment_status = request.form['payment_status']
                cur.execute("INSERT INTO pay (username, products, cost, duedate, payment_status) VALUES (%s,%s,%s,%s,%s)", (username, products, cost, duedate, payment_status))
                con.commit()
                flash('Payment Added successfully')
    finally:
        return redirect(url_for('admin_panel'))

#edit user payment details

@app.route('/edit/<userid>', methods = ['POST', 'GET'])
def get_pay(userid):
    with con.cursor() as cur:
        cur.execute('SELECT * FROM pay WHERE userid = %s', (userid))
        data = cur.fetchall()
        cur.close()
        print(data[0])
        return render_template('edit.html', pay = data[0])



 #update user payment details
@app.route('/update/<userid>', methods=['POST'])
def update_pay(userid):
    cur=mysql.connection.cursor()
    if request.method == 'POST':
        username = request.form['username']
        products = request.form['products']
        cost = request.form['cost']
        duedate = request.form['duedate']
        payment_status = request.form['payment_status']
        cur.execute('UPDATE pay SET username = %s,products = %s,cost = %s,duedate = %s,payment_status = %s WHERE userid = %s', (username, products, cost, duedate, payment_status, userid))
        flash('Payment Updated Successfully')
        mysql.connection.commit()
        return redirect(url_for('admin_panel'))

 #delete the user payment details
@app.route('/delete/<string:userid>', methods = ['POST','GET'])
def delete_pay(userid):
    cur=mysql.connection.cursor()
    cur.execute('DELETE FROM pay WHERE userid = {0}'.format(userid))
    mysql.connection.commit()
    flash('Payment Removed Successfully')
    return redirect(url_for('admin_panel'))

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'chandanabanahatti@gmail.com'#put your eamil account
app.config['MAIL_PASSWORD'] = 'Banahatti@11' #put your email password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
#app.config['MAIL_DEFAULT_SENDER'] = '@gmail.com'
mail = Mail(app)
#send message to users for due_payment
@app.route('/sendmail', methods=['GET', 'POST'])
def sendmail():
    if request.method == 'POST':
        rec = request.form['recipient']
        msg = Message('Hello', sender='chandanabanahatti@gmail.com',recipients=[rec])
        msg.body = ('Dear customer, please pay the pending payment with '
                    'Dgital payment Book')
        msg.html = ('<h1>Digitalpayment Book</h1>'
                        '<p>Dear customer, please pay the pending payment with '
                        '<b>Digital payment book app</b>!</p>')
        mail.send(msg)
        flash(f'A test message was sent to {rec}.')
        return redirect(url_for('sendmail'))
    return render_template('sendmail.html')



if __name__ == '__main__':
   app.run(host='127.0.0.1',debug = True, port = 5000)