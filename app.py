import streamlit as st
import requests

# --- Page Config ---
st.set_page_config(
    page_title="Clinical Transcription Pipeline",
    page_icon="🏥",
    layout="wide"
)

# --- Header ---
st.title("🏥 Clinical Transcription Pipeline")
st.markdown("Upload a clinical consultation audio file to generate a structured clinical note automatically.")
st.divider()

# --- File Upload ---
uploaded_file = st.file_uploader(
    "Upload Audio File",
    type=["mp3", "wav", "m4a", "ogg", "flac"],
    help="Supported formats: mp3, wav, m4a, ogg, flac"
)

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/mp3")

    if st.button("Generate Clinical Note", type="primary"):

        with st.spinner("Processing... this may take a moment"):

            # Send file to FastAPI backend
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/process-consultation",
                    files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                )

                if response.status_code == 200:
                    data = response.json()

                    st.success("Processing complete!")
                    st.divider()

                    # --- Section 1: Transcript ---
                    st.header("📝 Transcript")
                    st.text_area(
                        label="Full Transcript",
                        value=data["transcript"],
                        height=200,
                        disabled=True
                    )

                    st.divider()

                    # --- Section 2: Structured Clinical Note ---
                    st.header("🗂️ Structured Clinical Note")
                    note = data["structured_note"]

                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Patient Info")
                        st.write(note.get("patient_info") or "Not mentioned")

                        st.subheader("Chief Complaint")
                        st.write(note.get("chief_complaint") or "Not mentioned")

                        st.subheader("History of Present Illness")
                        st.write(note.get("history_present_illness") or "Not mentioned")

                        st.subheader("Past Medical History")
                        items = note.get("past_medical_history")
                        if items:
                            for item in items:
                                st.markdown(f"- {item}")
                        else:
                            st.write("None reported")

                        st.subheader("Medications")
                        items = note.get("medications")
                        if items:
                            for item in items:
                                st.markdown(f"- {item}")
                        else:
                            st.write("None reported")

                        st.subheader("Allergies")
                        items = note.get("allergies")
                        if items:
                            for item in items:
                                st.markdown(f"- {item}")
                        else:
                            st.write("None reported")

                    with col2:
                        st.subheader("Social History")
                        social = note.get("social_history")
                        if social:
                            for key, value in social.items():
                                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                        else:
                            st.write("Not mentioned")

                        st.subheader("Family History")
                        st.write(note.get("family_history") or "Not mentioned")

                        st.subheader("Review of Systems")
                        ros = note.get("review_of_systems")
                        if ros:
                            for key, value in ros.items():
                                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                        else:
                            st.write("Not mentioned")

                        st.subheader("Assessment")
                        st.write(note.get("assessment") or "Not mentioned")

                        st.subheader("Plan")
                        st.write(note.get("plan") or "Not mentioned")

                        st.subheader("Follow Up")
                        st.write(note.get("follow_up") or "Not mentioned")

                    st.divider()

                    # --- Section 3: Evidence Map ---
                    st.header("🔍 Evidence Map")
                    st.markdown("Each field below shows the exact quote from the transcript that supports the extracted information.")
                    evidence = note.get("evidence_map", {})
                    if evidence:
                        for field, quote in evidence.items():
                            st.markdown(f"**{field.replace('_', ' ').title()}:** _{quote}_")
                    else:
                        st.write("No evidence map available")

                    st.divider()

                    # --- Section 4: Validation ---
                    st.header("✅ Validation")
                    validation = data["validation"]
                    if validation["is_valid"]:
                        st.success("All extracted fields are grounded in the transcript.")
                    else:
                        st.warning("Some fields could not be fully verified:")
                        for issue in validation["issues"]:
                            st.markdown(f"- {issue}")

                else:
                    # Show error from FastAPI
                    error = response.json().get("detail", "Unknown error")
                    st.error(f"Error: {error}")

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Make sure the FastAPI server is running.")