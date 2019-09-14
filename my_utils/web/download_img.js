function downloadImageToBase64(url, callback) {
    var STATE_DONE = 4;
    var HTTP_OK = 200;
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        // Wait for valid response
        if (xhr.readyState == STATE_DONE && xhr.status == HTTP_OK) {
            var blob = new Blob([xhr.response], {
                type: xhr.getResponseHeader("Content-Type")
            });
            // Create file reader and convert blob array to Base64 string
            var reader = new window.FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = function () {
                var base64data = reader.result;
                callback(base64data);
            }
        }
    };
    xhr.responseType = "arraybuffer";
    // Load async
    xhr.open("GET", url, true);
    xhr.send();
    return 0;
};
downloadImageToBase64(arguments[0], (data) => {
    var span = document.getElementById("base64imagedownload");
    if (!span) {
        span = document.createElement("span");
	span.setAttribute("style", "display: none");
	span.setAttribute("id", "base64imagedownload");
        span.textContent = data;
        document.body.appendChild(span);
    } else {
        span.textContent = data;
    };
});
