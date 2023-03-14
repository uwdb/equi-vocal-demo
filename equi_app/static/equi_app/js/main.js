// TODO: buttons in the main container should be fixed to the bottom of the page (not as part of the scrollable area)

const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

const graph = JSON.parse(document.getElementById('render-scene-graph').textContent);

const myPopoverTrigger = document.getElementById('image-graph-popover');
myPopoverTrigger.addEventListener('inserted.bs.popover', () => {
    $('#image-graph').empty();
    renderSceneGraph('#image-graph', graph);
  })

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

const createSampleOutput = (segment_src, segment_gt_label, i) => {
    return $(`
        <div class="card m-1 ${segment_gt_label}">
            <video width="85" controls autoplay loop muted class="p-2">
                <source src="${segment_src}" type="video/mp4"> Your browser does not support the video tag.
            </video>
        </div>
    `);
}

const createSceneGraph = () => {
    return $(`
        <button id='best-query-graph-popover' type="button" class="btn btn-primary btn-sm ms-2" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="bottom" data-bs-custom-class="custom-popover" data-bs-title="Scene graph visualization" data-bs-content='<div id="best-query-graph" class="row"></div>' data-bs-html="true">
            Scene Graph
        </button>
    `);
}

const createDatalog = (query_datalog) => {
    return $(`
    <button id='best-query-datalog-popover' type="button" class="btn btn-primary btn-sm ms-2" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="bottom" data-bs-custom-class="custom-popover" data-bs-title="Datalog rules" data-bs-content="<pre>${query_datalog}</pre>" data-bs-html="true">
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
        <div class="mt-2">
            <p> # of Positive Predictions: ${num_pos} </p>
            <p> # of Negative Predictions: ${num_neg} </p>
            <p> # of False Positive Predictions: ${num_false_pos} </p>
            <p> # of False Negative Predictions: ${num_false_neg} </p>
            <br>
            <p> Recall: ${recall.toFixed(3)} </p>
            <p> Precision: ${precision.toFixed(3)} </p>
            <p> F1 Score: ${f1.toFixed(3)} </p>

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

async function selectQuery(query_idx) {
    const response = await fetch("select_query/" + query_idx);
}

async function iterativeSynthesis(init) {
    $(this).attr("disabled", true);
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
        var iteration = data.iteration;
        var selected_gt_labels = data.selected_gt_labels;
        var current_npos = data.current_npos;
        var current_nneg = data.current_nneg;
        var best_query = data.best_query;
        var best_query_scene_graph = data.best_query_scene_graph;
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
        var prediction_container = $("#prediction-container").empty();

        var heading = $("<h3></h3>").addClass("mb-3").text("Best Query on Test Data")
        prediction_container.append(heading);

        // Best query details
        var best_query_heading = $("<h5></h5>").text("Best query: " + best_query);
        prediction_container.append(best_query_heading);

        // Best query scene graph
        prediction_container.append(createSceneGraph());
        prediction_container.append(createDatalog(best_query));
        const bestSceneGeraphPopoverTrigger = document.getElementById('best-query-graph-popover');
        const bestDatalogPopoverTrigger = document.getElementById('best-query-datalog-popover');
        new bootstrap.Popover(bestSceneGeraphPopoverTrigger);
        new bootstrap.Popover(bestDatalogPopoverTrigger);
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
        var pos_predictions = $("<div></div>").addClass("d-flex justify-content-evenly flex-wrap border border-1 border-secondary"); //document.getElementById("pos-gallery");
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
}