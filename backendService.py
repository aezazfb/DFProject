from flask import Flask, request, Response
from flask_cors import CORS
import subprocess
import os
import shutil

app = Flask(__name__)
CORS(app)

TOOLS_DIR = os.path.expanduser('~/tools')
KNOCKPY_PATH = os.path.join(TOOLS_DIR, 'knockpy', 'knockpy.py')
SUBLIST3R_PATH = os.path.join(TOOLS_DIR, 'Sublist3r', 'sublist3r.py')
MOSINT_DIR = os.path.join(TOOLS_DIR, 'mosint')
MOSINT_CMD_DIR = os.path.join(MOSINT_DIR, 'v3', 'cmd', 'mosint')
MOSINT_BINARY_PATH = os.path.join(MOSINT_CMD_DIR, 'mosint')
DNSENUM_COMMAND = 'dnsenum'

def ensure_tools_installed():
    os.makedirs(TOOLS_DIR, exist_ok=True)

    # Knockpy
    if not os.path.exists(KNOCKPY_PATH):
        subprocess.run(['git', 'clone', 'https://github.com/guelfoweb/knock.git', os.path.join(TOOLS_DIR, 'knockpy')])

    # Sublist3r
    if not os.path.exists(SUBLIST3R_PATH):
        subprocess.run(['git', 'clone', 'https://github.com/aboul3la/Sublist3r.git', os.path.join(TOOLS_DIR, 'Sublist3r')])

    # Mosint (Go version)
    if not os.path.exists(MOSINT_BINARY_PATH):
        subprocess.run(['git', 'clone', 'https://github.com/alpkeskin/mosint.git', MOSINT_DIR])
        subprocess.run(['go', 'build', '-o', 'mosint', 'main.go'], cwd=MOSINT_CMD_DIR)

    # ~/.mosint.yaml config
    mosint_config_path = os.path.expanduser('~/.mosint.yaml')
    if not os.path.exists(mosint_config_path):
        mosint_config_content = """# Config file for github.com/alpkeskin/mosint

services:
  breach_directory_api_key: SET_YOUR_API_KEY_HERE
  emailrep_api_key: SET_YOUR_API_KEY_HERE
  hunter_api_key: 4f3ee392e9dbd85db9de3c2e191db97b49665328
  intelx_api_key: SET_YOUR_API_KEY_HERE
  haveibeenpwned_api_key: SET_YOUR_API_KEY_HERE

settings:
  intelx_max_results: 20
"""
        with open(mosint_config_path, 'w') as f:
            f.write(mosint_config_content)

    # dnsenum
    if not shutil.which(DNSENUM_COMMAND):
        subprocess.run(['sudo', 'apt', 'install', '-y', 'dnsenum'])

def stream_command(cmd_list):
    def generate():
        process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            yield line
    return Response(generate(), mimetype='text/plain')

@app.route('/knock', methods=['POST'])
def knock():
    domain = request.json.get('domain')
    if not domain:
        return Response("Domain not provided", status=400)

    ensure_tools_installed()

    knock_process = subprocess.Popen(['python3', KNOCKPY_PATH, '-d', domain],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    knock_output, knock_error = knock_process.communicate()

    if knock_process.returncode != 0:
        return Response(f"Knockpy failed: {knock_error}", status=500)

    sublist3r_output_path = '/tmp/sublist3r_output.txt'
    sublist3r_process = subprocess.Popen(['python3', SUBLIST3R_PATH, '-d', domain, '-o', sublist3r_output_path],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    sublist3r_output, sublist3r_error = sublist3r_process.communicate()

    if sublist3r_process.returncode != 0:
        return Response(f"Sublist3r failed: {sublist3r_error}", status=500)

    return Response(sublist3r_output, mimetype='text/plain')

@app.route('/dnsenum', methods=['POST'])
def dnsenum():
    domain = request.json.get('domain')
    if not domain:
        return Response("Domain not provided", status=400)

    ensure_tools_installed()
    return stream_command([DNSENUM_COMMAND, domain])

@app.route('/mosint', methods=['POST'])
def mosint():
    email = request.json.get('email')
    if not email:
        return Response("Email not provided", status=400)

    ensure_tools_installed()
    return stream_command([MOSINT_BINARY_PATH, email])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
