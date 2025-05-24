# basic flask with socketio
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import json

# weather api imports
from weather import get_weather
import time

# wake on lan + security imports
import wakeonlan
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

# Hardware info import
import psutil

# Network info import
import subprocess
import ipaddress

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
        time.sleep(1)  # wait 1 second
        
def send_system_stats():
    while True:
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            ram_usage = psutil.virtual_memory().percent
            disk_space = psutil.disk_usage('/').percent
            system_stats = {
                'cpu_usage': cpu_usage,
                'ram_usage': ram_usage,
                'disk_space': disk_space
            }
            socketio.emit('system_stats_update', system_stats)
        except Exception as e:
            print("Error updating system stats:", e)
        time.sleep(1)  # wait 1 second

def send_network_stats():
    while True:
        try:
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent
            bytes_recv = net_io.bytes_recv
            time.sleep(1)
            net_io_new = psutil.net_io_counters()
            # Calculate speed in Mbps (dividing by 1024*1024/8 to convert bytes to Mbits)
            upload_speed = (net_io_new.bytes_sent - bytes_sent) / (1024 * 1024 / 8)
            download_speed = (net_io_new.bytes_recv - bytes_recv) / (1024 * 1024 / 8)
            network_stats = {
                'upload_speed': f"{upload_speed:.2f}",
                'download_speed': f"{download_speed:.2f}"
            }
            socketio.emit('network_stats_update', network_stats)
        except Exception as e:
            print("Error getting network stats:", e)
        time.sleep(1)
    
def ping_sweep(subnet="192.168.0.0/24"):
    active = []
    print("Scanning network...")
    for ip in ipaddress.IPv4Network(subnet):
        result = subprocess.run(["ping", "-n", "1", "-w", "300", str(ip)], stdout=subprocess.DEVNULL)
        if result.returncode == 0:
            active.append(str(ip))
    return active

def device_scanner():
    while True:
        current_state = set(ping_sweep())
        print("Current state:", current_state)
        # socketio.emit("network_devices", list(current_state))
        with open("static/DB/devices.json" , "w") as f:
            json.dump(list(current_state), f)
        time.sleep(1)


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
    socketio.start_background_task(send_system_stats)
    socketio.start_background_task(send_network_stats)
    socketio.start_background_task(device_scanner)
    socketio.run(app, host='0.0.0.0', port=21376)