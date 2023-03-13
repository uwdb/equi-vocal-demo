// these three methods make links and nodes
function makeLink(parentElementID, childElementID) {
    return new joint.dia.Link({
        source: {id: parentElementID},
        target: {id: childElementID},
        attrs: {'.marker-target': {stroke:'rgba(68,68,68,0.6)',
                                   fill: 'rgba(68,68,68,0.6)',
                                   d: 'M 4 0 L 0 2 L 4 4 z' },
                '.connection':{stroke: 'rgba(68,68,68,0.6)',
                               'stroke-width': '1px' }},
        smooth: true,
    });
  }

function makeLink2(parentElementID, tx, ty) {
    return new joint.dia.Link({
        source: {id: parentElementID},
        target: {x: tx, y: ty},
        attrs: { '.marker-target': {stroke:'rgba(68,68,68,0.6)',
                                    fill: 'rgba(68,68,68,0.6)',
                                    d: 'M 4 0 L 0 2 L 4 4 z' },
                 '.connection':{stroke: 'rgba(68,68,68,0.6)',
                                'stroke-width': '1px' }},
        smooth: true,
    });
  }

function makeElement(label, indexID, nodeclass, x, y) {
    x = typeof x !== 'undefined' ? x : 0;
    y = typeof y !== 'undefined' ? y : 0;
    var maxLine = _.max(label.split('\n'), function(l) { return l.length - (l.length - l.replace(/i/g, "").replace(/l/g, "").length); });
    var maxLineLength = maxLine.length - 0.62*(maxLine.length - maxLine.replace(/i/g, "").replace(/l/g,"").length);
    // Compute width/height of the rectangle based on the number
    // of lines in the label and the letter size. 0.6 * letterSize is
    // an approximation of the monospace font letter width.
    var letterSize = 8;
    var width = 5 + (letterSize * (maxLineLength + 1));
    var height = 10 + ((label.split('\n').length + 1) * letterSize);

    return new joint.shapes.basic.Rect({
        id: indexID,
        size: { width: width, height: height },
        attrs: {
            text: { text: label, 'font-size': letterSize },
            rect: {
                width: width, height: height,
                rx: 6, ry: 6,
                stroke: '#555'
            }
        },
        position:{x: x, y: y}
    });
}

// given a list of objects with an attribute of "pred"
// returns the index of the object with the predicate
function findIndexOfPredicate(arr, predicate){
    for(var i=0; i<arr.length; i++){
        if (arr[i].pred == predicate)
            return i;
    }
    return -1;
};

renderSceneGraph = function(selector, scene_graphs) {
    /* Creates a graph visualization.
     *
     * Args:
     *     selector: String id of the div where the graph should be displayed.
     *     scene_graph: JSON representation of the scene graph.
     */
    console.log("scene_graphs", scene_graphs);
    var obj_type = "object", pred_type = "pred", attr_type = "attr";
    for (var i = 0; i < scene_graphs.length; i++) {
        console.log(i);
        var nodes = [], links = [];
        var object_pred_map = {};
        var object2id = {};
        var predicates = scene_graphs[i]["scene_graph"];
        var duration = scene_graphs[i]["duration_constraint"];
        var col_div = $("<div></div>").addClass("col");
        var duration_div = $("<div></div>").html(`Duration &ge; ${duration} frame` + (duration > 1 ? "s" : ""));
        var graph_div = $("<div></div>");
        col_div.append(duration_div);
        col_div.append(graph_div);
        $(selector).append(col_div);
        // var objects = scene_graph['objects'];
        // var attributes = scene_graph['attributes'];
        // var relationships = scene_graph['relationships'];

        // add all the objects to the nodes
        const objects = new Set();
        for (var j = 0; j < predicates.length; j++) {
            for (variable of predicates[j]['variables']) {
                if (!objects.has(variable)) {
                    objects.add(variable);
                }
            }
        };
        for (obj of objects) {
            var node = {label: obj,
                    class: obj_type};
            nodes.push(node);
            object_pred_map[obj] = [];
            object2id[obj] = nodes.length-1;
        }

        for (var j = 0; j < predicates.length; j++) {
            // for each object, predicate, subject, we make a node
            // (if it doesn't already exist)
            if (predicates[j]['variables'].length == 2) {
                var subject = predicates[j]['variables'][0];
                var object = predicates[j]['variables'][1];
                var pred = predicates[j]['predicate'];
                // Create a node for the predicate
                var node = {
                    label: pred,
                    class: pred_type
                };
                nodes.push(node);
                var t = nodes.length-1;
                // Create a link from the subject to the predicate, and from the predicate to the object
                links.push({
                    source : object2id[subject],
                    target : t,
                    weight : 1
                });
                links.push({
                    source : t,
                    target : object2id[object],
                    weight: 1
                });
            }
            else {
                var unary = {label: predicates[j]['predicate'] + ": " + predicates[j]['parameter'],
                            class: attr_type};
                nodes.push(unary);
                links.push({source: object2id[predicates[j]['variables'][0]],
                            target: nodes.length - 1,
                            weight: 1});
            }
        };

        console.log("nodes", nodes);
        console.log("links", links);

        var num_nodes = nodes.length;

        var w = 1200, h = 1000;

        var graph = new joint.dia.Graph;

        var paper = new joint.dia.Paper({
            el: graph_div,
            width: 0,
            height: 0,
            gridSize: 1,
            model: graph,
            interactive: false
        });
        paper.$el.css('pointer-events', 'none');

        // Just give the viewport a little padding.
        V(paper.viewport).translate(20, 20);
        elements = [];
        for (var j = 0; j<nodes.length; j++){
            elements.push(makeElement(nodes[j].label, String(j), nodes[j].class));
        }
        for (var j=0; j<links.length; j++){
            elements.push(makeLink(String(links[j].source), String(links[j].target)));
        }
        graph.addCells(elements);
        for (var j = 0; j < nodes.length; j++){
            V(paper.findViewByModel(String(j)).el).addClass(nodes[j].class)
        }
        var g2 = joint.layout.DirectedGraph.layout(graph, {setLinkVertices: false,
                                                        nodeSep: 10,
                                                        rankSep: 20,
                                                        rankDir: 'LR'});
        paper.setDimensions(g2.width+40,g2.height+40);
        console.log(g2.width, g2.height);
    }
};
