/*jshint esversion:6*/

$(function () {
    var video = $("<video id='video' autoplay muted playsinline></video>")[0];
    var headerHeight = 61;

    var model;
    var cameraMode = "user";

    var inferCode, inferContext;

    var publishable_key = "rf_SFgRaqEsIPfd7Vj37buG";
        
    var modelName = "never-gonna";
    var version = "2";

    var flipVideo = true;
    var additionalFlip = false;
    var videoDenied = false;
    var startVideo = function () {
        return navigator.mediaDevices
            .getUserMedia({
                audio: false,
                video: {
                    facingMode: cameraMode
                }
            })
            .then(function (stream) {
                var settings = stream.getVideoTracks()[0].getSettings();
                if (settings && settings.facingMode && settings.facingMode == "environment")
                    flipVideo = false;

                return new Promise(function (resolve) {
                    video.srcObject = stream;
                    video.onloadeddata = function () {
                        video.play();
                        resolve();
                    };
                });
            })
            .catch(function (e) {
                videoDenied = true;
                var template = Handlebars.compile($("#videoDeniedTemplate").html());
                $("#content").html(template());
            });
    };

    var defaultInitCode = [
        "return {",
        "    last: Date.now(),",
        "    delay: 500",
        "};"
    ].join("\n");

    var defaultInferCode = [
        "var hasFoundRick = _.find(predictions, function(p) {",
        "    if(p.class == 'rick') return true;",
        "}) || false;",
        "",
        "if(inferContext.last + inferContext.delay <= Date.now()) {",
        "    inferContext.last = Date.now();",
        "    $.post('http://localhost:5000/rick', {",
        "        found: hasFoundRick",
        "    }, function() {}, 'JSON');",
        "}"
    ].join("\n");

    var getSavedConfiguration = function () {
        var saved = _.getItem("demoConfig_" + modelName);
        if (!saved || saved == "undefined") {
            return {
                flip: false,
                confidence: 0.5,
                initCode: defaultInitCode,
                inferCode: defaultInferCode
            };
        } else {
            return JSON.parse(saved);
        }
    };

    var utilizeConfiguration = function (config) {
        if (!model || !config) return;

        model.configure({
            threshold: config.confidence
        });

        additionalFlip = config.flip;
        var needToFlip = flipVideo ^ additionalFlip;

        if (needToFlip) {
            $("video").addClass("flip");
        } else {
            $("video").removeClass("flip");
        }

        try {
            if (config.initCode) {
                var initFn = Function(config.initCode);
                inferContext = initFn();
            }

            if (config.inferCode) {
                inferCode = Function(
                    [
                        "var predictions = arguments[0];",
                        "var inferContext = arguments[1];",
                        config.inferCode
                    ].join("\n")
                );
            }
        } catch (e) {
            console.log("Custom code error", e);
        }
    };

    var metadata;
    var loadModelPromise = new Promise(function (resolve, reject) {
        roboflow
            .auth({
                publishable_key: publishable_key,
                staging: window.location.host.indexOf("staging.roboflow.com") >= 0
            })
            .load({
                model: modelName,
                version: version,
                onMetadata: function (m) {
                    metadata = m;
                    $("#loadingText").text("Loading Model Weights...");
                    if (hasCameraAccess) return;

                    var template = Handlebars.compile($("#promptCameraTemplate").html());
                    $("#content").html(template(metadata));

                    $("#enableCamera").click(function () {
                        $(this).unbind("click");
                        $(this).text("Initializing...");
                        go();
                    });
                }
            })
            .then(function (m) {
                model = m;
                utilizeConfiguration(getSavedConfiguration());

                resolve();
            })
            .catch(function (e) {
                alert("Sorry, we were unable to load this model.");
                console.error(e && e.error);
            });
    });

    var go = function () {
        Promise.all([startVideo(), loadModelPromise]).then(function (p) {
            if (videoDenied) return;

            var template = Handlebars.compile($("#displayModelTemplate").html());
            $("#content").html(template());
            $("#videoContainer").prepend(video);
            if (flipVideo) $("video").addClass("flip");

            $("#getCode").removeClass("hidden");
            $("#modelName").text(metadata.name + " v" + version);

            $("#getCode").click(function () {
                var template = Handlebars.compile($("#codeSnippetTemplate").html());
                swal.fire({
                    confirmButtonText: "Download Sample App",
                    showCancelButton: true,
                    cancelButtonText: "Done",
                    html: template({
                        roboflow: roboflow.VERSION,
                        publishable_key: publishable_key,
                        model: modelName,
                        version: version
                    })
                }).then(function (result) {
                    if (result && result.isConfirmed) {
                        window.open("/files/roboflow-customer-demo.zip");
                    }
                });
            });

            $("#settings").click(function () {
                var template = Handlebars.compile($("#settingsTemplate").html());
                swal.fire({
                    confirmButtonText: "Save",
                    showCancelButton: true,
                    cancelButtonText: "Cancel",
                    html: template(getSavedConfiguration()),
                    onOpen: function () {
                        $("#settingsDialog").bind({
                            keypress: function (e) {
                                e.stopPropagation();
                            }
                        });
                    },
                    preConfirm: function () {
                        var confidence = parseFloat($("#confidence").val());
                        var flip = $("#flip").prop("checked");

                        _.setItem(
                            "demoConfig_" + modelName,
                            JSON.stringify({
                                flip: !!flip,
                                confidence: confidence,
                                initCode: $("#initCode").val(),
                                inferCode: $("#inferCode").val()
                            })
                        );
                    }
                }).then(function (result) {
                    if (result && result.isConfirmed) {
                        utilizeConfiguration(getSavedConfiguration());
                    }
                });
            });

            resizeCanvas();
            detectFrame();
        });
    };

    var hasCameraAccess = false;
    navigator.mediaDevices.enumerateDevices().then(function (devices) {
        hasCameraAccess = /*false &&*/ !!_.find(devices, function (d) {
            return d.kind == "videoinput" && d.label;
        });

        if (hasCameraAccess) go();
    });

    var canvas, ctx;
    var font = "16px sans-serif";

    function videoDimensions(video) {
        // Ratio of the video's intrisic dimensions
        var videoRatio = video.videoWidth / video.videoHeight;

        // The width and height of the video element
        var width = video.offsetWidth,
            height = video.offsetHeight;

        // The ratio of the element's width to its height
        var elementRatio = width / height;

        // If the video element is short and wide
        if (elementRatio > videoRatio) {
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

    $(window).resize(function () {
        resizeCanvas();
    });

    var resizeCanvas = function () {
        $("canvas").remove();

        canvas = $("<canvas/>");

        ctx = canvas[0].getContext("2d");

        var dimensions = videoDimensions(video);

        // console.log(video.videoWidth, video.videoHeight, video.offsetWidth, video.offsetHeight, dimensions);

        canvas[0].width = video.videoWidth;
        canvas[0].height = video.videoHeight;

        canvas.css({
            width: dimensions.width,
            height: dimensions.height,
            left: ($(window).width() - dimensions.width) / 2,
            top: (61 + $(window).height() - dimensions.height) / 2
        });

        $("#videoContainer").append(canvas);
    };

    var renderPredictions = function (predictions) {
        var dimensions = videoDimensions(video);

        var scale = 1;

        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

        predictions.forEach(function (prediction) {
            if(prediction.class != "rick") return;

            if (flipVideo ^ additionalFlip) {
                prediction.bbox.x = video.videoWidth - prediction.bbox.x;
            }

            var x = prediction.bbox.x;
            var y = prediction.bbox.y;

            var width = prediction.bbox.width;
            var height = prediction.bbox.height;

            // Draw the bounding box.
            ctx.strokeStyle = "000";
            ctx.lineWidth = 4;
            ctx.fillRect(
                (x - width / 2) / scale,
                (y - height / 2) / scale,
                width / scale,
                height / scale
            );

            // // Draw the label background.
            // ctx.fillStyle = prediction.color;
            // var textWidth = ctx.measureText(prediction.class).width;
            // var textHeight = parseInt(font, 10); // base 10
            // ctx.fillRect(
            //     (x - width / 2) / scale,
            //     (y - height / 2) / scale,
            //     textWidth + 8,
            //     textHeight + 4
            // );
        });

        // predictions.forEach(function (prediction) {
        //     var x = prediction.bbox.x;
        //     var y = prediction.bbox.y;

        //     var width = prediction.bbox.width;
        //     var height = prediction.bbox.height;

        //     // Draw the text last to ensure it's on top.
        //     ctx.font = font;
        //     ctx.textBaseline = "top";
        //     ctx.fillStyle = "#000000";
        //     ctx.fillText(
        //         prediction.class,
        //         (x - width / 2) / scale + 4,
        //         (y - height / 2) / scale + 1
        //     );
        // });
    };

    var prevTime;
    var pastFrameTimes = [];
    var detectFrame = function () {
        if (!model) return requestAnimationFrame(detectFrame);

        model
            .detect(video)
            .then(function (predictions) {
                requestAnimationFrame(detectFrame);
                renderPredictions(predictions);

                if (prevTime) {
                    pastFrameTimes.push(Date.now() - prevTime);
                    if (pastFrameTimes.length > 30) pastFrameTimes.shift();

                    var total = 0;
                    _.each(pastFrameTimes, function (t) {
                        total += t / 1000;
                    });

                    var fps = pastFrameTimes.length / total;
                    $("#fps").text(Math.round(fps));
                }
                prevTime = Date.now();

                if (inferCode) inferCode(predictions, inferContext);
            })
            .catch(function (e) {
                console.log("CAUGHT", e);
                requestAnimationFrame(detectFrame);
            });
    };

    _.mixin({
        getItem: function (k) {
            try {
                return localStorage.getItem(k);
            } catch (e) {
                return localStorageFallback[k] || null;
            }
        },
        setItem: function (k, v) {
            try {
                localStorage.setItem(k, v);
            } catch (e) {
                localStorageFallback[k] = v;
            }
        },
        removeItem: function (k) {
            try {
                localStorage.removeItem(k);
            } catch (e) {
                delete localStorageFallback[k];
            }
        },
        clear: function () {
            try {
                localStorage.clear();
            } catch (e) {
                localStorageFallback = {};
            }
        }
    });
});