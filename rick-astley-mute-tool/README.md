# Computer Vision Rick Astley Muter

This project utilizes an advanced computer vision model to mute your
speakers when Rick Astley is detected on your screen.

https://user-images.githubusercontent.com/870796/161333961-6f4ba4c9-0ce3-4087-9e44-96caa01aca0c.mp4

* [See it in action on YouTube](https://youtu.be/uDUFPrNmBNU),
* [Read more on our blog](https://blog.roboflow.com/rick-realtime-intrusion-checker-kernel/) or
* [Download the dataset](https://universe.roboflow.com/april-public-yibrz/never-gonna/2/export) and [try the model](https://universe.roboflow.com/april-public-yibrz/never-gonna) on [Roboflow Universe](https://universe.roboflow.com).

## How to Use

Use [OBS](https://obsproject.com/)'s Virtual Camera feature to pipe your screen through
to your web browser.

Clone this repo, cd into the `server` directory and `npm install` the dependencies.

Start the web server with `sudo node index.js`.

Navigate to `http://localhost:5000` and use OBS Webcam as the video source.

Try to rickroll yourself. Your audio will mute when Rick is on screen and unmute otherwise.

## Tools Used

The data behind the model was collected, annotated, and trained using
a free [Roboflow](https://roboflow.com) account.
