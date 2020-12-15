
import cv2
import imutils
import io
import numpy as np


def preprocess(img):
    image = cv2.imdecode(np.frombuffer(
        img.read(), dtype=np.uint8), cv2.IMREAD_COLOR)
    image = apply_resize(image, 2048)
    (processed, gray, binary, drawn) = apply_skew_correction(image)

    gray = apply_resize(gray, 512)

    if binary is not None:
        binary = apply_resize(binary, 512)

    drawn = apply_resize(drawn, 512)

    return (
        io.BytesIO(cv2.imencode('.jpg', image)[1]),
        io.BytesIO(cv2.imencode('.jpg', gray)[1]),
        None if binary is None else io.BytesIO(
            cv2.imencode('.jpg', binary)[1]),
        io.BytesIO(cv2.imencode('.jpg', drawn)[1]),
        io.BytesIO(cv2.imencode('.jpg', processed)[1])
    )


def apply_resize(image, max_size):
    height, width = image.shape[:2]

    if max(height, width) < max_size:
        return image

    return imutils.resize(image, width=max_size) if height < width else imutils.resize(image, height=max_size)


def apply_binarization(blurred_gray):
    _, result = cv2.threshold(blurred_gray, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return result


def apply_skew_correction(img):
    height, width = img.shape[:2]
    blur_size = max(width, height)
    blur_size = int(blur_size * 0.001)

    if (blur_size < 11):
        blur_size = 11

    if blur_size % 2 == 0:
        blur_size += 1

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)

    def apply(image, original_image):
        edge = cv2.Canny(image, 50, 100)
        contours = cv2.findContours(
            edge.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0 if imutils.is_cv2(
        ) else 0 if imutils.is_cv4() else 1]

        cloned_image = original_image.copy()
        cv2.drawContours(cloned_image, contours, -1, (0, 255, 0), 8)

        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        area = None

        for contour in contours:
            approx = cv2.approxPolyDP(
                contour, 0.02 * cv2.arcLength(contour, True), True)

            if len(approx) == 4:
                area = approx
                break

        if area is None:
            return (None, cloned_image)

        cv2.drawContours(cloned_image, [area], -1, (255, 0, 0), 8)

        points = np.array(area.reshape(4, 2))
        rect = np.zeros((4, 2), dtype=np.float32)

        summed = points.sum(axis=1)
        rect[0] = points[np.argmin(summed)]
        rect[2] = points[np.argmax(summed)]

        diff = np.diff(points, axis=1)
        rect[1] = points[np.argmin(diff)]
        rect[3] = points[np.argmax(diff)]

        (tl, tr, br, bl) = rect

        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(width_a), int(width_b))

        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(height_a), int(height_b))

        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]
        ], dtype=np.float32)
        mat = cv2.getPerspectiveTransform(rect, dst)
        original_image = cv2.warpPerspective(
            original_image, mat, (max_width, max_height))

        return (original_image, cloned_image)

    binary = None
    result, drawn = apply(gray, img)

    if result is None:
        binary = apply_binarization(gray)
        result, drawn = apply(binary, img)

    return (img if result is None else result, gray, binary, drawn)
