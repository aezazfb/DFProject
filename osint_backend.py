from flask import Flask, request, Response
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

def stream_command(cmd_list):
    """
    This function streams the output of a subprocess command.
    It will return each line as it's generated.
    """
    def generate():
        process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            yield line
    return Response(generate(), mimetype='text/plain')

@app.route('/knock', methods=['POST'])
def knock():
    """
    Runs the knockpy tool for subdomain enumeration.
    Expects the domain as input.
    """
    domain = request.json.get('domain')
    if not domain:
        return Response("Domain not provided", status=400)
    return stream_command(['python3', '/home/kali/knock/knockpy.py', '-d', domain])

@app.route('/dnsenum', methods=['POST'])
def dnsenum():
    """
    Runs the dnsenum tool for DNS enumeration.
    Expects the domain as input.
    """
    domain = request.json.get('domain')
    if not domain:
        return Response("Domain not provided", status=400)
    return stream_command(['dnsenum', domain])

@app.route('/mosint', methods=['POST'])
def mosint():
    """
    Runs the Mosint tool for gathering email information.
    Expects the email as input.
    """
    email = request.json.get('email')
    if not email:
        return Response("Email not provided", status=400)
    
    # Call Mosint with the email as a positional argument (not a flag)
    return stream_command(['/home/kali/mosint/v3/mosint', email])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
