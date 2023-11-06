###### Readme generated in part by ChatGPT

# Screendance
Screendance is a Python application designed to interface with MQTT (Message Queuing Telemetry Transport) to control lighting systems based on screen content. It captures the screen's display, calculates the average color and brightness, and sends this information to an MQTT topic, which can then be used to control the lighting in real-time.

## Features
- Screen capture for real-time display analysis.
- Calculation of average color and brightness for specified screen sections.
- MQTT integration for sending color and brightness data.
- Configurable settings for display resolution, light grid, and MQTT connection details.

## Configuration
The application uses a `config.json` file to set up various parameters such as display settings, light grid configuration, and MQTT server details. Here is an example of the configuration structure:

``` json
{
    "display": {
        "index": 1, // which monitor to use
        "resolution_width": 1920,
        "resolution_height": 1080
    },
    "lights": {
        "prefix": "living_room_", // this will result in living_room_1, living_room_2, etc.
        "initial_index": 1, // which number to start at 
        "columns": 3,
        "rows": 2
    },
    "MQTT": {
        "host": "homeassistant.local",
        "port": 1883,
        "write_topic": "gaming/lights/screendance",
        "read_topic": "gaming/lights/illuminate"
    },
    "misc": {
        "delay": 0.1 // seconds
    },
    "credentials": {
        "enabled": true,
        "file": "./mqtt_credentials.cred.json"
    },
    "debug": false
}
```

## Usage
To use Screendance, ensure that you have the correct configuration in your `config.json` file. The application will read the configuration and connect to the MQTT server using the provided details.

The main script `screendance.py` includes all the necessary functions to capture the screen, calculate the color and brightness, and publish the data to the MQTT topic.

## Installation
To install Screendance, clone the repository and install the required dependencies:

``` bash
git clone https://github.com/Nasawa/Screendance.git
cd Screendance
pip install -r requirements.txt
```

## MQTT Credentials Configuration

The application requires a separate credentials file named `mqtt_credentials.cred.json` for establishing a secure connection to the MQTT server. This file should contain the MQTT username and password in JSON format.

### Setting up `mqtt_credentials.cred.json`

1. **Create the file**: In the root directory of the project, create a file named `mqtt_credentials.cred.json`.

2. **Add your credentials**: Open the file in a text editor and insert your MQTT credentials in the following structure:

   ```json
   {
     "username": "your_mqtt_username",
     "password": "your_mqtt_password"
   }
   ```

   Replace `your_mqtt_username` and `your_mqtt_password` with your actual MQTT credentials.

3. **Save the file**: Save the changes and ensure the file is in the `.gitignore` file to prevent it from being committed to your version control system, as it contains sensitive information.

### Security Note

It's crucial to keep your MQTT credentials secure. Do not share the `mqtt_credentials.cred.json` file or include it in your public code repositories. Always confirm that it is listed in your `.gitignore` file to avoid accidental exposure.


## Running the Application
Run the application with the following command:

``` bash
python screendance.py
```

Ensure that your MQTT broker is running and that the topics are correctly set up to receive the data from Screendance.

## Contributing
Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License - see the LICENSE file for details.