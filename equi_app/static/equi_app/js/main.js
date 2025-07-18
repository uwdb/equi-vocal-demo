// TODO: buttons in the main container should be fixed to the bottom of the page (not as part of the scrollable area)

const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

$('._popover').on('click', function (e) {
    $('._popover').not(this).popover('hide');
});

const graph = JSON.parse(document.getElementById('render-scene-graph').textContent);

const myPopoverTrigger = document.getElementById('image-graph-popover');
myPopoverTrigger.addEventListener('inserted.bs.popover', () => {
    $('#image-graph').empty();
    renderSceneGraph('#image-graph', graph);
  });

const configPopoverTrigger = document.getElementById('config-popover');
if (configPopoverTrigger) {
    configPopoverTrigger.addEventListener('inserted.bs.popover', () => {
        const labelingBudget = parseInt(configPopoverTrigger.dataset.labelingBudget);
        const videosPerPage = parseInt(configPopoverTrigger.dataset.videosPerPage);
        const beamWidth = parseInt(configPopoverTrigger.dataset.beamWidth);
        const disabledSubmit = configPopoverTrigger.dataset.disabledSubmit;
        $('#config-form').html(`
            <form onsubmit="submitConfigForm(event)">
            <div class="row">
            <input type="hidden" name="queryId" value="${configPopoverTrigger.dataset.queryId}">
            <label for="labelingBudget" class="col-sm-2 col-form-label">Labeling Budget</label>
            <div class="col-sm-2">
                <select class="form-select" id="labelingBudget" name="labelingBudget" ${disabledSubmit ? 'disabled' : ''}>
                    <option value="20" ${labelingBudget == 20 ? 'selected' : ''}>20</option>
                    <option value="30" ${labelingBudget == 30 ? 'selected' : ''}>30</option>
                    <option value="40" ${labelingBudget == 40 ? 'selected' : ''}>40</option>
                    <option value="50" ${labelingBudget == 50 ? 'selected' : ''}>50</option>
                </select>
            </div>
            <label for="videosPerPage" class="col-sm-2 col-form-label">Videos Per Page</label>
            <div class="col-sm-2">
                <select class="form-select" id="videosPerPage" name="videosPerPage" ${disabledSubmit ? 'disabled' : ''}>
                    <option value="10" ${videosPerPage == 10 ? 'selected' : ''}>10</option>
                    <option value="20" ${videosPerPage == 20 ? 'selected' : ''}>20</option>
                    <option value="30" ${videosPerPage == 30 ? 'selected' : ''}>30</option>
                </select>
            </div>
            <label for="beamWidth" class="col-sm-2 col-form-label">Beam Width</label>
            <div class="col-sm-2">
                <select class="form-select" id="beamWidth" name="beamWidth" ${disabledSubmit ? 'disabled' : ''}>
                    <option value="1" ${beamWidth == 1 ? 'selected' : ''}>1</option>
                    <option value="5" ${beamWidth == 5 ? 'selected' : ''}>5</option>
                    <option value="10" ${beamWidth == 10 ? 'selected' : ''}>10</option>
                    <option value="15" ${beamWidth == 15 ? 'selected' : ''}>15</option>
                    <option value="20" ${beamWidth == 20 ? 'selected' : ''}>20</option>
                </select>
            </div>
            </div>
            <input type="submit" id="configSubmitButton" class="mt-3 btn btn-outline-primary" value="Set parameters" ${disabledSubmit ? 'disabled' : ''}>
        </form>
        `);
        // <button type="submit" class="mt-3 btn btn-outline-primary">Set parameters</button>
    })
}

// Store vids of initial examples
const initial_positive = new Set();
const initial_negative = new Set();

// For labeling initail examples, we use checkboxs where selecting one will deselect others.
$(".button_init").click(setButtonOnClick);

