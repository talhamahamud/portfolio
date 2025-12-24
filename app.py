from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import datetime
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename
import markdown

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_this' # Change this in production
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

# Custom Markdown Postprocessor for Image Captions
from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension
import re

class ImageCaptionPostprocessor(Postprocessor):
    """Convert <img> tags to <figure> with <figcaption>"""
    def run(self, text):
        # Pattern to match img tags with alt text
        img_pattern = r'<img\s+([^>]*?)alt="([^"]*)"([^>]*?)/?>'
        
        def replace_img(match):
            before_alt = match.group(1)
            alt_text = match.group(2)
            after_alt = match.group(3)
            
            # Reconstruct the img tag
            img_tag = f'<img {before_alt}alt="{alt_text}"{after_alt}>'
            
            # Wrap in figure with figcaption
            if alt_text:  # Only add caption if alt text exists
                return f'<figure class="image-with-caption">{img_tag}<figcaption>{alt_text}</figcaption></figure>'
            else:
                return img_tag
        
        return re.sub(img_pattern, replace_img, text)

class ImageCaptionExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(ImageCaptionPostprocessor(md), 'image_caption', 175)

# Custom Text Filter
@app.template_filter('markdown')
def render_markdown(text):
    return markdown.markdown(text, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.nl2br',
        ImageCaptionExtension()
    ])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database Helper Function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Login Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Admin Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Initialize Database
def init_db():
    conn = get_db_connection()
    # Create table with date column
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    conn = get_db_connection()
    # Fetch recent 5 posts for home page
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC LIMIT 5').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/blog')
def blog():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<int:post_id>')
def post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    if post is None:
        return "Post not found", 404
    return render_template('post.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'password123': # Hardcoded admin password
            session['logged_in'] = True
            session['is_admin'] = True  # Set admin flag
            return redirect(url_for('create'))
        else:
            error = 'Invalid password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('is_admin', None)  # Clear admin flag
    return redirect(url_for('index'))

@app.route('/admin/new', methods=('GET', 'POST'))
@admin_required  # Only admins can create posts
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if title and content:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('blog'))

    return render_template('create_post.html')

@app.route('/blog/<int:id>/edit', methods=('GET', 'POST'))
@admin_required
def edit(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?',
                     (title, content, id))
        conn.commit()
        conn.close()
        return redirect(url_for('post', post_id=id))
        
    conn.close()
    return render_template('create_post.html', post=post)

@app.route('/blog/<int:id>/delete', methods=('POST',))
@admin_required  # Only admins can delete posts
def delete(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()
    if post:
        conn.execute('DELETE FROM posts WHERE id = ?', (id,))
        conn.commit()
    conn.close()
    return redirect(url_for('blog'))

@app.route('/blog/<int:id>/upvote', methods=['POST'])
def upvote(id):
    conn = get_db_connection()
    conn.execute('UPDATE posts SET upvotes = COALESCE(upvotes, 0) + 1 WHERE id = ?', (id,))
    conn.commit()
    
    # Get new count
    new_count = conn.execute('SELECT upvotes FROM posts WHERE id = ?', (id,)).fetchone()['upvotes']
    conn.close()
    
    
    return {'success': True, 'upvotes': new_count}

@app.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    if file and allowed_file(file.filename):
        # Create directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Secure and Unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        return {'url': url_for('static', filename=f'uploads/{filename}')}
    
    return {'error': 'File type not allowed'}, 400

if __name__ == '__main__':
    # Initialize DB (run once manually or check existence)
    # We will let the user call init_db helper or just run it on startup for simplicity here
    init_db() 
    app.run(debug=True)
