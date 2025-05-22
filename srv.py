# basic flask with socketio
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit

# weather api imports
from weather import get_weather
import time

# wake on lan + security imports
import wakeonlan
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()
socketio = SocketIO(app)


API_KEY = "f263012af952d70aba19d0072080042b"
LAT = 51.12
LON = 17.22

users = {
    "igrolodz": generate_password_hash("asERcvAR2312!"),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/wol')
def WOL():
    return render_template('WOL.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username in users and check_password_hash(users.get(username), password):
        return redirect(url_for('home'))
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401


def send_weather_loop():
    while True:
        try:
            weather = get_weather(API_KEY, LAT, LON)
            socketio.emit('weather_update', weather)
        except Exception as e:
            print("Error updating weather:", e)
        time.sleep(1)  # wait 10 seconds

@socketio.on('connect')
def handle_connect():
    print("Client connected")


@app.route('/wake', methods=['GET'])
@auth.login_required
def wake_pc():
    try:
        print("Received wake command")
        wakeonlan.main(["D8:43:AE:3E:45:0F"])  # Uses default port 9 and broadcast address
        return jsonify({'message': 'Wake command sent successfully! ARCTIC should be on in a few seconds!'})
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    socketio.start_background_task(send_weather_loop)
    socketio.run(app, host='0.0.0.0', port=21376)