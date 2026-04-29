from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/', methods=['GET', 'POST'])
def login():
    print(f"DEBUG: Login route called with method: {request.method}")
    print(f"DEBUG: Request form data: {request.form}")
    print(f"DEBUG: Request args: {request.args}")
    
    if request.method == 'POST':
        user_id = request.form.get('user_id', '')
        print(f"DEBUG: User ID from form: '{user_id}'")
        session['user_id'] = user_id
        print(f"DEBUG: Set session user_id to: {session.get('user_id')}")
        return redirect(url_for('dashboard'))
    
    print("DEBUG: Rendering login form")
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Login</title>
    </head>
    <body>
        <h1>Test Login</h1>
        <form method="POST" action="/">
            <input type="text" name="user_id" placeholder="Enter User ID" required>
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    print(f"DEBUG: Dashboard route called")
    print(f"DEBUG: Session contents: {dict(session)}")
    if 'user_id' not in session or not session.get('user_id'):
        print("DEBUG: No user_id in session or user_id is empty, redirecting to login")
        return redirect(url_for('login'))
    return f"<h1>Welcome, {session['user_id']}!</h1>"

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)