# women-s-safety-chatbot
This is a basic bot I created as my few new projects since I  am new to this, will love to further enhance them with time, for detailed stuff refer to other files I uploaded :D


#Now let's go with detailed stuff


The **Women Safety Chatbot** is a security-focused application designed to assist users in emergency situations. This chatbot provides a quick and efficient way to notify emergency contacts and authorities by sending an alert message along with the user’s location.  

#### **Key Features:**  
✅ **Emergency Alert System** – Sends an SOS message to pre-stored emergency contacts.  
✅ **Location Retrieval** – Automatically fetches the user’s location or allows manual entry.  
✅ **Emergency Contact Storage** – Users can save important contacts for quick access.  
✅ **WhatsApp & SMS Alerts** – Uses Twilio API to send distress messages efficiently.  
✅ **User-Friendly Interface** – A clean, modern, and intuitive design for seamless interaction.  

This chatbot ensures that help is just one tap away, providing users with a sense of security wherever they go. 🚨

One nice thing I could say about is that the location retreival may not be precised but let me tell you how it works, the chatbot retrieves the user's location by first fetching their IP address using an online service. It then determines the approximate latitude and longitude with the Geocoder library. Using Geopy's Nominatim, these coordinates are converted into a readable address. The retrieved location is automatically sent to emergency contacts for assistance. Since IP-based location may not always be precise, the bot also allows users to manually enter their location to ensure accuracy. This ensures that help can reach them as quickly as possible in an emergency. 
