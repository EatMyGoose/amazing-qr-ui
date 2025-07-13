from io import BytesIO
from PIL import Image
from typing import Callable
from loguru import logger

def remove_alpha(input: BytesIO) -> BytesIO:
    logger.info("[Operation] Removing Alpha")
    input.seek(0)
    src_image = Image.open(input)

    if not src_image.has_transparency_data:
        logger.info("Image has no alpha channel")
        return input
    
    # Sanitise alpha channel
    rgba_src_image = src_image.convert("RGBA")

    white_canvas = Image.new("RGBA", rgba_src_image.size, (255,255,255, 255))
    white_canvas.paste(rgba_src_image, (0,0), mask=rgba_src_image) 

    output_image_buffer = BytesIO()
    output_image_buffer.name = input.name
    white_canvas.save(output_image_buffer)
    output_image_buffer.seek(0)
    return output_image_buffer

def square_pad(input: BytesIO) -> BytesIO:
    logger.info("[Operation] Padding image")
    input.seek(0)
    src_image = Image.open(input)

    width, height = src_image.size
    larger_dimension = max(width, height)
    
    square_canvas = (
        Image.new('RGBA', (larger_dimension, larger_dimension), (255,255,255,0))
        if src_image.has_transparency_data else 
        Image.new('RGB', (larger_dimension, larger_dimension), (255,255,255))
    )

    square_canvas.paste(
        src_image,
        (
            int((larger_dimension - width) / 2),
            int((larger_dimension - height) / 2)
        )
    )

    output_image_buffer = BytesIO()
    output_image_buffer.name = input.name

    square_canvas.save(output_image_buffer)
    output_image_buffer.seek(0)
    return output_image_buffer

def preprocess_image(
    src_image: BytesIO, 
    maintain_aspect_ratio: bool,
    replace_alpha: bool
) -> BytesIO:
    pipeline: list[Callable[[BytesIO], BytesIO]] = []

    if maintain_aspect_ratio:
        pipeline.append(square_pad)
    
    if replace_alpha:
        pipeline.append(remove_alpha)

    if len(pipeline) == 0:
        # no pre-processing needed
        return src_image
    
    working_image = src_image
    for operation in pipeline:
        working_image = operation(working_image)

    return working_image






