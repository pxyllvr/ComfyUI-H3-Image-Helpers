import torch
import comfy.utils

class H3RefsToImageBatch:
    """
    Converts Fantastic H3 Media Loader 'references' (H3_REFS) into a normal IMAGE batch.
    - Only accepts pictures (errors on any video or audio)
    - Fully dynamic: 0, 1, or many images all work
    - When empty, returns a tiny blank so the graph never crashes
    - Resizes all images to match the first image's size
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "references": ("H3_REFS",),
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
    CATEGORY = "conditioning/video_models"

    def convert(self, references, empty_behavior="blank", upscale_method="bilinear"):
        if not isinstance(references, dict):
            raise ValueError("Expected H3_REFS bundle from Fantastic H3 Media Loader")

        videos = references.get("videos") or []
        audios = references.get("audios") or []
        video_audios = [v for v in (references.get("video_audios") or []) if v is not None]

        if any(videos) or any(audios) or any(video_audios):
            raise ValueError(
                "H3RefsToImageBatch only accepts pure image references. "
                "Videos or audio were found in the Media Loader."
            )

        pictures = [p for p in (references.get("pictures") or []) if p is not None]
        count = len(pictures)

        if count == 0:
            if empty_behavior == "error":
                raise ValueError("No images in the Media Loader references")
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


NODE_CLASS_MAPPINGS = {"H3RefsToImageBatch": H3RefsToImageBatch}
NODE_DISPLAY_NAME_MAPPINGS = {"H3RefsToImageBatch": "H3 Refs → Image Batch"}
