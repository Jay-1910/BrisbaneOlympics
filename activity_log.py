import datetime
import os
import geocoder

def log_activity(username, activity):
    activity_log_file = get_activity_log_filename()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get the user's live location (city name)
    user_location = get_user_location()
    
    log_entry = f"{timestamp}: {username} - {activity} - Location: {user_location}\n"
    
    with open(activity_log_file, "a") as file:
        file.write(log_entry)

def get_user_location():
    g = geocoder.ip("me")
    city = g.city  # Get the city name
    return city

def get_activity_log():
    activity_log_file = get_activity_log_filename()
    try:
        with open(activity_log_file, "r") as file:
            return file.readlines()
    except FileNotFoundError:
        return []

def get_activity_log_filename():
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    activity_log_file = f"activity_log_{today_date}.txt"
    if not os.path.exists(activity_log_file):
        with open(activity_log_file, "w") as file:
            file.write("User Activity Log\n\n")
    return activity_log_file
