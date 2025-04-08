from flask import Flask, render_template, redirect, url_for, flash, request, session, Response, send_from_directory
from datetime import datetime , timedelta
import os
import re
import pickle
import cv2
import tensorflow as tf
from functools import wraps
import numpy as np
from PIL import Image
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "supersecretkey"

#MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'autotrustai'

mysql = MySQL(app)


# Load the TensorFlow model
model = tf.saved_model.load("models/")  


#upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(img_path):
    """ Convert image to the expected model format """
    img = Image.open(img_path).convert("RGB")
    img = img.resize((300, 300 * img.size[1] // img.size[0]))  # Resize to model input size
    inp_numpy = np.array(img)[None]
    
    return inp_numpy

def predict_image(img_path):
    classes = [ "Fraud" ,  "Non-Fraud" , ]
    inp = tf.constant(preprocess_image(img_path), dtype='float32')
    class_scores = model(inp)[0].numpy() 
    prediction = classes[class_scores.argmax()]# Get the output 

    return  prediction, class_scores

current_time = datetime.now()

##################################################################################################################
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)


#########################################-------index---------##################################################
@app.route('/')
def index():
   
   return render_template("index.html", title='InsurSafe AI', current_time=current_time)


##########################################------admin--------##################################################
@app.route('/admin/admin')
def admin():
   return render_template("admin/admin.html", title='Admin')

@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():   
   msg = ''
   if request.method == 'POST' :
      email = request.form.get('email')
      password = request.form.get('password')

      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute("SELECT * FROM tbl_admins WHERE is_active = 1 AND email = %s", (email,))
      account = cursor.fetchone()
      if account and check_password_hash(account['password'], password):
         session['loggedin'] = True
         session['id'] = account['id']
         session['adminname'] = account['username']
         msg = 'Logged in successfully !'
         if 5 <= current_time.hour <= 11:
            greeting = "Good morning"
         elif 12 <= current_time.hour <= 15:
            greeting = "Good afternoon"
         else:
            greeting = "Good evening"
         return render_template("/admin/pages/dashboard.html", title='Admin dashboard', msg = msg, msg_type="success", greeting=greeting)
      else:
         msg = 'Incorrect email or password !'
         return render_template("/admin/admin.html", title='Admin', msg = msg, msg_type="error")
   
 
@app.route('/adminlogout')
def adminlogout():
    session.clear()   
    return redirect(url_for('admin'))

@app.route('/admin/pages/dashboard')
def dashboard():
   return render_template("/admin/pages/dashboard.html", title='Dashboard')
 
@app.route('/admin/pages/usersmanagement')
def usersmanagement():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM tbl_users") 
    users = cursor.fetchall()
    cursor.close()  
    return render_template("/admin/pages/usersmanagement.html", title='User Management', users=users)


@app.route('/admin/pages/companies')
def companies():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM tbl_insurance_company") 
    companies = cursor.fetchall()
    cursor.close()    
    return render_template("/admin/pages/companies.html", title='Companies', companies=companies)


@app.route('/admin/pages/claimverification')
def claimverification():
   return render_template("/admin/pages/claimverification.html", title='Claim verification')

@app.route('/verification', methods=['GET', 'POST'])
def verification():
   result = None

   if request.method == 'POST':
        if 'imagefile' not in request.files:
            return "No file uploaded", 400
        
        file = request.files['imagefile']
        
        if file.filename == '' or not allowed_file(file.filename):
            return "Invalid file type", 400
       
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(img_path)

        result = predict_image(img_path) 

        cursor = mysql.connection.cursor()
        cursor.execute("""INSERT INTO tbl_claims_verification (image_name, prediction, score) VALUES (%s, %s, %s)""", (file.filename, result[0],round(result[1][0] * 100, 2)))
        mysql.connection.commit()
        cursor.close()

   return render_template("/admin/pages/claimverification.html", title='Claim verification', result=result)


@app.route('/admin/pages/claims_history')
def claims_history():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM tbl_claims_verification ORDER BY created_at DESC")
    claims = cursor.fetchall()
    cursor.close()
    
    return render_template("/admin/pages/claims_history.html", title='Claims History', claims=claims)




####################################################------user------##################################################

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('user'))
        return f(*args, **kwargs)
    return decorated_function


