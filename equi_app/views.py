import random
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from rest_framework.views import APIView
from django.templatetags.static import static
import os, json
import numpy as np

import sys
sys.path.append("/Users/zhangenhao/Desktop/UW/Research/equi-vocal-demo/EQUI-VOCAL")
from src.synthesize import test_algorithm_interactive

class index(APIView):
    def get(self, request, format=None):
        request.session = {}
        vids = [2312, 569, 2669, 9478, 5090, 3220, 7969, 6926, 1233, 7829]
        labels = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
        query_text = "A purple object is far from a cyan object, then they move near each other."
        query_datalog = """
g1(vid, fid, oid1, oid2) :-
    Objects(vid, fid, oid1, _, _, _, _, _),
    Objects(vid, fid, oid2, _, _, _, _, _),
    Relationships(vid, fid, _, oid1, 'Far', oid2),
    Attributes(vid, fid, oid1, 'color', 'purple'),
    Attributes(vid, fid, oid2, 'color', 'cyan'),
    oid1 != oid2.

g1_star(vid, fid, fid, oid1, oid2) :- g1(vid, fid, oid1, oid2).
g1_star(vid, fid_start, fid_end, oid1, oid2) :-
    g1_star(vid, fid_start, fid, oid1, oid2),
    g1(vid, fid_end, oid1, oid2), fid_end = fid + 1.

g2(vid, fid, oid1, oid2) :-
    Objects(vid, fid, oid1, _, _, _, _, _),
    Objects(vid, fid, oid2, _, _, _, _, _),
    Relationships(vid, fid, _, oid1, 'Near', oid2),
    oid1 != oid2.

g2_star(vid, fid, fid, oid1, oid2) :- g2(vid, fid, oid1, oid2).
g2_star(vid, fid_start, fid_end, oid1, oid2) :-
    g2_star(vid, fid_start, fid, oid1, oid2),
    g2(vid, fid_end, oid1, oid2), fid_end = fid + 1.

q(vid) :- g1_star(vid, fid11, fid12, oid1, oid2),
    g2_star(vid, fid21, fid22, oid1, oid2), fid21 > fid12.
        """
        context = {
            'video_paths': [('equi_app/clevrer/video_{}-{}/video_{}.mp4'.format(str(vid//1000*1000).zfill(5), str((vid//1000+1)*1000).zfill(5), str(vid).zfill(5)), label) for vid, label in zip(vids, labels)],
            'query_text': query_text,
            'query_datalog': query_datalog
        }
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
        predicate_dict = [{"name": "Near", "parameters": [1], "nargs": 2}, {"name": "Far", "parameters": [3], "nargs": 2}, {"name": "LeftOf", "parameters": None, "nargs": 2}, {"name": "Behind", "parameters": None, "nargs": 2}, {"name": "RightOf", "parameters": None, "nargs": 2}, {"name": "FrontOf", "parameters": None, "nargs": 2}, {"name": "RightQuadrant", "parameters": None, "nargs": 1}, {"name": "LeftQuadrant", "parameters": None, "nargs": 1}, {"name": "TopQuadrant", "parameters": None, "nargs": 1}, {"name": "BottomQuadrant", "parameters": None, "nargs": 1}, {"name": "Color", "parameters": ["gray", "red", "blue", "green", "brown", "cyan", "purple", "yellow"], "nargs": 1}, {"name": "Shape", "parameters": ["cube", "sphere", "cylinder"], "nargs": 1}, {"name": "Material", "parameters": ["metal", "rubber"], "nargs": 1}]

        input_dir = "/Users/zhangenhao/Desktop/UW/Research/equi-vocal-demo/EQUI-VOCAL/inputs"
        dataset_name = "demo_queries_scene_graph"
        query_str = 'Conjunction(Conjunction(Color_purple(o0), Color_cyan(o1)), Far_3.0(o0, o1)); Near_1.0(o0, o1)'

        with open(os.path.join(input_dir, dataset_name, "train/{}_inputs.json".format(query_str)), 'r') as f:
            inputs = json.load(f)
        with open(os.path.join(input_dir, dataset_name, "train/{}_labels.json".format(query_str)), 'r') as f:
            labels = json.load(f)
        inputs = np.asarray(inputs)
        labels = np.asarray(labels)

        # algorithm = test_algorithm_interactive(method="vocal_postgres", dataset_name=dataset_name, n_init_pos=5, n_init_neg=5, npred=7, depth=3, max_duration=15, beam_width=10, pool_size=100, k=100, budget=50, multithread=4, query_str=query_str, predicate_dict=predicate_dict, lru_capacity=None, reg_lambda=0.001, strategy='topk', max_vars=3, port=5432, input_dir=input_dir)

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
        #         print(type(response["iteration"]))
        #         print(type(response["selected_gt_labels"]))
        #         print(type(response["current_npos"]))
        #         print(type(response["current_nneg"]))
        #         print(type(response["best_query"]))
        #         print(type(response["best_score"]))
        #         log.append(response)
        # print("init index", init_labeled_index)
        # print("init vids", init_vids)
        # print("log", log)
        # init_vids = [2312  569 2669 9478 5090 3220 7969 6926 1233 7829]
        log = [{'iteration': 0, 'selected_gt_labels': [0, 0], 'current_npos': 5, 'current_nneg': 7, 'best_query': 'Color_purple(o0)', 'best_score': 0.7682307692307693, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_07000-08000/video_07068.mp4', '/static/equi_app/clevrer/video_07000-08000/video_07734.mp4']}, {'iteration': 1, 'selected_gt_labels': [0, 0], 'current_npos': 5, 'current_nneg': 9, 'best_query': 'Color_cyan(o0); Color_purple(o1)', 'best_score': 0.9070909090909091, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_09000-10000/video_09391.mp4', '/static/equi_app/clevrer/video_06000-07000/video_06663.mp4']}, {'iteration': 2, 'selected_gt_labels': [0, 0], 'current_npos': 5, 'current_nneg': 11, 'best_query': 'LeftQuadrant(o0); Conjunction(RightQuadrant(o0), Shape_cube(o1))', 'best_score': 0.997, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_04000-05000/video_04249.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00183.mp4']}, {'iteration': 3, 'selected_gt_labels': [0, 0], 'current_npos': 5, 'current_nneg': 13, 'best_query': 'Conjunction(Color_purple(o0), Color_cyan(o1)); Conjunction(BottomQuadrant(o2), Far_3.0(o0, o1))', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_02000-03000/video_02380.mp4', '/static/equi_app/clevrer/video_05000-06000/video_05599.mp4']}, {'iteration': 4, 'selected_gt_labels': [0, 0, 1], 'current_npos': 6, 'current_nneg': 15, 'best_query': 'Far_3.0(o0, o1); Near_1.0(o0, o1); Conjunction(Color_cyan(o0), Color_purple(o1))', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_03000-04000/video_03037.mp4', '/static/equi_app/clevrer/video_05000-06000/video_05087.mp4', '/static/equi_app/clevrer/video_09000-10000/video_09968.mp4']}, {'iteration': 5, 'selected_gt_labels': [1, 1, 1], 'current_npos': 9, 'current_nneg': 15, 'best_query': 'Far_3.0(o0, o1); Conjunction(Conjunction(Color_cyan(o0), Color_purple(o1)), Near_1.0(o0, o1))', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00102.mp4', '/static/equi_app/clevrer/video_03000-04000/video_03783.mp4', '/static/equi_app/clevrer/video_08000-09000/video_08467.mp4']}, {'iteration': 6, 'selected_gt_labels': [1, 1, 1], 'current_npos': 12, 'current_nneg': 15, 'best_query': 'Far_3.0(o0, o1); Conjunction(Color_purple(o0), Near_1.0(o0, o1)); Color_cyan(o1)', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_01000-02000/video_01875.mp4', '/static/equi_app/clevrer/video_06000-07000/video_06719.mp4', '/static/equi_app/clevrer/video_05000-06000/video_05508.mp4']}, {'iteration': 7, 'selected_gt_labels': [1, 1, 1], 'current_npos': 15, 'current_nneg': 15, 'best_query': 'Far_3.0(o0, o1); Near_1.0(o0, o1); Conjunction(Color_cyan(o0), Color_purple(o1))', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_02000-03000/video_02035.mp4', '/static/equi_app/clevrer/video_05000-06000/video_05724.mp4', '/static/equi_app/clevrer/video_07000-08000/video_07039.mp4']}, {'iteration': 8, 'selected_gt_labels': [1, 1, 1], 'current_npos': 18, 'current_nneg': 15, 'best_query': 'Far_3.0(o0, o1); Near_1.0(o0, o1); Conjunction(Color_cyan(o0), Color_purple(o1))', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_04000-05000/video_04350.mp4', '/static/equi_app/clevrer/video_07000-08000/video_07731.mp4', '/static/equi_app/clevrer/video_05000-06000/video_05379.mp4']}, {'iteration': 9, 'selected_gt_labels': [0, 0, 1], 'current_npos': 19, 'current_nneg': 17, 'best_query': 'Far_3.0(o0, o1); Conjunction(Color_cyan(o0), Color_purple(o1)); Near_1.0(o0, o1)', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_07000-08000/video_07857.mp4', '/static/equi_app/clevrer/video_04000-05000/video_04235.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00524.mp4']}, {'iteration': 10, 'selected_gt_labels': [1, 1, 1], 'current_npos': 22, 'current_nneg': 17, 'best_query': 'Far_3.0(o0, o1); Conjunction(Conjunction(Color_cyan(o0), Color_purple(o1)), Near_1.0(o0, o1))', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_08000-09000/video_08368.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00432.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00296.mp4']}, {'iteration': 11, 'selected_gt_labels': [0, 1, 0], 'current_npos': 23, 'current_nneg': 19, 'best_query': 'Far_3.0(o0, o1); Conjunction(Color_purple(o0), Near_1.0(o0, o1)); Color_cyan(o1)', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_03000-04000/video_03718.mp4', '/static/equi_app/clevrer/video_02000-03000/video_02905.mp4', '/static/equi_app/clevrer/video_04000-05000/video_04417.mp4']}, {'iteration': 12, 'selected_gt_labels': [1, 0], 'current_npos': 24, 'current_nneg': 20, 'best_query': 'Far_3.0(o0, o1); Near_1.0(o0, o1); Conjunction(Color_cyan(o0), Color_purple(o1))', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_04000-05000/video_04028.mp4', '/static/equi_app/clevrer/video_07000-08000/video_07338.mp4']}, {'iteration': 13, 'selected_gt_labels': [1, 1], 'current_npos': 26, 'current_nneg': 20, 'best_query': 'Far_3.0(o0, o1); Conjunction(Conjunction(Color_cyan(o0), Color_purple(o1)), Near_1.0(o0, o1))', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_06000-07000/video_06152.mp4', '/static/equi_app/clevrer/video_06000-07000/video_06874.mp4']}, {'iteration': 14, 'selected_gt_labels': [0, 0], 'current_npos': 26, 'current_nneg': 22, 'best_query': 'Far_3.0(o0, o1); Conjunction(Color_purple(o1), Near_1.0(o0, o1)); Color_cyan(o0)', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_01000-02000/video_01480.mp4', '/static/equi_app/clevrer/video_06000-07000/video_06322.mp4']}, {'iteration': 15, 'selected_gt_labels': [0, 0], 'current_npos': 26, 'current_nneg': 24, 'best_query': 'Far_3.0(o0, o1); Conjunction(Color_purple(o0), Near_1.0(o0, o1)); Color_cyan(o1)', 'best_score': 0.996, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_04000-05000/video_04730.mp4', '/static/equi_app/clevrer/video_02000-03000/video_02831.mp4']}]
        request.session["iteration"] = 0
        request.session["log"] = log
        return JsonResponse(log[0])