function setButtonOnClick() {
    const clickedButton = $(this);
    if (clickedButton.prop('checked')) {
        if (clickedButton.hasClass("btn_pos")) {
            initial_positive.add(parseInt(clickedButton.parent().data("vid")));
            initial_negative.delete(parseInt(clickedButton.parent().data("vid")));
        }
        else {
            initial_negative.add(parseInt(clickedButton.parent().data("vid")));
            initial_positive.delete(parseInt(clickedButton.parent().data("vid")));
        }
        const buttons = clickedButton.siblings(".button_init");
        buttons.prop('checked', false);;
    }
    else {
        if (clickedButton.hasClass("btn_pos")) {
            initial_positive.delete(parseInt(clickedButton.parent().data("vid")));
        }
        else {
            initial_negative.delete(parseInt(clickedButton.parent().data("vid")));
        }
    }
    // Update the text
    $("#init_label_stats").html(`You have provided ${initial_positive.size} positive and ${initial_negative.size} negative examples.`);
}

const createSampleInput = (segment_src, segment_label, i, prefix, task_name) => {
    if (task_name == "show_more") {
        return $(`
            <div class="card m-1">
                <video width="210" controls muted class="p-2" ontimeupdate="updateTime(this)">
                    <source src="${segment_src[1]}" type="video/mp4"> Your browser does not support the video tag.
                </video>
                <div class="ps-2">Timestamp:</div>
                <div class="card-body btn-group btn-group-sm p-2 button_group_init" role="group" aria-label="Binary label of the video segment" data-vid="${segment_src[0]}">
                    <input type="checkbox" class="btn-check btn_pos init_btn_${i} button_init" id="init_btnradio1_${i}" autocomplete="off">
                    <label class="btn btn-outline-primary" for="init_btnradio1_${i}">Positive</label>

                    <input type="checkbox" class="btn-check btn_neg init_btn_${i} button_init" id="init_btnradio2_${i}" autocomplete="off">
                    <label class="btn btn-outline-primary" for="init_btnradio2_${i}">Negative</label>
                </div>
            </div>
        `);
    }
    else if (task_name == "live" || task_name == "live_init") {
        return $(`
            <div class="card m-1">
                <video width="210" controls muted class="p-2" ontimeupdate="updateTime(this)">
                    <source src="${segment_src}" type="video/mp4"> Your browser does not support the video tag.
                </video>
                <div class="ps-2">Timestamp:</div>
                <div class="card-body btn-group btn-group-sm p-2" role="group" aria-label="Binary label of the video segment">
                    <input type="radio" class="btn-check to_submit" name="${prefix}_btnradio_${i}" id="${prefix}_btnradio1_${i}" autocomplete="off" checked>
                    <label class="btn btn-outline-primary" for="${prefix}_btnradio1_${i}">Positive</label>

                    <input type="radio" class="btn-check" name="${prefix}_btnradio_${i}" id="${prefix}_btnradio2_${i}" autocomplete="off">
                    <label class="btn btn-outline-primary" for="${prefix}_btnradio2_${i}">Negative</label>
                </div>
            </div>
        `);
    }
    else {
        // Default. Labels are disabled and will not be submitted to backend.
        return $(`
            <div class="card m-1">
                <video width="210" controls muted class="p-2" ontimeupdate="updateTime(this)">
                    <source src="${segment_src}" type="video/mp4"> Your browser does not support the video tag.
                </video>
                <div class="ps-2">Timestamp:</div>
                <div class="card-body btn-group btn-group-sm p-2" role="group" aria-label="Binary label of the video segment">
                    <input type="radio" class="btn-check" name="${prefix}_btnradio_${i}" id="${prefix}_btnradio1_${i}" autocomplete="off" ${segment_label == 1 ? 'checked' : 'disabled'}>
                    <label class="btn btn-outline-primary" for="${prefix}_btnradio1_${i}">Positive</label>

                    <input type="radio" class="btn-check" name="${prefix}_btnradio_${i}" id="${prefix}_btnradio2_${i}" autocomplete="off" ${segment_label == 1 ? 'disabled' : 'checked'}>
                    <label class="btn btn-outline-primary" for="${prefix}_btnradio2_${i}">Negative</label>
                </div>
            </div>
        `);
    }
}

