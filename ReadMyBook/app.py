from flask import Flask, render_template, request,send_file,redirect
from PIL import Image
from gtts import gTTS
import pytesseract
from PyPDF2 import PdfReader
from flaskext.mysql import MySQL
import pygame
import mysql.connector
app = Flask(__name__)
###For Sound Effect####
pygame.init()
pygame.mixer.init()
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="coderprem",
  database="readmybook"
)
cursor = mydb.cursor()

mysql=MySQL()
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='coderprem'
app.config['MYSQL_DATABASE_DB']='readmybook'
app.config['MYSQL_DATABASE_HOST']='localhost'
mysql.init_app(app)

@app.route('/')
def home():
    return render_template("Loginpage.html")

@app.route('/aut',methods=["get","post"])
def aut():
    email=request.form['e']
    password1 = request.form['p']
    print(email)
    print(password1)
    cursor=mysql.connect().cursor()
    message4="Incorrect Username or password!"
    cursor.execute("select * from user where email='"+email+"' or mobile='"+email+"'and password='"+password1+"'")
    data=cursor.fetchone()
    print(data)
    if data is None:
        return render_template("Loginpage.html",message4=message4)
    else:
        pygame.mixer.music.load("intrormb.mp3")
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.2)
        return render_template("readmybook.html")

@app.route('/sign',methods=["get","post"])
def sign():
    email2=request.form['email2']
    cpassword = request.form['cpassword']
    firstname=request.form['first_name']
    phone=request.form['phone']
    lastname = request.form['last_name']
    print(email2)
    print(cpassword)
    print(firstname)
    print(phone)
    print(lastname)
    mycursor = mydb.cursor()
    sql = "insert into user(firstname,lastname,email,mobile,password) values (%s,%s,%s,%s,%s)"
    val = (firstname, lastname,email2, phone, cpassword)
    mycursor.execute(sql, val)
    mydb.commit()
    message5="Your Account Created Successfully!"
    return render_template("loginpage.html",message5=message5)

@app.route('/englishtovoice', methods=['get','post'])
def englishtovoice():
    return render_template('englishtovoice.html')
@app.route('/signup', methods=['get','post'])
def signup():
    return render_template('signup.html')

@app.route('/pdftovoice', methods=['get','post'])
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

@app.route('/imgtovoice', methods=['get','POST'])
def imgtovoice():
    selected_option = request.form.get('option')
    image = '/Users/premnathpalanichamy/Desktop/Final year project/static/uploaded_image.jpg'
    imgobj = Image.open(image)
    print(selected_option)
    country=selected_option
    text = pytesseract.image_to_string(imgobj)
    tts = gTTS(text, lang='en',tld=country)
    tts.save('/Users/premnathpalanichamy/Desktop/Final year project/static/rmb.mp3')
    image_path = '/static/uploaded_image.jpg'
    message="Your AudioBook is Ready! Play and Enjoy It"
    message2="AudioBook Generated Successfully. Please, Scroll down to read it!"
    return render_template("englishtovoice.html",image_path=image_path,message=message,message2=message2)
#to link back button
@app.route('/back',methods=['get','post'])
def back():
    return render_template("readmybook.html")
###download files
@app.route('/download')
def download():
    file_path = '/Users/premnathpalanichamy/Desktop/Final year project/static/rmb.mp3'  # Replace with the actual path to your file
    return send_file(file_path, as_attachment=True)
@app.route('/on',methods=['get','post'])
def on():
    pygame.mixer.music.load("Interstellar Cornfield ! Instrumental ! Bgm.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)

    while pygame.mixer.music.get_busy():
        continue
    return redirect(request.url)

@app.route('/off',methods=['get','post'])
def off():
    pygame.mixer.music.stop()
    return render_template("englishtovoice.html")
@app.route('/off1',methods=['get','post'])
def off1():
    pygame.mixer.music.stop()
    return render_template("pdftovoice.html")

@app.route('/ptv', methods=['get','post'])
def ptv():
    reader = PdfReader('/Users/premnathpalanichamy/Desktop/Final year project/static/pdfbook.pdf')
 # printing number of pages in pdf file
    print(len(reader.pages))
    # getting a specific page from the pdf file
    page = reader.pages[0]
 # extracting text from page
    text = page.extract_text()
    selected_option = request.form.get('option')
    print(selected_option)
    country=selected_option
    tts = gTTS(text, lang='en',tld=country)
    tts.save('/Users/premnathpalanichamy/Desktop/Final year project/static/pdfaudio.mp3')
    message1="Now your AudioBook is Ready! Play and Enjoy It"
    message3 = "AudioBook Generated Successfully. Please, Scroll down to read it!"
    pdf_path = '/static/pdfbook.pdf'
    return render_template("pdftovoice.html",pdf_path=pdf_path,message1=message1,message3=message3)
if __name__ == '__main__':
    app.run(debug=True,port=5000)
