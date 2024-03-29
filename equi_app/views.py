import random
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from sklearn.metrics import f1_score
from rest_framework.views import APIView
from django.templatetags.static import static
import os, json
import numpy as np
import pickle
import time
import datetime
import sys
# sys.path.append("/gscratch/balazinska/enhaoz/complex_event_video")
from src.synthesize import test_algorithm_interactive
from src.utils import dsl_to_program

module_dir = os.path.dirname(__file__)   #get current directory

input_dir = json.load(open(os.path.join(settings.BASE_DIR, 'config.json')))['input_dir']

with open(os.path.join(module_dir, 'example_queries.json')) as f:
    example_queries = json.load(f)
activity_log_filename = os.path.join(module_dir, "log.json")

# Global variable to store the algorithm object for each user
user_to_obj = {}

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def append_record(record):
    # record is a dictionary
    with open(activity_log_filename, 'a') as f:
        json.dump(record, f, cls=NpEncoder)
        f.write(os.linesep)
    # The list can be assembled later
    # with open('my_file') as f:
    #     my_list = [json.loads(line) for line in f]

class index(APIView):
    def get(self, request, query_idx=0, format=None):
        request, context = init_page(request, query_idx)
        return render(request, 'equi_app/index.html', context)

class show_more_segments(APIView):
    def get(self, request, format=None):
        query_idx = 3
        labeling_budget = request.session['labeling_budget']
        videos_per_page = request.session["videos_per_page"]
        beam_width = request.session['beam_width']
        request, context = init_page(request, query_idx, labeling_budget, videos_per_page, beam_width)
        response = {
            'video_paths': [(vid, static(video_path)) for vid, video_path, label in context['video_paths']],
            'labeling_budget': context['labeling_budget'],
            'videos_per_page': context['videos_per_page'],
            'beam_width': context['beam_width']
        }
        return JsonResponse(response, encoder=NpEncoder)

