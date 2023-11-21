/*jshint esversion:8*/

// system packages
const fs = require('fs');
const path = require('path');
const os = require('os');

// basic helpers
const async = require('async');
const _ = require('lodash');

// drawing utilities
const { createCanvas, loadImage, CanvasRenderingContext2D } = require('canvas');
const floodfill = require('@roboflow/floodfill')(CanvasRenderingContext2D);

// for writing annotations
var Handlebars = require('handlebars');
var vocTemplate = Handlebars.compile(fs.readFileSync(__dirname + "/voc.tmpl", "utf-8"));

// how many images we want to create
const IMAGES_TO_GENERATE = 5000;
// how many to generate at one time
const CONCURRENCY = Math.max(1, os.cpus().length - 1);

// approximate aspect ratio of our phone camera
// scaled to match the input of CreateML models
const CANVAS_WIDTH = 416;
const CANVAS_HEIGHT = 550;

// the most objects you want in your generated images
const MAX_OBJECTS = 10;

// where to store our images
const OUTPUT_DIR = path.join(__dirname, "output");

// location of jpgs on your filesystem (validation set from here: https://www.figure-eight.com/dataset/open-images-annotated-with-bounding-boxes/)
const OPEN_IMAGES = path.join(os.homedir(), "OpenImages");
// text file of good candidate images (I selected these for size & no fruit content)
const BACKGROUNDS = fs.readFileSync(__dirname + "/OpenImages.filtered.txt", "utf-8").split("\n");

// location of folders containing jpgs on your filesystem (clone from here: https://github.com/Horea94/Fruit-Images-Dataset)
const FRUITS = path.join(os.homedir(), "Fruit-Images-Dataset/Training");
// get class names
const folders = _.filter(fs.readdirSync(FRUITS), function(filename) {
    // filter out hidden files like .DS_STORE
    return filename.indexOf('.') != 0;
});
var classes = _.map(folders, function(folder) {
    // This dataset has some classes like "Apple Golden 1" and "Apple Golden 2"
    // We want to combine these into just "Apple" so we only take the first word
    return folder.split(" ")[0];
});
// for each class, get a list of images
const OBJECTS = {};
_.each(folders, function(folder, i) {
    var cls = classes[i]; // get the class name

    var objs = [];
    objs = _.filter(fs.readdirSync(path.join(FRUITS, folder)), function(filename) {
        // only grab jpg images
        return filename.match(/\.jpe?g/);
    });

    objs = _.map(objs, function(image) {
        // we need to know which folder this came from
        return path.join(folder, image);
    });
    
    if(!OBJECTS[cls]) {
        OBJECTS[cls] = objs;
    } else {
        // append to existing images
        _.each(objs, function(obj) {
            OBJECTS[cls].push(obj);
        });
    }
});
// when we randomly select a class, we want them equally weighted
classes = _.uniq(classes);

// create our output directory if it doesn't exist
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR);

// create the images
_.defer(function() {
    var num_completed = 0;
    const progress_threshold = Math.max(1, Math.round( Math.min(100, IMAGES_TO_GENERATE/1000) ) );
    async.timesLimit(IMAGES_TO_GENERATE, CONCURRENCY, function(i, cb) {
        createImage(i, function() {
            // record progress to console
            num_completed++;
            if(num_completed%progress_threshold === 0) {
                console.log((num_completed/IMAGES_TO_GENERATE*100).toFixed(1)+'% finished.');
            }
            cb(null);
        });
    }, function() {
        // completely done generating!
        console.log("Done");
        process.exit(0);
    });
});