const createSampleOutput = (segment_src, segment_gt_label, i) => {
    return $(`
        <div class="card m-1 ${segment_gt_label}">
            <video width="170" controls loop muted class="p-2">
                <source src="${segment_src}" type="video/mp4"> Your browser does not support the video tag.
            </video>
        </div>
    `);
}

const createSceneGraph = () => {
    return $(`
        <button id='best-query-graph-popover' type="button" class="btn btn-primary btn-sm ms-2" style="--bs-btn-padding-y: .2rem; --bs-btn-padding-x: .4rem; --bs-btn-font-size: .7rem;" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="bottom" data-bs-custom-class="custom-popover" data-bs-title="Scene graph visualization" data-bs-content='<div id="best-query-graph" class="row"></div>' data-bs-html="true">
            Scene Graph
        </button>
    `);
}

const createDatalog = (query_datalog) => {
    return $(`
    <button id='best-query-datalog-popover' type="button" class="btn btn-primary btn-sm ms-2" style="--bs-btn-padding-y: .2rem; --bs-btn-padding-x: .4rem; --bs-btn-font-size: .7rem;" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="bottom" data-bs-custom-class="custom-popover" data-bs-title="Datalog rules" data-bs-content="<pre>${query_datalog}</pre>" data-bs-html="true">
        Datalog
    </button>
    `);
}

const createStats = (num_pos, num_neg, num_false_pos, num_false_neg) => {
    var num_true_pos = num_pos - num_false_pos;
    var precision = (num_true_pos/num_pos);
    var recall = (num_true_pos/(num_true_pos + num_false_neg));
    var f1 = (2*precision*recall)/(precision + recall);
    return $(`
        <div class="alert alert-success mt-2">
            <strong> # of Positive Predictions:</strong> ${num_pos}
            <br>
            <strong> # of Negative Predictions:</strong> ${num_neg}
            <br>
            <strong> # of False Positive Predictions:</strong> ${num_false_pos}
            <br>
            <strong> # of False Negative Predictions:</strong> ${num_false_neg}
        </div>
        <div class="alert alert-success mt-2">
            <strong> Recall:</strong> ${recall.toFixed(3)}
            <br>
            <strong> Precision:</strong> ${precision.toFixed(3)}
            <br>
            <strong> F1 Score:</strong> ${f1.toFixed(3)}
        </div>
    `);
}

const createTopQueriesDropdown = (top_k_queries_with_scores) => {
    // For every best_query, best_score pair, create an option, and select the first one
    var options = ``;
    for (var i = 0; i < Math.min(top_k_queries_with_scores.length, 100); i++) {
        options += `<option value="${i}" ${i == 0 ? "selected": ""}>${top_k_queries_with_scores[i][0]} (${top_k_queries_with_scores[i][1].toFixed(3)})</option>`;
    }
    return `
        ${options}
    `;
}

async function showMoreSegments() {
    const response = await fetch("show_more_segments/");
    var data = await response.json();
    var segments = data.video_paths;
    $("#gallery").empty();
    for (var i = 0; i < segments.length; i++) {
        $("#gallery").append(createSampleInput(segments[i], null, i, "init", "show_more"));
    }
    $(".button_init").click(setButtonOnClick);
}

// First thing: remove/disable the button, and show a spinner
$(document).ready(function () {
    disabledSpinnerButton();
});

function disabledSpinnerButton() {
    $("button.spinnable").click(function () {
        // disable button
        $(this).prop("disabled", true);
        // add spinner to button
        $(this).html('<span class="spinner-border spinner-border-sm mr-05" role="status" aria-hidden="true"></span> Loading');
    });
}