class iterative_synthesis(APIView):
    def get(self, request, format=None):
        request.session["iteration"] += 1
        log = request.session["log"]
        if request.session["iteration"] < len(log):
            return JsonResponse(log[request.session["iteration"]])
        else:
            request.session = {}
            return JsonResponse({"terminated": True})

# algorithm = test_algorithm_interactive(method="vocal_postgres", dataset_name="synthetic_scene_graph_easy", n_init_pos=3, n_init_neg=3, npred=7, depth=3, max_duration=1, beam_width=5, pool_size=10, k=100, budget=17, multithread=4, query_str='Conjunction(Conjunction(Conjunction(Behind(o0, o1), BottomQuadrant(o0)), Color_brown(o0)), Near_1.0(o0, o2))', predicate_dict=predicate_dict, lru_capacity=None, reg_lambda=0.001, strategy='topk', max_vars=3, port=5432, input_dir="/Users/zhangenhao/Desktop/UW/Research/equi-vocal-demo/EQUI-VOCAL/inputs")
# log [{'iteration': 0, 'selected_gt_labels': [0], 'current_npos': 3, 'current_nneg': 4, 'best_query': 'Color_brown(o0)', 'best_score': 0.8561428571428571, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00122.mp4']}, {'iteration': 1, 'selected_gt_labels': [0, 0], 'current_npos': 3, 'current_nneg': 6, 'best_query': 'Color_brown(o0); Shape_cylinder(o1)', 'best_score': 0.998, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00341.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00224.mp4']}, {'iteration': 2, 'selected_gt_labels': [0, 0], 'current_npos': 3, 'current_nneg': 8, 'best_query': 'Color_brown(o0); Shape_cylinder(o1); BottomQuadrant(o2)', 'best_score': 0.997, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00343.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00313.mp4']}, {'iteration': 3, 'selected_gt_labels': [0, 0], 'current_npos': 3, 'current_nneg': 10, 'best_query': 'BottomQuadrant(o0); Color_brown(o0); Near_1.0(o0, o1)', 'best_score': 0.997, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00367.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00401.mp4']}, {'iteration': 4, 'selected_gt_labels': [0, 0], 'current_npos': 3, 'current_nneg': 12, 'best_query': 'Conjunction(Conjunction(BottomQuadrant(o0), Color_brown(o1)), Near_1.0(o0, o1)); BottomQuadrant(o1)', 'best_score': 0.996, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00062.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00036.mp4']}, {'iteration': 5, 'selected_gt_labels': [0], 'current_npos': 3, 'current_nneg': 13, 'best_query': 'BottomQuadrant(o0); Conjunction(Color_brown(o1), Near_1.0(o0, o1)); BottomQuadrant(o1)', 'best_score': 0.996, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00448.mp4']}, {'iteration': 6, 'selected_gt_labels': [1], 'current_npos': 4, 'current_nneg': 13, 'best_query': 'Conjunction(Conjunction(BottomQuadrant(o0), Color_brown(o1)), Near_1.0(o0, o1)); BottomQuadrant(o1)', 'best_score': 0.996, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00074.mp4']}]

