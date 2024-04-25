import datetime
import os
from flask import Flask, jsonify, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from github import Github
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
# from flask_mail import Mail, Message
from bson import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

app.config['MONGO_URI'] = 'mongodb://parthhalwane:artimas2024pccoe@ac-yjnwgro-shard-00-00.ewdp2pv.mongodb.net:27017,ac-yjnwgro-shard-00-01.ewdp2pv.mongodb.net:27017,ac-yjnwgro-shard-00-02.ewdp2pv.mongodb.net:27017/?replicaSet=atlas-1276tn-shard-0&ssl=true&authSource=admin'
# app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = 'kolekarp04082003@gmail.com'
# app.config['MAIL_PASSWORD'] = 'xuux kbue owpp gfxv'
# app.config['MAIL_DEFAULT_SENDER'] = 'kolekarp04082003@gmail.com'

sender_emails = {'admin': 'artimas.pccoeaimsa@gmail.com', 'hackmatrix': 'hackmatrix.artimas@gmail.com', 'cyberneticvision': 'cyberneticvisions.artimas@gmail.com',
                 'houdiniheist': 'houdiniheist.artimas@gmail.com', 'pixelperfect': 'pixelperfect.artimas@gmail.com', 'neurodrain': 'neurodrain.artimas@gmail.com', 'amongus': 'amongus.artimas@gmail.com'}
sender_passwords = {'admin': 'nyia jzxb tdhx ufce', 'hackmatrix': 'yoiv gjgh prdy hoom', 'cyberneticvision': 'ebua amef adxt yhsi',
                    'houdiniheist': 'agyp chut sqwr mnjo', 'pixelperfect': 'cunb opdg ivph ygpl', 'neurodrain': 'gkts zorh dkga osdr', 'amongus': 'rpri zdqu laob wbva'}

client = MongoClient(app.config['MONGO_URI'])
db = client.artimas
# mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_id, name, email, password, college, department, phone, verified, events=[]):
        self.id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.college = college
        self.department = department
        self.phone = phone
        self.verified = verified
        self.events = events


def get_user_by_email(email):
    return db.users.find_one({'email': email})


def get_user_by_id(user_id):
    return db.users.find_one({'_id': ObjectId(user_id)})


def register_user(name, email, password, college, department, phone, verification_token):
    hashed_password = generate_password_hash(password)
    new_user = {
        'name': name,
        'email': email,
        'password': hashed_password,
        'college': college,
        'department': department,
        'phone': phone,
        'verified': False,
        'verification_token': verification_token,
        'events': []
    }
    user_id = db.users.insert_one(new_user).inserted_id

    verification_link = f'https://artimas.pccoeaimsa.org/verify/{verification_token}'
    subject = 'Email Verification for Registration'
    body = render_template('email_verification.html',
                           user=new_user, verification_link=verification_link)
    send_email(sender_email=sender_emails['admin'], sender_password=sender_passwords['admin'], recipient_emails=[
               new_user['email']], subject=subject, html_content=body)

    return str(user_id)


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    if user_data:
        if user_data['verified'] == True:
            return User(str(user_data['_id']), user_data['name'], user_data['email'], user_data['password'], user_data['college'], user_data['department'], user_data['phone'], user_data['verified'], user_data['events'])
    return None

@app.route('/')
def index():
    return render_template('index.html', messages='')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    message_type = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_data = get_user_by_email(email)

        if user_data and check_password_hash(user_data['password'], password):
            user = User(str(user_data['_id']), user_data['name'], user_data['email'], user_data['password'],
                        user_data['college'], user_data['department'], user_data['phone'], user_data['verified'])
            if user_data['verified'] == True:
                login_user(user)
                return redirect(url_for('events'))
            else:
                message_type = 'warning'
                return render_template('login.html', message='Please ensure you have verified your email through the verification link sent on the email.', message_type=message_type)

        elif user_data:
            message_type = 'kindofwarning'
            return render_template('login.html', message='Please enter the correct password', message_type=message_type)

        else:
            message_type = 'error'
            return render_template('login.html', message='Please ensure to sign up before you Sign in', message_type=message_type)

    return render_template('login.html', messages=message, message_type=message_type)


@app.route('/register', methods=['POST', 'GET'])
def register():
    message = None
    message_type = None
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        college = request.form.get('college')
        department = request.form.get('department')
        phone = request.form.get('phone')

        existing_user = get_user_by_email(email)
        if existing_user:
            if existing_user['verified'] == True:
                message_type = 'error'
                message = 'Email already registered. Please use a different email.'
                message_type = message_type
            else:
                message_type = 'warning'
                message = 'You have already registered, please click the verification link sent on the email.'
                message_type = message_type
        else:
            verification_token = generate_verification_token()
            user_id = register_user(
                name, email, password, college, department, phone, verification_token)
            user = User(user_id, name, email, password,
                        college, department, phone, False)
            message_type = 'success'
            message = 'Registration successful. Please check your email for verification instructions.'
            message_type = message_type

    return render_template('register.html', message=message, message_type=message_type)


