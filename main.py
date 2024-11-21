import os
import scratchattach as sa
import requests
from cleantext import clean
import signal
import sys
import json

def shutdown_handler(signal_received, frame):
    """Handle graceful shutdown on interrupt or termination signals."""
    print("Shutting down gracefully...")
    client.stop()  # Stop the cloud request handler
    sys.exit(0)

# Register signal handlers for graceful termination
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

print("Subprocess infinite.py is running")

# Replace with your session details
session = sa.login_by_id(
  "DETAILS OMMITED"
)
user = session.connect_linked_user()
cloud = session.connect_cloud(1097538630)  # Replace with your project ID
client = cloud.requests()

print(user.username)

# Load merges.json
def load_merges():
    try:
        with open("merges.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: merges.json not found, creating a new one.")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in merges.json")
        return []

# Save updated merges.json
def save_merges(merges):
    try:
        with open("merges.json", "w") as file:
            json.dump(merges, file, indent=4)
        print("Updated merges.json successfully.")
    except Exception as e:
        print(f"Error saving merges.json: {e}")

merges = load_merges()

@client.request
def ping():
    print("Ping request received")
    with open("users.txt", "a") as f:
        f.write(client.get_requester())
    return "pong"



@client.request
def pair(argument1, argument2):
    print("Pair request received")
    print(argument1, argument2)

    # Check if the merge exists in merges.json
    for merge in merges:
        if merge["first"] == argument1 and merge["second"] == argument2:
            print(f"Merge found in file: {merge}")
            return clean(merge["result"])

    # If not found, call external API
    response = requests.get(f'https://infiniteback.org/pair?first={argument1}&second={argument2}')
    print(response.text.title())
    try:
        json_response = response.json()
        cleaned_result = clean(json_response["result"].title())
        
        # Add the new merge to the merges list and save to file
        new_merge = {"first": argument1, "second": argument2, "result": cleaned_result}
        merges.append(new_merge)
        save_merges(merges)  # Save the updated list to the file
        
        return cleaned_result
    except requests.exceptions.JSONDecodeError:
        return "Error: Invalid response format"
    except KeyError:
        return "Error: 'result' key missing"

@client.event
def on_ready():
    print("Request handler is running")

try:
    client.start(thread=True)
    # Keep the main thread running
    while True:
        pass
except KeyboardInterrupt:
    shutdown_handler(None, None)
