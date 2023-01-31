function addCameraInputOption (id, label) {
    var option = document.createElement("option");
    option.setAttribute("value", id);
    option.innerHTML = label;
    document.getElementById("camera_input").appendChild(option);
}

var bounding_box_colors = {};

var confidence = 0.5;

function changeConfidence(value) {
    document.getElementById("confidence").value = value;
    confidence = value;
    console.log(confidence);
}

function drawBoundingBoxes (predictions, canvas, ctx, user_stated_confidence = 0.5) {
    for (var i = 0; i < predictions.length; i++) {
        var confidence = predictions[i].confidence;

        if (confidence < user_stated_confidence) {
            continue;
        }

        if (predictions[i].class in bounding_box_colors) {
            ctx.strokeStyle = bounding_box_colors[predictions[i].class];
        } else {
            var o = Math.round, r = Math.random, s = 255;
            ctx.strokeStyle = "#" + Math.floor(Math.random()*16777215).toString(16);
            bounding_box_colors[predictions[i].class] = ctx.strokeStyle;
        }

        var rect = canvas.getBoundingClientRect();

        var prediction = predictions[i];
        var x = prediction.bbox.x - prediction.bbox.width / 2;
        var y = prediction.bbox.y - prediction.bbox.height / 2;
        var width = prediction.bbox.width;
        var height = prediction.bbox.height;

        var scaling = window.devicePixelRatio;

        ctx.rect(x, y, width, height);

        ctx.fillStyle = "rgba(0, 0, 0, 0)";
        ctx.fill();

        ctx.fillStyle = ctx.strokeStyle;
        ctx.lineWidth = "4";
        ctx.strokeRect(x, y, width, height);
        ctx.font = "25px Arial";
        ctx.fillText(prediction.class + " " + Math.round(confidence * 100) + "%", x, y - 10);
    }
}

// get webcam feed
var video = document.createElement("video");
video.setAttribute("autoplay", "");
video.setAttribute("muted", "");
video.setAttribute("playsinline", "");

// create canvas
var canvas = document.createElement("canvas");
canvas.setAttribute("width", "640");
canvas.setAttribute("height", "480");
document.getElementById("canvas").appendChild(canvas);

// get canvas context
var ctx = canvas.getContext("2d");

// if user pastes in image url, run inference
var image_url = document.getElementById("image_url");

image_url.addEventListener("input", function() {
    console.log("image url changed");
    var image = new Image();
    image.src = document.getElementById("image_url").value;
    // set anonymous canvas to image
    image.crossOrigin = "Anonymous";
    image.onload = function() {
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
    }
    // set canvas to image
    image.onload = function() {
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
    }
    roboflow.auth({
        publishable_key: "rf_arRagmpkRzqLfrKDYQ18"
    }).load({
        model: "cash-counter",
        version: 10
    }).then(function(model) {
        model.detect(image).then(function(predictions) {
            console.log(predictions);
            drawBoundingBoxes(predictions, canvas, ctx, confidence);
        });
    });
});

navigator.mediaDevices.getUserMedia({ video: true, audio: false }).then(function(stream) {
    video.srcObject = stream;
    video.play();

    // add camera inputs to list
    var videoTracks = stream.getVideoTracks();
    for (var i = 0; i < videoTracks.length; i++) {
        addCameraInputOption(i, videoTracks[i].label);
    }

    roboflow.auth({
        publishable_key: "rf_YOUR_KEY"
    }).load({
        model: "cash-counter",
        version: 10
    }).then(function(model) {
        setInterval(function() {
            model.detect(video).then(function(predictions) {
                // draw frame on canvas
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                // update pre to show predictions
                document.getElementById("predictions").innerHTML = JSON.stringify(predictions, null, 4);

                drawBoundingBoxes(predictions, canvas, ctx, confidence);
            });
        }, 1000 / 30);
    });
});