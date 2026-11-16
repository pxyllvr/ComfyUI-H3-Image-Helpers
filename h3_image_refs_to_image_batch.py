import torch
import comfy.utils

class H3ImageRefsToImageBatch:
    """
    Converts MiniMax-H3-Image Media Loader 'references' (H3_IMAGE_REFS)
    into a normal IMAGE batch.
    - Image-only (the new loader never emits video/audio)
    - Filters out the None padding slots
    - Fully dynamic: 0–16 images
    - Resizes all images to match the first image's size
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "references": ("H3_IMAGE_REFS",),
            },
            "optional": {
                "empty_behavior": (["blank", "error"], {"default": "blank",
                                                         "tooltip": "What to do when no images are present"}),
                "upscale_method": (["bilinear", "bicubic", "nearest", "area", "lanczos"],
                                   {"default": "bilinear"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "count")
    FUNCTION = "convert"
    CATEGORY = "conditioning/image_models"

    def convert(self, references, empty_behavior="blank", upscale_method="bilinear"):
        if not isinstance(references, dict):
            raise ValueError("Expected H3_IMAGE_REFS bundle from H3-Image Media Loader")

        raw_pictures = references.get("pictures") or []
        pictures = [p for p in raw_pictures if p is not None]
        count = len(pictures)

        if count == 0:
            if empty_behavior == "error":
                raise ValueError("No images in the H3-Image Media Loader references")
            blank = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            return (blank, 0)

        target_h = pictures[0].shape[1]
        target_w = pictures[0].shape[2]

        resized = []
        for img in pictures:
            if img.shape[1] == target_h and img.shape[2] == target_w:
                resized.append(img)
                continue
            up = comfy.utils.common_upscale(
                img.movedim(-1, 1),
                target_w,
                target_h,
                upscale_method,
                "center"
            )
            resized.append(up.movedim(1, -1))

        batch = torch.cat(resized, dim=0)
        return (batch, count)


NODE_CLASS_MAPPINGS = {"H3ImageRefsToImageBatch": H3ImageRefsToImageBatch}
NODE_DISPLAY_NAME_MAPPINGS = {"H3ImageRefsToImageBatch": "H3 Image Refs → Image Batch"}
