import sys
import time
import webview
import logging
import threading
from flask import Flask, request, render_template_string


# Suppress Flask logs and Flask CLI banner
logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
sys.modules['flask.cli'].show_server_banner = lambda *x: None

def solve_captcha(sitekey):
    global captcha_token
    captcha_token = None

    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Solve Captcha</title>
    <script src="https://js.hcaptcha.com/1/api.js?onload=onLoadCallback&render=explicit" async defer></script>
    <style>
        html, body {
            height: 100%;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
        }
    </style>
    <script type="text/javascript">
        var onLoadCallback = function() {
            hcaptcha.render('hcaptcha-widget', {
                'sitekey' : '{{ sitekey }}',
                'theme' : 'light',
                'callback' : onCaptchaSuccess
            });
        };

        var onCaptchaSuccess = function(token) {
            fetch("/captcha_solved?token=" + token)
                .then(response => {
                    if(response.ok) {
                        window.close(); // Close the window/tab
                    }
                });
        };
    </script>
</head>
<body>
    <div id="hcaptcha-widget"></div>
</body>
</html>
''', sitekey=sitekey)

    @app.route('/captcha_solved')
    def captcha_solved():
        global captcha_token
        captcha_token = request.args.get('token')
        return "Success", 200

    def run_flask_app():
        app.run(port=5000)

    def destroy(window):
        start_time = time.time()
        global captcha_token
        while not captcha_token:
            time.sleep(0.1)
            if time.time() - start_time > 15:  # 15 seconds timeout
                break
        window.destroy()

    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    # Create and start the webview window
    window = webview.create_window('Solve Captcha', 'http://127.0.0.1:5000', width=750, height=750)
    webview.start(destroy, window)

    return captcha_token
