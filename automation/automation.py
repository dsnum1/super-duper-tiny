from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import asyncio
import websockets
import serial
import numpy as np


# Sampling rate (samples per second)
fs = 16000  
# Duration of the window in seconds
duration = 0.8  # 800 milliseconds

def audio_callback(indata, frames, time, status):
    """
    This callback function is called for each audio block.
    """
    if status:
        print(status)
    # Process audio input here
    print(np.linalg.norm(indata))  # Example processing: compute the norm of the input data


from selenium.webdriver.common.action_chains import ActionChains



def parse_inference(data):
    results = {}
    lines = data.split('\n')
    for line in lines:
        if ":" in line:
            key, value = line.split(':', 1)
            results[key.strip()] = value.strip()
    return results


driver = webdriver.Edge()
driver.get("https://www.sticksports.com/web-games/game/stick-cricket/world-t2/")


# ask if user is ready
a = input("user_ready?")
print('user output {a}')

# exeucting key press
inference_results = {}
shot_classification = {
    "cover_drive":0,
    "on_drive":0,
    "pull_shot":0,
    "square_cut":0,
    "idle":1
}

actions = ActionChains(driver)
with serial.Serial('COM9', 921600, timeout=0.05) as ser:
    print("Serial Connected")
    while True:
        line = ser.readline().decode('utf-8')
        if "Timing" in line or "Anomaly" in line or ":" in line:  # Filter relevant lines
            # print(line)  # Optionally print the raw data for debugging
            updated_results = parse_inference(line)
            inference_results.update(updated_results)
            # print(inference_results)  # Print updated dictionary
            try:
                shot_classification["cover_drive"] = inference_results["cover drive"] 
                shot_classification["on_drive"] = inference_results["on drive"] 
                shot_classification["pull_shot"] = inference_results["pull shot"] 
                shot_classification["square_cut"] = inference_results["square cut"] 
                shot_classification["idle"] = inference_results["idle"] 
                max_shot = max(shot_classification, key=shot_classification.get)

                actions = ActionChains(driver)
                # Inside your loop:
                print(max_shot)
                actions.reset_actions()  # Clear all the queued actions
                if max_shot == "cover_drive" or max_shot == "square_cut":
                    actions.send_keys(Keys.ARROW_RIGHT).perform()
                elif max_shot == "pull_shot" or max_shot == "on_drive":
                    actions.send_keys(Keys.ARROW_LEFT).perform()

                else:
                    # print('came here')
                    pass
            except:
                continue

            


        # message = ser.read_until(b'\n')
        # decoded_message = message.decode('utf-8', errors='replace')
        # if len(decoded_message) ==0:
        #     continue 
        # instruction = decoded_message[0]
        # print(decoded_message)
        # if instruction == 'L':
        #     actions.send_keys(Keys.ARROW_LEFT)  # Simulating an "up arrow" keypress
        #     actions.perform()
        # elif instruction == 'F':
        #     actions.send_keys(Keys.ARROW_UP)  # Simulating an "up arrow" keypress
        #     actions.perform()
        # elif instruction == 'R':
        #     actions.send_keys(Keys.ARROW_RIGHT)  # Simulating an "up arrow" keypress
        #     actions.perform()

        # print('Sending message:', decoded_message)
        # print(len(decoded_message))

time.sleep(5)
driver.close()