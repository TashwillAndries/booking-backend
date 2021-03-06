import hmac
from flask import *
from flask_cors import CORS

from flask_mail import Mail, Message
import datetime
from smtplib import SMTPRecipientsRefused
import sqlite3


import cloudinary
import cloudinary.uploader


# user class
class User(object):
    def __init__(self, id,
                 username, password):
        self.id = id
        self.username = username
        self.password = password


# admin class
class Admin(object):
    def __init__(self, admin_id, admin_username, admin_password):
        self.admin_id = admin_id
        self.admin_username = admin_username
        self.admin_password = admin_password


class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('hotel.db')
        self.cursor = self.conn.cursor()

    def sending_to_database(self, query, values):
        self.cursor.execute(query, values)
        # self.conn.commit()

    def single_select(self, query):
        self.cursor.execute(query)
        # self.conn.commit()

    def fetch(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def commit(self):
        self.conn.commit()


# fetching users from the database
def fetch_users():
    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users_data = cursor.fetchall()

        new_data = []

        for data in users_data:
            new_data.append(User(data[0], data[5], data[6]))

        return new_data


# creating table for users
def init_user_table():
    conn = sqlite3.connect('hotel.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "address TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table successfully")
    conn.close()


init_user_table()
users = fetch_users()


# creating table for the products
def init_products_table():
    with sqlite3.connect('hotel.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS room (room_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "hotel_name TEXT NOT NULL,"
                     "room_number TEXT NOT NULL,"
                     "description TEXT NOT NULl,"
                     "suit_type TEXT NOT NULL,"
                     "picture TEXT NOT NULL,"
                     "price TEXT NOT NULL)")
    print("room table created successfully")


init_products_table()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


# fetch admin function
def fetch_admin():
    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin")
        users_data = cursor.fetchall()

        new_data = []

        for data in users_data:
            new_data.append(Admin(data[0], data[1], data[2]))

        return new_data


# admin account table
def init_admin_table():
    with sqlite3.connect('hotel.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS admin(admin_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "admin_username TEXT NOT NULL,"
                     "admin_password TEXT NOT NULL)")
        print("admin table created successfully")


init_admin_table()
admin = fetch_admin()

adminname_table = {a.admin_username: a for a in admin}
adminid_table = {a.admin_id: a for a in admin}


def init_appointment_table():
    with sqlite3.connect('hotel.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS appointment(appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "date_made TEXT NOT NULL,"
                     "check_in_date TEXT NOT NULL unique,"
                     "check_out_date TEXT NOT NULL unique,"
                     "appointment_user TEXT NOT NULL,"
                     "hotel_name TEXT NOT NULL,"
                     "room_no TEXT NOT NULL,"
                     "total TEXT NOT NULL,"
                     "CONSTRAINT fk_user FOREIGN KEY (appointment_user) REFERENCES user(user_id),"
                     "CONSTRAINT fk_room FOREIGN KEY (room_no) REFERENCES room(room_number))")


init_appointment_table()


def init_hotels_table():
    with sqlite3.connect('hotel.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS hotels(hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "hotel_picture TEXT NOT NULL,"
                     "hotel_name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "rating TEXT NOT NULL)")
        print("hotel table created successfully")


init_hotels_table()


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'this-is-a-secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'justtotestmywork@gmail.com'
app.config['MAIL_PASSWORD'] = 'justtesting'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['CORS-HEADERS'] = ['Content-Type']
mail = Mail(app)
CORS(app, resources={r"/*": {"origins": "*"}})


# route to register users
@app.route('/user-registration/', methods=['POST'])
def user_registration():
    response = {}
    db = Database()
    try:
        if request.method == "POST":
            user_id = request.json['user_id']
            first_name = request.json['first_name']
            surname = request.json['last_name']
            address = request.json['address']
            email = request.json['email']
            username = request.json['username']
            password = request.json['password']

            query = "INSERT INTO user (user_id, first_name,last_name,address" \
                    ",email,username,password) VALUES(?,?,?,?,?,?,?)"
            values = (user_id, first_name, surname, address, email, username, password)
            db.sending_to_database(query, values)
            db.commit()

            message = Message('Thank You', sender='justtotestmywork@gmail.com', recipients=[email])
            message.body = "Thank you for registering hope you enjoy your stay"
            mail.send(message)
            response["message"] = 'Success'
            response["status_code"] = 201
            return response

    except SMTPRecipientsRefused:
        response['message'] = "Please enter a valid email address"
        response['status_code'] = 400
        return response


@app.route("/register-admin/", methods=['POST'])
def admin_registration():
    response = {}
    db = Database()
    if request.method == "POST":
        username = request.json['admin_username']
        password = request.json['admin_password']

        query = "INSERT INTO admin (admin_username,admin_password) VALUES(?,?)"
        values = (username, password)
        db.sending_to_database(query, values)
        db.commit()
        response["message"] = 'Success'
        response["status_code"] = 201
        return response
    else:
        response['message'] = "failed"
        response['status_code'] = 400


@app.route("/user-login/", methods=["POST"])
def login_user():
    response = {}
    if request.method == "POST":
        username = request.json["username"]
        password = request.json["password"]
        conn = sqlite3.connect("hotel.db")
        c = conn.cursor()
        statement = f"SELECT * FROM user WHERE username='{username}' and password ='{password}'"
        c.execute(statement)
        if not c.fetchone():
            response['message'] = "failed"
            response["status_code"] = 401
            return response
        else:
            response['message'] = "welcome user"
            response["status_code"] = 201
            return response
    else:
        return "wrong method"


@app.route("/admin-login/", methods=["POST"])
def login():
    response = {}
    if request.method == "POST":
        username = request.json["admin_username"]
        password = request.json["admin_password"]
        conn = sqlite3.connect("hotel.db")
        c = conn.cursor()
        statement = (f"SELECT * FROM admin WHERE admin_username='{username}' and admin_password ="
                     f"'{password}'")
        c.execute(statement)
        if not c.fetchone():
            response['message'] = "failed"
            response["status_code"] = 401
            return response
        else:
            response['message'] = "welcome admin user"
            response["status_code"] = 201
            return response
    else:
        return "wrong method"


@app.route('/show-appointments/', methods=['GET'])
def show_users():
    response = {}
    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointment")

        all_users = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = all_users
    return response


@app.route('/show-user/<username>', methods=["GET"])
def view_user(username):
    response = {}
    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE username='" + str(username) + "'")
        response['status_code'] = 200
        response['data'] = cursor.fetchone()
        response['message'] = "user retrieved successfully"
    return jsonify(response)


@app.route('/create-hotel/', methods=['POST'])
def create_hotel():
    response = {}
    database = Database()

    if request.method == 'POST':
        hotel_name = request.json['hotel_name']
        hotel_price = request.json['price']
        rating = request.json['rating']

        query = "INSERT INTO hotels (hotel_picture, hotel_name, price, rating) VALUES(?,?,?,?)"
        values = (hotel_upload(), hotel_name, hotel_price, rating)
        database.sending_to_database(query, values)
        response['message'] = "hotel added successfully"
        response['status_code'] = 201
        return response


@app.route('/create-room/', methods=['POST'])
def room_create():
    response = {}
    database = Database()

    if request.method == 'POST':
        hotel_name = request.json['hotel_name']
        room_number = request.json['room_number']
        description = request.json['description']
        type = request.json['suit_type']
        picture = request.json["picture"]
        price = request.json['price']

        query = "INSERT INTO room (hotel_name,room_number,description,suit_type,picture,price) Values(?,?,?,?,?,?)"
        values = (hotel_name, room_number, description, type, picture, price)
        database.sending_to_database(query, values)
        database.commit()
        response['message'] = "room added successfully"
        response['status_code'] = 201
        return response


# protected route that creates appointment
@app.route('/create-appointment/', methods=['POST'])
def appointment_create():
    response = {}
    database = Database()
    try:
        if request.method == "POST":
            date_made = datetime.datetime.now()
            check_in = request.json['check_in_date']
            check_out = request.json['check_out_date']
            user = request.json['appointment_user']
            hotel_name = request.json['hotel_name']
            room_no = request.json['room_no']
            total = request.json['total']

            query = "INSERT INTO appointment(date_made,check_in_date, check_out_date, appointment_user,hotel_name," \
                    "room_no, total)Values(?,?,?,?,?,?,?)"
            values = (date_made, check_in, check_out, user, hotel_name, room_no, total)
            database.sending_to_database(query, values)
            database.commit()
            response['message'] = "appointment added successfully"
            response['status_code'] = 201
            return response

    except sqlite3.IntegrityError:
        response['message'] = "appointment already made"
        response['status_code'] = 401
        return response


# send a email to the user
@app.route('/send-email/', methods=["POST"])
def send_email():
    response = {}
    try:
        email = request.json['email']
        total = request.json['total']
        check_in_date = datetime.date.today()
        message = Message('Thank You', sender='justtotestmywork@gmail.com', recipients=[email])
        message.body = "Thank you booking on" + " " + str(check_in_date) + " " + "hope you enjoy your day\n" \
                        "a total of" + " " + "R" + str(total) + " " + "to be paid 2 weeks before check-in date"
        mail.send(message)

        response["message"] = "Email sent successfully."
        response["status_code"] = 201
        return response
    except SMTPRecipientsRefused:
        response['message'] = "Please enter a valid email address."
        response['status_code'] = 403
        return response


# route to show all the rooms
@app.route('/get-rooms/', methods=['GET'])
def get_rooms():
    response = {}
    database = Database()

    query = "SELECT * FROM room"
    database.single_select(query)
    response['status_code'] = 201
    response['data'] = database.fetch()
    return response


@app.route('/get-hotels/', methods=['GET'])
def get_hotels():
    response = {}
    database = Database()

    query = "SELECT * FROM hotels"
    database.single_select(query)
    response['status_code'] = 201
    response['data'] = database.fetch()
    return response


@app.route('/show-appointments/', methods=['GET'])
def get_appointments():
    response = {}
    database = Database()

    query = "SELECT * FROM appointments"
    database.single_select(query)
    response['status_code'] = 201
    response['data'] = database.fetch()
    return response


@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):
    response = {}
    database = Database()

    query = "DELETE FROM user WHERE user_id='" + str(user_id) + "'"
    database.single_select(query)
    database.commit()
    response['status_code'] = 200
    response['message'] = "user deleted successfully."
    return response


# route to edit rooms
@app.route('/edit-room/<int:room_id>/', methods=['PUT'])
def edit_product(room_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('hotel.db') as conn:
            cursor = conn.cursor()
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("room_number") is not None:
                put_data["room_number"] = incoming_data.get("room_number")
                with sqlite3.connect('hotel.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE room SET room_number =? WHERE room_id =?", (put_data['room_number'],
                                                                                       room_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201

            if incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")
                with sqlite3.connect('hotel.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE room SET description =? WHERE room_id =?",
                                   (put_data['description'], room_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201

            if incoming_data.get("suit_type") is not None:
                put_data["suit_type"] = incoming_data.get("suit_type")
                with sqlite3.connect('hotel.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE room SET quantity =? WHERE room_id =?",
                                   (put_data['suit_type'], room_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
                    return response


# route that updates appointments
@app.route('/update-appointment/<int:appointment_id>/', methods=['PUT'])
def edit_appointment(appointment_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('hotel.db') as conn:
            cursor = conn.cursor()
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("check_in_date") is not None:
                put_data["check_in_date"] = incoming_data.get("check_in_date")
                with sqlite3.connect('hotel.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE appointment SET check_in_date =? WHERE appointment_id =?",
                                   (put_data['check_in_date'],
                                    appointment_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201

            if incoming_data.get("check_out_date") is not None:
                put_data["check_out_date"] = incoming_data.get("check_out_date")
                with sqlite3.connect('hotel.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE appointment SET check_out_date =? WHERE appointment_id =?",
                                   (put_data['check_out_date'],
                                    appointment_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201

            if incoming_data.get("appointment_user") is not None:
                put_data["appointment_user"] = incoming_data.get("appointment_user")
                with sqlite3.connect('hotel.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE appointment SET appointment_user =? WHERE appointment_id =?",
                                   (put_data['appointment_user'],
                                    appointment_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201

            if incoming_data.get("hotel_name") is not None:
                put_data["hotel_name"] = incoming_data.get("hotel_name")
                with sqlite3.connect('hotel.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE appointment SET hotel_name =? WHERE appointment_id =?",
                                   (put_data['hotel_name'],
                                    appointment_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201

            if incoming_data.get("room_no") is not None:
                put_data["room_no"] = incoming_data.get("room_no")
                with sqlite3.connect('hotel.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE appointment SET room_no =? WHERE appointment_id =?",
                                   (put_data['room_no'],
                                    appointment_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201

            if incoming_data.get("total") is not None:
                put_data["total"] = incoming_data.get("total")
                with sqlite3.connect('hotel.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE appointment SET total =? WHERE appointment_id =?",
                                   (put_data['total'],
                                    appointment_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
            return response


@app.route("/delete-appointment/<int:appointment_id>")
def delete_appointment(appointment_id):
    response = {}
    database = Database()

    query = "DELETE FROM appointment WHERE appointment_id='" + str(appointment_id) + "'"
    database.single_select(query)
    database.commit()
    response['status_code'] = 200
    response['message'] = "appointment deleted successfully."
    return response


def upload_file():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name='dtjgqnwbk', api_key='547853474672121',
                      api_secret='fXXsay0Fd5RmSPMS5TwZUaJFsRk')
    upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        product_image = request.json['picture']
        app.logger.info('%s file_to_upload', product_image)
        if product_image:
            upload_result = cloudinary.uploader.upload(product_image)
            app.logger.info(upload_result)
            return upload_result['url']


def hotel_upload():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name='dtjgqnwbk', api_key='547853474672121',
                      api_secret='fXXsay0Fd5RmSPMS5TwZUaJFsRk')
    upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        product_image = request.json['hotel_picture']
        app.logger.info('%s file_to_upload', product_image)
        if product_image:
            upload_result = cloudinary.uploader.upload(product_image)
            app.logger.info(upload_result)
            return upload_result['url']


# route that gets a single product by its ID
@app.route('/get-room/<int:room_id>/', methods=["GET"])
def get_room(room_id):
    response = {}
    database = Database()

    query = "SELECT * FROM room WHERE room_id=" + str(room_id)
    database.single_select(query)

    response["status_code"] = 200
    response["description"] = "product retrieved successfully"
    response['data'] = database.fetch()
    return response


if __name__ == '__main__':
    app.run()
