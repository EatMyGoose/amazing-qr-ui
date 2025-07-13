from io import BytesIO
from PIL import Image, ImageSequence
from typing import Callable
from loguru import logger
import os

def get_lowercase_extension(path: str) -> str:
    _, ext = os.path.splitext(path)
    return ext.lower()

def has_gif_extension(path: str) -> str:
    return  get_lowercase_extension(path) == ".gif"

def remove_alpha(src_image: Image) -> Image:
    logger.info("[Operation] Removing Alpha")

    if not src_image.has_transparency_data:
        logger.info("Image has no alpha channel")
        return src_image
    
    # Sanitise alpha channel
    rgba_src_image = src_image.convert("RGBA")

    white_canvas = Image.new("RGBA", rgba_src_image.size, (255,255,255, 255))
    white_canvas.paste(rgba_src_image, (0,0), mask=rgba_src_image) 

    return white_canvas

def square_pad(src_image: Image) -> BytesIO:
    logger.info("[Operation] Padding image")

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

    return square_canvas

def preprocess_gif(
    src_image: Image.Image,
    frame_pipeline: list[Callable[[BytesIO], BytesIO]],    
    output_image_name: str
) -> BytesIO:
    processed_frames = ImageSequence.all_frames(
        src_image,
        frame_pipeline
    )

    frame_interval_ms = src_image.info.get("duration")
    gif_image_buffer = BytesIO()
    gif_image_buffer.name = output_image_name
    processed_frames[0].save(gif_image_buffer, save_all=True, append_images=processed_frames[1:], duration=frame_interval_ms, loop=0)
    gif_image_buffer.seek(0)
    return gif_image_buffer

def preprocess_image(
    src_image_buffer: BytesIO, 
    maintain_aspect_ratio: bool,
    replace_alpha: bool
) -> BytesIO:
    pipeline: list[Callable[[Image.Image], Image.Image]] = []

    if maintain_aspect_ratio:
        pipeline.append(square_pad)
    
    if replace_alpha:
        pipeline.append(remove_alpha)

    if len(pipeline) == 0:
        # no pre-processing needed
        return src_image_buffer
    
    src_image = Image.open(src_image_buffer)

    def image_pipeline(working_image: Image.Image) -> Image.Image:
        for operation in pipeline:
            working_image = operation(working_image)
        return working_image

    is_gif_image: bool = has_gif_extension(src_image_buffer.name)
    logger.info(f"<{src_image_buffer.name}>, is_gif_image: <{is_gif_image}>")

    if is_gif_image:
        return preprocess_gif(src_image, image_pipeline, src_image_buffer.name)
    else:
        processed_image = image_pipeline(src_image)
        
        processed_image_buffer = BytesIO()
        processed_image_buffer.name = src_image_buffer.name

        processed_image.save(processed_image_buffer)

        processed_image_buffer.seek(0)
        return processed_image_buffer

def get_gif_frame_interval_ms(image_buffer: BytesIO | None) -> int | None:
    if image_buffer is None or not has_gif_extension(image_buffer.name):
        return None
    else:
        loaded_gif = Image.open(image_buffer)
        interval_ms = loaded_gif.info.get("duration")
        logger.info(f"<{image_buffer}> - frame interval(ms) = <{interval_ms}>")
        return interval_ms

def add_frame_interval_and_loop_to_gif(
    image_buffer: BytesIO, 
    frame_interval_ms: int) -> BytesIO:

    logger.info(f"Adding frame interval of <{frame_interval_ms}ms> to <{image_buffer.name}> ")    

    loaded_gif = Image.open(image_buffer)
    gif_frames = ImageSequence.all_frames(loaded_gif)

    gif_image_buffer = BytesIO()
    gif_image_buffer.name = image_buffer.name
    gif_frames[0].save(gif_image_buffer, save_all=True, append_images=gif_frames[1:], duration=frame_interval_ms, loop=0)
    gif_image_buffer.seek(0)
    return gif_image_buffer
        
    

