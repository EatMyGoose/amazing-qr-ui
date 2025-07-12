import streamlit as st
from qr_generator import generate_qr
import udf
from typing import get_args

def init_state(key: str, value: any) -> None:
    if key not in st.session_state:
        st.session_state[key] = value

init_state("text-payload", "")
init_state("select-redundancy", "M")
init_state("checkbox-colour", True)
init_state("slider-contrast", 1.0)
init_state("slider-brightness", 1.0)
init_state("checkbox-colour", True)
init_state("upload-image", None)
init_state("slider-size", 5)


payload = st.text_input("QR Payload", placeholder="QR Payload", key="text-payload")
size = st.slider("Size", min_value=1, max_value=20, key="slider-size")
redundancy = st.selectbox("Redundancy", options=get_args(udf.QRRedundancy), key="select-redundancy")
contrast = st.slider("Contrast", min_value=0.0, max_value=4.0, key="slider-contrast")
brightness = st.slider("Brightness", min_value=0.0, max_value=4.0, key="slider-brightness")
coloured =st.checkbox("Coloured", key="checkbox-colour")
image = st.file_uploader("Background Image", ["jpg", "png", "bmp", "gif"])

if image:
    qr_code = generate_qr(
        payload,
        size,
        redundancy,
        image,
        coloured,
        contrast,
        brightness
    )
    st.image(qr_code, caption="QR Preview", use_container_width=True)
    st.download_button("Download Image", qr_code, file_name=image.name)
