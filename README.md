# EQUI-VOCAL Web Application

A prototype implementation of EQUI-VOCAL, which is a system to automatically synthesize compositional queries over videos from limited user interactions. See the [technical report](https://arxiv.org/abs/2301.00929) and the [website](https://db.cs.washington.edu/projects/visualworld/) for more details.

## Setup Instructions
First, set up the backend [code](https://github.com/uwdb/EQUI-VOCAL).

### Download resources
Download [training videos](http://clevrer.csail.mit.edu/) at Dataset → Training Videos\

Create new folder equi_app/static/equi_app/clevrer and place downloaded videos in it

Download demo_queries_scene_graph and move to EQUI-VOCAL/inputs

### Django
python manage.py runserver
