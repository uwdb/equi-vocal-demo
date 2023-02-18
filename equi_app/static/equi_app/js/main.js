// TODO: buttons in the main container should be fixed to the bottom of the page (not as part of the scrollable area)

function showMoreSegments() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "show_more_segments/", true);
    xhttp.onload = function() {
        var data = JSON.parse(this.response);
        var segments = data.video_paths;
        // var gallery = document.getElementById("gallery");
        // gallery.innerHTML = "";
        $("#gallery").empty();
        for (var i = 0; i < segments.length; i++) {
            $("#gallery").append(`
                <div class="card m-1">
                    <video width="240" controls autoplay loop muted class="p-2">
                        <source src="${segments[i]}" type="video/mp4"> Your browser does not support the video tag.
                    </video>
                    <div class="card-body btn-group btn-group-sm" role="group" aria-label="Binary label of the video segment">
                        <input type="radio" class="btn-check" name="btnradio_${i}" id="btnradio1_${i}" autocomplete="off" checked>
                        <label class="btn btn-outline-primary" for="btnradio1_${i}">Positive</label>

                        <input type="radio" class="btn-check" name="btnradio_${i}" id="btnradio2_${i}" autocomplete="off" disabled>
                        <label class="btn btn-outline-primary" for="btnradio2_${i}">Negative</label>
                    </div>
                </div>
            `);
        }
    };
    xhttp.send();
}

function iterativeSynthesis(init) {
    var url;
    if (init == 'init') {
        url = "iterative_synthesis_init/";
    } else {
        url = "iterative_synthesis/";
    }
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", url, true);
    xhttp.onload = function() {
        var data = JSON.parse(this.response);
        if (data.terminated == true) {
            // Update the gallery
            var main_container = document.getElementById("main-container");
            var heading = document.createElement("h5");
            heading.classList.add("pt-5", "pb-5");
            heading.innerHTML = `Algorithm terminated.`;
            main_container.appendChild(heading);
            // Update button
            document.getElementById("btn").remove();
            // TODO: Add a button to restart.
        }
        else {
            var segments = data.video_paths;
            var predicted_segments = data.predicted_paths;
            var iteration = data.iteration;
            var selected_gt_labels = data.selected_gt_labels;
            var current_npos = data.current_npos;
            var current_nneg = data.current_nneg;
            var best_query = data.best_query;
            var best_score = data.best_score;
            // Append to the main container
            var main_container = document.getElementById("main-container");
            // Update heading
            var heading = document.createElement("h5");
            heading.innerHTML = `Iteration ${iteration}`;
            heading.classList.add("pt-5");
            main_container.appendChild(heading);
            // Update stats
            var stats = document.createElement("div");
            stats.classList.add("alert", "alert-info", "mt-3");
            stats.innerHTML = `
                <strong>Current iteration</strong>: ${iteration}
                <br>
                <strong>Current positive examples</strong>: ${current_npos}
                <br>
                <strong>Current negative examples</strong>: ${current_nneg}
            `;
            main_container.appendChild(stats);
            // Update the top-k query
            var top_k_queries_div = document.createElement("div");
            top_k_queries_div.classList.add("alert", "alert-info");
            top_k_queries_div.innerHTML = `
                <strong>Top-1 query</strong>: ${best_query}
                <br>
                <strong>Top-1 score</strong>: ${best_score}
            `;
            main_container.appendChild(top_k_queries_div);
            // Update gallery
            var gallery = document.createElement("div");
            gallery.classList.add("d-flex", "flex-wrap", "border", "border-1", "border-secondary");
            for (var i = 0; i < segments.length; i++) {
                var video = document.createElement("video");
                video.setAttribute("width", "240");
                video.setAttribute("controls", "");
                video.setAttribute("autoplay", "");
                video.setAttribute("loop", "");
                video.setAttribute("muted", "")
                video.classList.add("p-2");
                var source = document.createElement("source");
                source.setAttribute("src", segments[i]);
                source.setAttribute("type", "video/mp4");
                source.innerHTML = " Your browser does not support the video tag.";
                video.appendChild(source);
                gallery.appendChild(video);
            }
            main_container.appendChild(gallery);
            // Update button
            document.getElementById("btn").remove();
            var button_div = document.createElement("div");
            button_div.id = "btn";
            button_div.classList.add("d-flex", "justify-content-center", "pt-5", "pb-5");
            var button = document.createElement("button");
            button.setAttribute("type", "button");
            button.classList.add("btn");
            button.classList.add("btn-outline-primary");
            button.setAttribute("onclick", "iterativeSynthesis()");
            button.innerHTML = "Confirm labels";
            button_div.appendChild(button);
            main_container.appendChild(button_div);
            // Update prediction
            // var prediction = document.getElementById("prediction");
            // prediction.innerHTML = "Predicted positive segments:<br>";
            // for (var i = 0; i < predicted_segments.length; i++) {
            //     var video = document.createElement("video");
            //     video.setAttribute("width", "240");
            //     video.setAttribute("controls", "");
            //     video.setAttribute("loop", "");
            //     var source = document.createElement("source");
            //     source.setAttribute("src", segments[i]);
            //     source.setAttribute("type", "video/mp4");
            //     source.innerHTML = " Your browser does not support the video tag.";
            //     video.appendChild(source);
            //     prediction.appendChild(video);
            // }
        }
    };
    xhttp.send();
}