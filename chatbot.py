import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import geocoder
import requests
from geopy.geocoders import Nominatim
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Secure database path
DB_PATH = os.path.join(os.path.expanduser("~"), "emergency_contacts.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def add_contact_to_db():
    contact = simpledialog.askstring("Add Contact", "Enter emergency contact number:")
    if contact:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO contacts (number) VALUES (?)", (contact,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Emergency contact added successfully!")

def get_contacts_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT number FROM contacts")
    contacts = [row[0] for row in cursor.fetchall()]
    conn.close()
    return contacts

def get_location():
    try:
        g = geocoder.ip("me")
        if g.ok and g.latlng:
            geolocator = Nominatim(user_agent="womens_safety_bot")
            location = geolocator.reverse(g.latlng, exactly_one=True)
            return location.address if location else "Location not found"
        return "Location not found"
    except Exception:
        return "Error retrieving location"

def send_sms_alert(location):
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        print("Twilio credentials are missing! Set them in a .env file.")
        return
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    emergency_numbers = get_contacts_from_db()
    for number in emergency_numbers:
        try:
            client.messages.create(
                body=f"\U0001F6A8 Emergency Alert! \U0001F6A8\nLocation: {location}\nPlease take immediate action!",
                from_=TWILIO_PHONE_NUMBER,
                to=number
            )
            print(f"SMS alert sent to {number}")
        except Exception as e:
            print(f"Error sending SMS: {e}")

# GUI Setup
root = tk.Tk()
root.title("Women Safety Bot")
root.configure(bg='#E0F6E3')
root.geometry("500x750")
root.resizable(False, False)

FONT = ('Poppins', 12)
BUTTON_FONT = ('Poppins', 12, 'bold')

chatbox = scrolledtext.ScrolledText(root, height=15, width=50, bg='white', wrap=tk.WORD, font=FONT)
chatbox.pack(pady=10)
chatbox.insert(tk.END, " Bot: Are you in danger?\n")

def handle_yes():
    location = get_location()
    chatbox.insert(tk.END, f"\n Bot: Location retrieved: {location}\n")
    chatbox.insert(tk.END, "\n Bot: Notifying emergency contacts via SMS...\n")
    send_sms_alert(location)
    chatbox.see(tk.END)

def handle_no():
    chatbox.insert(tk.END, "\n Bot: How can I assist you?\n")
    chatbox.see(tk.END)

def send_message():
    user_text = entry.get()
    if user_text.strip():
        chatbox.insert(tk.END, f"\n You: {user_text}\n")
        entry.delete(0, tk.END)
        chatbox.see(tk.END)

yes_button = tk.Button(root, text="Yes", command=handle_yes, font=BUTTON_FONT, bg='red', fg='white')
yes_button.pack(pady=5)

no_button = tk.Button(root, text="No", command=handle_no, font=BUTTON_FONT, bg='blue', fg='white')
no_button.pack(pady=5)

entry = tk.Entry(root, font=FONT, width=40)
entry.pack(pady=5)

send_button = tk.Button(root, text="Send", command=send_message, font=BUTTON_FONT)
send_button.pack(pady=5)

init_db()
root.mainloop()
