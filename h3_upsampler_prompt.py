class H3UpsamplerPrompt:
    """
    Builds the correct P-H3-Image prompt-upsampler input string.
    - 0 images  → "Aspect ratio: ...\\nRequest: ..."
    - 1+ images → the full <|im_start|>user ... <Picture N> ... Edit <Picture 1>. ... format
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "image_count": ("INT", {"default": 0, "min": 0, "max": 16}),
            },
            "optional": {
                "aspect_ratio": ("STRING", {"default": "1:1",
                                             "tooltip": "Only used when image_count is 0"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("upsampler_input",)
    FUNCTION = "build"
    CATEGORY = "conditioning/video_models"

    def build(self, prompt, image_count, aspect_ratio="1:1"):
        prompt = (prompt or "").strip()

        if image_count <= 0:
            text = f"Aspect ratio: {aspect_ratio}\nRequest: {prompt}"
            return (text,)

        picture_blocks = []
        for i in range(1, image_count + 1):
            picture_blocks.append(
                f"<Picture {i}>: <|vision_start|><|image_pad|><|vision_end|>"
            )
        pictures_str = "".join(picture_blocks)

        text = (
            "<|im_start|>user\n"
            f"{pictures_str}Edit <Picture 1>. {prompt}\n"
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
            "<think>"
        )
        return (text,)


NODE_CLASS_MAPPINGS = {"H3UpsamplerPrompt": H3UpsamplerPrompt}
NODE_DISPLAY_NAME_MAPPINGS = {"H3UpsamplerPrompt": "H3 Upsampler Prompt"}
