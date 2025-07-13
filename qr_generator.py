from amzqr import amzqr
import os
from io import BytesIO
import udt
from tempfile import TemporaryDirectory
from typing import Tuple
from loguru import logger
from pathlib import Path

def get_filename(path:str) -> str:
    return Path(path).name

def generate_qr(
    payload: str,
    size: int,
    redundancy: udt.QRRedundancy,
    image: BytesIO | None,
    color: bool,
    contrast: float,
    brightness: float
) -> Tuple[BytesIO, str]:
    # Shuffle data to-and-fro the filesystem since the library expects files
    with TemporaryDirectory() as temp_dir:

        src_file_name:str | None = os.path.join(temp_dir,image.name) if image else None

        if src_file_name:
            logger.info(f"Copying file <{image.name}> to temp dir <{temp_dir}>")
            # Write uploaded image to temp file 
            with open(src_file_name, mode="wb+") as input_file_handle:
                image.seek(0)
                input_file_handle.write(image.read())
                input_file_handle.seek(0)

        _, __, output_path = amzqr.run(
            payload,
            version=size,
            level=redundancy,
            picture=src_file_name,
            colorized=color,
            contrast=contrast,
            brightness=brightness,
            save_name=None,
            save_dir=temp_dir
        )
        logger.info(f"QR Code written to <{output_path}>")

        with open(output_path, "rb") as output_file:
            filename: str = get_filename(output_path)
            output_file.seek(0)
            copy = BytesIO(output_file.read())
            copy.name = filename
            copy.seek(0)

            return (copy, filename)