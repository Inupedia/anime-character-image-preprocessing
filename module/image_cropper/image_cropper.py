from typing import Union

from .boundary_cropper import BoundaryCropper
from .smart_cropper import SmartCropper


class ImageCropper:
    def __init__(self, cropper_type: str):
        self.cropper_type = cropper_type

    def create_cropper(self) -> Union[BoundaryCropper, SmartCropper]:
        if self.cropper_type == "boundary-crop":
            return BoundaryCropper()
        elif self.cropper_type == "smart-crop":
            return SmartCropper()
        else:
            raise ValueError(f"Invalid cropper type: {self.cropper_type}")
