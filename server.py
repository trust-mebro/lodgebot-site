from flask import Flask, jsonify, send_from_directory
import subprocess
import time
import os

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'upload.html')

@app.route('/run-adb')
def run_adb():
    try:
        log = []

        def run(cmd, wait=0):
            log.append(f"> {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            log.append(result.stdout or result.stderr)
            if wait > 0:
                time.sleep(wait)

        run("adb shell monkey -p com.adobe.scan.android -c android.intent.category.LAUNCHER 1", wait=10)
        run("adb shell input tap 520 2276", wait=10)
        run("adb shell input tap 520 2276", wait=10)
        run("adb shell input tap 520 2276", wait=10)
        run("adb shell input tap 520 2276", wait=10)
        run("adb shell input tap 882 2270", wait=10)
        run("adb shell input tap 679 1047", wait=5)
        run("adb shell input tap 348 604", wait=5)
        run("adb shell input tap 934 2283", wait=5)
        run(r'adb pull "/storage/emulated/0/Documents/Adobe Scan 16 Jul 2025.pdf" "D:\python\project\project_website\lodgebot-site"', wait=1)
        project_path = r"D:\python\project\project_website\lodgebot-site"
        trinity_cmd = "python trinity.py"

        log.append(f"\n> cd {project_path}")
        os.chdir(project_path)

        log.append(f"> {trinity_cmd}")
        result = subprocess.run(trinity_cmd, shell=True, capture_output=True, text=True)
        log.append(result.stdout or result.stderr)

        # IMPORTANT: update the destination folder as needed
        

        return jsonify({"output": "\n".join(log)})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
