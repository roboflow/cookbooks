/*jshint esversion:6*/

$(function() {
    const video = $("video")[0];
    const seen = new Set()
    var counter = 0

    var model;

    var cameraMode = "environment"; // or "user"

    const startVideoStreamPromise = navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
            facingMode: cameraMode
        }
    }).then(function(stream) {
        return new Promise(function(resolve) {
            video.srcObject = stream;
            video.onloadeddata = function() {
                video.play();
                resolve();
            };
        });
    });

    var publishable_key = "rf_DH6zabhN9DNqv5ZlrFtEkAPy9g42";
    var toLoad = {
        model: "microsoft-coco",
        version: 2 // <<<--- YOUR VERSION THERE
    };

    const loadModelPromise = new Promise(function(resolve, reject) {
        roboflow.auth({
            publishable_key: publishable_key
        }).load(toLoad).then(function(m) {
            model = m;
            resolve();
        });
    });

    Promise.all([
        startVideoStreamPromise,
        loadModelPromise
    ]).then(function() {
        $('body').removeClass('loading');
        resizeCanvas();
        detectFrame();
    });

    var canvas, ctx;
    const font = "16px sans-serif";

    function randomIntFromInterval(min, max) { // min and max included 
        return Math.floor(Math.random() * (max - min + 1) + min)
      }
      
    function videoDimensions(video) {
        // Ratio of the video's intrisic dimensions
        var videoRatio = video.videoWidth / video.videoHeight;

        // The width and height of the video element
        var width = video.offsetWidth, height = video.offsetHeight;

        // The ratio of the element's width to its height
        var elementRatio = width/height;

        // If the video element is short and wide
        if(elementRatio > videoRatio) {
            width = height * videoRatio;
        } else {
            // It must be tall and thin, or exactly equal to the original ratio
            height = width / videoRatio;
        }

        return {
            width: width,
            height: height
        };
    }

    $(window).resize(function() {
        resizeCanvas();
    });

    const resizeCanvas = function() {
        $('canvas').remove();

        canvas = $('<canvas/>');

        ctx = canvas[0].getContext("2d");

        var dimensions = videoDimensions(video);

        console.log(video.videoWidth, video.videoHeight, video.offsetWidth, video.offsetHeight, dimensions);

        canvas[0].width = video.videoWidth;
        canvas[0].height = video.videoHeight;

        canvas.css({
            width: dimensions.width,
            height: dimensions.height,
            left: ($(window).width() - dimensions.width) / 2,
            top: ($(window).height() - dimensions.height) / 2
        });

        $('body').append(canvas);
    };

    const renderPredictions = function(predictions) {

        // changes:
        // 1. treat preditions like a stack, pop out one prediction and work with that if conf is right (load class into seen)
        // 2. add popped prediction.class to lookup set that clears via timeout every few sec
        // 3. add counter which track individual detection each time it comes out
        // 4. increase the random seed range
        
        var dimensions = videoDimensions(video);
        
        var scale = 1;
        
        // added some random box alterations to make objects harder to localize
        const low = 70, hi = 100
        const xRand = randomIntFromInterval(low, hi)
        const yRand = randomIntFromInterval(low, hi)
        
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
        
        let flag = false, prediction = null
        
        while(!flag && predictions.length > 1) {
            prediction = predictions.pop()
            if(prediction.confidence < .17 && !seen.has(prediction.class)) {
                flag = true
                seen.add(prediction.class)
                setTimeout(() => {seen.clear()}, 5000);
            }
                
        }

        if(flag && prediction) {
            const x = (prediction.bbox.x < 300 ? prediction.bbox.x : prediction.bbox.x + xRand)
            const y = (prediction.bbox.y < 300 ? prediction.bbox.y : prediction.bbox.y + yRand)
    
            const width = prediction.bbox.width;
            const height = prediction.bbox.height;
    
            // Draw the bounding box.
            ctx.strokeStyle = prediction.color;
            ctx.lineWidth = 4;
            ctx.strokeRect((x-width/2)/scale, (y-height/2)/scale, width/scale, height/scale);
    
            // Draw the label background.
            ctx.fillStyle = prediction.color;
            const textWidth = ctx.measureText(prediction.class).width;
            const textHeight = parseInt(font, 10); // base 10
            ctx.fillRect((x-width/2)/scale, (y-height/2)/scale, textWidth + 8, textHeight + 4);
    
            // Draw the text last to ensure it's on top.
            ctx.font = font;
            ctx.textBaseline = "top";
            ctx.fillStyle = "#000000";
            ctx.fillText("ghost", (x-width/2)/scale+4, (y-height/2)/scale+1);

            counter++
            document.getElementById("counter_h3").innerHTML = "Spooky Ghost Counter = " + counter;
        }
    };

    var prevTime;
    var pastFrameTimes = [];
    const detectFrame = function() {
        if(!model) return requestAnimationFrame(detectFrame);

        // reduce minimum detection threshold
        model.configure({
            threshold: 0.15
        });

        model.detect(video).then(function(predictions) {
            requestAnimationFrame(detectFrame);
            renderPredictions(predictions);

            if(prevTime) {
                pastFrameTimes.push(Date.now() - prevTime);
                if(pastFrameTimes.length > 30) pastFrameTimes.shift();

                var total = 0;
                _.each(pastFrameTimes, function(t) {
                    total += t/1000;
                });

                var fps = pastFrameTimes.length / total;
                $('#fps').text(Math.round(fps));
            }
            prevTime = Date.now();
        }).catch(function(e) {
            console.log("CAUGHT", e);
            requestAnimationFrame(detectFrame);
        });
    };
});
