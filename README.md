# H3 Image Helpers

Small utility nodes for MiniMax H3 / MiniMax-H3-Image / P-H3-Image workflows in ComfyUI.

These nodes help convert reference bundles into standard IMAGE batches, build dynamic upsampler prompts, and handle resolution selection without manual tweaking.

## Nodes

### H3 Refs → Image Batch
Converts the `references` output (`H3_REFS`) from the Fantastic H3 Media Loader into a normal IMAGE batch.

- Image-only (errors if videos or audio are present)
- Handles 0 images gracefully (returns a tiny blank + count=0)
- Resizes all images to match the first image’s size
- Returns the batch and an image count

### H3 Image Refs → Image Batch
Same idea as above, but for the MiniMax-H3-Image Media Loader (`H3_IMAGE_REFS`).

- Filters out the None padding slots
- Supports up to 16 images
- Same resize-to-first and empty-handling behavior

### H3 Upsampler Prompt
Builds the correct prompt-upsampler input string based on image count.

- **0 images** → `Aspect ratio: ...\nRequest: ...` (txt2img style)
- **1+ images** → the full `<|im_start|>user` + `<Picture N>` blocks + `Edit <Picture 1>.` format

Wire the `count` output from either of the batch nodes into this node’s `image_count` input.

### H3 Resolution Selector
Resolution calculator with an optional override from `image_1`.

- Calculates width/height from aspect ratio + megapixels (aligned to a multiple, default 32)
- When `use_image_size` is enabled, it takes the aspect ratio from the connected image but still scales the final dimensions to the chosen megapixels target

## Installation

1. Clone or download this repository into your `ComfyUI/custom_nodes/` folder:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/pxyllvr/H3ImageHelpers.git
   ```
2. Restart ComfyUI.

No extra dependencies beyond a normal ComfyUI install.

## Usage notes

- The two “Refs → Image Batch” nodes are intentionally separate because the Media Loaders use different custom types (`H3_REFS` vs `H3_IMAGE_REFS`).
- Both batch nodes resize references to the first image so downstream nodes see a consistent batch.
- The upsampler node is mainly useful with P-H3-Image workflows where the upsampler input text must change depending on whether you’re doing text-to-image or an edit.
- The resolution selector is handy for keeping megapixel targets consistent while still matching an edit source’s aspect ratio.

## Credits

Utility nodes built around the Fantastic H3 Media Loader (Adudeguyman) and the MiniMax-H3-Image Media Loader. Inspired by the official P-H3-Image and MiniMax-H3-Image workflows.
