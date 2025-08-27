import streamlit as st
import os
from pathlib import Path

st.set_page_config(page_title="🌙 Deteksi Hilal - Debug Mode")

st.title("🌙 Deteksi Hilal - Debug Mode")

# Test imports
st.write("### Import Test:")

try:
    import pandas as pd
    st.success("✅ pandas imported successfully")
except Exception as e:
    st.error(f"❌ pandas error: {e}")

try:
    import numpy as np
    st.success("✅ numpy imported successfully")
except Exception as e:
    st.error(f"❌ numpy error: {e}")

try:
    import cv2
    st.success("✅ opencv imported successfully")
except Exception as e:
    st.error(f"❌ opencv error: {e}")

try:
    from ultralytics import YOLO
    st.success("✅ ultralytics imported successfully")
except Exception as e:
    st.error(f"❌ ultralytics error: {e}")

try:
    import requests
    st.success("✅ requests imported successfully")
except Exception as e:
    st.error(f"❌ requests error: {e}")

# Test file system
st.write("### File System Test:")
st.write(f"Current directory: {Path.cwd()}")
st.write(f"Files in directory: {list(Path('.').glob('*'))}")

# Test environment
st.write("### Environment Test:")
st.write(f"Python version: {st.session_state}")

# Simple functionality test
media_file = st.file_uploader("Test upload", type=["jpg", "png"])
if media_file:
    st.success(f"File uploaded: {media_file.name}")
    st.image(media_file, caption="Test image", use_column_width=True)