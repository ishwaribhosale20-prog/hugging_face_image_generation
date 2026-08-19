import os
import uuid
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from supabase import create_client, Client


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="centered"
)


# ============================================================
# UI STYLE
# ============================================================

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


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🎨 AI Image Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Turn your imagination into a beautiful AI image</div>',
    unsafe_allow_html=True
)


# ============================================================
# CHECK ENVIRONMENT
# ============================================================

if not HF_TOKEN:
    st.error("Hugging Face token is missing. Please add HF_TOKEN to .env.")
    st.stop()

if not SUPABASE_URL:
    st.error("Supabase URL is missing. Please add SUPABASE_URL to .env.")
    st.stop()

if not SUPABASE_KEY:
    st.error("Supabase key is missing. Please add SUPABASE_KEY to .env.")
    st.stop()


# ============================================================
# CLIENTS
# ============================================================

@st.cache_resource
def get_huggingface_client():
    return InferenceClient(
        api_key=HF_TOKEN,
        provider="auto"
    )


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


hf_client = get_huggingface_client()
supabase = get_supabase_client()


# ============================================================
# PROMPT
# ============================================================

prompt = st.text_area(
    "✍️ Enter your prompt",
    placeholder=(
        "Example: A beautiful garden with children playing "
        "under warm golden sunlight, realistic, sharp focus"
    ),
    height=130
)


# ============================================================
# GENERATE IMAGE
# ============================================================

if st.button("✨ Generate Image"):

    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    final_prompt = (
        prompt.strip()
        + ", highly detailed, sharp focus, clear image, "
          "beautiful lighting, detailed textures, high quality"
    )

    try:

        # ----------------------------------------------------
        # Generate image using Hugging Face
        # ----------------------------------------------------

        with st.spinner("✨ Creating your image..."):

            image = hf_client.text_to_image(
                prompt=final_prompt,
                model="black-forest-labs/FLUX.1-schnell"
            )


        # ----------------------------------------------------
        # Convert image to bytes
        # ----------------------------------------------------

        image_bytes = BytesIO()

        image.save(
            image_bytes,
            format="PNG"
        )

        image_bytes.seek(0)

        image_data = image_bytes.getvalue()


        # ----------------------------------------------------
        # Create unique filename
        # ----------------------------------------------------

        image_id = str(uuid.uuid4())

        file_name = f"{image_id}.png"

        storage_path = f"generated-images/{file_name}"


        # ----------------------------------------------------
        # Upload image to Supabase Storage
        # ----------------------------------------------------

        with st.spinner("☁️ Saving image..."):

            supabase.storage.from_(
                "generated-images"
            ).upload(
                path=storage_path,
                file=image_data,
                file_options={
                    "content-type": "image/png",
                    "upsert": "false"
                }
            )


        # ----------------------------------------------------
        # Get public image URL
        # ----------------------------------------------------

        image_url = supabase.storage.from_(
            "generated-images"
        ).get_public_url(storage_path)


        # ----------------------------------------------------
        # Save generation information to database
        # ----------------------------------------------------

        supabase.table("generations").insert({
            "prompt": prompt.strip(),
            "image_url": image_url
        }).execute()


        # ----------------------------------------------------
        # Display image
        # ----------------------------------------------------

        st.success("✨ Image generated successfully!")

        st.image(
            image,
            caption="AI Generated Image",
            use_container_width=True
        )


        # ----------------------------------------------------
        # Download
        # ----------------------------------------------------

        st.download_button(
            label="⬇️ Download Image",
            data=image_data,
            file_name="generated_image.png",
            mime="image/png"
        )


    except Exception as e:

        st.error(
            "Something went wrong while generating or saving the image."
        )

        st.exception(e)