# algorithm = test_algorithm_interactive(method="vocal_postgres", dataset_name="synthetic_scene_graph_easy", n_init_pos=5, n_init_neg=5, npred=7, depth=3, max_duration=15, beam_width=10, pool_size=100, k=100, budget=30, multithread=4, query_str='Conjunction(Conjunction(Conjunction(Behind(o0, o1), BottomQuadrant(o0)), Color_brown(o0)), Near_1.0(o0, o2))', predicate_dict=predicate_dict, lru_capacity=None, reg_lambda=0.001, strategy='topk', max_vars=3, port=5432, input_dir="/Users/zhangenhao/Desktop/UW/Research/equi-vocal-demo/EQUI-VOCAL/inputs")
# log [{'iteration': 0, 'selected_gt_labels': [0], 'current_npos': 5, 'current_nneg': 6, 'best_query': 'Color_brown(o0)', 'best_score': 0.9080909090909091, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00365.mp4']}, {'iteration': 1, 'selected_gt_labels': [0], 'current_npos': 5, 'current_nneg': 7, 'best_query': 'Conjunction(BottomQuadrant(o0), Color_brown(o0))', 'best_score': 0.998, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00128.mp4']}, {'iteration': 2, 'selected_gt_labels': [0], 'current_npos': 5, 'current_nneg': 8, 'best_query': 'Color_brown(o0); BottomQuadrant(o0)', 'best_score': 0.998, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00476.mp4']}, {'iteration': 3, 'selected_gt_labels': [0], 'current_npos': 5, 'current_nneg': 9, 'best_query': 'Color_brown(o0); Conjunction(BottomQuadrant(o0), Near_1.0(o0, o1))', 'best_score': 0.997, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00470.mp4']}, {'iteration': 4, 'selected_gt_labels': [0], 'current_npos': 5, 'current_nneg': 10, 'best_query': 'Conjunction(Color_brown(o0), LeftQuadrant(o1)); Far_3.0(o1, o2); Conjunction(BottomQuadrant(o2), FrontOf(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00479.mp4']}, {'iteration': 5, 'selected_gt_labels': [0], 'current_npos': 5, 'current_nneg': 11, 'best_query': 'Conjunction(BottomQuadrant(o0), Color_brown(o0)); Conjunction(Conjunction(Color_brown(o0), FrontOf(o1, o2)), Near_1.0(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00163.mp4']}, {'iteration': 6, 'selected_gt_labels': [0, 1], 'current_npos': 6, 'current_nneg': 12, 'best_query': 'Conjunction(Behind(o0, o1), FrontOf(o1, o2)); BottomQuadrant(o0); Conjunction(Color_brown(o0), Near_1.0(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00057.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00360.mp4']}, {'iteration': 7, 'selected_gt_labels': [0, 1], 'current_npos': 7, 'current_nneg': 13, 'best_query': 'Conjunction(BottomQuadrant(o0), Color_brown(o0)); Conjunction(Color_brown(o0), Near_1.0(o0, o1)); Behind(o0, o2)', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00211.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00464.mp4']}, {'iteration': 8, 'selected_gt_labels': [0, 1], 'current_npos': 8, 'current_nneg': 14, 'best_query': 'Conjunction(Conjunction(Behind(o0, o1), BottomQuadrant(o0)), FrontOf(o1, o2)); Conjunction(Color_brown(o0), Near_1.0(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00015.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00140.mp4']}, {'iteration': 9, 'selected_gt_labels': [0, 1], 'current_npos': 9, 'current_nneg': 15, 'best_query': 'Color_brown(o0); BottomQuadrant(o0); Conjunction(Conjunction(Behind(o0, o1), BottomQuadrant(o0)), Near_1.0(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00076.mp4', '/static/equi_app/clevrer/video_00000-01000/video_00389.mp4']}, {'iteration': 10, 'selected_gt_labels': [0], 'current_npos': 9, 'current_nneg': 16, 'best_query': 'Color_brown(o0); BottomQuadrant(o0); Conjunction(Conjunction(Behind(o0, o1), BottomQuadrant(o0)), Near_1.0(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00152.mp4']}, {'iteration': 11, 'selected_gt_labels': [0], 'current_npos': 9, 'current_nneg': 17, 'best_query': 'Color_brown(o0); BottomQuadrant(o0); Conjunction(Conjunction(Behind(o0, o1), BottomQuadrant(o0)), Near_1.0(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00101.mp4']}, {'iteration': 12, 'selected_gt_labels': [0], 'current_npos': 9, 'current_nneg': 18, 'best_query': 'Color_brown(o0); BottomQuadrant(o0); Conjunction(Conjunction(Behind(o0, o1), BottomQuadrant(o0)), Near_1.0(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00153.mp4']}, {'iteration': 13, 'selected_gt_labels': [0], 'current_npos': 9, 'current_nneg': 19, 'best_query': 'Color_brown(o0); BottomQuadrant(o0); Conjunction(Conjunction(Behind(o0, o1), BottomQuadrant(o0)), Near_1.0(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00302.mp4']}, {'iteration': 14, 'selected_gt_labels': [0], 'current_npos': 9, 'current_nneg': 20, 'best_query': 'Color_brown(o0); BottomQuadrant(o0); Conjunction(Conjunction(Behind(o0, o1), BottomQuadrant(o0)), Near_1.0(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00472.mp4']}, {'iteration': 15, 'selected_gt_labels': [0], 'current_npos': 9, 'current_nneg': 21, 'best_query': 'Color_brown(o0); BottomQuadrant(o0); Conjunction(Conjunction(Behind(o0, o1), BottomQuadrant(o0)), Near_1.0(o0, o2))', 'best_score': 0.995, 'terminated': False, 'video_paths': ['/static/equi_app/clevrer/video_00000-01000/video_00062.mp4']}]