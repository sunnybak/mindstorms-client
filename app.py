from flask import Flask, request
import time

app = Flask(__name__)

@app.route('/')
def hello_world():
	time.sleep(5)
	return 'Create a businss plan for a new startup.'

@app.route('/receive')
def receive():
	print('Profile received: ' + request.args.get('name') + ' works on ' + request.args.get('work'))
	return 'ok'

# create a new POST route called summary which simply takes the post requests and prints the summary
@app.route('/summary', methods=['POST'])
def summary():
	print(request.json)
	return 'ok'

# main driver function
if __name__ == '__main__':
	app.run()
