from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from rest_framework.views import APIView

class index(APIView):
    def get(self, request, format=None):
        context = {
            'video_path_list': ['equi_app/clevrer/video_00000.mp4',
                                'equi_app/clevrer/video_00001.mp4',
                                'equi_app/clevrer/video_00002.mp4'
                                ],
        }
        return render(request, 'equi_app/index.html', context)