async function iterativeSynthesis(flag) {
    // Close all popovers
    $('._popover').popover('hide');
    if (configPopoverTrigger) {
        // Disable the config popover submit button
        configPopoverTrigger.dataset.disabledSubmit = true;
    }
    var response;
    if (flag == 'live_init') {
        // Get the user labels
        var init_vids = [];
        var user_labels = [];
        initial_positive.forEach(value => {
            init_vids.push(value);
            user_labels.push(1);
        });

        initial_negative.forEach(value => {
            init_vids.push(value);
            user_labels.push(0);
        });
        console.log(init_vids);
        console.log(user_labels);

        const settings = {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_labels: user_labels,
                init_vids: init_vids
            })
        };
        response = await fetch("iterative_synthesis_live/", settings);
    }
    else if (flag == 'live') {
        // Get the user labels
        var user_labels = [];
        var elementArray = document.getElementsByClassName("to_submit");
        elementArray = [].slice.call(elementArray, 0);
        for (var i = 0; i < elementArray.length; ++i) {
            if (elementArray[i].checked) {
                user_labels.push(1);
            }
            else {
                user_labels.push(0);
            }
            elementArray[i].classList.replace("to_submit", "submitted")
            // elementArray[i].disabled = true;
            // TODO: disable previous buttons for labels by making them unclickable
        }
        console.log(user_labels);
        // TODO: disable previous toggle buttons
        const settings = {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_labels: user_labels
            })
        };
        response = await fetch("iterative_synthesis_live/", settings);
    }
    else if (flag == 'init') {
        response = await fetch("iterative_synthesis_init/");
    } else {
        response = await fetch("iterative_synthesis/");
    }
    // Receive the response, and update the page
    var data = await response.json();
    console.log(data);
    var main_container = $("#main-container");
    if (data.state == "terminated") {
        if (flag == 'live' || flag == 'live_init') {
            var iteration = data.iteration;
            var current_npos = data.current_npos;
            var current_nneg = data.current_nneg;
            var best_query = data.best_query;
            var best_query_scene_graph = data.best_query_scene_graph;
            var best_score = data.best_score;
            var best_query_list = data.best_query_list;
            var best_score_list = data.best_score_list;
            var top_k_queries_with_scores = data.top_k_queries_with_scores;
            console.log(best_query_list);
            // Update stats and top-k queries
            var options = createTopQueriesDropdown(top_k_queries_with_scores);
            var stats = $("<div></div>").addClass("alert alert-info mt-3").html(`
                <strong>Current iteration</strong>: ${iteration}
                <br>
                <strong>Current positive examples</strong>: ${current_npos}
                <br>
                <strong>Current negative examples</strong>: ${current_nneg}
                <br>
                <strong>Top-100 queries (with scores)</strong>:
                <select class="form-select form-select-sm mt-2">
                ${options}
                </select>
            `);
            main_container.append(stats);
        }
        // Update the gallery
        var heading = $("<h5></h5>").addClass("pt-5").text("Algorithm terminated.");
        main_container.append(heading);
        // Update button
        $("#btn").remove();
        var button = $("<div></div>").addClass("d-flex justify-content-center pt-3 pb-5").html(`
            <button type="button" class="btn btn-outline-primary" onclick="window.location.reload()">Restart</button>
        `);
        main_container.append(button);
    }
    else if (data.state == "label_more") {
        // Only for live query task.
        // Remove button
        $("#btn").remove();
        // Update the gallery
        var segments = data.video_paths;
        var iteration = data.iteration;
        var sample_idx = data.sample_idx;
        var gallery = $("<div></div>").addClass("d-flex flex-wrap border border-1 border-secondary");
        gallery.append(createSampleInput(segments[0], 0, sample_idx, iteration, flag)); // 0 is a dummy label
        main_container.append(gallery);
        // Update button
        var button_div = $("<div></div>")
            .addClass("d-flex justify-content-center pt-5 pb-5")
            .attr('id', 'btn');
        var button = $("<button></button>")
        .addClass("btn btn-outline-primary spinnable")
        .attr('onclick', "iterativeSynthesis('live')")
        .attr('type', 'button')
        .text("Confirm labels");
        button_div.append(button);
        main_container.append(button_div);
        disabledSpinnerButton();
    }
    else {
        $("#btn").remove();
        var segments = data.video_paths;
        var iteration = data.iteration;
        if (iteration > 0) {
            var current_npos = data.current_npos;
            var current_nneg = data.current_nneg;
            var best_query = data.best_query;
            var best_query_scene_graph = data.best_query_scene_graph;
            var best_score = data.best_score;
            var best_query_list = data.best_query_list;
            var best_score_list = data.best_score_list;
            var top_k_queries_with_scores = data.top_k_queries_with_scores;

            console.log(best_query_list);
            // Update stats and top-k queries
            var options = createTopQueriesDropdown(top_k_queries_with_scores);
            var stats = $("<div></div>").addClass("alert alert-info mt-3").html(`
                <strong>Current iteration</strong>: ${iteration}
                <br>
                <strong>Current positive examples</strong>: ${current_npos}
                <br>
                <strong>Current negative examples</strong>: ${current_nneg}
                <br>
                <strong>Top-100 queries (with scores)</strong>:
                <select class="form-select form-select-sm mt-2">
                ${options}
                </select>
            `);
            main_container.append(stats);

            // Update prediction
            $('.popover').remove();
            // Before deallocating the audio/video elements setting the following seems to force clean up of the element.
            $('#prediction-container video').each(function () {
                this.pause();
                this.removeAttribute('src'); // empty source
                this.load();
            });
            var prediction_container = $("#prediction-container").empty();
            var heading = $("<h3></h3>").addClass("mb-3").text("Best Query on Test Data")
            prediction_container.append(heading);

            // Best query details
            var best_query_heading = $("<span></span>").addClass("lead fs-6").text("Best query: " + best_query);
            prediction_container.append(best_query_heading);

            // Best query scene graph
            prediction_container.append(createSceneGraph());
            // prediction_container.append(createDatalog(best_query));
            const bestSceneGeraphPopoverTrigger = document.getElementById('best-query-graph-popover');
            // const bestDatalogPopoverTrigger = document.getElementById('best-query-datalog-popover');
            new bootstrap.Popover(bestSceneGeraphPopoverTrigger);
            // new bootstrap.Popover(bestDatalogPopoverTrigger);
            bestSceneGeraphPopoverTrigger.addEventListener('inserted.bs.popover', () => {
                $('#best-query-graph').empty();
                renderSceneGraph('#best-query-graph', best_query_scene_graph);
            })

            var predicted_pos_segments = data.predicted_pos_video_paths;
            var predicted_neg_segments = data.predicted_neg_video_paths;
            var predicted_pos_gt_labels = data.predicted_pos_video_gt_labels;
            var predicted_neg_gt_labels = data.predicted_neg_video_gt_labels;

            var num_pred_pos = predicted_pos_segments.length;
            var num_pred_neg = predicted_neg_segments.length;

            //Counting true positives
            var num_false_pos = 0;
            for(var i = 0; i < predicted_pos_gt_labels.length; i++){
                if(predicted_pos_gt_labels[i] ==0){
                    num_false_pos += 1;
                }
            }
            var num_false_neg = 0;
            for(var i = 0; i < predicted_neg_gt_labels.length; i++){
                if(predicted_neg_gt_labels[i] ==1){
                    num_false_neg += 1;
                }
            }

            // Stats
            prediction_container.append(createStats(num_pred_pos, num_pred_neg, num_false_pos, num_false_neg));

            //Positive Gallery
            var pos_predictions = $("<div></div>").addClass("d-flex justify-content-evenly flex-wrap border border-1 border-secondary mb-3"); //document.getElementById("pos-gallery");
            var pos_heading = $("<h6>Positive</h6>").addClass("p-2 w-100");
            var breakdiv = $("<div></div>").addClass("w-36");
            pos_predictions.append(pos_heading);
            pos_predictions.append(breakdiv);

            for (var i = 0; i < predicted_pos_segments.length; i++) {
                if(predicted_pos_gt_labels[i]==1){
                    bkgrnd_class = "bg-success";
                }
                else{
                    bkgrnd_class = "bg-danger";
                }

                pos_predictions.append(createSampleOutput(predicted_pos_segments[i], bkgrnd_class, i));
            }
            prediction_container.append(pos_predictions);

            //Negative gallery
            var neg_predictions = $("<div></div>").addClass("d-flex justify-content-evenly flex-wrap border border-1 border-secondary"); //document.getElementById("neg-gallery");
            var neg_heading = $("<h6>Negative</h6>").addClass("p-2 w-100")
            neg_predictions.append(neg_heading)
            neg_predictions.append(breakdiv)
            for (var i = 0; i < predicted_neg_segments.length; i++) {
                if(predicted_neg_gt_labels[i]==0){
                    bkgrnd_class = "bg-success";
                }
                else{
                    bkgrnd_class = "bg-danger";
                }
                neg_predictions.append(createSampleOutput(predicted_neg_segments[i], bkgrnd_class, i));
            }
            prediction_container.append(neg_predictions);
        }
        var selected_gt_labels;
        if (flag == 'live' || flag == 'live_init') {
            // Live query task doesn't have ground truth labels, so we create a dummy array
            selected_gt_labels = new Array(segments.length).fill(0);
        }
        else {
            selected_gt_labels = data.selected_gt_labels;
        }
        // Update heading
        var heading = $("<h5></h5>").addClass("pt-5").text(`Iteration ${iteration}`);
        main_container.append(heading);
        // Update gallery
        var gallery = $("<div></div>").addClass("d-flex flex-wrap border border-1 border-secondary");
        for (var i = 0; i < segments.length; i++) {
            gallery.append(createSampleInput(segments[i], selected_gt_labels[i], i, iteration, flag));
        }
        main_container.append(gallery);
        // Update button
        var button_div = $("<div></div>")
            .addClass("d-flex justify-content-center pt-5 pb-5")
            .attr('id', 'btn');
        if (flag == 'live' || flag == 'live_init') {
            var button = $("<button></button>")
                .addClass("btn btn-outline-primary spinnable")
                .attr('onclick', "iterativeSynthesis('live')")
                .attr('type', 'button')
                .text("Confirm labels");
        }
        else {
            var button = $("<button></button>")
                .addClass("btn btn-outline-primary spinnable")
                .attr('onclick', "iterativeSynthesis()")
                .attr('type', 'button')
                .text("Confirm labels");
        }
        button_div.append(button);
        main_container.append(button_div);
        disabledSpinnerButton();
    }
}

