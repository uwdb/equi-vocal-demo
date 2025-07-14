# EQUI-VOCAL Web Application

A prototype implementation of EQUI-VOCAL, which is a system to automatically synthesize compositional queries over videos from limited user interactions. See the [technical report](https://arxiv.org/abs/2301.00929) and the [website](https://db.cs.washington.edu/projects/visualworld/) for more details.

## Setup Instructions
First, set up the backend [code](https://github.com/uwdb/EQUI-VOCAL).

### Download resources
1. Download [training videos](http://clevrer.csail.mit.edu/) at Dataset → Training Videos.

2. Create a new folder `equi_app/static/equi_app/clevrer/`, and place downloaded videos in it.

3. Ensure that the `inputs/demo_queries_scene_graph` directory is present in your locally cloned EQUI-VOCAL repository.

### Start Django server
1. Modify `config.json`.

2. Run the following commands to set up the Django application:
```sh
python manage.py migrate
```
3. Run the Django server:
```sh
python manage.py runserver
```
