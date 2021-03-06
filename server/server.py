# USAGE
# python server.py

import cv2
from flask import Flask
from flask import Response
from flask import render_template
from flask import request, session, send_file
import json
from io import BytesIO
from datetime import datetime
from get_gestures_from_webcam import get_gestures_from_webcam as gestures
from scripts import questions as qs
from scripts import queries as qr
from scripts import statistics as st

app = Flask(__name__)

app.secret_key = '5b7373780e35434090c87dc4c9d15a2d'


def serve_streams(recording_start_time):
    camera = cv2.VideoCapture(0)
    yield from gestures.get_gestures(camera, recording_start_time)
    gestures.save_data()
    camera.release()


@app.route("/")
def index():
    session['startTime'] = datetime.now()
    return render_template("index.html")


@app.route("/statistics")
def statistics():
    binary_image = st.getGestures(session['startTime'])
    img_io = BytesIO()
    rgb_im = binary_image.convert('RGB')
    rgb_im.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(
        img_io,
        mimetype='image/jpeg',
        as_attachment=False,
        attachment_filename='statistics.jpeg')


@app.route("/video_feed")
def video_feed():
    recording_start_time = datetime.now()
    return Response(serve_streams(recording_start_time),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/questions", methods=['GET', 'POST'])
def questions():
    # gestures.save_data()
    if request.method == 'GET':
        return qs.create_question_game()
    else:
        # gestures.save_data()
        user_answers = qs.get_correct_answers(request.form.getlist('answersTime[]'))
        return json.dumps({'status': 'OK', 'results': user_answers})


@app.route('/check_wave')
def check_wave():
    gestures.save_data()
    close_camera = qr.check_close_camera(datetime.now())
    return json.dumps({'closeCamera': close_camera})


@app.route('/do_close_camera', methods=['POST'])
def do_close_camera():
    print("do close {}".format(request.form.get('do_close_camera')))
    if request.form.get('do_close_camera') == "true":
        gestures.set_record(False)
    elif request.form.get('do_close_camera') == "false":
        gestures.set_record(True)

    return json.dumps({'response': "ok"})


if __name__ == '__main__':
    app.run(port=80, debug=True,
            threaded=True, use_reloader=False)