async function setRun() {
    var run_id = $("#run_id").val();
    const settings = {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            run_id: run_id
        })
    };
    response = await fetch("set_run/", settings);
    var data = await response.json();
    var segments = data.video_paths;
    var labels = data.labels;
    $("#gallery").empty();
    for (var i = 0; i < segments.length; i++) {
        console.log(createSampleInput(segments[i], labels[i], i, "init", 'user_study'));
        $("#gallery").append(createSampleInput(segments[i], labels[i], i, "init", 'user_study'));
    }
}

function updateTime(video) {
    video.nextElementSibling.innerHTML = "Timestamp: " + video.currentTime.toFixed(3) + " seconds";
}

async function submitConfigForm(event) {
    event.preventDefault(); // Prevent the form from submitting normally
    // Close all popovers
    $('._popover').popover('hide');
    const formData = new FormData(event.target); // Get form data

    // Convert form data to JSON
    const formDataJson = {};
    formData.forEach((value, key) => {
        formDataJson[key] = value;
    });

    // Send form data to the backend
    response = await fetch("set_params/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(formDataJson),
    });
    var data = await response.json();
    // Update config popover
    configPopoverTrigger.dataset.labelingBudget = data.labeling_budget;
    configPopoverTrigger.dataset.videosPerPage = data.videos_per_page;
    configPopoverTrigger.dataset.beamWidth = data.beam_width;
    console.log(configPopoverTrigger.dataset.beamWidth);
    // Update the initialization pane
    var segments = data.video_paths;
    $("#gallery").empty();
    initial_positive.clear();
    initial_negative.clear();
    $("#init_label_stats").html(`You have provided 0 positive and 0 negative examples.`);
    for (var i = 0; i < segments.length; i++) {
        $("#gallery").append(createSampleInput(segments[i], null, i, "init", "live_init"));
    }
    $(".button_init").click(setButtonOnClick);
}