def nocache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        if isinstance(response, Response):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
        return response
    return decorated_function




@app.route('/user/user')
def user():
   return render_template("/user/user.html", title='User')

@app.route('/userlogin', methods=['GET','POST'])
@nocache
def userlogin():   
   msg = ''
   if request.method == 'POST' :
      email = request.form.get('email')
      password = request.form.get('password')

      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute("SELECT * FROM tbl_users WHERE email = %s", (email,))
      account = cursor.fetchone()
      if account and check_password_hash(account['password'], password):
         session['loggedin'] = True
         session['id'] = account['id']
         session['username'] = account['username']
         msg = 'Logged in successfully !'
         if 5 <= current_time.hour <= 11:
            greeting = "Good morning"
         elif 12 <= current_time.hour <= 15:
            greeting = "Good afternoon"
         else:
            greeting = "Good evening"
         return render_template("/user/pages/dashboard.html", title='User dashboard', msg = msg, msg_type="success", greeting=greeting, fname=session['username'])
      else:
         msg = 'Incorrect email or password !'
         return render_template("/user/user.html", title='User', msg = msg, msg_type="error")
   
 
@app.route('/userlogout')
@nocache
def userlogout():
    session.clear()
    response = redirect(url_for('user'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
    

@app.route("/user/pages/dashboard")
@login_required
@nocache
def userdashboard():
    if 5 <= current_time.hour <= 11:
        greeting = "Good morning"
    elif 12 <= current_time.hour <= 15:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    return render_template("/user/pages/dashboard.html", title='User dashboard', greeting=greeting, fname=session['username'])


@app.route('/usersignup', methods=['GET','POST'])
@nocache
def usersignup():
   msg = ''
   if request.method == 'POST':
      fname = request.form.get('fname')
      lname = request.form.get('lname')
      gender = request.form.get('gender')
      email = request.form.get('email')
      phone = request.form.get('phone')
      city = request.form.get('city')
      street = request.form.get('street')
      password = generate_password_hash(request.form.get('password'))
   
      cursor = mysql.connection.cursor()
      cursor.execute(f"SELECT * FROM tbl_users WHERE email = '{email}'")
      existing_user = cursor.fetchone()
      
      if existing_user:
         msg = 'Account already exists !'
         return render_template("/user/user.html", title='User', msg = msg, msg_type="warning")
      elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
         msg = 'Invalid email address !'
         return render_template("/user/user.html", title='User', msg = msg, msg_type="error")
      elif not re.match(r'[A-Za-z]+', fname):
         msg = 'First name must contain only characters !'
         return render_template("/user/user.html", title='User', msg = msg, msg_type="info")
      else:       
         cursor.execute("""INSERT INTO tbl_users (first_name, last_name, username, gender, email, phone, city, street, password, join_date)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (fname, lname, (fname + " " + lname,), gender, email, phone, city, street, password, current_time))
         mysql.connection.commit()
         cursor.close()
         msg = 'Account created successfully !'
         return render_template("/user/user.html", title='User', msg = msg, msg_type="success")

@app.route('/user/forgot_pw')
def forgot_pw():
   return render_template("/user/forgot_pw.html", title='Forgot password')

# @app.route('/user/pages/new_account')
# def new_account():
#    return render_template("/user/pages/new_account.html", title='New account')







#############################################-------insurance_company----------####################################
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('insurance_company'))
        return f(*args, **kwargs)
    return decorated_function


def nocache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        if isinstance(response, Response):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
        return response
    return decorated_function

@app.route('/insurance_company/insurance_company')
def insurance_company():
   return render_template("/insurance_company/insurance_company.html", title='Insurance Company')




@app.route('/insurance_company_login', methods=['GET', 'POST']) 
@nocache
def insurance_company_login():   
    msg = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_insurance_company WHERE email = %s", (email,))
        account = cursor.fetchone()

        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']  # ID de l'assurance
            session['company_name'] = account['company_name']
            session['company_id'] = account['id']  # Stocke l'ID de la compagnie pour filtrer les utilisateurs

            msg = 'Logged in successfully !'
            return redirect(url_for('insurance_company_dashboard'))
        else:
            msg = 'Incorrect email or password !'   
            return render_template("/insurance_company/insurance_company.html", title='Insurance Company', msg=msg, msg_type="error")  



     


@app.route('/insurance_company_logout')
@nocache
def insurance_company_logout():
    session.clear()
    response = redirect(url_for('insurance_company'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response



@app.route("/insurance_company/pages/dashboard")
def insurance_company_dashboard():
    cursor = mysql.connection.cursor()

    # Date actuelle et date du mois précédent
    today = datetime.today()
    first_day_current_month = today.replace(day=1)
    first_day_previous_month = (first_day_current_month - timedelta(days=1)).replace(day=1)

    # Nombre total d'utilisateurs
    cursor.execute("SELECT COUNT(*) FROM tbl_users")
    total_users = cursor.fetchone()[0]

    # Nombre d'utilisateurs du mois précédent
    cursor.execute("SELECT COUNT(*) FROM tbl_users WHERE join_date < %s", (first_day_current_month,))
    previous_total_users = cursor.fetchone()[0]

    user_growth = round(((total_users - previous_total_users) / previous_total_users * 100), 2) if previous_total_users > 0 else round(total_users * 100, 2)


   
    # Nombre total de réclamations analysées
    cursor.execute("SELECT COUNT(*) FROM tbl_claims_verification")
    total_claims = cursor.fetchone()[0]

    # Nombre de réclamations analysées le mois précédent
    cursor.execute("SELECT COUNT(*) FROM tbl_claims_verification WHERE created_at < %s", (first_day_current_month,))
    previous_total_claims = cursor.fetchone()[0]

    claims_growth = round(((total_claims - previous_total_claims) / previous_total_claims * 100), 2) if previous_total_claims > 0 else round(total_claims * 100, 2)

    # Nombre total de fraudes détectées
    cursor.execute("SELECT COUNT(*) FROM tbl_claims_verification WHERE fraud_detected = 1")
    total_frauds = cursor.fetchone()[0]

    # Nombre de fraudes détectées le mois précédent
    cursor.execute("SELECT COUNT(*) FROM tbl_claims_verification WHERE fraud_detected = 1 AND created_at < %s", (first_day_current_month,))
    previous_total_frauds = cursor.fetchone()[0]

    fraud_growth = round(((total_frauds - previous_total_frauds) / previous_total_frauds * 100), 2) if previous_total_frauds > 0 else round(total_frauds * 100, 2)

   
    

    cursor.close()

    return render_template(
        "insurance_company/pages/dashboard.html",
        total_users=total_users,
        user_growth=user_growth,
        total_claims=total_claims,
        claims_growth=claims_growth,
        total_frauds=total_frauds,
        fraud_growth=fraud_growth,
    )

    


@app.route('/insurance_company_signup', methods=['GET','POST'])
@nocache
def insurance_company_signup():
    msg = ''
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        registration_number = request.form.get('registration_number')
        official_email = request.form.get('official_email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        country = request.form.get('country')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        responsible_phone = request.form.get('responsible_phone')
        password = generate_password_hash(request.form.get('password'))

        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT * FROM tbl_insurance_company WHERE email = '{email}'")
        existing_company = cursor.fetchone()

        if existing_company:
            msg = 'Account already exists !'
            return render_template("/insurance_company/insurance_company.html", title='Insurance Company', msg=msg, msg_type="warning")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
            return render_template("/insurance_company/insurance_company.html", title='Insurance Company', msg=msg, msg_type="error")
        else:
            cursor.execute("""INSERT INTO tbl_insurance_company 
                (company_name, registration_number, official_email, phone, address, country, 
                full_name, email, responsible_phone, password, join_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s)""", 
                (company_name, registration_number, official_email, phone, address, country, 
                full_name, email, responsible_phone, password, current_time))

            mysql.connection.commit()
            cursor.close()
            msg = 'Account created successfully !'
            return render_template("/insurance_company/insurance_company.html", title='Insurance Company', msg=msg, msg_type="success")



@app.route('/insurance_company/pages/claimverification2')
def claimverification2():
   return render_template("/insurance_company/pages/claimverification.html", title='Claim verification')

@app.route('/verification2', methods=['GET', 'POST'])
def verification2():
   result = None

   if request.method == 'POST':
        if 'imagefile' not in request.files:
            return "No file uploaded", 400
        
        file = request.files['imagefile']
        
        if file.filename == '' or not allowed_file(file.filename):
            return "Invalid file type", 400
       
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(img_path)

        result = predict_image(img_path)    

   return render_template("/insurance_company/pages/claimverification.html", title='Claim verification', result=result)
 


@app.route('/insurance_company/pages/usermanagement')
def user_management():
    if 'company_id' not in session:
        return "Unauthorized", 403  # Assurez-vous que l'utilisateur est connecté

    company_id = session['company_id']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM tbl_users WHERE company_id = %s", (company_id,))
    users = cursor.fetchall()
    cursor.close()
    
    return render_template("/insurance_company/pages/usermanagement.html", title='User Management', users=users)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Récupérer les informations de l'utilisateur avant suppression
    cursor.execute("SELECT first_name, last_name FROM tbl_users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        full_name = f"{user['first_name']} {user['last_name']}"
        cursor.execute("DELETE FROM tbl_users WHERE id = %s", (user_id,))
        mysql.connection.commit()
        flash(f"The user {full_name} has been successfully deleted.", "success")

    else:
        flash("User not found.", "danger")

    cursor.close()
    return redirect(url_for('user_management'))




@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        email = request.form['email']
        phone = request.form['phone']
        city = request.form['city']
        street = request.form['street']

        cursor.execute("""
            UPDATE tbl_users 
            SET first_name=%s, last_name=%s, gender=%s, email=%s, phone=%s, city=%s, street=%s 
            WHERE id=%s
        """, (first_name, last_name, gender, email, phone, city, street, user_id))

        mysql.connection.commit()
        cursor.close()
        flash(f"The user information for {first_name} {last_name} has been successfully updated.", "success")
        return redirect(url_for('user_management'))
    
    cursor.execute("SELECT * FROM tbl_users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    return render_template("/insurance_company/pages/edit_user.html", user=user)

@app.route('/insurance_company/pages/claims_history2')
def claims_history2():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM tbl_claims_verification ORDER BY created_at DESC")
    claims = cursor.fetchall()
    cursor.close()
    
    return render_template("/insurance_company/pages/claims_history.html", title='Claims History', claims=claims)


@app.route('/insurance_company/pages/search_users', methods=['GET'])
@login_required
@nocache
def search_users():
    query = request.args.get('query', '').strip()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if query:
        cursor.execute("""SELECT * FROM tbl_users 
                  WHERE ID LIKE %s 
                  OR first_name LIKE %s 
                  OR last_name LIKE %s 
                  OR gender LIKE %s 
                  OR phone LIKE %s 
                  OR city LIKE %s 
                  OR street LIKE %s 
                  OR email LIKE %s""", 
               (f"%{query}%", f"%{query}%", f"%{query}%", 
                f"%{query}%", f"%{query}%", f"%{query}%", 
                f"%{query}%", f"%{query}%"))  # Ajout du dernier paramètre

    else:
        cursor.execute("SELECT * FROM tbl_users")

    users = cursor.fetchall()
    cursor.close()

    return render_template("/insurance_company/pages/usermanagement.html", title='Insurance Dashboard', users=users)





@app.route('/process_payment', methods=['POST'])
def process_payment():
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        expiry_month = request.form.get('expiry_month')
        expiry_year = request.form.get('expiry_year')
        card_name = request.form.get('card_name')
        cvc = request.form.get('cvc')

        if not card_number or not expiry_month or not expiry_year or not card_name or not cvc:
            flash('All fields are required!', 'warning')
            return redirect(url_for('claimverification2'))  # Rediriger vers la page appropriée

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM tbl_payments WHERE card_number = %s", (card_number,))
        existing_payment = cursor.fetchone()

        if existing_payment:
            flash('Payment information already exists!', 'warning')
        else:
            cursor.execute("""INSERT INTO tbl_payments 
                (card_number, expiry_month, expiry_year, card_name, cvc) 
                VALUES (%s, %s, %s, %s, %s)""", 
                (card_number, expiry_month, expiry_year, card_name, cvc))

            mysql.connection.commit()
            cursor.close()

            flash('Payment processed successfully!', 'success')

        return redirect(url_for('claimverification2'))  # Toujours rediriger après flash()


@app.route('/insurance_company/pages/forgot_pw')
def insurance_company_forgot_pw():
   return render_template("/insurance_company/pages/forgot_pw.html", title='Forgot password')

if __name__ == '__main__':
    app.run(debug=True)