const createImage = function(filename, cb) {
    // select and load a random background
    const BG = _.sample(BACKGROUNDS);
    loadImage(path.join(OPEN_IMAGES, BG)).then(function(img) {
        var canvas = createCanvas(CANVAS_WIDTH, CANVAS_HEIGHT);
        var context = canvas.getContext('2d');

        // scale the background to fill our canvas and paint it in the center
        var scale = Math.max(canvas.width / img.width, canvas.height / img.height);
        var x = (canvas.width / 2) - (img.width / 2) * scale;
        var y = (canvas.height / 2) - (img.height / 2) * scale;
        context.drawImage(img, x, y, img.width * scale, img.height * scale);

        // calculate how many objects to add
        // highest probability is 1, then 2, then 3, etc up to MAX_OBJECTS
        // if you want a uniform probability, remove one of the Math.random()s
        var objects = 1+Math.floor(Math.random()*Math.random()*(MAX_OBJECTS-1));

        var boxes = [];
        async.timesSeries(objects, function(i, cb) {
            // for each object, add it to the image and then record its bounding box
            addRandomObject(canvas, context, function(box) {
                boxes.push(box);
                cb(null);
            });
        }, function() {
            // write our files to disk
            async.parallel([
                function(cb) {
                    // write the JPG file
                    const out = fs.createWriteStream(path.join(__dirname, "output", filename+".jpg"));
                    const stream = canvas.createJPEGStream();
                    stream.pipe(out);
                    out.on('finish', function() {
                        cb(null);
                    });
                },
                function(cb) {
                    // write the bounding boxes to the XML annotation file
                    fs.writeFileSync(
                        path.join(__dirname, "output", filename+".xml"),
                        vocTemplate({
                            filename: filename + ".jpg",
                            width: CANVAS_WIDTH,
                            height: CANVAS_HEIGHT,
                            boxes: boxes
                        })
                    );

                    cb(null);
                }
            ], function() {
                // we're done generating this image
                cb(null);
            });
        });
    });
};

// select a random class, then select an image from that class
// add it to a random location on our canvas
// and return the info about its bounding box
const addRandomObject = function(canvas, context, cb) {
    const cls = _.sample(classes);
    const object = _.sample(OBJECTS[cls]);

    loadImage(path.join(FRUITS, object)).then(function(img) {
        // erase white edges
        var objectCanvas = createCanvas(img.width, img.height);
        var objectContext = objectCanvas.getContext('2d');

        objectContext.drawImage(img, 0, 0, img.width, img.height);

        // flood fill starting at all the corners
        const tolerance = 32;
        objectContext.fillStyle = "rgba(0,255,0,0)";
        objectContext.fillFlood(3, 0, tolerance);
        objectContext.fillFlood(img.width-1, 0, tolerance);
        objectContext.fillFlood(img.width-1, img.height-1, tolerance);
        objectContext.fillFlood(0, img.height-1, tolerance);

        // cleanup edges
        objectContext.blurEdges(1);
        objectContext.blurEdges(0.5);

        // make them not all look exactly the same
        // objectContext.randomHSL(0.1, 0.25, 0.4);
        objectContext.randomHSL(0.05, 0.4, 0.4);

        // randomly scale the image
        var scaleAmount = 0.5;
        const scale = 1 + Math.random()*scaleAmount*2-scaleAmount;

        var w = img.width * scale;
        var h = img.height * scale;

        // place object at random position on top of the background
        const max_width = canvas.width - w;
        const max_height = canvas.height - h;

        var x = Math.floor(Math.random()*max_width);
        var y = Math.floor(Math.random()*max_height);

        context.save();

        // randomly rotate and draw the image
        const radians = Math.random()*Math.PI*2;
        context.translate(x+w/2, y+h/2);
        context.rotate(radians);
        context.drawImage(objectCanvas, -w/2, -h/2, w, h);
        context.restore();

        // return the type and bounds of the object we placed
        // VOC XML's top-left pixel is 1,1
        cb({
            cls: cls,
            xmin: Math.floor(x)+1,
            xmax: Math.ceil(x + w)+1,
            ymin: Math.floor(y)+1,
            ymax: Math.ceil(y + h)+1
        });
    });
};
