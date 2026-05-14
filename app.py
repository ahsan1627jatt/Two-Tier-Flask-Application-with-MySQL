import os
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Ahsan's Personal Info for the app
AHSAN_INFO = {
    'name': 'Ahsan Sarwar',
    'role': 'DevOps Engineer Intern Aspirant',
    'location': 'Liaqatpur, Punjab, Pakistan',
    'email': 'Ahsanjutt1627@gmail.com',
    'github': 'https://github.com/ahsan1627jatt',
    'linkedin': 'https://www.linkedin.com/in/ahsan-sarwar-3232b4290',
    'bio': 'Computer Science graduate passionate about Docker, Linux, and Cloud Automation'
}

# MySQL Configuration from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'mysql')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'root')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'devops')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

def init_db():
    """Initialize database table if not exists"""
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            mysql.connection.commit()
            cur.close()
            print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database init error: {e}")

@app.route('/')
def index():
    """Home page - Display all messages"""
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id, name, message, created_at FROM messages ORDER BY created_at DESC')
        messages = cur.fetchall()
        cur.close()
        return render_template('index.html', messages=messages, ahsan=AHSAN_INFO)
    except Exception as e:
        print(f"❌ Error fetching messages: {e}")
        return render_template('index.html', messages=[], ahsan=AHSAN_INFO)

@app.route('/submit', methods=['POST'])
def submit():
    """Submit a new message"""
    try:
        new_message = request.form.get('new_message')
        name = request.form.get('name', 'Anonymous')
        
        if not new_message or len(new_message.strip()) == 0:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute(
            'INSERT INTO messages (name, message) VALUES (%s, %s)',
            (name[:50], new_message[:500])  # Limit input length
        )
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'success': True,
            'message': new_message,
            'name': name,
            'timestamp': 'Just now'
        })
    except Exception as e:
        print(f"❌ Submit error: {e}")
        return jsonify({'error': 'Failed to save message'}), 500

@app.route('/health')
def health():
    """Health check endpoint for Docker"""
    return jsonify({'status': 'healthy', 'app': 'Ahsan Flask App'})

@app.route('/about')
def about():
    """About page with Ahsan's info"""
    return render_template('about.html', ahsan=AHSAN_INFO)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)