@app.route('/verify/<token>')
def verify_email(token):
    user = db.users.find_one({'verification_token': token})

    if user:
        db.users.update_one({'_id': user['_id']}, {'$set': {'verified': True}})
        flash('Email verification successful. You can now log in.', 'success')
    else:
        flash('Invalid verification token. Please try again or contact support.', 'error')

    return redirect(url_for('index'))


@app.route('/events')
# @login_required
def events():
    # print(current_user.events)
    return render_template('events.html', user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


def send_email(sender_email, sender_password, recipient_emails, subject, html_content):
    # Set up the MIMEMultipart object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(recipient_emails)
    msg['Subject'] = subject

    # Attach the HTML content to the MIMEMultipart object
    msg.attach(MIMEText(html_content, 'html'))

    # Connect to the SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        # Start TLS for security
        server.starttls()

        # Log in to the email account
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_emails, msg.as_string())


def generate_verification_token():
    return str(ObjectId())

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')
  
@app.route('/sponsors')
def sponsors():
    return render_template('sponsors.html')
  
@app.route('/houdiniheist')
@login_required
def houdini_heist():
    return render_template('register_houdiniheist.html', user=current_user)


@app.route('/neurodrain')
@login_required
def neurodrain():
    return render_template('register_neurodrain.html', user=current_user)


@app.route('/pixelperfect')
@login_required
def pixelperfect():
    return render_template('register_pixelperfect.html', user=current_user)


@app.route('/hackmatrix')
@login_required
def hackmatrix():
    return render_template('register_hackmatrix.html', user=current_user)


@app.route('/amongus')
@login_required
def amongus():
    return render_template('register_amongus.html', user=current_user)


@app.route('/submitForm/neurodrain', methods=['POST'])
def submit_neurodrain():
    event = 'neurodrain'
    event_collection = db[event]
    msg = None

    try:
        # form_data = request.form  # Use request.form to get form data
        # Convert to a flat dictionary
        form_data = request.form.to_dict(flat=True)
        is_pccoe = True

        if 'paymentScreenshot' in request.files:
            payment_screenshot = request.files['paymentScreenshot']
            if payment_screenshot.filename != '':
                # Generate a unique filename (e.g., using timestamp)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"payment_screenshot_{timestamp}.png"

                # Read the file content as bytes
                file_content = payment_screenshot.read()

                # Use PyGithub to upload the file content to the repository
                g = Github('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')
                repo = g.get_repo('Prathmesh-Kolekar/Artimas24')

                # Specify the file path and commit message
                file_path = f'data/{filename}'
                commit_message = 'Upload payment screenshot'

                response = repo.create_file(
                    file_path, commit_message, file_content, branch='main')
                is_pccoe = False

        current_date = datetime.datetime.today()

        if 'pccoepune.org' in request.form.get('Email'):
            subject = 'Event Registration Confirmation'
            template = render_template('registeration_confirmation.html', user_name=request.form.get(
                'Name'), event=event)  # Adjust the path to your HTML template
            send_email(sender_emails['neurodrain'], sender_passwords['neurodrain'], [
                       request.form.get('Email')], subject, template)

        else:
            is_pccoe = False
            subject = 'Event Registration Initiated'
            template = render_template('registeration_hold.html', user_name=request.form.get(
                'Name'), event=event)  # Adjust the path to your HTML template
            send_email(sender_emails['neurodrain'], sender_passwords['neurodrain'], [
                       request.form.get('Email')], subject, template)

        # Create a single document with a dictionary structure
        # Process event registration form data
        event_data = {
            'date': current_date,
            'name': request.form.get('Name'),
            'college': request.form.get('College'),
            'department': request.form.get('Department'),
            'email': request.form.get('Email'),
            'contact': request.form.get('Phone'),
            'rules_accepted': 'Rules' in request.form,
            # 'user_id': current_user.id,  # Add the user ID for reference
            'is_pccoe': is_pccoe
        }

        # Insert the event data into the respective collection
        # event_collection.insert_one(event_data)

        # Update the events array for the current user
        db.users.update_one({'email': request.form.get('Email')}, {
                            '$push': {'events': event}})

        # subject = 'Event Registration Confirmation'
        # template = render_template('registeration_confirmation.html',user_name = request.form.get('Name'),event=event)  # Adjust the path to your HTML template
        # send_email(subject,request.form.get('Email'), template )

        db[event].insert_one(event_data)

        return jsonify({'success': True, 'message': 'Form data stored successfully.'}), 200
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Error storing form data.'}), 500


