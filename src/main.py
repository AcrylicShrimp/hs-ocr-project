import api
import base64
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, Response, abort, request
from glob import iglob
import itertools
import json
import os
from pathlib import Path
import preprocess

load_dotenv()

app = Flask(__name__)


@app.route('/api/version', methods=['GET'])
def version():
    return '0.0.3'


@app.route('/api/ocr-requests', methods=['POST'])
def newOCRRequest():
    if 'image' not in request.files:
        abort(400, Response('image file must be exist'))
        return

    if 'api' not in request.form:
        abort(400, Response('api field must be exist'))
        return

    api_type = request.form.get('api')

    if api_type not in ['naver', 'google']:
        abort(400, Response('api field should be naver or google'))
        return

    if 'type' not in request.form:
        abort(400, Response('type field must be exist'))
        return

    image_type = request.form.get('type')

    if image_type != 'png' and image_type != 'jpg':
        abort(400, Response('type field should be png or jpg'))
        return

    image, gray, binary, drawn, processed = preprocess.preprocess(
        request.files['image'].stream)

    # result = api.handle_api(api_type, image_type, processed)
    result = api.handle_api(api_type, image_type, image)

    timestamp = datetime.now().strftime('%Y-%m-%d %H-%M-%S.%f')
    path = 'tmp/{}'.format(timestamp)
    Path(path).mkdir(parents=True, exist_ok=True)

    with open(os.path.join(path, 'image.jpg'), 'wb') as file:
        file.write(image.getbuffer())
    with open(os.path.join(path, 'gray.jpg'), 'wb') as file:
        file.write(gray.getbuffer())
    if binary is not None:
        with open(os.path.join(path, 'binary.jpg'), 'wb') as file:
            file.write(binary.getbuffer())
    with open(os.path.join(path, 'drawn.jpg'), 'wb') as file:
        file.write(drawn.getbuffer())
    with open(os.path.join(path, 'processed.jpg'), 'wb') as file:
        file.write(processed.getbuffer())
    with open(os.path.join(path, 'result.txt'), 'w') as file:
        file.write(result)

    return {
        'result': result,
        'grayImage': 'data:image/jpeg;charset=utf-8;base64, {}'.format(base64.b64encode(gray.getvalue()).decode('utf-8')),
        'binaryImage': None if binary is None else 'data:image/jpeg;charset=utf-8;base64, {}'.format(base64.b64encode(binary.getvalue()).decode('utf-8')),
        'drawnImage': 'data:image/jpeg;charset=utf-8;base64, {}'.format(base64.b64encode(drawn.getvalue()).decode('utf-8')),
        'processedImage': 'data:image/jpeg;charset=utf-8;base64, {}'.format(base64.b64encode(processed.getvalue()).decode('utf-8')),
    }


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

        with open(os.path.join(directory, 'image.jpg'), 'rb') as image:
            image_binary = base64.b64encode(image.read()).decode('utf-8')

        with open(os.path.join(directory, 'gray.jpg'), 'rb') as gray:
            gray_binary = base64.b64encode(gray.read()).decode('utf-8')

        try:
            with open(os.path.join(directory, 'binary.jpg'), 'rb') as binary:
                binary_binary = base64.b64encode(binary.read()).decode('utf-8')
        except FileNotFoundError:
            binary_binary = None

        with open(os.path.join(directory, 'drawn.jpg'), 'rb') as drawn:
            drawn_binary = base64.b64encode(drawn.read()).decode('utf-8')

        with open(os.path.join(directory, 'processed.jpg'), 'rb') as processed:
            processed_binary = base64.b64encode(
                processed.read()).decode('utf-8')

        with open(os.path.join(directory, 'result.txt'), 'r') as result:
            result_text = json.loads(result.read())

        histories.append({
            'timestamp': timestamp.isoformat(),
            'image': 'data:image/jpeg;charset=utf-8;base64, {}'.format(image_binary),
            'grayImage': 'data:image/jpeg;charset=utf-8;base64, {}'.format(gray_binary),
            'binaryImage': None if binary_binary is None else 'data:image/jpeg;charset=utf-8;base64, {}'.format(binary_binary),
            'drawnImage': 'data:image/jpeg;charset=utf-8;base64, {}'.format(drawn_binary),
            'processedImage': 'data:image/jpeg;charset=utf-8;base64, {}'.format(processed_binary),
            'result': result_text
        })

    return {'histories': histories}


if __name__ == '__main__':
    app.run()
