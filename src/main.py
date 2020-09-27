from dotenv import load_dotenv
from flask import Flask, Response, abort, request
import json
import requests
import os

load_dotenv()

NAVER_OCR_URL = os.getenv('NAVER_OCR_URL')
NAVER_OCR_SECRET = os.getenv('NAVER_OCR_SECRET')

app = Flask(__name__)


@app.route('/api/version', methods=['GET'])
def version():
    return '0.0.1'


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

    return requests.post('https://{}/infer'.format(NAVER_OCR_URL), headers={
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


if __name__ == '__main__':
    app.run()