@app.route('/submitForm/amongus', methods=['POST'])
def submit_amongus():
    event = 'amongus'
    event_collection = db[event]
    msg = None

    try:
        # form_data = request.form  # Use request.form to get form data
        # Convert to a flat dictionary
        form_data = request.form.to_dict(flat=True)
        is_pccoe = True

        if 'paymentScreenshot' in request.files:
            payment_screenshot = request.files['paymentScreenshot']
            if payment_screenshot.filename != '':
                # Generate a unique filename (e.g., using timestamp)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"payment_screenshot_{timestamp}.png"

                # Read the file content as bytes
                file_content = payment_screenshot.read()

                # Use PyGithub to upload the file content to the repository
                g = Github('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')
                repo = g.get_repo('Prathmesh-Kolekar/Artimas24')

                # Specify the file path and commit message
                file_path = f'data/{filename}'
                commit_message = 'Upload payment screenshot'

                response = repo.create_file(
                    file_path, commit_message, file_content, branch='main')
                is_pccoe = False

        current_date = datetime.datetime.today()

        if 'pccoepune.org' in request.form.get('Email'):
            subject = 'Event Registration Confirmation'
            template = render_template('registeration_confirmation.html', user_name=request.form.get(
                'Name'), event=event)  # Adjust the path to your HTML template
            send_email(sender_emails['amongus'], sender_passwords['amongus'], [
                       request.form.get('Email')], subject, template)

        else:
            is_pccoe = False
            subject = 'Event Registration Initiated'
            template = render_template('registeration_hold.html', user_name=request.form.get(
                'Name'), event=event)  # Adjust the path to your HTML template
            send_email(sender_emails['amongus'], sender_passwords['amongus'], [
                       request.form.get('Email')], subject, template)

        # Create a single document with a dictionary structure
        # Process event registration form data
        event_data = {
            'date': current_date,
            'name': request.form.get('Name'),
            'college': request.form.get('College'),
            'department': request.form.get('Department'),
            'email': request.form.get('Email'),
            'contact': request.form.get('Phone'),
            'rules_accepted': 'Rules' in request.form,
            # 'user_id': current_user.id,  # Add the user ID for reference
            'is_pccoe': is_pccoe
        }

        # Insert the event data into the respective collection
        # event_collection.insert_one(event_data)

        # Update the events array for the current user
        db.users.update_one({'email': request.form.get('Email')}, {
                            '$push': {'events': event}})

        # subject = 'Event Registration Confirmation'
        # template = render_template('registeration_confirmation.html',user_name = request.form.get('Name'),event=event)
        # send_email(subject,request.form.get('Email'), template )

        db[event].insert_one(event_data)

        return jsonify({'success': True, 'message': 'Form data stored successfully.'}), 200
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Error storing form data.'}), 500


@app.route('/submitForm/pixelperfect', methods=['POST'])
def submit_pixelperfect():
    event = 'pixelperfect'
    event_collection = db[event]
    msg = None

    try:
        # form_data = request.form  # Use request.form to get form data
        # Convert to a flat dictionary
        form_data = request.form.to_dict(flat=True)
        is_pccoe = True

        if 'paymentScreenshot' in request.files:
            payment_screenshot = request.files['paymentScreenshot']
            if payment_screenshot.filename != '':
                # Generate a unique filename (e.g., using timestamp)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"payment_screenshot_{timestamp}.png"

                # Read the file content as bytes
                file_content = payment_screenshot.read()

                # Use PyGithub to upload the file content to the repository
                g = Github('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')
                repo = g.get_repo('Prathmesh-Kolekar/Artimas24')

                # Specify the file path and commit message
                file_path = f'data/{filename}'
                commit_message = 'Upload payment screenshot'

                response = repo.create_file(
                    file_path, commit_message, file_content, branch='main')
                is_pccoe = False

        current_date = datetime.datetime.today()

        if 'pccoepune.org' in request.form.get('Email'):
            subject = 'Event Registration Confirmation'
            template = render_template('registeration_confirmation.html', user_name=request.form.get(
                'Name'), event=event)  # Adjust the path to your HTML template
            send_email(sender_emails['pixelperfect'], sender_passwords['pixelperfect'], [
                       request.form.get('Email')], subject, template)

        else:
            is_pccoe = False
            subject = 'Event Registration Initiated'
            template = render_template('registeration_hold.html', user_name=request.form.get(
                'Name'), event=event)  # Adjust the path to your HTML template
            send_email(sender_emails['pixelperfect'], sender_passwords['pixelperfect'], [
                       request.form.get('Email')], subject, template)

        # Create a single document with a dictionary structure
        # Process event registration form data
        event_data = {
            'date': current_date,
            'name': request.form.get('Name'),
            'college': request.form.get('College'),
            'department': request.form.get('Department'),
            'email': request.form.get('Email'),
            'contact': request.form.get('Phone'),
            'rules_accepted': 'Rules' in request.form,
            # 'user_id': current_user.id,  # Add the user ID for reference
            'is_pccoe': is_pccoe
        }

        # Insert the event data into the respective collection
        # event_collection.insert_one(event_data)

        # Update the events array for the current user
        db.users.update_one({'email': request.form.get('Email')}, {
                            '$push': {'events': event}})

        # subject = 'Event Registration Confirmation'
        # template = render_template('registeration_confirmation.html',user_name = request.form.get('Name'),event=event)  # Adjust the path to your HTML template
        # send_email(subject,request.form.get('Email'), template )

        db[event].insert_one(event_data)

        return jsonify({'success': True, 'message': 'Form data stored successfully.'}), 200
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Error storing form data.'}), 500


