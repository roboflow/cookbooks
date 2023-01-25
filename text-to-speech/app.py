import time
import os

import pyttsx3
import roboflow

rf = roboflow.Roboflow(api_key=os.environ["ROBOFLOW_API_KEY"])

workspace = rf.workspace()

engine = pyttsx3.init()
engine.setProperty("rate", 150)

def say(text: str) -> None:
    """
    Speak out text and print that text to the console.
    """
    engine.say(text)
    print(text)

    engine.runAndWait()

def get_room_type(image_file: str) -> dict:
    """
    Get the type of room a photo was taken in (i.e. kitchen).
    """
    indoor_scene_recognition = workspace.project("mit-indoor-scene-recognition")

    model = indoor_scene_recognition.version(5).model
    
    prediction = model.predict(image_file)

    room = prediction.json()

    return room

def get_items_in_room(image: str) -> list:
    """
    Find items in a room.
    """
    project = workspace.project('all_finalize')

    model = project.version(3).model

    prediction = model.predict(image, confidence=10)

    predictions = prediction.json()

    labels = [p["class"] for p in predictions["predictions"]]

    prediction.save("out.png")

    return labels

def narrate_room(room_type: str, labels: list) -> None:
    """
    Speak out the type of room a photo was taken in and the objects in the room.
    """
    say(f"You are in a {room_type}")

    time.sleep(1)

    if len(labels) > 0:
        say("I see")
        time.sleep(0.5)

    for label in labels:
        label = label.lower()
        say("A " + label)

        time.sleep(0.5)

image = "images/kitchen1.jpeg"

room = get_room_type(image)
labels = get_items_in_room(image)

room_type = room["predictions"][0]["top"]

narrate_room(room_type, labels)
