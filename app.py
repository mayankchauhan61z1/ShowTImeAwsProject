
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
app.config['SESSION_PERMANENT'] = False

app.config['UPLOAD_FOLDER'] = 'static/posters'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# remove 8 comment when get dynamodb working

#======================
# DynamoDB connection
#======================

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')
ses = boto3.client('ses', region_name='us-east-1')
def invite_customer_to_ses(email):
    try:
        # This triggers the AWS Verification email to the customer automatically
        ses.verify_email_identity(EmailAddress=email)
        print(f"Verification email sent to {email}")
    except Exception as e:
        print(f"SES Invite Error: {e}")


# dynomodbtable(create these tables in dynamodb manually)
users_table = dynamodb.Table('users') # for store user data(login and signup)
admin_table = dynamodb.Table('admins') # for store and check admin login
contact_table = dynamodb.Table('ContactForm') # for feedback form
bookings_table = dynamodb.Table('bookings') # for track booked table
moviesdata_table = dynamodb.Table('moviesdata') # for store admin new movies

#=====================
# SNS
#=====================

ADMIN_TOPIC_ARN = "arn:aws:sns:us-east-1:045395708809:ADMIN_TOPIC_ARN"
CUSTOMER_TOPIC_ARN = "arn:aws:sns:us-east-1:045395708809:CUSTOMER_TOPIC_ARN"

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

def send_customer_email(email, subject, message):
    """Send booking confirmation directly to one customer email using SES."""
    try:
        response = ses.send_email(
            Source="mayankchauhan.61z1@gmail.com",  # sender (must be verified in SES)
            Destination={'ToAddresses': [email]},      # receiver (customer who booked)
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': message}}
            }
        )
        print(f"Booking email sent to {email}! ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error sending customer email: {e}")

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
        "poster": "Images/nobalReincarnationPoster.jpg",
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
    # Fetch all movies from DynamoDB
    response = moviesdata_table.scan()
    db_movies = {m['movie_id']: m for m in response.get('Items', [])}
    
    # Merge: Code Movies + Database Movies
    all_movies = {**movies, **db_movies}
    return render_template('index.html', movies=movies, slides=slides)

@app.route('/home')
def home():
    # 1. Fetch all movies from DynamoDB
    response = moviesdata_table.scan()
    db_movies = {m['movie_id']: m for m in response.get('Items', [])}

    # 2. Merge: Code Movies + Database Movies
    all_movies = {**movies, **db_movies}

    # 3. Session check (your style)
    if 'user' in session:
        return render_template('index.html', name=session['user'], movies=all_movies, slides=slides)
    else:
        return render_template('index.html', name="Guest", movies=all_movies, slides=slides)



# for direction to about page
@app.route('/about')
@app.route('/search_suggestions')
def search_suggestions():
    query = request.args.get('query', '').lower()
    results = []

    # 1. Combine local hardcoded dictionaries safely
    local_movies = {**movies, **slides}

    # 2. Fetch live movies from DynamoDB safely
    db_movies = {}
    try:
        response = moviesdata_table.scan()
        db_movies = {m['movie_id']: m for m in response.get('Items', [])}
    except Exception as e:
        print(f"DynamoDB Search Scan Error: {e}")

    # 3. Merge everything together (Local + Database)
    all_movies = {**local_movies, **db_movies}

    # 4. Loop through everything safely
    for movie_id, movie in all_movies.items():
        # CRITICAL FIX: Look for both lowercase and uppercase keys to prevent KeyError crashes!
        movie_title = movie.get('title') or movie.get('Title') or ""
        movie_genre = movie.get('genre') or movie.get('Genre') or "N/A"

        # Check if the search query matches the title
        if query in movie_title.lower():
            results.append({
                "title": movie_title,
                "genre": movie_genre,
                "movie_id": movie_id
            })

    return jsonify(results)

# @app.route('/adminDashbord')
# def adminDashbord():
#     return render_template('AdminDashbord.html')

#@app.route('/admindashboard')
#def admin_dashboard_alt():
#    if session.get('role') != 'admin':
#        return "Unauthorized", 403
    # Fetch from DynamoDB
#    response = moviesdata_table.scan()
#    db_movies = {m['movie_id']: m for m in response.get('Items', [])}
    
    # Merge hardcoded + Database movies
#    all_movies = {**movies, **db_movies}

#    return render_template('AdminDashbord.html', movies=movies)

@app.route('/AdminLogin')
def AdminLogin():
    return render_template('AdminL&S.html')

@app.route('/movie/<movie_id>')
def movie_detail(movie_id):
    # 1. Check hardcoded movies first
    movie_data = movies.get(movie_id) or slides.get(movie_id)
    
    # 2. If not found in code, check DynamoDB
    if not movie_data:
        try:
            response = moviesdata_table.get_item(Key={'movie_id': movie_id})
            movie_data = response.get('Item')
        except Exception as e:
            print(f"DynamoDB Error: {e}")
            return "Database connection error", 500

    # 3. If STILL not found, show error
    if not movie_data:
        return "Movie not found", 404
        
    return render_template('movie.html', movie_data=movie_data, movie_id=movie_id)


