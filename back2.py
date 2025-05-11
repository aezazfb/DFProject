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
    
    # Run knockpy first
    knock_process = subprocess.Popen(['python3', '/home/kali/knock/knockpy.py', '-d', domain], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    knock_output, knock_error = knock_process.communicate()
    
    if knock_process.returncode != 0:
        return Response(f"Knockpy failed: {knock_error}", status=500)
    
    # If Knockpy succeeded, run Sublist3r
    sublist3r_process = subprocess.Popen(['python3', '/home/kali/knock/Sublist3r/sublist3r.py', '-d', domain, '-o', '/tmp/sublist3r_output.txt'], 
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    sublist3r_output, sublist3r_error = sublist3r_process.communicate()
    
    if sublist3r_process.returncode != 0:
        return Response(f"Sublist3r failed: {sublist3r_error}", status=500)
    
    return Response(sublist3r_output, mimetype='text/plain')

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