class iterative_synthesis_init(APIView):
    def get(self, request, format=None):
        # request.session['query_idx'] = 1
        print("query_idx:", request.session["query_idx"])
        query_idx = request.session['query_idx']
        example_query = example_queries[query_idx]

        predicate_dict = [{"name": "Near", "parameters": [1], "nargs": 2}, {"name": "Far", "parameters": [3], "nargs": 2}, {"name": "LeftOf", "parameters": None, "nargs": 2}, {"name": "Behind", "parameters": None, "nargs": 2}, {"name": "RightOf", "parameters": None, "nargs": 2}, {"name": "FrontOf", "parameters": None, "nargs": 2}, {"name": "RightQuadrant", "parameters": None, "nargs": 1}, {"name": "LeftQuadrant", "parameters": None, "nargs": 1}, {"name": "TopQuadrant", "parameters": None, "nargs": 1}, {"name": "BottomQuadrant", "parameters": None, "nargs": 1}, {"name": "Color", "parameters": ["gray", "red", "blue", "green", "brown", "cyan", "purple", "yellow"], "nargs": 1}, {"name": "Shape", "parameters": ["cube", "sphere", "cylinder"], "nargs": 1}, {"name": "Material", "parameters": ["metal", "rubber"], "nargs": 1}]

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
        video_paths = [static('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5))) for vid in inputs]
        request.session["video_paths"] = video_paths
        test_video_paths = [static('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5))) for vid in test_inputs]
        request.session["test_video_paths"] = test_video_paths
        request.session["test_labels"] = test_labels.tolist()
        print("test_labels", test_labels)
        # algorithm = test_algorithm_interactive(method="vocal_postgres", dataset_name=dataset_name, n_init_pos=5, n_init_neg=5, npred=7, depth=3, max_duration=15, beam_width=10, pool_size=100, k=100, budget=50, multithread=150, query_str=query_str, predicate_dict=predicate_dict, lru_capacity=None, reg_lambda=0.001, strategy='topk', max_vars=3, port=5432, input_dir=input_dir)

        # init_labeled_index = algorithm.labeled_index.copy()
        # init_vids = inputs[init_labeled_index]
        # log = []
        # while True:
        #     log_dict = algorithm.demo_main()
        #     if log_dict["state"] == "terminated":
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
        #         response["state"] = log_dict["state"]
        #         response["video_paths"] = [static('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(inputs[idx]//1000*1000).zfill(5), str((inputs[idx]//1000+1)*1000).zfill(5), str(inputs[idx]).zfill(5))) for idx in selected_segments]
        #         response["predicted_labels_test"] = log_dict["predicted_labels_test"]
        #         log.append(response)
        # print("init vids", init_vids)
        # print("log", log)

        log = example_query["log"]

        request.session["iteration"] = 0
        request.session["log"] = log
        response = log[0]
        response["video_paths"] = [request.session["video_paths"][idx] for idx in response["selected_segments"]]
        # For iteration 0, we won't have any stats yet.
        return JsonResponse(post_processing(response, test_video_paths, test_labels.tolist()))

class iterative_synthesis_live(APIView):
    def post(self, request, format=None):
        log_record = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": request.session.session_key,
            "query_idx": request.session['query_idx'],
            "run_id": request.session["run_id"],
            "action": "start_iterative_synthesis_live",
        }
        append_record(log_record)
        user_labels = request.data['user_labels']
        if request.session.session_key not in user_to_obj:
            # First time, initialize the algorithm
            print("query_idx:", request.session["query_idx"])
            query_idx = request.session['query_idx']
            example_query = example_queries[0] # FIXME: only support the first query for now

            predicate_dict = [{"name": "Near", "parameters": [1], "nargs": 2}, {"name": "Far", "parameters": [3], "nargs": 2}, {"name": "LeftOf", "parameters": None, "nargs": 2}, {"name": "Behind", "parameters": None, "nargs": 2}, {"name": "RightOf", "parameters": None, "nargs": 2}, {"name": "FrontOf", "parameters": None, "nargs": 2}, {"name": "RightQuadrant", "parameters": None, "nargs": 1}, {"name": "LeftQuadrant", "parameters": None, "nargs": 1}, {"name": "TopQuadrant", "parameters": None, "nargs": 1}, {"name": "BottomQuadrant", "parameters": None, "nargs": 1}, {"name": "Color", "parameters": ["gray", "red", "blue", "green", "brown", "cyan", "purple", "yellow"], "nargs": 1}, {"name": "Shape", "parameters": ["cube", "sphere", "cylinder"], "nargs": 1}, {"name": "Material", "parameters": ["metal", "rubber"], "nargs": 1}]

            dataset_name = "demo_queries_scene_graph"
            query_str = example_query["query_str"]
            # query_str = 'Conjunction(Conjunction(Color_red(o0), Color_yellow(o1)), LeftOf(o0, o1)); RightOf(o0, o1)'

            with open(os.path.join(input_dir, dataset_name, "train/{}_inputs.json".format(query_str)), 'r') as f:
                inputs = json.load(f)
            with open(os.path.join(input_dir, dataset_name, "train/{}_labels.json".format(query_str)), 'r') as f:
                labels = json.load(f)
            inputs = np.asarray(inputs)
            labels = np.asarray(labels)
            video_paths = [static('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5))) for vid in inputs]
            request.session["video_paths"] = video_paths
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

            if "init_vids" in request.data:
                init_vids = request.data["init_vids"]
                init_labeled_index = [int(np.where(inputs == vid)[0][0]) for vid in init_vids]
                request.session["init_labeled_index"] = init_labeled_index
            else:
                init_labeled_index = request.session["init_labeled_index"]

            print("init_labeled_index", init_labeled_index, "user_labels", user_labels, "beam_width", request.session['beam_width'], "budget", request.session['labeling_budget'])
            algorithm = test_algorithm_interactive(init_labeled_index=init_labeled_index, user_labels=user_labels, method="vocal_postgres", dataset_name=dataset_name, n_init_pos=len(init_labeled_index), n_init_neg=0, npred=7, depth=3, max_duration=15, beam_width=request.session['beam_width'], pool_size=25, n_sampled_videos=100, k=100, budget=request.session['labeling_budget'], multithread=30, query_str=query_str, predicate_dict=predicate_dict, lru_capacity=None, reg_lambda=0.001, strategy='topk', max_vars=3, port=5432, input_dir=input_dir) # n_init_pos is set to the number of initial labels and n_init_neg is set to 0. We only care about n_init_pos + n_init_neg.
            log_dict = algorithm.interactive_live()
        else:
            print("run_id", request.session["run_id"])
            algorithm = user_to_obj[request.session.session_key]
            log_dict = algorithm.interactive_live(user_labels)
        request.session["iteration"] = log_dict["iteration"]
        user_to_obj[request.session.session_key] = algorithm

        print("iteration done")
        if log_dict["state"] == "terminated":
            log_record = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": request.session.session_key,
                "query_idx": request.session['query_idx'],
                "run_id": request.session["run_id"],
                "action": log_dict["state"],
                "iteration": log_dict["iteration"],
                "user_labels": user_labels,
                "current_npos": log_dict["current_npos"],
                "current_nneg": log_dict["current_nneg"],
                "best_query_list": log_dict["best_query_list"],
                "best_score_list": log_dict["best_score_list"],
                "top_k_queries_with_scores": log_dict["top_k_queries_with_scores"],
            }
            response = {}
            response["state"] = log_dict["state"]
            response["iteration"] = log_dict["iteration"]
            response["current_npos"] = log_dict["current_npos"]
            response["current_nneg"] = log_dict["current_nneg"]
            response["best_query"] = log_dict["best_query_list"][0]
            response["best_score"] = log_dict["best_score_list"][0]
            response["best_query_list"] = log_dict["best_query_list"]
            response["best_score_list"] = log_dict["best_score_list"]
            response["top_k_queries_with_scores"] = log_dict["top_k_queries_with_scores"]
            response["predicted_labels_test"] = log_dict["predicted_labels_test"]
            append_record(log_record)
            return JsonResponse(post_processing(response, request.session["test_video_paths"], request.session["test_labels"]))
        else:
            response = {}
            response["state"] = log_dict["state"]
            # TODO: there is an error when the number of initial labels is greater than the labeling budget
            # TODO: consider the case when there is no more positive or negative videos provided as the initial labels
            selected_segments = log_dict["selected_segments"]
            response["iteration"] = log_dict["iteration"]
            response["sample_idx"] = log_dict["sample_idx"]
            response["video_paths"] = [request.session["video_paths"][idx] for idx in selected_segments]
            if log_dict["state"] == "label_more" or log_dict["iteration"] == 0:
                log_record = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "session_id": request.session.session_key,
                    "action": log_dict["state"],
                    "query_idx": request.session['query_idx'],
                    "run_id": request.session["run_id"],
                    "iteration": log_dict["iteration"],
                    "user_labels": user_labels,
                    "selected_gt_labels": log_dict["selected_gt_labels"],
                    "selected_segments": log_dict["selected_segments"],
                    "sample_idx": log_dict["sample_idx"], # The index of the selected segment at the current iteration
                }
                append_record(log_record)
                return JsonResponse(response)
            else:
                response["current_npos"] = log_dict["current_npos"]
                response["current_nneg"] = log_dict["current_nneg"]
                response["best_query"] = log_dict["best_query_list"][0]
                response["best_score"] = log_dict["best_score_list"][0]
                response["best_query_list"] = log_dict["best_query_list"]
                response["best_score_list"] = log_dict["best_score_list"]
                response["top_k_queries_with_scores"] = log_dict["top_k_queries_with_scores"]
                response["predicted_labels_test"] = log_dict["predicted_labels_test"]
                log_record = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "session_id": request.session.session_key,
                    "action": log_dict["state"],
                    "query_idx": request.session['query_idx'],
                    "run_id": request.session["run_id"],
                    "iteration": log_dict["iteration"],
                    "user_labels": user_labels,
                    "selected_gt_labels": log_dict["selected_gt_labels"],
                    "selected_segments": log_dict["selected_segments"],
                    "sample_idx": log_dict["sample_idx"], # The index of the selected segment at the current iteration
                    "current_npos": log_dict["current_npos"],
                    "current_nneg": log_dict["current_nneg"],
                    "best_query_list": log_dict["best_query_list"],
                    "best_score_list": log_dict["best_score_list"],
                    "top_k_queries_with_scores": log_dict["top_k_queries_with_scores"],
                    "predicted_labels_test": log_dict["predicted_labels_test"],
                }
                append_record(log_record)
                return JsonResponse(post_processing(response, request.session["test_video_paths"], request.session["test_labels"]))


class iterative_synthesis(APIView):
    def get(self, request, format=None):
        request.session["iteration"] += 1
        log = request.session["log"]
        if request.session["iteration"] < len(log):
            response = log[request.session["iteration"]]
            response["video_paths"] = [request.session["video_paths"][idx] for idx in response["selected_segments"]]
            return JsonResponse(post_processing(response, request.session["test_video_paths"], request.session["test_labels"]))
        else:
            request.session.clear()
            return JsonResponse({"state": "terminated"})

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

    log_copy["best_query_scene_graph"] = dsl_to_program(log_copy["best_query"])
    # FIXME: temporarily set the best query list to be a list of one element
    log_copy["best_query_list"] = [log_copy["best_query"]]
    log_copy["best_score_list"] = [log_copy["best_score"]]
    # log_copy["top_k_queries_with_scores"] = list(zip(log_copy["best_query_list"], log_copy["best_score_list"]))
    return log_copy

class set_run(APIView):
    def post(self, request, format=None):
        run_id = int(request.data['run_id'])
        query_idx = request.session['query_idx']
        request.session['run_id'] = run_id
        example_query = example_queries[query_idx]
        vids = example_query["vids"][run_id]
        labels = example_query["labels"]
        video_paths = [static('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5))) for vid in vids]

        log_record = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": request.session.session_key,
            "query_idx": query_idx,
            "run_id": run_id,
            "action": "set_run",
        }
        append_record(log_record)
        return JsonResponse({'video_paths': video_paths, 'labels': labels})

class set_params(APIView):
    def post(self, request, format=None):
        query_idx = int(request.data['queryId'])
        labeling_budget = int(request.data['labelingBudget'])
        videos_per_page = int(request.data['videosPerPage'])
        beam_width = int(request.data['beamWidth'])
        request, context = init_page(request, query_idx, labeling_budget, videos_per_page, beam_width)
        response = {
            'video_paths': [(vid, static(video_path)) for vid, video_path, label in context['video_paths']],
            'labeling_budget': context['labeling_budget'],
            'videos_per_page': context['videos_per_page'],
            'beam_width': context['beam_width']
        }
        return JsonResponse(response, encoder=NpEncoder)
        # return redirect(request, 'equi_app/index.html', context)
        # return init_page(request, query_idx, labeling_budget, videos_per_page, beam_width)

def init_page(request, query_idx, labeling_budget=50, videos_per_page=10, beam_width=5):
    request.session["init"] = True # To make sure the session is initialized
    request.session.clear()
    if request.session.session_key in user_to_obj:
        del user_to_obj[request.session.session_key]
    log_record = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": request.session.session_key,
        "query_idx": query_idx,
        "run_id": 0,
        "action": "start_task"
    }
    append_record(log_record)

    request.session['query_idx'] = query_idx
    request.session['run_id'] = 0
    request.session['labeling_budget'] = labeling_budget
    request.session['videos_per_page'] = videos_per_page
    request.session['beam_width'] = beam_width
    if query_idx < 3: # Guided query tasks
        example_query = example_queries[query_idx]
        vids = example_query["vids"]
        labels = example_query["labels"]
    else: # Live query tasks
        example_query = example_queries[0]
        # Initialization: randomly sample n_init_pos videos from positive videos and n_init_neg videos from negative videos
        # (but the user can still decide to label any video segment as positive or negative)
        dataset_name = "demo_queries_scene_graph"
        query_str = example_query["query_str"]
        with open(os.path.join(input_dir, "{}/train/{}_inputs.json".format(dataset_name, query_str)), 'r') as f:
            inputs = json.load(f)
        with open(os.path.join(input_dir, "{}/train/{}_labels.json".format(dataset_name, query_str)), 'r') as f:
            labels = json.load(f)
        inputs = np.asarray(inputs) # input video ids
        labels = np.asarray(labels)
        pos_idx = np.where(labels == 1)[0]
        neg_idx = np.where(labels == 0)[0]

        init_labeled_index = random.sample(pos_idx.tolist(), videos_per_page // 2) + random.sample(neg_idx.tolist(), videos_per_page // 2)
        request.session["init_labeled_index"] = init_labeled_index
        vids = inputs[init_labeled_index]
        labels = labels[init_labeled_index]
        print("vids", vids),
        print("labels", labels)

    query_text = example_query["query_text"]
    query_scene_graph = dsl_to_program(example_query["query_str"])
    print(example_query["query_str"])
    print(query_scene_graph)
    query_datalog = example_query["query_datalog"]
    if query_idx < 3:
        config = example_query["config"]
    else:
        config = None
    context = {
        'video_paths': [(vid, 'equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5)), label) for vid, label in zip(vids, labels)],
        'query_idx': query_idx,
        'query_text': query_text,
        'query_datalog': query_datalog,
        'query_scene_graph': query_scene_graph,
        'config': config,
        'labeling_budget': labeling_budget,
        'videos_per_page': videos_per_page,
        'beam_width': beam_width,
    }
    request.session.modified = True
    print("query_idx:", request.session['query_idx'])
    return request, context
    # return render(request, 'equi_app/index.html', context)