#=====================
# SIGNUP API
#=====================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('L&S.html')

    # POST signup
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form['password']

    hashed_password = generate_password_hash(password)

    # 1. Save to DynamoDB
    try:
        users_table.put_item(
            Item={
                'email': email,
                'name': name,
                'password': hashed_password,
                'subscribed': False
            },
            ConditionExpression='attribute_not_exists(email)'
        )
    except Exception as e:
        if "ConditionalCheckFailedException" in str(e):
            flash("An account with this email already exists. Please login.")
        else:
            print(f"DB Error: {e}")
            flash("Database error. Please try again.")
        return redirect(url_for('signup'))

    # 2. SES and SNS Notifications
    try:
        invite_customer_to_ses(email)
        
        confirmation_message = "user signup successfully! Please check your email to verify"
        send_customer_email(email, "Movie Ticket Booking Confirmation", confirmation_message)

        send_admin_notification("New User Signup", f"User {name} ({email}) has registered.")
    except Exception as e:
        print(f"Notification Error: {e}")

    # 3. Redirect to login
    return redirect(url_for('login'))

#=====================
# LOGIN API
#=====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('L&S.html')

    # POST login
    email = request.form['email']
    password = request.form['password']

    response = users_table.get_item(Key={'email': email})
    user_item = response.get('Item')

    if user_item and check_password_hash(user_item['password'], password):
        username = user_item.get('name') or user_item.get('username')
        session['user'] = email
        session['email'] = email
        session['username'] = username

        try:
            confirmation_message = "You have successfully logged into ShowTime!"
            send_customer_email(email, "Login Notification", confirmation_message)
        except Exception as e:
            print(f"Login Email Error: {e}")

        flash("Login successful!", "success")
        return redirect(url_for('home'))
    else:
        flash("Wrong email or password", "error")
        return redirect(url_for('login'))

#==========================
#Forgot Password
#==========================

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        response = users_table.get_item(Key={'email': email})
        user = response.get('Item')

        if not user:
            flash("Email not registered.")
            return redirect(url_for('forgot_password'))

        # Generate reset token and update DynamoDB
        reset_token = str(uuid.uuid4())
        users_table.update_item(
            Key={'email': email},
            UpdateExpression="set reset_token=:t",
            ExpressionAttributeValues={':t': reset_token}
        )

        # Build reset link
        reset_link = f"http://35.153.200.170/reset/{reset_token}"

        # Using your existing helper function!
        subject = "Password Reset - ShowTime"
        message = f"Click here to reset your password: {reset_link}"
        
        send_customer_email(email, subject, message)

        flash("Password reset link sent to your email.")
        return redirect(url_for('login'))

    return render_template('forgot.html')


#==========================
#Reset Password
#==========================

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form['password']
        # Ensure your app uses the same hashing method as your signup
        hashed_pw = generate_password_hash(new_password)

        # Find user with this specific reset_token
        response = users_table.scan(
            FilterExpression=Attr('reset_token').eq(token)
        )
        items = response.get('Items', [])

        if not items:
            flash("Invalid or expired token.")
            return redirect(url_for('login'))

        email = items[0]['email']

        # Update password and CLEAN UP (remove the token so it can't be used again)
        users_table.update_item(
            Key={'email': email},
            UpdateExpression="set password=:p remove reset_token",
            ExpressionAttributeValues={':p': hashed_pw}
        )

        flash("Password updated successfully. Please log in.")
        return redirect(url_for('login'))

    # GET request → show reset page with the token passed to the form
    return render_template('reset.html', token=token)

#==========================
# Logout
#==========================

@app.route('/logout')
def logout():
    # ✅ Clear session on logout
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))


#==========================
# Book Ticket 
#==========================
# @app.route('/book', methods=['POST'])
# def book():
#     if 'user' not in session:
#         return jsonify({"message": "You must login before booking tickets."}), 403

#     data = request.get_json()
#     email = session['user']
#     movie_id = data['movie_id']
#     seats = int(data['seats'])
#     theater = data['theater']
#     showtime = data['showtime']

#     movie = movies.get(movie_id) or slides.get(movie_id)
#     if not movie:
#         return jsonify({"message": "Invalid movie selection."}), 400

#     total_amount = seats * movie['price']

#     bookings_table.put_item(Item={
#         'user_email': email,
#         'booking_id': str(uuid.uuid4()),
#         'movie_id': movie_id,
#         'movie_title': movie['title'],
#         'seats': seats,
#         'seat_numbers': data['seat_numbers'],
#         'amount': total_amount,
#         'theater': theater,
#         'showtime': showtime,
#         'booking_date': datetime.utcnow().isoformat()
#     })
#     # Send SNS notification
#     confirmation_message = (
#         f"Booking confirmed!\n\n"
#         f"Movie: {movie['title']}\n"
#         f"Theater: {theater}\n"
#         f"Showtime: {showtime}\n"
#         f"Seats: {seats} ({', '.join(data['seat_numbers'])})\n"
#         f"Total Amount: ₹{total_amount}\n\n"
#         f"Thank you for booking with us!"
#     )

