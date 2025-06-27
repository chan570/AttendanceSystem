# app.py

import streamlit as st
import zipfile
import os
import shutil
from face_utils import load_student_images, start_attendance
from location_utils import get_teacher_location
import pandas as pd

STUDENT_DIR = "student_data"

st.set_page_config(page_title="Face Attendance", layout="centered")
st.title("📷 Face Recognition Attendance System")

# Upload ZIP
uploaded_files = st.file_uploader(
    "Upload student images (you can select multiple)", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

if uploaded_files:
    if os.path.exists(STUDENT_DIR):
        shutil.rmtree(STUDENT_DIR)
    os.makedirs(STUDENT_DIR)

    for uploaded_file in uploaded_files:
        file_path = os.path.join(STUDENT_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    st.success(f"{len(uploaded_files)} image(s) uploaded.")

    with st.spinner("Encoding student faces..."):
        known_encodings, known_names = load_student_images(STUDENT_DIR)

    st.write(f"✅ {len(known_names)} student(s) loaded.")

    if st.button("🎥 Start Attendance"):
        teacher_location = get_teacher_location()
        if not teacher_location:
            st.error("Could not detect your location.")
        else:
            st.info(f"Detected teacher location: {teacher_location}")
            start_attendance(known_encodings, known_names, teacher_location)

    # Show attendance file if exists
    if os.path.exists("Attendance.csv"):
        df = pd.read_csv("Attendance.csv")
        st.subheader("📋 Attendance Recorded:")
        st.dataframe(df)

        st.download_button("📥 Download Attendance CSV", data=df.to_csv(index=False),
                           file_name="Attendance.csv", mime="text/csv")
