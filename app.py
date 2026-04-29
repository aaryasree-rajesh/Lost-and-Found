from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_should_be_long_and_random'

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Database setup
DATABASE = 'lost_and_found.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create lost_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lost_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            location TEXT,
            date_lost DATE,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create found_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS found_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            location TEXT,
            date_found DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default admin if not exists
    cursor.execute("SELECT * FROM admins WHERE admin_id = ?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admins (admin_id, password) VALUES (?, ?)", ("admin", "admin123"))
    
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Strip whitespace from user_id
        user_id = request.form.get('user_id', '').strip()
        
        # Check if user exists, if not create new user
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            # Create new user
            try:
                cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
                conn.commit()
            except sqlite3.IntegrityError:
                pass
        
        conn.close()
        
        # Instead of using session, redirect with user_id as parameter
        return redirect(url_for('dashboard', user_id=user_id))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Get user_id from URL parameter as fallback
    user_id = request.args.get('user_id')
    
    if not user_id:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user_id=user_id)

@app.route('/report_lost', methods=['GET', 'POST'])
def report_lost():
    # Get user_id from URL parameter
    user_id = request.args.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        item_name = request.form['item_name']
        category = request.form['category']
        description = request.form['description']
        location = request.form['location']
        date_lost = request.form['date_lost']
        
        # Get user id from database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            user_db_id = user[0]
            cursor.execute("""
                INSERT INTO lost_items (user_id, item_name, category, description, location, date_lost)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_db_id, item_name, category, description, location, date_lost))
            conn.commit()
        
        conn.close()
        flash('Lost item reported successfully!')
        # Redirect with user_id parameter
        return redirect(url_for('dashboard', user_id=user_id))
    
    # Pass user_id to template
    return render_template('report_lost.html', user_id=user_id)

@app.route('/report_found', methods=['GET', 'POST'])
def report_found():
    # Get user_id from URL parameter
    user_id = request.args.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        item_name = request.form['item_name']
        category = request.form['category']
        description = request.form['description']
        location = request.form['location']
        date_found = request.form['date_found']
        
        # Get user id from database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            user_db_id = user[0]
            cursor.execute("""
                INSERT INTO found_items (user_id, item_name, category, description, location, date_found)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_db_id, item_name, category, description, location, date_found))
            conn.commit()
        
        conn.close()
        flash('Found item reported successfully!')
        # Redirect with user_id parameter
        return redirect(url_for('dashboard', user_id=user_id))
    
    # Pass user_id to template
    return render_template('report_found.html', user_id=user_id)

@app.route('/search')
def search():
    # Get user_id from URL parameter
    user_id = request.args.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    keyword = request.args.get('keyword', '')
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Search lost items
    lost_query = """
        SELECT l.*, u.user_id FROM lost_items l
        JOIN users u ON l.user_id = u.id
        WHERE 1=1
    """
    found_query = """
        SELECT f.*, u.user_id FROM found_items f
        JOIN users u ON f.user_id = u.id
        WHERE 1=1
    """
    
    params = []
    if category:
        lost_query += " AND l.category = ?"
        found_query += " AND f.category = ?"
        params.append(category)
        params.append(category)
    
    if location:
        lost_query += " AND l.location = ?"
        found_query += " AND f.location = ?"
        params.append(location)
        params.append(location)
    
    if keyword:
        lost_query += " AND (l.item_name LIKE ? OR l.description LIKE ?)"
        found_query += " AND (f.item_name LIKE ? OR f.description LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
    
    cursor.execute(lost_query, params[:len(params)//2])
    lost_items = cursor.fetchall()
    
    cursor.execute(found_query, params[len(params)//2:])
    found_items = cursor.fetchall()
    
    conn.close()
    
    # Pass user_id to template
    return render_template('search.html', 
                          lost_items=lost_items, 
                          found_items=found_items,
                          category=category,
                          location=location,
                          keyword=keyword,
                          user_id=user_id)

@app.route('/my_reports')
def my_reports():
    # Get user_id from URL parameter
    user_id = request.args.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get user id
    cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        user_db_id = user[0]
        
        # Get user's lost items
        cursor.execute("""
            SELECT * FROM lost_items 
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_db_id,))
        lost_items = cursor.fetchall()
        
        # Get user's found items
        cursor.execute("""
            SELECT * FROM found_items 
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_db_id,))
        found_items = cursor.fetchall()
        
        conn.close()
        
        # Pass user_id to template
        return render_template('my_reports.html', 
                              lost_items=lost_items, 
                              found_items=found_items,
                              user_id=user_id)
    
    conn.close()
    return redirect(url_for('dashboard', user_id=user_id))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE admin_id = ? AND password = ?", (admin_id, password))
        admin = cursor.fetchone()
        conn.close()
        
        if admin:
            session['admin_id'] = admin_id
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM lost_items")
    total_lost = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM found_items")
    total_found = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    # Get recent reports
    cursor.execute("""
        SELECT l.*, u.user_id FROM lost_items l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.created_at DESC
        LIMIT 5
    """)
    recent_lost = cursor.fetchall()
    
    cursor.execute("""
        SELECT f.*, u.user_id FROM found_items f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
        LIMIT 5
    """)
    recent_found = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                          total_lost=total_lost,
                          total_found=total_found,
                          total_users=total_users,
                          recent_lost=recent_lost,
                          recent_found=recent_found)

@app.route('/admin/reports')
def admin_reports():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT l.*, u.user_id FROM lost_items l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.created_at DESC
    """)
    lost_items = cursor.fetchall()
    
    cursor.execute("""
        SELECT f.*, u.user_id FROM found_items f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
    """)
    found_items = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_reports.html', lost_items=lost_items, found_items=found_items)

@app.route('/admin/users')
def admin_users():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT u.*, 
               (SELECT COUNT(*) FROM lost_items WHERE user_id = u.id) as lost_count,
               (SELECT COUNT(*) FROM found_items WHERE user_id = u.id) as found_count
        FROM users u
        ORDER BY u.created_at DESC
    """)
    users = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)