#     send_customer_notification("Movie Ticket Booking Confirmation", confirmation_message)

#     return jsonify({"message": f"Booking confirmed for {movie['title']} ({seats} seats). Total: ₹{total_amount}"})

@app.route('/book', methods=['POST'])
def book():
    if 'user' not in session:
        return jsonify({"message": "You must login before booking tickets."}), 403

    # Support JSON and Form data
    data = request.get_json(silent=True) or request.form.to_dict()
    customer_email = session.get('user')
    movie_id = data.get('movie_id')
    
    # 1. Fetch Movie Details (Code or DB)
    movie = movies.get(movie_id) or slides.get(movie_id)
    if not movie:
        res = moviesdata_table.get_item(Key={'movie_id': movie_id})
        movie = res.get('Item')

    if not movie:
        return jsonify({"message": "Movie not found."}), 400

    # 2. Calculate values
    seats = int(data.get('seats', 1))
    total_amount = seats * movie.get('price', 0)
    theater = data.get('theater', 'Default Theater')
    showtime = data.get('showtime', 'Default Time')
    seat_list = data.get('seat_numbers', [])
    if isinstance(seat_list, str): seat_list = seat_list.split(',')

    # 3. Create the Summary Message
    confirmation_message = (
        f"Booking Confirmed!\n\n"
        f"Movie: {movie['title']}\n"
        f"Theater: {theater}\n"
        f"Showtime: {showtime}\n"
        f"Seats: {seats} ({', '.join(seat_list)})\n"
        f"Amount Paid: ₹{total_amount}\n\n"
        f"Thank you for booking with us! "
        f"User: {customer_email}"
    )

    try:
        # A. Save to DynamoDB
        bookings_table.put_item(Item={
            'user_email': customer_email,
            'booking_id': str(uuid.uuid4()),
            'movie_id': movie_id,
            'movie_title': movie['title'],
            'seats': seats,
            'seat_numbers': seat_list,
            'amount': total_amount,
            'theater': theater,
            'showtime': showtime,
            'booking_date': datetime.utcnow().isoformat()
        })

        # B. Send SNS Admin Alert (So you know you made a sale!)
        try:
            send_admin_notification("New Ticket Sold!", confirmation_message)
        except Exception as e:
            print(f"SNS Error: {e}")

        # C. Send SES Customer Email
        try:
            send_customer_email(customer_email, f"Ticket: {movie['title']}", confirmation_message)
        except Exception as e:
            print(f"SES Error: {e}")

        return jsonify({"message": f"Booking successful for {movie['title']}!"})

    except Exception as e:
        print(f"Critical Booking Error: {e}")
        return jsonify({"error": "Database error. Please try again."}), 500


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
        return redirect(url_for('admin_dashboard'))
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
    # Fetch from DB so they show up on login/refresh
    response = moviesdata_table.scan()
    db_movies = {m['movie_id']: m for m in response.get('Items', [])}
    # Merge hardcore local and dynamobd data
    all_movies = {**movies, **db_movies}
    # msg = None

    if request.method == 'POST':
        # movie_id = request.form['movie_id']
        movie_id = str(uuid.uuid4())
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

        movie_item = {
            'movie_id': movie_id,
            'title': request.form['title'],
            'description': request.form['description'],
            'genre': request.form['genre'],
            'release_date': request.form['release_date'],
            'price': int(request.form['price']),
            'address': request.form['address'],
            'theatersName': request.form['theatersName'],
            'duration': request.form['duration'],
            'theaters': request.form['theaters'].split(','),
            'showtimes': request.form['showtimes'].split(','),
            'poster': f"posters/{filename}"
        }

        # 3. Save to DynamoDB
        try:
            moviesdata_table.put_item(Item=movie_item)
            
            # Send notification
            send_admin_notification("New Movie Added", f"Movie '{movie_item['title']}' added.")
            flash(f"Movie '{movie_item['title']}' added successfully!")
            
        except Exception as e:
            print(f"Error saving to DynamoDB: {e}")
            flash("Error: Could not save movie data.")

    return render_template('AdminDashbord.html', movies=all_movies)

@app.route('/delete/<movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    # 1. Check if movie exists in hardcoded dictionary
    if movie_id in movies:
        del movies[movie_id]
    
    # 2. Always attempt to delete from DynamoDB
    try:
        moviesdata_table.delete_item(Key={'movie_id': movie_id})
        flash("Movie deleted successfully!")
    except Exception as e:
        print(f"Database delete error: {e}")
        flash("Error: Could not delete from database.")

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
    app.run(host="0.0.0.0", port=5000)


