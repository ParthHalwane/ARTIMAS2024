
    return render_template('login.html', messages=message,message_type=message_type)

@app.route('/register', methods=['POST','GET'])
def register():
    message = None
    message_type = None
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = get_user_by_email(email)
        if existing_user:
            if existing_user['verified']==True:
                message_type = 'error'
                message = 'Email already registered. Please use a different email.'
                message_type=message_type
            else: