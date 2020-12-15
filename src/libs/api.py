
from google.cloud import vision
import json
import os
import requests


def naver_api(image_type, image_stream):
    naver_ocr_url = os.environ['NAVER_OCR_URL']
    naver_ocr_secret = os.environ['NAVER_OCR_SECRET']

    result = json.loads(requests.post('https://{}/general'.format(naver_ocr_url), headers={
        'X-OCR-SECRET': naver_ocr_secret
    }, files={
        'file': image_stream
    }, data={
        'message': json.dumps({
            'version': 'V2',
            'requestId': 'ocr-request',
            'timestamp': 0,
            'images': [{
                'format': image_type,
                'name': 'image'
            }]
        })
    }).text)

    return json.dumps({
        'texts': list(map(lambda field: {
            'text': field['inferText'],
            'confidence': field['inferConfidence']
        }, result['images'][0]['fields']))
    })


def google_api(image_type, image_stream):
    client = vision.ImageAnnotatorClient()
    result = client.document_text_detection(
        image=vision.Image(content=image_stream.read()))

    texts = [{
        'text': result.full_text_annotation.text,
        'confidence': sum(map(lambda page: page.confidence, result.full_text_annotation.pages)) / float(len(result.full_text_annotation.pages))
    }]

    return json.dumps({
        'texts': texts
    })


API_DICT = {
    'naver': naver_api,
    'google': google_api
}


def handle_api(api, image_type, image_stream):
    return API_DICT[api](image_type, image_stream)
