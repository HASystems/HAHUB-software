#!/usr/bin/python

#############################################################################################
# Reference for this tutorial for writing ReSTful service --
#
# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
#
# did not include security (as we do not require for our HAHUB service)
#
# Should add another resouce such as /todo/api/v1.0/ha.rc
# -- for viewing and modifying/adding/deleting the ha.rc file entries
#
#############################################################################################

from flask import Flask, jsonify, abort, make_response, request, url_for

app = Flask(__name__)

tasks = [
	{
		'id': 1,
		'title': u'Buy Groceries',
		'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
		'done': False
	},
	{
		'id': 2,
		'title': u'Learn Python',
		'description': u'Need to find a good Python tutorial on the web',
		'done': False
	}
]

@app.route('/', methods=['GET'])
def index():
	return redirect('/todo/api/v1.0/tasks', code=302)

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
	return jsonify({'tasks': [make_public_task(task) for task in tasks]})
	# return jsonify({'tasks': tasks})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	return jsonify({'task': make_public_task(task[0])})
	# return jsonify({'task':task[0]})

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
	if not request.json or not 'title' in request.json:
		abort(400)
	task = {
		'id': tasks[-1]['id']+1,
		'title': request.json['title'],
		'description': request.json.get('description', ""),
		'done': False
	}
	tasks.append(task)
	return jsonify({'task': make_public_task(task)})
	# return jsonify({'task':task}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	if not request.json:
		abort(400)
	if 'title' in request.json and type(request.json['title']) != unicode:
		abort(400)
	if 'description' in request.json and type(request.json['description']) is not unicode:
		abort(400)
	if 'done' in request.json and type(request.json['done']) is not bool:
		abort(400)
	task[0]['title'] = request.json.get('title', task[0]['title'])
	task[0]['description'] = request.json.get('description', task[0]['description'])
	task[0]['done'] = request.json.get('done', task[0]['done'])
	return jsonify({'task': make_public_task(task[0])})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	tasks.remove(task[0])
	return jsonify({'result': True})

def make_public_task(task):
	new_task = {}
	for field in task:
		new_task[field] = task[field]
		if field == 'id':
			new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)

	return new_task
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)
