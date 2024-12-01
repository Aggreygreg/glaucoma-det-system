import sqlite3
import bcrypt

# Connect to SQLite database (it will create a new file if it doesn't exist)
conn = sqlite3.connect('glaucoma.db', check_same_thread=False)  # Allow multithreading
c = conn.cursor()

# Create user table (for doctors)
c.execute(''' 
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    specialty TEXT NOT NULL,
    hospital TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    contact_phone TEXT NOT NULL
)
''')

# Create patient table
c.execute('''
CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    date_of_diagnosis TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    notes TEXT,
    doctor_id INTEGER,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)  -- Corrected foreign key reference
)
''')
conn.commit()

# Function to register a new doctor
def register_doctor(username, password, specialty, hospital, email, phone):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute('''
            INSERT INTO doctors (username, password, specialty, hospital, contact_email, contact_phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, hashed_pw, specialty, hospital, email, phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists

# Function to verify doctor login
def verify_login(username, password):
    c.execute('SELECT password FROM doctors WHERE username=?', (username,))
    result = c.fetchone()
    if result:
        stored_hash = result[0]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True
    return False

# Function to get doctor ID by username
def get_doctor_id_by_username(username):
    c.execute('SELECT doctor_id FROM doctors WHERE username=?', (username,))
    result = c.fetchone()
    return result[0] if result else None

# Function to add a new patient record
def add_patient(first_name, last_name, age, gender, diagnosis, date_of_diagnosis, email, phone, notes, doctor_id):
    c.execute('''
        INSERT INTO patients (first_name, last_name, age, gender, diagnosis, date_of_diagnosis, email, phone, notes, doctor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (first_name, last_name, age, gender, diagnosis, date_of_diagnosis, email, phone, notes, doctor_id))
    conn.commit()

# Function to get all patients created by the doctor
def get_all_patients(doctor_id):
    c.execute('SELECT * FROM patients WHERE doctor_id=?', (doctor_id,))
    return c.fetchall()

# Function to get patient by ID
def get_patient_by_id(patient_id):
    c.execute('SELECT * FROM patients WHERE patient_id=?', (patient_id,))
    return c.fetchone()