@app.route('/submitForm/houdiniheist', methods=['POST'])
def submit_houdiniheist():
    event = 'houdiniheist'
    c = 0
    try:
        # form_data = request.form  # Use request.form to get form data
        # Convert to a flat dictionary
        form_data = request.form.to_dict(flat=True)
        is_pccoe = True

        # print(form_data)
        # Check if 'paymentScreenshot' is in request.files
        if 'paymentScreenshot' in request.files:
            payment_screenshot = request.files['paymentScreenshot']
            if payment_screenshot.filename != '':
                # Generate a unique filename (e.g., using timestamp)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"payment_screenshot_{timestamp}.png"

                # Read the file content as bytesF
                file_content = payment_screenshot.read()

                # Use PyGithub to upload the file content to the repository
                g = Github('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')
                repo = g.get_repo('Prathmesh-Kolekar/Artimas24')

                # Specify the file path and commit message
                file_path = f'data/{filename}'
                commit_message = 'Upload payment screenshot'

                # Print or log file content
                # print(f"File Content: {file_content}")

                # Print or log file path
                # print(f"File Path: {file_path}")

                # Create the file in the repository
                response = repo.create_file(
                    file_path, commit_message, file_content, branch='main')
                is_pccoe = False

                # Print or log GitHub API response
                # print(f"GitHub API Response: {response}")

        # Get the current date and time
        current_date = datetime.datetime.today()

        # Extract member data
        members = []
        # print(list(form_data))
        for i in range(1, 4):  # Update range to 4 to include member 3
            member_email = form_data.get(f'email{i}', {})
            # print(member_data)

            if 'pccoepune.org' in member_email:
                c += 1

            if member_email != 'aimsa.pccoepune.org':
                db.users.update_one({'email': member_email}, {
                                    '$push': {'events': event}})
                # print()
                member_entry = {
                    'name': form_data.get(f'name{i}', ''),
                    'email': form_data.get(f'email{i}', ''),
                    'college': form_data.get(f'college{i}', ''),
                    'phone': form_data.get(f'phone{i}', ''),
                }

            else:
                member_entry = {
                    'name': '',
                    'email': '',
                    'college': '',
                    'phone': '',
                }
            members.append(member_entry)

        if c == 3:
            is_pccoe = True
            subject = 'Event Registration Confirmation'
            template = render_template('registeration_confirmation_team.html', user_names=[
                                       members[0]['name'], members[1]['name'], members[2]['name']], event=event)  # Adjust the path to your HTML template
            send_email(sender_emails['houdiniheist'], sender_passwords['houdiniheist'], [
                       form_data.get('email1')], subject, template)

        else:
            is_pccoe = False
            subject = 'Event Registration Initiated'
            template = render_template('registeration_hold_team.html', user_names=[
                                       members[0]['name'], members[1]['name'], members[2]['name']], event=event)  # Adjust the path to your HTML template
            send_email(sender_emails['houdiniheist'], sender_passwords['houdiniheist'], [
                       form_data.get('email1')], subject, template)

        # Create a single document with a dictionary structure
        form_entry = {
            'date': current_date,
            'members': members,
            'is_pccoe': is_pccoe
        }

        # print(form_entry)

        db[event].insert_one(form_entry)

        return jsonify({'success': True, 'message': 'Form data stored successfully.'}), 200
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Error storing form data.'}), 500


