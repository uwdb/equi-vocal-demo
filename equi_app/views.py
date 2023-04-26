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
import psycopg2 as psycopg
sys.path.append("/Users/manasiganti/EQUI-VOCAL")
from src.synthesize import test_algorithm_interactive
from src.utils import str_to_program_postgres

module_dir = os.path.dirname(__file__)   #get current directory
with open(os.path.join(module_dir, 'example_queries.json')) as f:
    example_queries = json.load(f)

user_to_obj = {}

class index(APIView):
    def get(self, request, query_idx=0, format=None):
        request.session.clear()
        if request.session.session_key in user_to_obj:
            del user_to_obj[request.session.session_key]
        request.session['query_idx'] = query_idx
        example_query = example_queries[query_idx]

        if(query_idx==3):
            input_dir = "/Users/manasiganti/EQUI-VOCAL/inputs"
            dataset_name = "demo_queries_scene_graph"
            query_str = example_query["query_str"]
            with open(os.path.join(input_dir, dataset_name, "train/{}_inputs.json".format(query_str)), 'r') as f:
                vids = json.load(f)
            with open(os.path.join(input_dir, dataset_name, "train/{}_labels.json".format(query_str)), 'r') as f:
                labels = json.load(f)
            vids = np.asarray(vids)
            labels = np.asarray(labels)
        else:
            vids = example_query["vids"]
            labels = example_query["labels"]
        video_paths = video_paths = [static('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5))) for vid in vids]            
        filters = udf_labels(video_paths, [vid for vid in vids])
        udf_opts = udf_options()


        
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
            'video_paths': [('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5)), label, filterstr) for vid, label, filterstr in zip(vids, labels, filters)][0:10],
            'udfs_color_options': udf_opts[0],
            'udfs_shape_options': udf_opts[1],
            'udfs_material_options': udf_opts[2],
            'query_idx': query_idx,
            'query_text': query_text,
            'query_datalog': query_datalog,
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

        input_dir = "/Users/manasiganti/EQUI-VOCAL/inputs"
        dataset_name = "demo_queries_scene_graph"
        query_str = example_query["query_str"]
        # query_str = 'Conjunction(Conjunction(Color_red(o0), Color_yellow(o1)), LeftOf(o0, o1)); RightOf(o0, o1)'

        with open(os.path.join(input_dir, dataset_name, "train/{}_inputs.json".format(query_str)), 'r') as f:
            inputs = json.load(f) #length 500
        with open(os.path.join(input_dir, dataset_name, "train/{}_labels.json".format(query_str)), 'r') as f:
            labels = json.load(f)
        inputs = np.asarray(inputs)
        labels = np.asarray(labels)
        video_paths = [static('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5))) for vid in inputs]

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

        # For iteration 0, we won't have any stats yet.
        return JsonResponse(post_processing(log[0], test_video_paths, test_labels.tolist()))

class iterative_synthesis_live(APIView):
    def post(self, request, format=None):
        user_labels = request.data['user_labels']
        if request.session.session_key not in user_to_obj:
            # First time, initialize the algorithm
            print("query_idx:", request.session["query_idx"])
            query_idx = request.session['query_idx']
            example_query = example_queries[query_idx]

            predicate_dict = [{"name": "Near", "parameters": [1], "nargs": 2}, {"name": "Far", "parameters": [3], "nargs": 2}, {"name": "LeftOf", "parameters": None, "nargs": 2}, {"name": "Behind", "parameters": None, "nargs": 2}, {"name": "RightOf", "parameters": None, "nargs": 2}, {"name": "FrontOf", "parameters": None, "nargs": 2}, {"name": "RightQuadrant", "parameters": None, "nargs": 1}, {"name": "LeftQuadrant", "parameters": None, "nargs": 1}, {"name": "TopQuadrant", "parameters": None, "nargs": 1}, {"name": "BottomQuadrant", "parameters": None, "nargs": 1}, {"name": "Color", "parameters": ["gray", "red", "blue", "green", "brown", "cyan", "purple", "yellow"], "nargs": 1}, {"name": "Shape", "parameters": ["cube", "sphere", "cylinder"], "nargs": 1}, {"name": "Material", "parameters": ["metal", "rubber"], "nargs": 1}]

            input_dir = "/Users/manasiganti/EQUI-VOCAL/inputs"
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

            algorithm = test_algorithm_interactive(method="vocal_postgres", dataset_name=dataset_name, n_init_pos=10, n_init_neg=10, npred=7, depth=3, max_duration=15, beam_width=10, pool_size=100, k=100, budget=50, multithread=8, query_str=query_str, predicate_dict=predicate_dict, lru_capacity=None, reg_lambda=0.001, strategy='topk', max_vars=3, port=5432, input_dir=input_dir)
            # user_to_obj[request.session.session_key] = algorithm
            request.session["iteration"] = 0
            log_dict = algorithm.interactive_live()

        else:
            algorithm = user_to_obj[request.session.session_key]
            request.session["iteration"] += 1
            log_dict = algorithm.interactive_live(user_labels)
        user_to_obj[request.session.session_key] = algorithm

        print("iteration done")

        if log_dict["state"] == "terminated":
            request.session = {}
            return JsonResponse({"state": "terminated"})
        else:
            response = {}
            response["state"] = log_dict["state"]
            selected_segments = log_dict["selected_segments"]
            response["iteration"] = log_dict["iteration"]
            response["sample_idx"] = log_dict["sample_idx"]
            response["video_paths"] = request.session["video_paths"] #[request.session["video_paths"][idx] for idx in selected_segments]
            if log_dict["state"] == "label_more" or log_dict["iteration"] == 0:
                return JsonResponse(response)
            else:
                response["current_npos"] = log_dict["current_npos"]
                response["current_nneg"] = log_dict["current_nneg"]
                response["best_query"] = log_dict["best_query"]
                response["best_score"] = log_dict["best_score"]
                response["predicted_labels_test"] = log_dict["predicted_labels_test"]
                return JsonResponse(post_processing(response, request.session["test_video_paths"], request.session["test_labels"]))

class iterative_synthesis(APIView):
    def get(self, request, format=None):
        request.session["iteration"] += 1
        log = request.session["log"]
        if request.session["iteration"] < len(log):
            return JsonResponse(post_processing(log[request.session["iteration"]], request.session["test_video_paths"], request.session["test_labels"]))
        else:
            request.session = {}
            return JsonResponse({"state": "terminated"})

def udf_labels(video_paths, video_ids):
    #filter_labels_path = 

    if(os.path.exists(os.path.join(module_dir,'filter_labels.json'))):
        with open('equi_app/filter_labels.json', 'r') as f:
            print("HI PRELOADED 1")
            return json.load(f)
    else:
        dsn = "dbname=equi_app user=manasiganti host=localhost" #clean up later
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                output_filters = []
                for (path, vid) in zip(video_paths, video_ids):
                    cur.execute("SELECT DISTINCT Color FROM Obj_clevrer WHERE vid={vid};".format(vid=vid)) #todo: no for loop
                    vid_filters_color = cur.fetchall()
                    cur.execute("SELECT DISTINCT Shape FROM Obj_clevrer WHERE vid={vid};".format(vid=vid))
                    vid_filters_shape = cur.fetchall()
                    cur.execute("SELECT DISTINCT Material FROM Obj_clevrer WHERE vid={vid};".format(vid=vid))
                    vid_filters_material = cur.fetchall()
                    # separate by space?
                    filterstr = ""
                    for fil in vid_filters_color:
                        filterstr += fil[0] + " "                
                    for fil in vid_filters_shape:
                        filterstr += fil[0] + " "
                    for fil in vid_filters_material:
                        filterstr += fil[0] + " "
                    output_filters.append(filterstr.rstrip())
                    #print(filterstr)
                with open('equi_app/filter_labels.json', 'w') as f:
                  json.dump(output_filters, f, ensure_ascii=False)
                return output_filters

# user defined predicates to filter on and their values (options to filter by)
def udf_options():
    if(os.path.exists(os.path.join(module_dir,'filter_options.json'))):
        with open('equi_app/filter_options.json', 'r') as f:
            print("HI PRELOADED 2")
            return json.load(f) 
    else:
        dsn = "dbname=equi_app user=manasiganti host=localhost" #clean up later
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT Color FROM Obj_clevrer;") 
                color_options = cur.fetchall()
                cur.execute("SELECT DISTINCT Shape FROM Obj_clevrer;")
                shape_options = cur.fetchall()
                cur.execute("SELECT DISTINCT Material FROM Obj_clevrer;")
                material_options = cur.fetchall()
                output_options = [color_options, shape_options, material_options]
                with open('equi_app/filter_options.json', 'w') as f:
                  json.dump(output_options, f, ensure_ascii=False)
                return output_options

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