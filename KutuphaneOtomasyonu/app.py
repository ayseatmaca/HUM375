import json
import os
import sqlite3
from flask import Flask, send_from_directory, request, jsonify
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

DB_FILE = 'library.db'
OLD_JSON_DB = 'database.json'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Books Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            year TEXT,
            isbn TEXT,
            genre TEXT,
            cover TEXT,
            status TEXT DEFAULT 'available' -- 'available' or 'borrowed'
        )
    ''')
    # Members Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            join_date TEXT
        )
    ''')
    # Transactions Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT,
            member_id INTEGER,
            borrow_date TEXT,
            return_date TEXT,
            status TEXT DEFAULT 'active', -- 'active' or 'returned'
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(member_id) REFERENCES members(id)
        )
    ''')
    
    # Check if migration from JSON is needed
    c.execute('SELECT COUNT(*) as count FROM books')
    count = c.fetchone()['count']
    if count == 0 and os.path.exists(OLD_JSON_DB):
        try:
            with open(OLD_JSON_DB, 'r', encoding='utf-8') as f:
                books = json.load(f)
                for b in books:
                    c.execute('''
                        INSERT INTO books (id, title, author, year, isbn, genre, cover, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'available')
                    ''', (str(b.get('id', '')), b.get('title',''), b.get('author',''), str(b.get('year','')), b.get('isbn',''), b.get('genre',''), b.get('cover','')))
            print("Successfully migrated data from database.json to library.db")
        except Exception as e:
            print(f"Error migrating json to sqlite: {e}")
            
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return app.send_static_file('kutuphane.html')

# --- BOOKS API ---

@app.route('/api/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in books])

@app.route('/api/books', methods=['POST'])
def add_book():
    new_book = request.json
    book_id = new_book.get('id', str(datetime.now().timestamp()))
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO books (id, title, author, year, isbn, genre, cover, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'available')
    ''', (str(book_id), new_book.get('title'), new_book.get('author'), new_book.get('year'), 
          new_book.get('isbn'), new_book.get('genre'), new_book.get('cover')))
    conn.commit()
    conn.close()
    
    new_book['id'] = book_id
    new_book['status'] = 'available'
    return jsonify(new_book), 201

