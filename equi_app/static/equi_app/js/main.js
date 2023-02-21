// TODO: buttons in the main container should be fixed to the bottom of the page (not as part of the scrollable area)

const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

const createSampleInput = (segment_src, segment_label, i) => {
    return $(`
        <div class="card m-1">
            <video width="240" controls autoplay loop muted class="p-2">
                <source src="${segment_src}" type="video/mp4"> Your browser does not support the video tag.
            </video>
            <div class="card-body btn-group btn-group-sm" role="group" aria-label="Binary label of the video segment">
                <input type="radio" class="btn-check" name="btnradio_${i}" id="btnradio1_${i}" autocomplete="off" ${segment_label == 1 ? 'checked' : 'disabled'}>
                <label class="btn btn-outline-primary" for="btnradio1_${i}">Positive</label>

                <input type="radio" class="btn-check" name="btnradio_${i}" id="btnradio2_${i}" autocomplete="off" ${segment_label == 1 ? 'disabled' : 'checked'}>
                <label class="btn btn-outline-primary" for="btnradio2_${i}">Negative</label>
            </div>
        </div>
    `);
}

async function showMoreSegments() {
    const response = await fetch("show_more_segments/");
    var data = await response.json();
    var segments = data.video_paths;
    var selected_gt_labels = data.labels;
    $("#gallery").empty();
    for (var i = 0; i < segments.length; i++) {
        $("#gallery").append(createSampleInput(segments[i], selected_gt_labels[i], i));
    }
}

async function iterativeSynthesis(init) {
    // TODO: fix button names and ids
    var url;
    if (init == 'init') {
        url = "iterative_synthesis_init/";
    } else {
        url = "iterative_synthesis/";
    }
    const response = await fetch(url);
    var data = await response.json();
    var main_container = $("#main-container");
    if (data.terminated == true) {
        // Update the gallery
        var heading = $("<h5></h5>").addClass("pt-5").text("Algorithm terminated.");
        main_container.append(heading);
        // Update button
        $("#btn").remove();
        // TODO: Add a button to restart.
        var button = $("<div></div>").addClass("d-flex justify-content-center pt-3 pb-5").html(`
            <button type="button" class="btn btn-outline-primary" onclick="window.location.reload()">Restart</button>
        `);
        main_container.append(button);
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
        // Update heading
        var heading = $("<h5></h5>").addClass("pt-5").text(`Iteration ${iteration}`);
        main_container.append(heading);
        // Update stats
        var stats = $("<div></div>").addClass("alert alert-info mt-3").html(`
            <strong>Current iteration</strong>: ${iteration}
            <br>
            <strong>Current positive examples</strong>: ${current_npos}
            <br>
            <strong>Current negative examples</strong>: ${current_nneg}
        `);
        main_container.append(stats);
        // Update the top-k query
        var top_k_queries_div = $("<div></div>").addClass("alert alert-info").html(`
            <strong>Top-1 query</strong>: ${best_query}
            <br>
            <strong>Top-1 score</strong>: ${best_score}
        `);
        main_container.append(top_k_queries_div);
        // Update gallery
        var gallery = $("<div></div>").addClass("d-flex flex-wrap border border-1 border-secondary");
        for (var i = 0; i < segments.length; i++) {
            gallery.append(createSampleInput(segments[i], selected_gt_labels[i], i));
        }
        main_container.append(gallery);
        // Update button
        $("#btn").remove();
        var button_div = $("<div></div>")
            .addClass("d-flex justify-content-center pt-5 pb-5")
            .attr('id', 'btn');
        var button = $("<button></button>")
            .addClass("btn btn-outline-primary")
            .attr('onclick', "iterativeSynthesis()")
            .attr('type', 'button')
            .text("Confirm labels");
        button_div.append(button);
        main_container.append(button_div);
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
}