@app.route('/submitForm/hackmatrix', methods=['POST'])
def submit_hackmatrix():
    event = 'hackmatrix'
    try:
        # form_data = request.form  # Use request.form to get form data
        # Convert to a flat dictionary
        form_data = request.form.to_dict(flat=True)
        is_pccoe = True

        # print(form_data)
        # Check if 'paymentScreenshot' is in request.files
        if 'paymentScreenshot' in request.files:
            payment_screenshot = request.files['paymentScreenshot']
            if payment_screenshot.filename != '':
                # Generate a unique filename (e.g., using timestamp)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"payment_screenshot_{timestamp}.png"

                # Read the file content as bytes
                file_content = payment_screenshot.read()

                # Use PyGithub to upload the file content to the repository
                g = Github('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')
                repo = g.get_repo('Prathmesh-Kolekar/Artimas24')

                # Specify the file path and commit message
                file_path = f'data/{filename}'
                commit_message = 'Upload payment screenshot'

                # Print or log file content
                # print(f"File Content: {file_content}")

                # Print or log file path
                # print(f"File Path: {file_path}")

                # Create the file in the repository
                response = repo.create_file(
                    file_path, commit_message, file_content, branch='main')
                # is_pccoe=False

                # Print or log GitHub API response
                # print(f"GitHub API Response: {response}")

        # Get the current date and time
        current_date = datetime.datetime.today()

        # Extract member data
        members = []
        # print(list(form_data))
        c = 0
        for i in range(1, 5):  # Update range to 4 to include member 3
            member_email = form_data.get(f'email{i}', {})
            # print(member_data)

            if 'pccoepune.org' in member_email:
                c += 1
            if member_email != 'aimsa.pccoepune.org':
                db.users.update_one({'email': member_email}, {
                                    '$push': {'events': event}})
                # print()

                member_entry = {
                    'name': form_data.get(f'name{i}', ''),
                    'email': form_data.get(f'email{i}', ''),
                    'college': form_data.get(f'college{i}', ''),
                    'phone': form_data.get(f'phone{i}', ''),
                    'github' : form_data.get(f'github{i}', ''),
                }

            else:
                member_entry = {
                    'name': '',
                    'email': '',
                    'college': '',
                    'phone': '',
                    'github': '',
                }
            members.append(member_entry)
        # print(members[0]['name'],members[0])
        if c == 4:
            is_pccoe = True
            subject = 'Event Registration Confirmation'
            template = render_template('registeration_confirmation_team.html', user_names=[
                                       members[0]['name'], members[1]['name'], members[2]['name'],members[3]['name']], event=event)  # Adjust the path to your HTML template
            send_email(sender_emails['hackmatrix'], sender_passwords['hackmatrix'], [
                       form_data.get('email1')], subject, template)

        else:
            is_pccoe = False
            subject = 'Event Registration Initiated'
            template = render_template('registeration_hold_team.html', user_names=[
                                       members[0]['name'], members[1]['name'], members[2]['name'],members[3]['name']], event=event)  # Adjust the path to your HTML template
            send_email(sender_emails['hackmatrix'], sender_passwords['hackmatrix'], [
                       form_data.get('email1')], subject, template)

        form_entry = {
            'date': current_date,
            'members': members,
            'is_pccoe': is_pccoe
        }

        # print(form_entry)

        db[event].insert_one(form_entry)

        return jsonify({'success': True, 'message': 'Form data stored successfully.'}), 200
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Error storing form data.'}), 500


@app.route('/verifyEmail/<event>', methods=['GET'])
def verify_person(event):
    email_to_verify = request.args.get('email')
    # event_collection = db[event]

    user = db.users.find_one({'email': email_to_verify, 'verified': True})

    if user:
        # print(user)
        if event in user['events']:
            return jsonify({'exists': True, 'error': 'Member already registered for the event.'})
        else:
            return jsonify({'exists': False, 'error': None})
    else:
        return jsonify({'exists': True, 'error': 'Member does not have an account yet'})


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/registercount')
@login_required
def registration_count():
    if current_user.email == 'parthhalwane@gmail.com' or current_user.email == 'prathmesh.kolekar21@pccoepune.org':

        user_count = db.users.count_documents({})  # Counting documents in the users collection
        return jsonify({'user_count': user_count})  # Returning JSON response with user count
    else:
        return render_template('index.html')

# @app.route('/temp_dash')
# @login_required
# def temp_dash():
#     return render_template('temp_dash.html', user=current_user)

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/<path:undefined_route>')
def handle_undefined_route(undefined_route):
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