@app.route('/api/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    updated_data = request.json
    conn = get_db_connection()
    conn.execute('''
        UPDATE books 
        SET title = ?, author = ?, year = ?, isbn = ?, genre = ?, cover = ?
        WHERE id = ?
    ''', (updated_data.get('title'), updated_data.get('author'), updated_data.get('year'),
          updated_data.get('isbn'), updated_data.get('genre'), updated_data.get('cover'), str(book_id)))
    conn.commit()
    
    book = conn.execute('SELECT * FROM books WHERE id = ?', (str(book_id),)).fetchone()
    conn.close()
    
    if book:
        return jsonify(dict(book))
    return jsonify({"error": "Book not found"}), 404

@app.route('/api/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM books WHERE id = ?', (str(book_id),))
    if not c.fetchone():
        conn.close()
        return jsonify({"error": "Book not found"}), 404
        
    c.execute('DELETE FROM books WHERE id = ?', (str(book_id),))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# --- MEMBERS API ---

@app.route('/api/members', methods=['GET'])
def get_members():
    conn = get_db_connection()
    members = conn.execute('SELECT * FROM members').fetchall()
    conn.close()
    return jsonify([dict(m) for m in members])

@app.route('/api/members', methods=['POST'])
def add_member():
    data = request.json
    join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    
    if phone:
        if cursor.execute('SELECT id FROM members WHERE phone = ?', (phone,)).fetchone():
            conn.close()
            return jsonify({"error": "Bu telefon numarası ile kayıtlı bir üye zaten var!"}), 400
            
    if email:
        if cursor.execute('SELECT id FROM members WHERE email = ?', (email,)).fetchone():
            conn.close()
            return jsonify({"error": "Bu e-posta adresi ile kayıtlı bir üye zaten var!"}), 400

    cursor.execute('''
        INSERT INTO members (full_name, phone, email, join_date)
        VALUES (?, ?, ?, ?)
    ''', (data.get('full_name'), phone, email, join_date))
    member_id = cursor.lastrowid
    conn.commit()
    
    member = conn.execute('SELECT * FROM members WHERE id = ?', (member_id,)).fetchone()
    conn.close()
    return jsonify(dict(member)), 201

@app.route('/api/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    
    if phone:
        if cursor.execute('SELECT id FROM members WHERE phone = ? AND id != ?', (phone, member_id)).fetchone():
            conn.close()
            return jsonify({"error": "Bu telefon numarası başka bir üye tarafından kullanılıyor!"}), 400
            
    if email:
        if cursor.execute('SELECT id FROM members WHERE email = ? AND id != ?', (email, member_id)).fetchone():
            conn.close()
            return jsonify({"error": "Bu e-posta adresi başka bir üye tarafından kullanılıyor!"}), 400
            
    cursor.execute('''
        UPDATE members 
        SET full_name = ?, phone = ?, email = ?
        WHERE id = ?
    ''', (data.get('full_name'), phone, email, member_id))
    conn.commit()
    member = conn.execute('SELECT * FROM members WHERE id = ?', (member_id,)).fetchone()
    conn.close()
    if member:
        return jsonify(dict(member))
    return jsonify({"error": "Member not found"}), 404

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM members WHERE id = ?', (member_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# --- TRANSACTIONS API ---

@app.route('/api/transactions/borrow', methods=['POST'])
def borrow_book():
    data = request.json
    book_id = str(data.get('book_id'))
    member_id = data.get('member_id')
    borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db_connection()
    b = conn.execute('SELECT status FROM books WHERE id = ?', (book_id,)).fetchone()
    if not b or b['status'] == 'borrowed':
        conn.close()
        return jsonify({"error": "Kitap zaten ödünçte veya bulunamadı"}), 400
        
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (book_id, member_id, borrow_date, status)
        VALUES (?, ?, ?, 'active')
    ''', (book_id, member_id, borrow_date))
    
    cursor.execute("UPDATE books SET status = 'borrowed' WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/transactions/return', methods=['POST'])
def return_book():
    data = request.json
    book_id = str(data.get('book_id'))
    return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    t = cursor.execute('''
        SELECT id FROM transactions 
        WHERE book_id = ? AND status = 'active'
        ORDER BY borrow_date DESC LIMIT 1
    ''', (book_id,)).fetchone()
    
    if not t:
        conn.close()
        return jsonify({"error": "Aktif işlem bulunamadı"}), 400
        
    cursor.execute('''
        UPDATE transactions SET status = 'returned', return_date = ?
        WHERE id = ?
    ''', (return_date, t['id']))
    
    cursor.execute("UPDATE books SET status = 'available' WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/books/<book_id>/history', methods=['GET'])
def get_book_history(book_id):
    conn = get_db_connection()
    history = conn.execute('''
        SELECT t.id, t.borrow_date, t.return_date, t.status, m.full_name, m.phone
        FROM transactions t
        JOIN members m ON t.member_id = m.id
        WHERE t.book_id = ?
        ORDER BY t.borrow_date DESC
    ''', (str(book_id),)).fetchall()
    conn.close()
    return jsonify([dict(h) for h in history])

@app.route('/api/members/<int:member_id>/history', methods=['GET'])
def get_member_history(member_id):
    conn = get_db_connection()
    history = conn.execute('''
        SELECT t.id, t.borrow_date, t.return_date, t.status, b.title, b.author
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        WHERE t.member_id = ?
        ORDER BY t.borrow_date DESC
    ''', (member_id,)).fetchall()
    conn.close()
    return jsonify([dict(h) for h in history])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
