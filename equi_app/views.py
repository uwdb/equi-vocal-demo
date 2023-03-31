import random
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from sklearn.metrics import f1_score
from rest_framework.views import APIView
from django.templatetags.static import static
import os, json
import numpy as np
import pickle
import sys
sys.path.append("/Users/zhangenhao/Desktop/UW/Research/equi-vocal-demo/EQUI-VOCAL")
from src.synthesize import test_algorithm_interactive
from src.utils import str_to_program_postgres

module_dir = os.path.dirname(__file__)   #get current directory
with open(os.path.join(module_dir, 'example_queries.json')) as f:
    example_queries = json.load(f)

class index(APIView):
    def get(self, request, query_idx=0, format=None):
        request.session.clear()
        request.session['query_idx'] = query_idx
        example_query = example_queries[query_idx]
        vids = example_query["vids"]
        labels = example_query["labels"]
        query_text = example_query["query_text"]
        query_scene_graph = str_to_program_postgres(example_query["query_str"])
        print(example_query["query_str"])
        print(query_scene_graph)
        query_datalog = example_query["query_datalog"]
        if query_idx != 3:
            config = example_query["config"]
        else:
            config = None
        context = {
            'video_paths': [('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5)), label) for vid, label in zip(vids, labels)],
            'query_text': query_text,
            'query_datalog': query_datalog,
            'show_parameters': query_idx == 3,
            'query_scene_graph': query_scene_graph,
            'config': config
        }
        request.session.modified = True
        print("query_idx:", request.session['query_idx'])
        return render(request, 'equi_app/index.html', context)

class show_more_segments(APIView):
    def get(self, request, format=None):
        vids = random.sample(range(10000), 10)
        # TODO: get labels from database
        labels = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
        video_paths = [static('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5))) for vid in vids]
        return JsonResponse({'video_paths': video_paths, 'labels': labels})

class iterative_synthesis_init(APIView):
    def get(self, request, format=None):
        # request.session['query_idx'] = 1
        print("query_idx:", request.session["query_idx"])
        query_idx = request.session['query_idx']
        example_query = example_queries[query_idx]

        predicate_dict = [{"name": "Near", "parameters": [1], "nargs": 2}, {"name": "Far", "parameters": [3], "nargs": 2}, {"name": "LeftOf", "parameters": None, "nargs": 2}, {"name": "Behind", "parameters": None, "nargs": 2}, {"name": "RightOf", "parameters": None, "nargs": 2}, {"name": "FrontOf", "parameters": None, "nargs": 2}, {"name": "RightQuadrant", "parameters": None, "nargs": 1}, {"name": "LeftQuadrant", "parameters": None, "nargs": 1}, {"name": "TopQuadrant", "parameters": None, "nargs": 1}, {"name": "BottomQuadrant", "parameters": None, "nargs": 1}, {"name": "Color", "parameters": ["gray", "red", "blue", "green", "brown", "cyan", "purple", "yellow"], "nargs": 1}, {"name": "Shape", "parameters": ["cube", "sphere", "cylinder"], "nargs": 1}, {"name": "Material", "parameters": ["metal", "rubber"], "nargs": 1}]

        input_dir = "/Users/zhangenhao/Desktop/UW/Research/equi-vocal-demo/EQUI-VOCAL/inputs"
        dataset_name = "demo_queries_scene_graph"
        query_str = example_query["query_str"]
        # query_str = 'Conjunction(Conjunction(Color_red(o0), Color_yellow(o1)), LeftOf(o0, o1)); RightOf(o0, o1)'

        with open(os.path.join(input_dir, dataset_name, "train/{}_inputs.json".format(query_str)), 'r') as f:
            inputs = json.load(f)
        with open(os.path.join(input_dir, dataset_name, "train/{}_labels.json".format(query_str)), 'r') as f:
            labels = json.load(f)
        inputs = np.asarray(inputs)
        labels = np.asarray(labels)

        # Test dataset for interactive demo
        with open(os.path.join(input_dir, dataset_name, "test/{}_inputs.json".format(query_str)), 'r') as f:
            test_inputs = json.load(f)
        with open(os.path.join(input_dir, dataset_name, "test/{}_labels.json".format(query_str)), 'r') as f:
            test_labels = json.load(f)

        test_inputs = np.asarray(test_inputs)[:100]
        test_labels = np.asarray(test_labels)[:100]
        test_video_paths = [static('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5))) for vid in test_inputs]
        request.session["test_video_paths"] = test_video_paths
        request.session["test_labels"] = test_labels.tolist()
        print("test_labels", test_labels)
        # algorithm = test_algorithm_interactive(method="vocal_postgres", dataset_name=dataset_name, n_init_pos=10, n_init_neg=10, npred=7, depth=3, max_duration=15, beam_width=10, pool_size=100, k=100, budget=50, multithread=4, query_str=query_str, predicate_dict=predicate_dict, lru_capacity=None, reg_lambda=0.001, strategy='topk', max_vars=3, port=5432, input_dir=input_dir)

        # init_labeled_index = algorithm.labeled_index.copy()
        # init_vids = inputs[init_labeled_index]
        # log = []
        # while True:
        #     log_dict = algorithm.interactive_main()
        #     if log_dict["terminated"]:
        #         print("Terminated")
        #         break
        #     else:
        #         response = {}
        #         response["iteration"] = log_dict["iteration"]
        #         selected_segments = log_dict["selected_segments"]
        #         response["selected_gt_labels"] = log_dict["selected_gt_labels"]
        #         response["current_npos"] = log_dict["current_npos"]
        #         response["current_nneg"] = log_dict["current_nneg"]
        #         response["best_query"] = log_dict["best_query"]
        #         response["best_score"] = log_dict["best_score"]
        #         response["terminated"] = log_dict["terminated"]
        #         response["video_paths"] = [static('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(inputs[idx]//1000*1000).zfill(5), str((inputs[idx]//1000+1)*1000).zfill(5), str(inputs[idx]).zfill(5))) for idx in selected_segments]
        #         response["predicted_labels_test"] = log_dict["predicted_labels_test"]
        #         log.append(response)
        # print("init vids", init_vids)
        # print("log", log)


        log = example_query["log"]

        request.session["iteration"] = 0
        request.session["log"] = log
        return JsonResponse(post_processing(log[0], test_video_paths, test_labels.tolist()))

class iterative_synthesis(APIView):
    def get(self, request, format=None):
        request.session["iteration"] += 1
        log = request.session["log"]
        if request.session["iteration"] < len(log):
            return JsonResponse(post_processing(log[request.session["iteration"]], request.session["test_video_paths"], request.session["test_labels"]))
        else:
            request.session = {}
            return JsonResponse({"terminated": True})

def post_processing(log, test_video_paths, test_labels):
    log_copy = dict(log)
    predicted_labels_test = log_copy["predicted_labels_test"]
    predicted_pos_video_paths = []
    predicted_pos_video_gt_labels = []
    predicted_neg_video_paths = []
    predicted_neg_video_gt_labels = []
    for (path, gt_l, p_l) in zip(test_video_paths, test_labels, predicted_labels_test):
        if p_l == 1:
            predicted_pos_video_paths.append(path)
            predicted_pos_video_gt_labels.append(gt_l)
        else:
            predicted_neg_video_paths.append(path)
            predicted_neg_video_gt_labels.append(gt_l)
    del log_copy["predicted_labels_test"]
    log_copy["predicted_pos_video_paths"] = predicted_pos_video_paths
    log_copy["predicted_pos_video_gt_labels"] = predicted_pos_video_gt_labels
    log_copy["predicted_neg_video_paths"] = predicted_neg_video_paths
    log_copy["predicted_neg_video_gt_labels"] = predicted_neg_video_gt_labels

    log_copy["best_query_scene_graph"] = str_to_program_postgres(log_copy["best_query"])
    return log_copy