import torch
import math

class H3ResolutionSelector:
    """
    Resolution selector with optional override from image_1.
    When 'use_image_size' is True and an image is connected, the image's
    aspect ratio is used but dimensions are still scaled to the chosen megapixels.
    Otherwise calculates from the selected aspect ratio + megapixels.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "aspect_ratio": ([
                    "1:1", "4:3", "3:2", "16:9", "21:9",
                    "3:4", "2:3", "9:16", "9:21"
                ], {"default": "1:1"}),
                "megapixels": ("FLOAT", {"default": 1.0, "min": 0.25, "max": 16.0, "step": 0.1}),
                "multiple": ("INT", {"default": 32, "min": 1, "max": 256, "step": 1,
                                     "tooltip": "Align width and height to this multiple"}),
                "use_image_size": ("BOOLEAN", {"default": False,
                                               "tooltip": "Use image_1 aspect ratio (still scales to megapixels)"}),
            },
            "optional": {
                "image_1": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "select"
    CATEGORY = "conditioning/video_models"

    def select(self, aspect_ratio, megapixels, multiple, use_image_size, image_1=None):
        if use_image_size and image_1 is not None:
            h = float(image_1.shape[1])
            w = float(image_1.shape[2])
            ar_w, ar_h = w, h
        else:
            try:
                ar_w, ar_h = map(float, aspect_ratio.split(":"))
            except Exception:
                ar_w, ar_h = 1.0, 1.0

        target_pixels = megapixels * 1_000_000
        ratio = ar_w / ar_h
        h = math.sqrt(target_pixels / ratio)
        w = h * ratio

        w = max(multiple, int(round(w / multiple)) * multiple)
        h = max(multiple, int(round(h / multiple)) * multiple)

        return (w, h)


NODE_CLASS_MAPPINGS = {"H3ResolutionSelector": H3ResolutionSelector}
NODE_DISPLAY_NAME_MAPPINGS = {"H3ResolutionSelector": "H3 Resolution Selector"}
