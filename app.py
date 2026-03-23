from flask import Flask, request, render_template, redirect, url_for
import os
from flask import jsonify
from datetime import datetime
from flask import session, flash
from werkzeug.utils import secure_filename
# remove comment when get dynamodb working
# import key_config as keys
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Replace with a secure secret key
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

app.config['UPLOAD_FOLDER'] = 'static/posters'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# remove 8 comment when get dynamodb working

#======================
# DynamoDB connection
#======================

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

# dynomodbtable(create these tables in dynamodb manually)
users_table = dynamodb.Table('users')
admin_table = dynamodb.Table('admins')
contact_table = dynamodb.Table('ContactForm')
bookings_table = dynamodb.Table('bookings')
#=====================
# SNS
#=====================

ADMIN_TOPIC_ARN = 'arn:aws:sns:us-east-1:ACCOUNT_ID:AdminNotifications'
CUSTOMER_TOPIC_ARN = 'arn:aws:sns:us-east-1:ACCOUNT_ID:CustomerNotifications'

def send_admin_notification(subject, message):
    """Send notification to admin topic (your email only)."""
    try:
        response = sns.publish(
            TopicArn=ADMIN_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        print(f"Admin notification sent! ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error sending admin notification: {e}")

def send_customer_notification(subject, message):
    """Send notification to customer topic (customers subscribed)."""
    try:
        response = sns.publish(
            TopicArn=CUSTOMER_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        print(f"Customer notification sent! ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error sending customer notification: {e}")

def subscribe_customer_email(email):
    """Subscribe a customer's email to CustomerNotifications topic."""
    try:
        response = sns.subscribe(
            TopicArn=CUSTOMER_TOPIC_ARN,
            Protocol='email',
            Endpoint=email
        )
        print(f"Subscription request sent to {email}. Confirm it from inbox.")
    except ClientError as e:
        print(f"Error subscribing customer email: {e}")


#==================
# MOVIE DATA 
#==================
movies = {
    "MOV001": {
        "title": "MARCO",
        "description": "It is a ruthless gangster seeking vengeance for his brother's brutal murder.",
        "poster": "Images/Action.jpg",
        "genre": "Action",
        "release_date": "2024-12-20",
        "duration": "2h 25m",
        "price": 200,
        "address": "271, RP Malik Rd, Shahazadi Mandi, Sadar Bazar, Agra Cantt, Idgah Colony, Agra, Uttar Pradesh 282001",
        "theatersName": "7D Theater",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["10:00 AM", "1:00 PM", "6:00 PM", "9:00 PM"]
    },
    "MOV002": {
        "title": "JUMANJI",
        "description": "It is a fan-film prequel that reveals the origin of the cursed game.",
        "poster": "Images/Advanture.jpg",
        "genre": "Adventure",
        "release_date": "1995-01-01",
        "duration": "1h 44m",
        "price": 180,
        "address": "Logix City Centre Mall, Lucknow, Uttar Pradesh",
        "theatersName": "PVR Logix IMAX",
        "theaters": ["PVR Cinemas", "IMAX", "Cinepolis"],
        "showtimes": ["11:00 AM", "4:00 PM", "8:00 PM"]
    },
    "MOV003": {
        "title": "GOLMAAL: FUN UNLIMITED",
        "description": "It is about four mischievous, con-artist-Gopal,Madhav,Lucky & Laxman who are expelled from college.",
        "poster": "Images/Comady.jpg",
        "genre": "Comedy",
        "release_date": "2006-07-14",
        "duration": "2h 30m",
        "price": 150,
        "address": "Mall of Avadh, Indira Nagar, Lucknow, Uttar Pradesh",
        "theatersName": "Mall Of Avadh",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["10:00 AM", "1:00 PM", "6:00 PM", "9:00 PM"]
    },
    "MOV004": {
        "title": "THE DRAMA",
        "description": "This movie exploring intense human experiences,relationships and personal struggle.",
        "poster": "Images/Drama.jpg",
        "genre": "Drama",
        "release_date": "2026-04-03",
        "duration": "2h 30m",
        "price": 200,
        "address": "Vinayak Plaza, Civil Lines, Lucknow, Uttar Pradesh",
        "theatersName": "PVR Vinayak",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["11:00 AM", "4:00 PM", "8:00 PM"]
    },
    "MOV005": {
        "title": "MALEFICENT",
        "description": "This is a live-action Disney film that reimagines Sleeping Beauty from the villain's perspective, exploring her backstory as a betrayed fairy protector.",
        "poster": "Images/Fantasy.jpg",
        "genre": "Fantasy",
        "release_date": "2014-05-30",
        "duration": "2h 15m",
        "price": 220,
        "address": "Civil Lines, Lucknow, Uttar Pradesh",
        "theatersName": "Magique Theater",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["10:00 AM", "1:00 PM", "6:00 PM", "9:00 PM"]
    },
    "MOV006": {
        "title": "THE CONJURING: LAST RITES",
        "description": "It is the final entry in the main conjuring series, following Ed and Lorraine Warren as they face a definitive, high-stakes case based on the haunting of the Smurl family Pennsylvania.",
        "poster": "Images/HORRER.jpg",
        "genre": "Horror",
        "release_date": "2025-09-05",
        "duration": "2h 15m",
        "price": 250,
        "address": "Wave Cinemas, Lucknow, Uttar Pradesh",
        "theatersName": "Wave Cinemas",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["11:00 AM", "4:00 PM", "8:00 PM"]
    },
    "MOV007": {
        "title": "THE SEARCH",
        "description": "The Search movie follows a man looking for life outside the universe who instead finds connection with a grieving family.",
        "poster": "Images/Mistory.jpg",
        "genre": "Mystery",
        "release_date": "2014-05-21",
        "duration": "2h 14m",
        "address": "3rd Floor, GIP Mall, Ghaziabad, Uttar Pradesh",
        "theatersName": "BIG Cinemas",
        "price": 180,
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["10:00 AM", "1:00 PM", "6:00 PM", "9:00 PM"]
    }
    
}

slides ={
    "MOV008": {
        "title": "Frieren: Beyond Journey's End, Season 2",
        "description": "Second season of. The adventure is over but life goes on for an elf mage just beginning to learn what living is all about...",
        "poster": "Images/frierenPoster.jpg",
        "genre": "Fantasy",
        "release_date": "2026-01-16",
        "duration": "24m each episode",
        "price": 50,
        "address": "CBW-58, Sector 32, Noida (near Noida City Centre Metro)",
        "theatersName": "PVR Logix Noida",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["11:00 AM", "4:00 PM", "8:00 PM"]
    },
    "MOV009": {
        "title": "Hell's Paradise Season 2",
        "description": "Second season of . The Edo period is nearinf its end. Gabimaru, shinobi formerly known as the strongest, in Iwagakure who is now...",
        "poster": "Images/hellParadisePoster.jpg",
        "genre": "Dark fantasy anime",
        "release_date": "2026-01-11",
        "duration": "24m each episode",
        "price": 50,
        "address": "CBW-58, Sector 32, Noida (near Noida City Centre Metro).",
        "theatersName": "PVR Logix Noida",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["11:30 AM", "4:30 PM", "8:30 PM"]
    },
    "MOV0010": {
        "title": "Jujutsu Kaisen (Culling Game, Part 1)",
        "description": "The third season of Jujutsu Kaisen. After the Shibuya incident, a deadly jujutsu battle known as the Culling Game orchestrated by Noritoshi Kamoe...",
        "poster": "Images/JJKCGPoster.jpg",
        "genre": "Dark Fantasy, Shonen, Action, Supernatural",
        "release_date": "2026-01-09",
        "duration": "24m each episode",
        "price": 50,
        "address": "CBW-58, Sector 32, Noida (near Noida City Centre Metro).",
        "theatersName": "PVR Logix Noida",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["12:00 AM", "5:00 PM", "9:00 PM"]
    },
    "MOV0011": {
        "title": "Kunon the Sorcerer Can See",
        "description": "Born blind, Kunon aims to be the first person to use water magic to create new eyes for himself. After five months of study, he has already surpasse...",
        "poster": "Images/ktscsPoster.jpg",
        "genre": "Fantasy, Magic, Adventure",
        "release_date": "2026-01-04",
        "duration": "23m each episode",
        "price": 50,
        "address": "CBW-58, Sector 32, Noida (near Noida City Centre Metro).",
        "theatersName": "PVR Logix Noida",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["1:00 PM", "6:00 PM", "10:00 PM"]
    },
    "MOV0012": {
        "title": "Noble Reincarnation: Born Blessed, So I'll Obtain Unlimited Power",
        "description": "Noah, the world's strongest six-year-old, holds the fortunate position of being the Thirteenth Prince of the emperor. Born with an infinite level cap",
        "poster": "Images/nobleReincarnationPoster.jpg",
        "genre": "Fantasy, Isekai, Adventure",
        "release_date": "2026-01-08",
        "duration": "23m each episode",
        "price": 50,
        "address": "CBW-58, Sector 32, Noida (near Noida City Centre Metro).",
        "theatersName": "PVR Logix Noida",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["1:30 PM", "6:30 PM", "10:30 PM"]
    },
    "MOV0013": {
        "title": "One Piece",
        "description": "Gold Roger was known as the 'Pirate King', the strongest and most Infamous being to have salled the Grand Line. The capture and execution...",
        "poster": "Images/onePiecePoster.jpg",
        "genre": "Shonen, Adventure, Fantasy, Action, Comedy",
        "release_date": "1999-10-20",
        "duration": "24m each episode",
        "price": 80,
        "address": "CBW-58, Sector 32, Noida (near Noida City Centre Metro)",
        "theatersName": "PVR Logix Noida",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["2:00 PM", "7:00 PM", "11:00 PM"]
    },
    "MOV0014": {
        "title": "Sentenced to Be a Hero",
        "description": "Hero is the worst punishment in the world. Those convicted of heinous crimes are sentenced to become 'Heroes' and forced to enter the...",
        "poster": "Images/SentencedToBeAHeroPoster.jpg",
        "genre": "Dark Fantasy, Action, Drama",
        "release_date": "2026-01-16",
        "duration": "24m each episode",
        "price": 50,
        "address": "CBW-58, Sector 32, Noida (near Noida City Centre Metro).",
        "theatersName": "PVR Logix Noida",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["2:30 PM", "7:30 PM", "11:00 PM"]
    }
}

#====================
# Home route
#====================

@app.route('/')
def index():
    return render_template('index.html', movies=movies, slides=slides)

@app.route('/home')
def home():
    if 'user' in session:
        return render_template('index.html', name=session['user'], movies=movies, slides=slides)
    else:
        return render_template('index.html', name="Guest", movies=movies, slides=slides)

# for direction to about page
@app.route('/about')
def about():
    return render_template('about.html')

# @app.route('/adminDashbord')
# def adminDashbord():
#     return render_template('AdminDashbord.html')

@app.route('/admindashboard')
def admin_dashboard_alt():
    if session.get('role') != 'admin':
        return "Unauthorized", 403
    return render_template('AdminDashbord.html', movies=movies)

@app.route('/AdminLogin')
def AdminLogin():
    return render_template('AdminL&S.html')

@app.route('/movie/<movie_id>')
def movie_detail(movie_id):
    if movie_id in movies:
        movie_data = movies[movie_id]
    elif movie_id in slides:
        movie_data = slides[movie_id]
    else:
        return "Movie not found", 404

    return render_template('movie.html', movie_data=movie_data, movie_id=movie_id)


#============================
# User Signup
#============================


# SIGNUP API
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('L&S.html')  # Optional signup page

    # POST method
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # Hash the password before storing
    hashed_password = generate_password_hash(password)

    users_table.put_item(
        Item={
            'email': email,
            'name': name,
            'password': hashed_password
        }
    )
    # Subscribe user to SNS topic
    subscribe_customer_email(email)
    # Send SNS notification
    send_admin_notification("New User Signup", f"User {name} ({email}) has registered.")

    msg = "Registration Complete. Please Login to your account"
    return render_template('L&S.html', msg=msg)


#============================
# User Login 
#============================


# LOGIN API
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('L&S.html')

    # POST login
    email = request.form['email']
    password = request.form['password']

    response = users_table.get_item(Key={'email': email})

    if 'Item' not in response:
        flash("User not found", "error")
        return redirect(url_for('login'))

    stored_password = response['Item']['password']

    if check_password_hash(stored_password, password):
        session['user'] = email
        session['session_id'] = str(uuid.uuid4())  # unique per login
        
        flash("Login successful!", "success")
        return redirect(url_for('home'))
    else:
        flash("Wrong password", "error")
        return redirect(url_for('login'))

#==========================
# Logout
#==========================

@app.route('/logout')
def logout():
    # ✅ Clear session on logout
    session.pop('user', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))


#==========================
# Book Ticket 
#==========================
@app.route('/book', methods=['POST'])
def book():
    if 'user' not in session:
        return jsonify({"message": "You must login before booking tickets."}), 403

    data = request.get_json()
    email = session['user']
    movie_id = data['movie_id']
    seats = int(data['seats'])
    theater = data['theater']
    showtime = data['showtime']

    movie = movies.get(movie_id) or slides.get(movie_id)
    if not movie:
        return jsonify({"message": "Invalid movie selection."}), 400

    total_amount = seats * movie['price']

    bookings_table.put_item(Item={
        'user_email': email,
        'booking_id': str(uuid.uuid4()),
        'movie_id': movie_id,
        'movie_title': movie['title'],
        'seats': seats,
        'seat_numbers': data['seat_numbers'],
        'amount': total_amount,
        'theater': theater,
        'showtime': showtime,
        'booking_date': datetime.utcnow().isoformat()
    })
    # Send SNS notification
    confirmation_message = (
        f"Booking confirmed!\n\n"
        f"Movie: {movie['title']}\n"
        f"Theater: {theater}\n"
        f"Showtime: {showtime}\n"
        f"Seats: {seats} ({', '.join(data['seat_numbers'])})\n"
        f"Total Amount: ₹{total_amount}\n\n"
        f"Thank you for booking with us!"
    )

    send_customer_notification("Movie Ticket Booking Confirmation", confirmation_message)

    return jsonify({"message": f"Booking confirmed for {movie['title']} ({seats} seats). Total: ₹{total_amount}"})

#=========================
# already booked tickets
#=========================

@app.route('/booked_seats/<movie_id>/<showtime>', methods=['GET'])
def booked_seats(movie_id, showtime):
    response = bookings_table.scan(
        FilterExpression=Attr('movie_id').eq(movie_id) & Attr('showtime').eq(showtime)
    )
    booked = []
    for item in response['Items']:
        booked.extend(item['seat_numbers'])
    return jsonify({"booked_seats": booked})

#=========================
# Admin signup 
#=========================

# @app.route('/admin/signup', methods=['GET', 'POST'])
# def admin_signup():
#     if request.method == 'GET':
#         return render_template('AdminL&S.html')

#     # POST
#     name = request.form['name']
#     email = request.form['email']
#     password = request.form['password']

#     hashed_password = generate_password_hash(password)

#     admin_table.put_item(
#         Item={
#             'email': email,
#             'name': name,
#             'password': hashed_password,
#             'role': 'admin'
#         }
#     )

#      # Send SNS notification
#     send_notification("New Admin Signup", f"Admin {name} ({email}) has registered.")

#     msg = "Admin registration successful. Please login."
#     return render_template('AdminL&S.html', msg=msg)

#=========================
# Admin Login 
#=========================


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('AdminL&S.html')

    # POST
    email = request.form['email']
    password = request.form['password']

    response = admin_table.get_item(Key={'email': email})

    if 'Item' not in response:
        return render_template('AdminL&S.html', msg="Admin not found")

    stored_password = response['Item']['password']

    # if check_password_hash(stored_password, password):
    #     return render_template('AdminDashbord.html', name=response['Item']['name'], movies=movies)
    if check_password_hash(stored_password, password):
        session['role'] = 'admin'
        session['user'] = email
        return redirect(url_for('admin_dashboard_alt'))
    else:
        return render_template('AdminL&S.html', msg="Wrong password")


#===================
# Contact Form
#===================

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')

    # POST method
    username = request.form['username']
    email = request.form['email']
    feedback = request.form['feedback']

    contact_table.put_item(
        Item={
            'email': email,       # Partition key
            'username': username,
            'feedback': feedback
        }
    )

    # Send SNS notification
    send_admin_notification("New Contact Form Submission", f"{username} ({email}) submitted feedback: {feedback}")

    msg = "Your feedback has been submitted successfully!"
    return render_template('contact.html', msg=msg)

#============================
# Admin Dashbord (Add Movie)
#============================

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    # msg = None

    if request.method == 'POST':
        movie_id = request.form['movie_id']
        title = request.form['title']
        description = request.form['description']
        genre = request.form['genre']
        release_date = request.form['release_date']
        price = int(request.form['price'])
        address = request.form['address']
        theatersName = request.form['theatersName']
        duration = request.form['duration']
        theaters = request.form['theaters'].split(',')
        showtimes = request.form['showtimes'].split(',')

        poster_file = request.files['poster']
        filename = secure_filename(poster_file.filename)
        poster_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        poster_file.save(poster_path)

        movies[movie_id] = {
            "title": title,
            "description": description,
            "genre": genre,
            "release_date": release_date,
            "price": price,
            "address": address,
            "theatersName": theatersName,
            "duration": duration,
            "poster": f"posters/{filename}",
            "theaters": theaters,
            "showtimes": showtimes
        }

        msg = f"Movie '{title}' added successfully!"
        send_admin_notification("New Movie Added", f"Movie '{title}' has been added to the system.")
        return render_template('AdminDashbord.html', msg=msg, movies=movies)
    # NEW

    # seats_table = dynamodb.Table('seats')
    # response = seats_table.scan()
    # seats = response.get('Items', [])

    # return render_template('AdminDashbord.html', msg=msg, movies=movies, seats=seats)

    return render_template('AdminDashbord.html', movies=movies)

@app.route('/delete/<movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if movie_id in movies:
        poster_path = os.path.join('static', movies[movie_id]['poster'])
        if os.path.exists(poster_path) and movies[movie_id]['poster'].startswith("posters/"):
            os.remove(poster_path)
        del movies[movie_id]
    return redirect(url_for('admin_dashboard'))


# NEW

# @app.route('/cancel_booking/<seat_id>', methods=['POST'])
# def cancel_booking(seat_id):
#     if session.get('role') != 'admin':
#         return "Unauthorized", 403

#     seats_table = dynamodb.Table('seats')
#     seats_table.update_item(
#         Key={'seat_id': seat_id},
#         UpdateExpression="SET seat_status = :s",
#         ExpressionAttributeValues={':s': 'available'}
#     )
#     flash(f"Seat {seat_id} released successfully!", "info")
#     return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)


