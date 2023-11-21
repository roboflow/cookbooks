var express = require('express');
var cors = require('cors');
var app = express();
const { exec } = require("child_process");

app.use(cors());

var bodyParser = require('body-parser');

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: false }));

// parse application/json
app.use(bodyParser.json());

app.get('/', function (req, res, next) {
  res.sendfile(__dirname + "/public/index.html");
});

app.post('/rick', function(req, res) {
    var hasFoundRick = req.body.found != "false";

    var command;
    if(hasFoundRick) {
        console.log("Set volume to 0");
        command = 'osascript -e "set Volume 0"';
    } else {
        console.log("Set volume to 80");
        command = 'osascript -e "set Volume 80"';
    }
    exec(command);

    res.json({
        success: true,
        rick: hasFoundRick
    });
});

app.use(express.static('public'));

app.listen(5000);