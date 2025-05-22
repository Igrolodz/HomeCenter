from flask import Flask, render_template, jsonify
import wakeonlan
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "igrolodz": generate_password_hash("asERcvAR2312!"),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@app.route('/')
def index():
    return render_template('index.html')

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
    app.run(host='0.0.0.0', port=21376, threaded=True)