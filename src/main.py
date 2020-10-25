import base64
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, Response, abort, request
from glob import iglob
import itertools
import json
import requests
import os
from pathlib import Path

load_dotenv()

NAVER_OCR_URL = os.getenv('NAVER_OCR_URL')
NAVER_OCR_SECRET = os.getenv('NAVER_OCR_SECRET')

app = Flask(__name__)


@app.route('/api/version', methods=['GET'])
def version():
    return '0.0.2'


@app.route('/api/ocr-requests', methods=['POST'])
def newOCRRequest():
    if 'image' not in request.files:
        abort(400, Response('image file must be exist'))
        return

    if 'type' not in request.form:
        abort(400, Response('type field must be exist'))
        return

    image_type = request.form.get('type')

    if image_type != 'png' and image_type != 'jpg':
        abort(400, Response('type field should be png or jpg'))
        return

    result = requests.post('https://{}/infer'.format(NAVER_OCR_URL), headers={
        'X-OCR-SECRET': NAVER_OCR_SECRET
    }, files={
        'file': request.files['image'].stream
    }, data={
        'message': json.dumps({
            'version': 'V2',
            'requestId': 'ocr-request',
            'timestamp': 0,
            'images': [{
                'format': image_type,
                'name': 'image',
                'templateIds': ['4567', '4568']
            }]
        })
    }).text

    timestamp = datetime.now().strftime('%Y-%m-%d %H-%M-%S.%f')
    path = 'tmp/{}'.format(timestamp)
    Path(path).mkdir(parents=True, exist_ok=True)

    request.files['image'].stream.seek(0)
    request.files['image'].save(os.path.join(
        path, 'image.{}'.format(image_type)))

    with open(os.path.join(path, 'result.txt'), 'w') as file:
        file.write(result)

    return result


@app.route('/api/ocr-requests/histories', methods=['GET'])
def getOCRRequestHistory():
    page = request.args.get('page', '0')

    try:
        page = int(page)
    except:
        abort(400, Response('page query param should be a integer'))

    if page < 0:
        abort(400, Response('page query param should be positive'))

    directories = [x for x in itertools.islice(
        iglob('tmp/*'), 10 * page, None) if os.path.isdir(x)]

    histories = []

    for directory in directories:
        _, timestamp = os.path.split(directory)
        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H-%M-%S.%f')

        print(timestamp)

        if os.path.isfile(os.path.join(directory, 'image.png')):
            image_type = 'png'
            image_type_mime = 'png'
        else:
            image_type = 'jpg'
            image_type_mime = 'jpeg'

        with open(os.path.join(directory, 'image.{}'.format(image_type)), 'rb') as image:
            image_binary = base64.b64encode(image.read()).decode('utf-8')

        with open(os.path.join(directory, 'result.txt'), 'r') as result:
            result_text = json.loads(result.read())

        histories.append({
            'timestamp': timestamp.isoformat(),
            'image': 'data:image/{};charset=utf-8;base64, {}'.format(image_type_mime, image_binary),
            'result': result_text
        })

    return {'histories': histories}


if __name__ == '__main__':
    app.run()
