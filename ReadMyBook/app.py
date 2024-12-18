from flask import Flask, render_template, request, send_file, redirect
from PIL import Image
from gtts import gTTS
import pytesseract
from PyPDF2 import PdfReader
import sqlite3
import os

app = Flask(__name__)

# SQLite database setup
DATABASE = 'readmybook.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enables accessing columns by name
    return conn

# Initialize the SQLite database if not already created
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                mobile TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def home():
    return render_template("Loginpage.html")

@app.route('/aut', methods=["GET", "POST"])
def aut():
    email = request.form['e']
    password1 = request.form['p']
    print(email)
    print(password1)

    conn = get_db_connection()
    cursor = conn.cursor()
    message4 = "Incorrect Username or password!"
    cursor.execute(
        "SELECT * FROM user WHERE (email=? OR mobile=?) AND password=?",
        (email, email, password1)
    )
    data = cursor.fetchone()
    conn.close()

    print(data)
    if data is None:
        return render_template("Loginpage.html", message4=message4)
    else:
        return render_template("readmybook.html")

@app.route('/sign', methods=["GET", "POST"])
def sign():
    email2 = request.form['email2']
    cpassword = request.form['cpassword']
    firstname = request.form['first_name']
    phone = request.form['phone']
    lastname = request.form['last_name']
    print(email2)
    print(cpassword)
    print(firstname)
    print(phone)
    print(lastname)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO user (firstname, lastname, email, mobile, password) VALUES (?, ?, ?, ?, ?)",
            (firstname, lastname, email2, phone, cpassword)
        )
        conn.commit()
        message5 = "Your Account Created Successfully!"
    except sqlite3.IntegrityError:
        message5 = "Account creation failed! Email or phone already exists."
    finally:
        conn.close()

    return render_template("loginpage.html", message5=message5)

@app.route('/englishtovoice', methods=['GET', 'POST'])
def englishtovoice():
    return render_template('englishtovoice.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/pdftovoice', methods=['GET', 'POST'])
def pdftovoice():
    return render_template('pdftovoice.html')

@app.route('/upload', methods=['POST'])
def upload():
    image = request.files['image']
    image.save('static/uploaded_image.jpg')
    image_path = '/static/uploaded_image.jpg'
    return render_template('englishtovoice.html', image_path=image_path)

@app.route('/uploadpdf', methods=['POST'])
def uploadpdf():
    pdf = request.files['PDF']
    pdf.save('static/pdfbook.pdf')
    pdf_path = '/static/pdfbook.pdf'
    return render_template('pdftovoice.html', pdf_path=pdf_path)

@app.route('/imgtovoice', methods=['GET', 'POST'])
def imgtovoice():
    selected_option = request.form.get('option')
    image = 'static/uploaded_image.jpg'
    imgobj = Image.open(image)
    print(selected_option)
    country = selected_option
    text = pytesseract.image_to_string(imgobj)
    tts = gTTS(text, lang='en', tld=country)
    tts.save('static/rmb.mp3')
    image_path = '/static/uploaded_image.jpg'
    message = "Your AudioBook is Ready! Play and Enjoy It"
    message2 = "AudioBook Generated Successfully. Please, Scroll down to read it!"
    return render_template("englishtovoice.html", image_path=image_path, message=message, message2=message2)

@app.route('/back', methods=['GET', 'POST'])
def back():
    return render_template("readmybook.html")

@app.route('/download')
def download():
    file_path = 'static/rmb.mp3'  # Replace with the actual path to your file
    return send_file(file_path, as_attachment=True)

@app.route('/ptv', methods=['GET', 'POST'])
def ptv():
    reader = PdfReader('static/pdfbook.pdf')
    # printing number of pages in pdf file
    print(len(reader.pages))
    # getting a specific page from the pdf file
    page = reader.pages[0]
    # extracting text from page
    text = page.extract_text()
    selected_option = request.form.get('option')
    print(selected_option)
    country = selected_option
    tts = gTTS(text, lang='en', tld=country)
    tts.save('static/pdfaudio.mp3')
    message1 = "Now your AudioBook is Ready! Play and Enjoy It"
    message3 = "AudioBook Generated Successfully. Please, Scroll down to read it!"
    pdf_path = '/static/pdfbook.pdf'
    return render_template("pdftovoice.html", pdf_path=pdf_path, message1=message1, message3=message3)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
