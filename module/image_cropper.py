import cv2
from PIL import Image


class ImageCropper:
    def __init__(self):
        self.image_path = None
        self.image = None

    def get_character_bounding_box(self) -> tuple:
        # convert image to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # apply Otsu's thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # find contours in the thresholded image
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # get the minimum bounding rectangle for the largest contour
        cnt = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(cnt)

        return x, y, w, h

    def crop_and_save(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(self.image_path)
        x, y, w, h = self.get_character_bounding_box()
        img = Image.open(self.image_path)
        img = img.crop((x, y, x + w, y + h))
        img.save(self.image_path)
