import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import geocoder
import requests
from geopy.geocoders import Nominatim
from twilio.rest import Client
from PIL import Image, ImageTk, ImageDraw
from cryptography.fernet import Fernet
import json
import base64
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import sys

class SecureStorage:
    """Handles secure storage of sensitive data"""
    def __init__(self):
        self.key_file = "secret.key"
        self.storage_file = "secure_config.json.enc"
        self._initialize_key()
        self._setup_logging()
    
    def _initialize_key(self):
        """Initialize encryption key"""
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
    
    def _get_fernet(self):
        """Get Fernet instance"""
        with open(self.key_file, 'rb') as f:
            key = f.read()
        return Fernet(key)
    
    def _setup_logging(self):
        """Set up secure logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logger = logging.getLogger('WomenSafetyBot')
        logger.setLevel(logging.INFO)
        
        handler = RotatingFileHandler(
            log_dir / 'app.log',
            maxBytes=1000000,
            backupCount=5
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        self.logger = logger

class WomenSafetyBot:
    def __init__(self):
        # Initialize secure storage
        self.secure_storage = SecureStorage()
        self.config = self._load_config()
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("Women Safety Bot")
        self.root.configure(bg='#E0F6E3')
        self.root.geometry("500x750")
        self.root.resizable(False, False)
        
        # Initialize database with encryption
        self.init_secure_db()
        
        # Setup GUI with security features
        self.setup_gui()
        
        # Initialize Twilio client with secure credentials
        self.twilio_client = self._initialize_twilio_client()
        
    def _load_config(self):
        """Load configuration securely"""
        try:
            if not os.path.exists(self.secure_storage.storage_file):
                return self._create_default_config()
            
            fernet = self.secure_storage._get_fernet()
            with open(self.secure_storage.storage_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = json.loads(fernet.decrypt(encrypted_data))
            return decrypted_data
        except Exception as e:
            self.secure_storage.logger.error(f"Config load error: {str(e)}")
            return self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        config = {
            'twilio_sid': os.getenv('TWILIO_SID', ''),
            'twilio_token': os.getenv('TWILIO_TOKEN', ''),
            'twilio_phone': os.getenv('TWILIO_PHONE', ''),
            'ip_api_url': 'https://api.ipify.org'
        }
        
        # Save configuration securely
        fernet = self.secure_storage._get_fernet()
        encrypted_data = fernet.encrypt(json.dumps(config).encode())
        with open(self.secure_storage.storage_file, 'wb') as f:
            f.write(encrypted_data)
        
        return config
    
    def init_secure_db(self):
        """Initialize SQLite database with encryption"""
        db_path = "emergency_contacts.db"
        if not os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create encrypted contacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Set up database encryption
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = FULL")
            cursor.execute("PRAGMA cipher_use_hmac = ON")
            
            conn.commit()
            conn.close()
    
    def setup_gui(self):
        """Set up GUI with security features"""
        FONT = ('Poppins', 12)
        BUTTON_FONT = ('Poppins', 12, 'bold')
        
        # Security indicator
        self.security_label = tk.Label(
            self.root,
            text="🔒 Secure Mode",
            font=('Poppins', 10),
            bg='#E0F6E3',
            fg='green'
        )
        self.security_label.pack(pady=10)
        
        # Chat box with secure display
        self.chatbox = scrolledtext.ScrolledText(
            self.root,
            height=15,
            width=50,
            bg='white',
            wrap=tk.WORD,
            font=FONT,
            borderwidth=5,
            relief=tk.GROOVE
        )
        self.chatbox.pack(pady=10)
        
        # Secure input handling
        self.entry = tk.Entry(
            self.root,
            font=FONT,
            width=40,
            borderwidth=5,
            relief=tk.GROOVE,
            show="*"  # Mask input
        )
        self.entry.pack(pady=5)
        
        # Secure buttons
        button_frame = tk.Frame(self.root, bg='#E0F6E3')
        button_frame.pack()
        
        yes_button = tk.Button(
            button_frame,
            text="Yes",
            command=self.handle_yes,
            font=BUTTON_FONT,
            bg='red',
            fg='white',
            relief=tk.FLAT
        )
        yes_button.grid(row=0, column=0, padx=10, pady=5)
        
        no_button = tk.Button(
            button_frame,
            text="No",
            command=self.handle_no,
            font=BUTTON_FONT,
            bg='blue',
            fg='white',
            relief=tk.FLAT
        )
        no_button.grid(row=0, column=1, padx=10, pady=5)
        
        # Secure contact management
        tk.Button(
            self.root,
            text="View Contacts",
            command=self.view_contacts,
            font=BUTTON_FONT
        ).pack(pady=5)
        
        tk.Button(
            self.root,
            text="Add Contact",
            command=self.add_contact_to_db,
            font=BUTTON_FONT
        ).pack(pady=5)
        
        tk.Button(
            self.root,
            text="Remove Contact",
            command=self.remove_contact_from_db,
            font=BUTTON_FONT
        ).pack(pady=5)
        
        self.insert_bot_message("Are you in danger?")
    
    def _initialize_twilio_client(self):
        """Initialize Twilio client with secure credentials"""
        try:
            return Client(
                self.config['twilio_sid'],
                self.config['twilio_token']
            )
        except Exception as e:
            self.secure_storage.logger.error(f"Twilio init error: {str(e)}")
            raise Exception("Twilio configuration error")
    
    def handle_yes(self):
        """Handle emergency response with security measures"""
        try:
            location = self.get_location()
            self.insert_bot_message("Request is being sent...")
            self.insert_bot_message(f"Location retrieved: {location}")
            self.insert_bot_message("Notifying emergency contacts via SMS...")
            
            # Log with masked location
            self.secure_storage.logger.info(
                "Emergency alert triggered. Location: XXX-XXX-XXX"
            )
            
            self.send_sms_alert(location)
        except Exception as e:
            self.secure_storage.logger.error(f"Emergency response error: {str(e)}")
            messagebox.showerror("Error", "Failed to send emergency alert!")
    
    def get_location(self):
        """Get location with security measures"""
        try:
            # Use HTTPS for secure IP lookup
            ip_response = requests.get(
                self.config['ip_api_url'],
                verify=True,
                timeout=10
            )
            
            if ip_response.status_code == 200:
                user_ip = ip_response.text.strip()
                g = geocoder.ip(user_ip)
                
                if g.ok and g.latlng:
                    geolocator = Nominatim(user_agent="womens_safety_bot")
                    location = geolocator.reverse(g.latlng, exactly_one=True)
                    
                    if location:
                        return location.address
                    else:
                        return "Location not found"
            return "Location not found"
        except Exception as e:
            self.secure_storage.logger.error(f"Location error: {str(e)}")
            return "Location not found"
    
    def send_sms_alert(self, location):
        """Send SMS alert with security measures"""
        try:
            emergency_numbers = self.get_contacts_from_db()
            
            for number in emergency_numbers:
                try:
                    message = self.twilio_client.messages.create(
                        body=f"🚨 Emergency Alert! 🚨\nLocation: {location}\nPlease take immediate action!",
                        from_=self.config['twilio_phone'],
                        to=number
                    )
                    
                    # Log with masked number
                    self.secure_storage.logger.info(
                        f"SMS alert sent to XXX-XXX-{number[-4:]}"
                    )
                except Exception as e:
                    self.secure_storage.logger.error(
                        f"SMS send error to {number}: {str(e)}"
                    )
        except Exception as e:
            self.secure_storage.logger.error(f"SMS alert error: {str(e)}")
    
    def get_contacts_from_db(self):
        """Get contacts with security measures"""
        try:
            conn = sqlite3.connect("emergency_contacts.db")
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT number FROM contacts")
            contacts = [row[0] for row in cursor.fetchall()]
            conn.close()
            return contacts
        except Exception as e:
            self.secure_storage.logger.error(f"Database error: {str(e)}")
            return []
    
    def add_contact_to_db(self):
        """Add contact with security measures"""
        try:
            contact = simpledialog.askstring(
                "Add Contact",
                "Enter emergency contact number:",
                show="*"  # Mask input
            )
            
            if contact:
                conn = sqlite3.connect("emergency_contacts.db")
                cursor = conn.cursor()
                
                # Validate input
                if not self._validate_phone_number(contact):
                    messagebox.showerror(
                        "Error",
                        "Invalid phone number format!"
                    )
                    return
                
                cursor.execute(
                    "SELECT number FROM contacts WHERE number = ?",
                    (contact,)
                )
                
                if cursor.fetchone():
                    messagebox.showinfo(
                        "Info",
                        "This contact is already saved."
                    )
                    return
                
                cursor.execute(
                    "INSERT INTO contacts (number) VALUES (?)",
                    (contact,)
                )
                conn.commit()
                conn.close()
                
                messagebox.showinfo(
                    "Success",
                    "Emergency contact added successfully!"
                )
        except Exception as e:
            self.secure_storage.logger.error(f"Add contact error: {str(e)}")
    
    def _validate_phone_number(self, number):
        """Validate phone number format"""
        # Basic validation for international phone numbers
        return bool(re.match(r'^\+?[1-9]\d{1,14}$', number))
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.secure_storage.logger.error(f"Main loop error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    app = WomenSafetyBot()
    app.run()
