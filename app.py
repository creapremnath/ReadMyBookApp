import os
import logging
from flask import Flask, render_template, request, send_file, redirect, session, url_for, jsonify
from database import init_db, db
from models import User, Pages
from PyPDF2 import PdfReader
import uuid
from config import IMAGEDIR, AUDIODIR, PDFDIR, SECRET_KEY
from controller import text_to_audio,image_to_text,text_to_audio2
from mp3joiner import merge_mp3

# Initialize Flask application
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Set up logging
log_folder = 'logs'
os.makedirs(log_folder, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_folder, 'app.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Initialize the database
init_db(app)

# Ensure directories exist
os.makedirs(IMAGEDIR, exist_ok=True)
os.makedirs(AUDIODIR, exist_ok=True)
os.makedirs(PDFDIR, exist_ok=True)

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        logging.info(f"User {session['user_name']} accessed the home page.")
        return redirect(url_for('readmybook'))
    logging.info("User accessed the home page (not logged in).")
    return render_template("loginpage.html")

@app.route('/aut', methods=["GET", "POST"])
def aut():
    if request.method == 'POST':
        email_or_mobile = request.form['e']
        password1 = request.form['p']
        logging.debug(f"Login attempt with email/phone: {email_or_mobile}")

        # Query the database for the user
        user = User.query.filter(
            (User.email == email_or_mobile) | (User.mobile == email_or_mobile),
            User.password == password1
        ).first()

        if user is None:
            logging.warning(f"Failed login attempt with email/phone: {email_or_mobile}")
            message4 = "Incorrect Username or Password!"
            return render_template("loginpage.html", message4=message4)
        else:
            session['user_id'] = user.user_id
            session['user_name'] = user.firstname
            session['email'] = user.email  # Store email in session
            logging.info(f"User {user.firstname} logged in successfully.")

            return redirect(url_for('readmybook'))
    return redirect(url_for('home'))
################################################################

def create_pages(user_id, page_type, page_uuid,file_extension):
    try:
        # Ensure that the page type and page_uuid are valid before attempting to create the page
        if not user_id or not page_type or not page_uuid:
            logging.error("Missing required parameters: user_id, page_type, or page_uuid")
            return "Error: Missing required parameters!"

        # Create a new page object and save it to the database
        new_page = Pages(
            user_id=user_id,
            page_uuid=page_uuid,
            page_type=page_type,
            file_extension=file_extension
        )
        db.session.add(new_page)  # Add the new page to the session
        db.session.commit()  # Commit the session to persist the new page
        logging.info(f"New page created: {page_type} with UUID: {page_uuid} for user {user_id}")
        return "Page created successfully!"
    except Exception as e:
        # Rollback the transaction in case of an error
        db.session.rollback()
        logging.error(f"Error creating new page: {str(e)}")
        return "Error creating new page!"

################################################################





@app.route('/sign', methods=["GET", "POST"])
def sign():
    if request.method == 'POST':
        email2 = request.form['email2']
        cpassword = request.form['cpassword']
        firstname = request.form['first_name']
        phone = request.form['phone']
        lastname = request.form['last_name']
        logging.debug(f"Sign-up attempt with email: {email2}, phone: {phone}")

        try:
            # Create new user and save to the database
            new_user = User(
                firstname=firstname,
                lastname=lastname,
                email=email2,
                mobile=phone,
                password=cpassword
            )
            db.session.add(new_user)
            db.session.commit()
            logging.info(f"New user created: {firstname} {lastname}, email: {email2}, phone: {phone}")
            message5 = "Your Account Created Successfully!"
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating new user: {str(e)}")
            message5 = "Account creation failed! Email or phone already exists."
        return render_template("loginpage.html", message5=message5)

@app.route('/readmybook', methods=['GET', 'POST'])
def readmybook():
    if 'user_id' not in session:
        logging.warning("User tried to access 'readmybook' page without being logged in.")
        return redirect(url_for('home'))

    email = session.get('email')  # Use .get() to avoid KeyError if not set
    user_id = session.get('user_id')  # Use .get() for safety
    data={ "user_id": user_id,
            "user_name": (session.get('user_name')).upper(),
                  "email": email
            }
    logging.info(f"User {session.get('user_name')} accessed the 'readmybook' page.")
    return render_template('readmybook.html',  user_id=user_id, userdata=data)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    user_name = session.get('user_name', 'Unknown')
    session.clear()  # Clear the session to log the user out
    logging.info(f"User {user_name} logged out.")
    return redirect(url_for('home'))

@app.route('/upload', methods=['POST'])
def upload():
    user_id = session['user_id']
    image = request.files['image']
    common_uuid=str(uuid.uuid4())
    image_name = f"{common_uuid}.jpg"
    image.save(f'{IMAGEDIR}/{image_name}')
    image_path = f"/{IMAGEDIR}/{image_name}"
    session['common_uuid'] = common_uuid
    logging.info(f"Image uploaded: {image.filename}")
    return render_template('englishtovoice.html', image_path=image_path,common_uuid=common_uuid, user_id=user_id)

@app.route('/uploadpdf', methods=['POST'])
def uploadpdf():
    user_id = session['user_id']
    pdf = request.files['PDF']
    common_uuid_pdf=str(uuid.uuid4())
    pdf_name = f"{common_uuid_pdf}.pdf"  # Use a common UUID for better uniqueness and avoid conflicts.
    pdf.save(f'{PDFDIR}/{pdf_name}')
    pdf_path = f"/{PDFDIR}/{pdf_name}"
    session['common_uuid_pdf'] = common_uuid_pdf
    logging.info(f"PDF uploaded: {pdf.filename}")
    return render_template('pdftovoice.html', pdf_path=pdf_path,common_uuid_pdf=common_uuid_pdf, user_id=user_id)

@app.route('/imgtovoice', methods=['GET', 'POST'])
def imgtovoice():
    user_id = session['user_id']
    common_uuid = session.get('common_uuid')
    if not common_uuid:
        return "Not Found!", 400

    selected_option = request.form.get('option')
    logging.info("selected Option",selected_option)

    # image to text conversion
    extracted_text=image_to_text(path=IMAGEDIR,image_name=f"{common_uuid}.jpg")
    logging.info(f"Text extracted from image: {extracted_text}")

    # text to audio conversion
    audio_filename=text_to_audio(voice=selected_option,text=extracted_text,audio_id=common_uuid)
    print(audio_filename)

    result = create_pages(user_id=user_id, page_type="image", page_uuid=common_uuid,file_extension="jpg")
    print(result)  # Output: "Page created successfully!" or "Error creating new page!"
    logging.info("Pages created successfully")

    message2 = "AudioBook Generated Successfully. Please, Scroll down to read it!"
    image_path = f"{IMAGEDIR}/{common_uuid}.jpg"  # Replace with the actual path to your image fileprint(image_path)
    return render_template('englishtovoice.html', image_path=image_path, audio_filename=audio_filename,message2=message2,user_id=user_id)



@app.route('/download')
def download():
    file_path = 'static/rmb.mp3'  # Replace with the actual path to your file
    logging.info(f"Downloading file: {file_path}")
    return send_file(file_path, as_attachment=True)

@app.route('/ptv', methods=['GET', 'POST'])
def ptv():
    user_id = session['user_id']
    common_uuid_pdf = session.get('common_uuid_pdf')
    if not common_uuid_pdf:
        return "Not Found!", 400
    reader = PdfReader(f'{PDFDIR}/{common_uuid_pdf}.pdf')
    selected_option = request.form.get('option')
    print(len(reader.pages))
    # extracting text from page
    #multiple pages pdf file
    text = ''
    files_to_merge=[]
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        page_text = page.extract_text()
        audio_list=text_to_audio2(voice=selected_option,text=page_text,audio_id=f"a{i}")

        print(f"Audio generated for page {i+1}: {audio_list}")
        files_to_merge.append(audio_list)
        text += page_text
    f = open("pdftroubleshoot.txt", "a")
    f.write(text)
    f.close()
    # merging audio files
    print("list of files to merge",files_to_merge)
    audio_path=merge_mp3(files=files_to_merge,output_file=common_uuid_pdf)
    message2 = "AudioBook Generated Successfully. Please, Scroll down to read it!"
    pdf_path = f"{PDFDIR}/{common_uuid_pdf}.pdf"
    logging.info(f"AudioBook generated from PDF.")
    result = create_pages(user_id=user_id, page_type="pdf", page_uuid=common_uuid_pdf,file_extension="pdf")
    print(result)  # Output: "Page created successfully!" or "Error creating new page!"
    logging.info("Pages created successfully")
    return render_template("pdftovoice.html", pdf_path=pdf_path, audio_filename=audio_path,message2=message2)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


@app.route('/englishtovoice', methods=['GET', 'POST'])
def englishtovoice():
    return render_template('englishtovoice.html')

@app.route('/back', methods=['GET', 'POST'])
def back():
    if 'user_id' not in session:  # Check if the user is logged in
        logging.warning("User tried to access 'readmybook' page without being logged in.")
        return redirect(url_for('readmybook'))  # Redirect to the 'readmybook' page if not logged in
    return render_template("loginpage.html")  # Render login page if user is logged in


@app.route('/myfiles')
def myfiles():
    if 'user_id' not in session:  # Check if the user is logged in
        logging.warning("User tried to access 'myfiles' page without being logged in.")
        return redirect(url_for('home'))  # Redirect to the home page if not logged in

    # Fetch files from the database for the logged-in user
    user_id = session['user_id']
    pages = Pages.query.filter_by(user_id=user_id).all()


    # Create a list of dictionaries representing the pages
    page_data = [
        {"id":page.id,"type": page.page_type, "title": f"Page ID {page.id}", "path": f"/static/{page.page_type}s/{page.page_uuid}.{page.file_extension}", "audio": f"/static/audios/{page.page_uuid}.mp3"}
        for page in pages
    ]
    print(page_data)
    # Log or debug the page data
    logging.info(f"Page data retrieved for user {user_id}: {page_data}")

    # Return the result as JSON (optional for API use)
    # If you want to debug, you can return this JSON in the browser
    # return jsonify(page_data)

    # Render the HTML page, passing the page data
    return render_template('myfiles.html', files=page_data)


@app.route('/deletefile', methods=['POST'])
def deletefiles():
    data = request.get_json()
    print(data)  # Extract JSON data from the request

    # Extract file_id from the payload
    file_id = data.get('file_id')

    # Check if file_id is provided
    if not file_id:
        return jsonify({'success': False, 'message': 'File ID is missing'}), 400

    # Find the file in the database using the file_id
    file_to_delete = Pages.query.filter_by(id=file_id).first()
    print("file_to_delete",file_to_delete)



    if file_to_delete:
        try:
            # Construct the file paths for file1 and file2
            file1 = f"static/{file_to_delete.page_type}s/{file_to_delete.page_uuid}.{file_to_delete.file_extension}"  # File 1 path
            file2 = f"{AUDIODIR}{file_to_delete.page_uuid}.mp3"  # File 2 path
            print(file1,file2)


            # Delete file1 if it exists
            try:
                os.remove(file1)
                os.remove(file2)
            except OSError:
                logging.error(f"Error deleting file: {file1}")


            # Delete the file record from the database
            db.session.delete(file_to_delete)
            db.session.commit()  # Commit the deletion to the database

            return jsonify({'success': True, 'message': 'Files deleted successfully'}), 200

        except Exception as e:
            # If there was an error during the deletion process
            db.session.rollback()  # Rollback any changes if something goes wrong
            return jsonify({'success': False, 'message': f'Error deleting files: {str(e)}'}), 500
    else:
        return jsonify({'success': False, 'message': 'File not found in the database'}), 404



@app.route('/pdftovoice', methods=['GET', 'POST'])
def pdftovoice():
    return render_template('pdftovoice.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
