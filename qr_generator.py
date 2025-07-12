from amzqr import amzqr
import os
from io import FileIO, BytesIO
import udf
from tempfile import TemporaryDirectory

def generate_qr(
    payload: str,
    size: int,
    redundancy: udf.QRRedundancy,
    image: FileIO,
    color: bool,
    contrast: float,
    brightness: float
) -> BytesIO:
    # Shuffle data to-and-fro the filesystem since the library expects files
    with TemporaryDirectory() as temp_dir:
        # Write uploaded image to temp file 
        src_file_name:str = os.path.join(temp_dir,image.name)
        with open(src_file_name, mode="wb+") as input_file_handle:
            image.seek(0)
            input_file_handle.write(image.read())
            input_file_handle.seek(0)

        _, __, output_filename = amzqr.run(
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

        with open(os.path.join(temp_dir, output_filename), "rb") as output_file:
            output_file.seek(0)
            copy = BytesIO(output_file.read())
            copy.seek(0)

            return copy