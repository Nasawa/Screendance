import json
import threading
import mss
import time
import colorsys
import numpy as np
from PIL import Image, ImageStat
import paho.mqtt.client as mqtt

# Load MQTT credentials from a JSON file
with open('mqtt_credentials.cred.json', 'r') as file:
    credentials = json.load(file)

# Load config from a JSON file
with open('config.json', 'r') as file:
    config = json.load(file)

# Define the MQTT server settings
MQTT_SERVER = config['MQTT']['host']
MQTT_PORT = config['MQTT']['port']
MQTT_WRITE_TOPIC = config['MQTT']['write_topic']
MQTT_READ_TOPIC = config['MQTT']['read_topic']
MQTT_USERNAME = credentials['username']
MQTT_PASSWORD = credentials['password']

is_script_enabled = False
sections = None

def capture_screen(monitor=config['display']['index']):
    with mss.mss() as sct:
        sct_img = sct.grab(sct.monitors[monitor])
        return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

def calculate_average_color_and_brightness(img, coordinates):
    # Crop the image to the specified coordinates
    cropped_img = img.crop(coordinates)
    # Convert the image to numpy array and calculate the mean color
    pixels = np.array(cropped_img)
    avg_color = np.mean(pixels.reshape(-1, 3), axis=0)

    # Normalize the RGB values
    normalized_rgb = [x / 255.0 for x in avg_color]

    # Convert RGB to HSV
    hsv_color = colorsys.rgb_to_hsv(*normalized_rgb)

    # Scale the HSV values to the expected range
    hue = hsv_color[0] * 360  # Hue from 0 to 360
    saturation = hsv_color[1] * 100  # Saturation from 0 to 100%
    value = hsv_color[2] * 100  # Value (brightness) from 0 to 100%

    # Return HSV values, with value being the brightness
    return {
        "color": {
            "hue": hue,
            "saturation": saturation
        },
        "brightness": value
    }

def calculate_grid_sections(width, height, columns, rows):
    sections = {}
    # Get the width of each section
    section_width = width // columns
    # Get the height of each section
    section_height = height // rows
    counter = 1

    for col in range(columns):
        for row in range(rows):
            left = col * section_width
            upper = row * section_height
            right = left + section_width
            lower = upper + section_height
            # Define the section boundaries
            sections[config['lights']['prefix'] + str(counter)] = (left, upper, right, lower)
            counter += 1

    return sections

# The callback for when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    global is_script_enabled
    print(f"Message received on topic {msg.topic} with QoS {msg.qos}. Full message: { msg.payload.decode('utf-8') }")
    print(f"pre: is_script_enabled is {is_script_enabled}")
    is_script_enabled = msg.payload.decode("utf-8") == 'True'
    print(f"post: is_script_enabled is {is_script_enabled}")
    thread = threading.Thread(target=screendance)
    thread.start()

def main():
    # Calculate the sections based on the given grid
    global sections
    sections = calculate_grid_sections(config['display']['resolution_width'], config['display']['resolution_height'], config['lights']['columns'], config['lights']['rows'])
    # print('sections', sections)

    client.subscribe(MQTT_READ_TOPIC)
    client.on_message = on_message
    screendance()

def screendance():
    global is_script_enabled
    while is_script_enabled:
        # print("test")
        # Capture the screen
        img = capture_screen()
        # Calculate color and brightness for each section and create a JSON object
        color_and_brightness = {section: calculate_average_color_and_brightness(img, coordinates) for section, coordinates in sections.items()}
        # Convert the color and brightness values to a serializable format
        color_and_brightness_serializable = {
            k: {
                'color': {c_k: round(c_v, 2) for c_k, c_v in v['color'].items()},  # Rounded to two decimal places for hue and saturation
                'brightness': round(v['brightness'], 2)  # Rounded to two decimal places for brightness
            } for k, v in color_and_brightness.items()
        }
        json_object = json.dumps(color_and_brightness_serializable, indent=4)

        # Publish a message
        if (is_script_enabled):
            client.publish(MQTT_WRITE_TOPIC, json_object)

        time.sleep(config['misc']['delay'])

        # Print the JSON object
        # print(json_object)

if __name__ == "__main__":
    # Create a client instance
    client = mqtt.Client()
    # Set the username and password
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    # Connect to the MQTT server
    client.connect(MQTT_SERVER, MQTT_PORT, 60)

    main()

    client.loop_forever()