"""Cropper factory and abstract base."""

from abc import ABC, abstractmethod


class BaseCropper(ABC):
    """Common interface for all cropper implementations."""

    @abstractmethod
    def crop_and_save_all(self, **kwargs) -> None:
        """Process all images and save cropped results."""


class ImageCropper:
    """Factory that creates the appropriate cropper."""

    @staticmethod
    def create(cropper_type: str, **kwargs) -> BaseCropper:
        from .boundary_cropper import BoundaryCropper
        from .smart_cropper import SmartCropper

        if cropper_type == "boundary-crop":
            return BoundaryCropper()
        elif cropper_type == "smart-crop":
            return SmartCropper(**kwargs)
        else:
            raise ValueError(f"Invalid cropper type: {cropper_type}")
