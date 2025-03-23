import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import geocoder
import requests
from geopy.geocoders import Nominatim
from twilio.rest import Client
from PIL import Image, ImageTk, ImageDraw

# Twilio API Setup
TWILIO_ACCOUNT_SID = "Add_yourID_fren"  # Replace with your Twilio SID
TWILIO_AUTH_TOKEN = "Add_yourTOKEN_fren"  # Replace with your Twilio Auth Token
TWILIO_PHONE_NUMBER = "Add_yourNUMBER_fren"  # Replace with your Twilio phone number

# Database Setup
def init_db():
    conn = sqlite3.connect("emergency_contacts.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL UNIQUE
        )
    """)
    
   

# Function to add contact while preventing duplicates
def add_contact_to_db():
    contact = simpledialog.askstring("Add Contact", "Enter emergency contact number:")
    if contact:
        conn = sqlite3.connect("emergency_contacts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT number FROM contacts WHERE number = ?", (contact,))
        existing_contact = cursor.fetchone()
        
        if existing_contact:
            messagebox.showinfo("Info", "This contact is already saved.")
        else:
            cursor.execute("INSERT INTO contacts (number) VALUES (?)", (contact,))
            conn.commit()
            messagebox.showinfo("Success", "Emergency contact added successfully!")
        
        conn.close()

# Function to get contacts
def get_contacts_from_db():
    conn = sqlite3.connect("emergency_contacts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT number FROM contacts")
    contacts = [row[0] for row in cursor.fetchall()]
    conn.close()
    return contacts

# Function to remove contact
def remove_contact_from_db():
    contacts = get_contacts_from_db()
    if not contacts:
        messagebox.showinfo("Remove Contact", "No contacts available to remove.")
        return
    
    contact_to_remove = simpledialog.askstring("Remove Contact", "Enter the exact contact number to remove:")
    if contact_to_remove:
        conn = sqlite3.connect("emergency_contacts.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE number = ?", (contact_to_remove,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Emergency contact removed successfully!")

# Function to view contacts
def view_contacts():
    contacts = get_contacts_from_db()
    if contacts:
        contact_list = "\n".join(set(contacts))  # Remove duplicates before displaying
        messagebox.showinfo("Saved Contacts", f"Emergency Contacts:\n{contact_list}")
    else:
        messagebox.showinfo("Saved Contacts", "No emergency contacts found.")

init_db()

# Get Location
def get_location():
    try:
        ip_response = requests.get("https://api64.ipify.org?format=json")
        if ip_response.status_code == 200:
            user_ip = ip_response.json().get("ip")
            g = geocoder.ip(user_ip)
            if g.ok and g.latlng:
                geolocator = Nominatim(user_agent="womens_safety_bot")
                location = geolocator.reverse(g.latlng, exactly_one=True)
                if location:
                    retrieved_location = f"{location.address} (Lat: {g.latlng[0]}, Lon: {g.latlng[1]})"
                else:
                    retrieved_location = "Location not found"
            else:
                retrieved_location = "Location not found"
        else:
            retrieved_location = "Location not found"
        
        return retrieved_location
    except Exception as e:
        return f"Error retrieving location: {str(e)}"

# Send Emergency Message via Twilio SMS
def send_sms_alert(location):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    emergency_numbers = get_contacts_from_db()
    for number in emergency_numbers:
        try:
            message = client.messages.create(
                body=f"\U0001F6A8 Emergency Alert! \U0001F6A8\nLocation: {location}\nPlease take immediate action!",
                from_=TWILIO_PHONE_NUMBER,
                to=number
            )
            print(f"SMS alert sent to {number}")
        except Exception as e:
            print(f"Error sending SMS: {e}")

# Handle Emergency Request
def handle_yes():
    location = get_location()
    chatbox.insert(tk.END, f"\n Bot: Request is being sent...\n")
    chatbox.insert(tk.END, f"\n Bot: Location retrieved: {location}\n")
    chatbox.insert(tk.END, f"\n Bot: Notifying emergency contacts via SMS...\n")
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

# Database Setup
def init_db():
    conn = sqlite3.connect("emergency_contacts.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL UNIQUE
        )
    """)
    
    # Remove all existing contacts except "8506017366"
    cursor.execute("DELETE FROM contacts WHERE number != '8506017366'")

    # Ensure "8506017366" is in the database
    cursor.execute("INSERT OR IGNORE INTO contacts (number) VALUES ('8506017366')")
    
    conn.commit()
    conn.close()

# GUI Setup
root = tk.Tk()
root.title("Women Safety Bot")
root.configure(bg='#E0F6E3')
root.geometry("500x750")
root.resizable(False, False)

FONT = ('Poppins', 12)
BUTTON_FONT = ('Poppins', 12, 'bold')

header_frame = tk.Frame(root, bg='#E0F6E3', height=50)
header_frame.pack(fill=tk.X)
title_label = tk.Label(header_frame, text="Women Safety Bot", font=('Poppins', 16, 'bold'), bg='#E0F6E3')
title_label.pack(pady=10)

chatbox = scrolledtext.ScrolledText(root, height=15, width=50, bg='white', wrap=tk.WORD, font=FONT, borderwidth=5, relief=tk.GROOVE)
chatbox.pack(pady=10)
chatbox.insert(tk.END, " Bot: Are you in danger?\n")
chatbox.see(tk.END)

button_frame = tk.Frame(root, bg='#E0F6E3')
button_frame.pack()

yes_button = tk.Button(button_frame, text="Yes", command=handle_yes, font=BUTTON_FONT, bg='red', fg='white', relief=tk.FLAT)
yes_button.grid(row=0, column=0, padx=10, pady=5)

no_button = tk.Button(button_frame, text="No", command=handle_no, font=BUTTON_FONT, bg='blue', fg='white', relief=tk.FLAT)
no_button.grid(row=0, column=1, padx=10, pady=5)

entry = tk.Entry(root, font=FONT, width=40, borderwidth=5, relief=tk.GROOVE)
entry.pack(pady=5)

send_button = tk.Button(root, text="Send", command=send_message, font=BUTTON_FONT)
send_button.pack(pady=5)

view_contacts_button = tk.Button(root, text="View Contacts", command=view_contacts, font=BUTTON_FONT)
view_contacts_button.pack(pady=5)

add_contact_button = tk.Button(root, text="Add Contact", command=add_contact_to_db, font=BUTTON_FONT)
add_contact_button.pack(pady=5)

remove_contact_button = tk.Button(root, text="Remove Contact", command=remove_contact_from_db, font=BUTTON_FONT)
remove_contact_button.pack(pady=5)

root.mainloop()
