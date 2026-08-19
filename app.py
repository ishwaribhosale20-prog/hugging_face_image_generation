import os
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


# ==========================================
# LOAD ENVIRONMENT
# ==========================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="centered"
)


# ==========================================
# UI
# ==========================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        180deg,
        #eaf7ff 0%,
        #ffffff 55%,
        #ffffff 100%
    );
}

.main-title {
    text-align: center;
    color: #1976d2;
    font-size: 42px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #607d8b;
    font-size: 17px;
    margin-bottom: 30px;
}

.stTextArea textarea {
    background-color: white !important;
    color: #222 !important;
    border: 1px solid #90caf9 !important;
    border-radius: 12px !important;
    font-size: 16px !important;
}

.stButton > button {
    width: 100%;
    background-color: #42a5f5;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px;
    font-size: 18px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #1976d2;
    color: white;
}

.stDownloadButton > button {
    width: 100%;
    border-radius: 12px;
    font-size: 17px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# TITLE
# ==========================================

st.markdown(
    '<div class="main-title">🎨 AI Image Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Turn your imagination into a beautiful AI image</div>',
    unsafe_allow_html=True
)


# ==========================================
# CHECK TOKEN
# ==========================================

if not HF_TOKEN:

    st.error(
        "Hugging Face token not found. "
        "Please add HF_TOKEN to your .env file."
    )

    st.stop()


# ==========================================
# HUGGING FACE CLIENT
# ==========================================

client = InferenceClient(
    api_key=HF_TOKEN,
    provider="auto"
)


# ==========================================
# PROMPT
# ==========================================

prompt = st.text_area(
    "✍️ Enter your prompt",
    placeholder=(
        "Example: A beautiful bird flying across "
        "a golden sunset sky, detailed feathers, "
        "cinematic lighting, sharp focus"
    )
)


# ==========================================
# GENERATE IMAGE
# ==========================================

if st.button("✨ Generate Image"):

    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    final_prompt = (
        prompt.strip()
        + ", highly detailed, sharp focus, "
          "clear image, beautiful lighting, "
          "high quality, detailed textures"
    )

    with st.spinner("✨ Creating your image..."):

        try:

            image = client.text_to_image(
                prompt=final_prompt,
                model="black-forest-labs/FLUX.1-schnell"
            )

        except Exception as e:

            st.error(f"Image generation failed: {e}")
            st.stop()


    # ==========================================
    # SAVE
    # ==========================================

    os.makedirs("outputs", exist_ok=True)

    output_path = "outputs/generated_image.png"

    image.save(output_path)


    # ==========================================
    # DISPLAY
    # ==========================================

    st.success("✨ Image generated successfully!")

    st.image(
        image,
        caption="AI Generated Image",
        use_container_width=True
    )


    # ==========================================
    # DOWNLOAD
    # ==========================================

    image_bytes = BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    st.download_button(
        label="⬇️ Download Image",
        data=image_bytes,
        file_name="generated_image.png",
        mime="image/png"
    )