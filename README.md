# EQUI-VOCAL Web Application

A prototype implementation of EQUI-VOCAL, which is a system to automatically synthesize compositional queries over videos from limited user interactions. See the [technical report](https://arxiv.org/abs/2301.00929) and the [website](https://db.cs.washington.edu/projects/visualworld/) for more details.

# Download resources
Download [training videos](http://clevrer.csail.mit.edu/) at Dataset → Training Videos\

Create new folder equi_app/static/equi_app/clevrer and place downloaded videos in it

Download demo_queries_scene_graph and move to EQUI-VOCAL/inputs

# Set up
in equi_app/views.py

	line 11: change filepath in sys.path.append() to path to EQUI-VOCAL directory

	line 12: comment out
	
	line 67: change input_dir value to path to EQUI-VOCAL/inputs folder 


# Start the server
brew services restart postgresql@14
pg_ctl -D /usr/local/var/postgresql@14 restart

# Connect to server
The name of the database is `equi_app`

psql equi_app

# Postgres UDF
compile (macOS):
```
cc -I /usr/local/Cellar/postgresql@14/14.6_1/include/postgresql@14/server -c functors.c
cc -bundle -flat_namespace -undefined suppress -o functors.so functors.o
```

# Virtual environment
source env/bin/activate

# Django
python manage.py runserver