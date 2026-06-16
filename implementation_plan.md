# Lecture Voice-to-Notes Generator - Implementation Plan

The goal is to design and build a professional-grade, highly interactive, and visually stunning Streamlit application titled **'Lecture Voice-to-Notes Generator'**. It will enable students to convert lecture audio into text, generate structured notes, summaries, interactive quizzes, and interactive flipping flashcards. It will also support personal note-taking, tagging, and advanced searching/highlighting.

## User Review Required

> [!IMPORTANT]
> **API Key Configuration:** The app will require a Gemini API key. We will provide a secure input field in the sidebar for users to enter their Gemini API key, and will also look for an environment variable (`GEMINI_API_KEY`) as a fallback.
> 
> **Audio Processing:** We will leverage Gemini 1.5 Flash's native capability to ingest audio files directly. This enables highly accurate transcription, summarization, and concept extraction without needing third-party speech-to-text API keys (like AssemblyAI or OpenAI Whisper).
> 
> **Live Audio Recording:** The app will feature a microphone recorder inside Streamlit (using `audio-recorder-streamlit` which is already installed in your environment) as well as file upload (MP3, WAV, M4A) for robustness.

## Open Questions

- *Are there any specific sample audio files you want pre-loaded for demo purposes, or is live recording and upload sufficient?* (By default, we will provide a clear uploading UI and guide the user on how to try it).

---

## Proposed Changes

### Streamlit Web Application

We will build the entire application in a single well-structured file `app.py` or separate modular files if logic grows large. A single file is highly standard and maintainable for Streamlit apps of this scale, supplemented by custom assets or helper functions.

#### [NEW] [app.py](file:///c:/Users/mdama/Desktop/ai%20intern/app.py)
This file will contain:
1. **Config & Styling Setup:** Custom styling using Google Fonts (Poppins, Inter), rich gradient banners, custom card containers, 3D flip-card CSS, and micro-animations.
2. **State Management:** Utilizing `st.session_state` to persist transcriptions, generated notes, quizzes, flashcards, user scores, tagging state, and personal notes across page reruns.
3. **Sidebar Controls:** API Key input, model settings, quick instructions, and option to load a demo lecture.
4. **Audio Transcription Module:**
   - Drag & drop uploader supporting `.mp3`, `.wav`, `.m4a`, `.ogg`.
   - Live recording using `audio-recorder-streamlit`.
   - Integration with Gemini API to transcribe and store the text.
5. **AI Generator Engine:**
   - **Notes Generator:** Generates a structured markdown output with summary, key definitions, detailed explanations, and key takeaways.
   - **Interactive Quiz Generator:** Generates 5 Multiple Choice Questions (MCQs) in JSON format. We will parse it and render it as an interactive quiz where the student can select answers, click "Submit Quiz", and get visual green/red feedback for correctness with detailed explanations.
   - **Flashcard Deck Generator:** Generates key-value terms/definitions. We will render them as interactive 3D HTML cards that flip around (front-to-back) when clicked, utilizing CSS keyframe transforms.
6. **Student Interaction Utilities:**
   - **Personal Notes Side-Editor:** Alongside the transcript, students can write, edit, and save their own thoughts.
   - **Crucial Points Tagging:** Automatically tag sections by keywords or allow custom tags.
   - **Search & Highlighting Engine:** A global search input that scans the transcript, AI notes, and personal notes, displaying matching occurrences with visual `<mark>` tags.

---

## Verification Plan

### Manual Verification
1. **Launch Streamlit:** Run `streamlit run app.py` and access it in the browser.
2. **Test Audio Recording:** Click the microphone, record a brief sample lecture, and confirm it successfully uploads and transcribes.
3. **Test File Upload:** Upload a sample MP3/WAV file.
4. **Verify Generation:**
   - Confirm study notes are formatted nicely.
   - Test the interactive quiz (submit answers and check the visual feedback).
   - Click on the flashcards to verify the 3D flipping animation works smoothly.
5. **Verify Note-taking & Search:** Type personal notes, tag points, search for keywords, and see if they highlight correctly.
