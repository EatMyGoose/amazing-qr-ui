import streamlit as st
from qr_generator import generate_qr
import udt
from typing import get_args
from image_preprocessor import preprocess_image

def init_state(key: str, value: any) -> None:
    if key not in st.session_state:
        st.session_state[key] = value

def set_state(key: str, value: any) -> None:
    st.session_state[key] = value

init_state("text-payload", "")
init_state("select-redundancy", "M")
init_state("checkbox-colour", True)
init_state("slider-contrast", 1.0)
init_state("slider-brightness", 1.0)
init_state("checkbox-colour", True)
init_state("checkbox-resize", True)
init_state("checkbox-remove-transparency", True)
init_state("upload-image", None)
init_state("slider-size", 5)

st.set_page_config(
    page_title="Pwetty QRs", 
    page_icon=":material/qr_code:", 
    layout="wide",
    menu_items={
        "About": "Tool to generate QR codes with background images  \nBased on [amazing-qr](https://github.com/x-hw/amazing-qr)"
    }
)

def reset_image_settings() -> None:
    set_state("checkbox-colour", True)
    set_state("slider-contrast", 1.0)
    set_state("slider-brightness", 1.0)
    set_state("checkbox-resize", True)
    set_state("checkbox-remove-transparency", True)


control_col, preview_col = st.columns(2, gap="medium")

with control_col:
    payload = st.text_input("QR Payload", placeholder="QR Payload", key="text-payload", help="Text embedded into the QR code (i.e. an URL)")
    size = st.slider("Size", min_value=1, max_value=20, key="slider-size", help="Size of the QR code - increase to capture more details in the background image")
    redundancy = st.selectbox("Redundancy", options=get_args(udt.QRRedundancy), key="select-redundancy", help="QR code redundancy factor - L(Lowest), H(highest)")

    image = st.file_uploader("Background Image", ["jpg", "png", "bmp", "gif"], help="Image used as the background of the QR code")

    no_image: bool = image is None
    coloured = st.checkbox("Coloured Output", key="checkbox-colour", disabled=no_image, help="Use color in QR code background image, disable for monochrome QR code")
    resize = st.checkbox("Automatically Resize", key="checkbox-resize", disabled=no_image, help="Automatically resize the image to maintain the original aspect ratio")
    replace_transparency = st.checkbox("Remove Transparency", key="checkbox-remove-transparency", disabled=no_image, help="Convert transparent pixels to white")
    contrast = st.slider("Contrast", min_value=0.0, max_value=4.0, key="slider-contrast", disabled=no_image, help="Contrast of the background image")
    brightness = st.slider("Brightness", min_value=0.0, max_value=4.0, key="slider-brightness", disabled=no_image, help="Brightness of the background image")
    st.button("Reset", on_click=reset_image_settings, use_container_width=True, key="button-reset", icon=":material/refresh:", disabled=no_image, help="Reset image settings back to default")

    input_image = (
        preprocess_image(image, resize, replace_transparency) 
        if (image is not None) 
        else image
    )

    qr_code, qr_code_filename = generate_qr(
        payload,
        size,
        redundancy,
        input_image,
        coloured,
        contrast,
        brightness
    )

with preview_col:
    st.download_button("Download QR Code", qr_code, file_name=qr_code_filename, use_container_width=True, icon=":material/download:", help="Download QR code")
    st.image(qr_code, caption="QR Preview", use_container_width=True)
