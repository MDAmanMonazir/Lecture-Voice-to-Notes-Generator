import streamlit as st
from google import genai
from audio_recorder_streamlit import audio_recorder
import json
import os
import tempfile
import time
import re

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Lecture Voice-to-Notes Generator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS for Premium Aesthetics and Animations
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Custom Background and Typography colors */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    /* Header Gradient Style */
    .header-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 35px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, transparent 60%);
        pointer-events: none;
    }

    .header-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 50%, #1d4ed8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }

    .header-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
        max-width: 750px;
        margin: 0 auto;
    }
    
    /* Card Component */
    .feature-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #111827;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        background-color: transparent;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.95rem;
        border: none;
        padding: 0 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: #1f2937;
        color: #f1f5f9;
    }

    /* Button Styling overrides */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(59, 130, 246, 0.35);
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
    }

    div.stButton > button:first-child:active {
        transform: translateY(0);
    }
    
    /* Secondary Button Styling (e.g. download notes, load demo) */
    div.stDownloadButton > button:first-child,
    .secondary-btn button {
        background: #1f2937 !important;
        color: #f1f5f9 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    div.stDownloadButton > button:first-child:hover,
    .secondary-btn button:hover {
        background: #374151 !important;
        border-color: #4b5563 !important;
        transform: translateY(-1px);
    }

    /* Input focus visual feedback */
    input, textarea, select {
        border-color: #374151 !important;
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
    }
    
    input:focus, textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }
    
    /* Visual Timeline and tag badges */
    .tag-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        margin-right: 8px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .tag-concept { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .tag-important { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .tag-exam { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .tag-question { background-color: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    
    .highlight-card {
        background-color: #1f2937;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .highlight-important { border-left-color: #ef4444; }
    .highlight-exam { border-left-color: #f59e0b; }
    .highlight-question { border-left-color: #a855f7; }

    /* Custom sidebar elements */
    .sidebar-section {
        background-color: #0f172a;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #1e293b;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Helper function to clean LLM markdown block outputs
def clean_json_string(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

# Helper function to highlight matching search term
def highlight_search(text, search_query):
    if not search_query:
        return text
    # Escape query to prevent broken regex
    escaped_query = re.escape(search_query)
    pattern = re.compile(f"({escaped_query})", re.IGNORECASE)
    # Highlight with CSS marker styles
    highlighted = pattern.sub(
        r'<mark style="background-color: #f59e0b; color: #0b0f19; font-weight: 700; border-radius: 4px; padding: 0 4px;">\1</mark>',
        text
    )
    return highlighted

# Session State Initialization
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "notes" not in st.session_state:
    st.session_state.notes = ""
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "personal_notes" not in st.session_state:
    st.session_state.personal_notes = ""
if "highlights" not in st.session_state:
    st.session_state.highlights = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "flashcard_index" not in st.session_state:
    st.session_state.flashcard_index = 0
if "demo_loaded" not in st.session_state:
    st.session_state.demo_loaded = False

# Demo Lecture Data Loader
def load_demo_data():
    st.session_state.transcript = (
        "Welcome back everyone. Today we are going to dive deep into Artificial Neural Networks, which form the "
        "bedrock of modern deep learning. We will look at how they learn, specifically through the processes of "
        "forward propagation and backpropagation.\n\n"
        "First, let's look at the basic building block: the artificial neuron, often called a node or a perceptron. "
        "A neuron receives multiple inputs, say x1, x2, and x3. Each input is multiplied by a corresponding weight, "
        "w1, w2, and w3. These weights represent the strength of the connection. We sum all these weighted inputs "
        "together and add a term called bias, which allows the network to shift the activation function up or down. "
        "Mathematically, the weighted sum is z = w1*x1 + w2*x2 + w3*x3 + bias. This weighted sum is then passed "
        "through an activation function.\n\n"
        "The activation function introduces non-linearity into the network, allowing it to learn complex, "
        "non-linear relationships. Common activation functions include the Sigmoid function, the Tanh function, "
        "and the Rectified Linear Unit, commonly known as ReLU. ReLU outputs the input directly if it is positive, "
        "and zero otherwise.\n\n"
        "When we stack these neurons in layers, we get a neural network. We have an input layer, one or more hidden "
        "layers, and an output layer. Passing inputs forward through the layers to get a prediction is called the "
        "forward pass or forward propagation.\n\n"
        "Once the network makes a prediction, we need to evaluate how good or bad it was. We do this using a loss "
        "function. For regression tasks, we often use Mean Squared Error or MSE, which calculates the average of "
        "the squared differences between the predicted values and the actual target values. The goal of training is "
        "to minimize this loss.\n\n"
        "So, how does the network minimize the loss? This is where backpropagation comes in. Backpropagation, short "
        "for backward propagation of errors, is an algorithm that calculates the gradient of the loss function with "
        "respect to the weights and biases of the network. It does this by using the chain rule from calculus, "
        "working backward from the output layer to the input layer. These gradients tell us how much our loss "
        "would change if we slightly adjust each weight and bias.\n\n"
        "We then use an optimization algorithm, most commonly Gradient Descent, to update the weights in the "
        "opposite direction of the gradient. The step size we take is controlled by a parameter called the learning "
        "rate. If the learning rate is too high, we might overshoot the minimum. If it is too low, training will "
        "be painfully slow.\n\n"
        "By repeating this cycle of forward propagation, loss calculation, backpropagation, and weight updates "
        "thousands of times, the neural network learns to make highly accurate predictions. That is all for today's "
        "introduction. Next time, we will write our first neural network from scratch in Python."
    )
    
    st.session_state.notes = (
        "# 📝 AI Structured Notes: Artificial Neural Networks & Backpropagation\n\n"
        "### 🧠 Lecture Summary\n"
        "This lecture provides a comprehensive introduction to Artificial Neural Networks (ANNs), explaining the core "
        "mechanisms that power modern deep learning. It details the structural building block of networks—the artificial "
        "neuron—and walks through the training cycle: forward propagation (making predictions), loss evaluation (measuring error), "
        "and backpropagation with gradient descent (updating parameters to learn).\n\n"
        "--- \n\n"
        "### 📖 Core Terminology & Definitions\n"
        "- **Artificial Neuron (Node/Perceptron):** The elementary unit of an ANN that takes inputs, applies weights and biases, and produces an output.\n"
        "- **Weights ($w$):** Parameters representing connection strengths between nodes, dictating input influence.\n"
        "- **Bias ($b$):** An offset value added to the weighted input sum, allowing the activation function to shift.\n"
        "- **Activation Function:** A mathematical operator that introduces non-linearity, enabling the model to learn intricate, complex patterns (e.g., Sigmoid, Tanh, ReLU).\n"
        "- **ReLU (Rectified Linear Unit):** An activation function defined as $f(x) = \\max(0, x)$. It is highly popular due to efficiency and combating vanishing gradients.\n"
        "- **Forward Propagation:** The process where input data travels sequentially through layers to generate a prediction.\n"
        "- **Loss Function (Cost Function):** A function (e.g., Mean Squared Error) measuring the difference between predicted outputs and ground-truth targets.\n"
        "- **Backpropagation:** An algorithm that calculates parameter gradients by working backward from the output layer to the input layer using the calculus chain rule.\n"
        "- **Gradient Descent:** Optimization algorithm that updates weights/biases in the direction opposite to the gradient to minimize loss.\n"
        "- **Learning Rate ($\\alpha$):** A tuning parameter specifying the step size taken during weights optimization.\n\n"
        "--- \n\n"
        "### 🔍 Detailed Concept Breakdown\n\n"
        "#### 1. Anatomy of a Neuron\n"
        "A neuron calculates a weighted sum of its inputs, adds a bias, and passes it through an activation function:\n"
        "$$z = \\sum_{i} w_i x_i + bias$$\n"
        "$$a = \\sigma(z)$$\n"
        "Without the activation function $\\sigma(z)$, any deep network simply collapses into a single linear equation, regardless of depth.\n\n"
        "#### 2. The Training Cycle\n"
        "The complete learning cycle follows these major phases:\n"
        "1. **Forward Pass:** Compute prediction step by step through layers.\n"
        "2. **Calculate Loss:** Determine the error using a loss metric (e.g., MSE for regression, Cross-Entropy for classification).\n"
        "3. **Backward Pass (Backprop):** Calculate derivative of loss with respect to every weight using the chain rule.\n"
        "4. **Parameter Updates:** Adjust parameters using Gradient Descent:\n"
        "   $$w_{new} = w_{old} - \\alpha \\cdot \\frac{\\partial L}{\\partial w}$$\n\n"
        "--- \n\n"
        "### 💡 Key Takeaways\n"
        "- **Non-linearity is crucial:** Without activation functions, deep networks are mathematically equivalent to single-layer linear regression models.\n"
        "- **Gradient alignment:** Gradient descent shifts weights in the opposite direction of the derivative to move 'downhill' toward global/local minimum loss.\n"
        "- **Learning Rate Sensitivity:** A learning rate too high causes oscillation or divergence; a rate too low results in high training times."
    )
    
    st.session_state.quiz = [
        {
            "question": "What is the primary mathematical purpose of an activation function in a neural network?",
            "options": [
                "To multiply inputs by connection strengths",
                "To introduce non-linearity, allowing the model to learn complex patterns",
                "To calculate the final prediction error",
                "To speed up the calculus chain rule during the backward pass"
            ],
            "correct_index": 1,
            "explanation": "Activation functions introduce non-linearity. Without them, stacking layers would only result in linear transformations, rendering deep networks no more powerful than simple linear regression."
        },
        {
            "question": "Which mathematical value allows the network to shift the activation function's starting point up or down?",
            "options": [
                "Weight",
                "Learning Rate",
                "Bias",
                "Loss Gradient"
            ],
            "correct_index": 2,
            "explanation": "The bias term is added to the sum of weighted inputs, allowing the node to offset or shift the activation function independently of the weights."
        },
        {
            "question": "Which process describes feeding inputs sequentially through the network layers to calculate a prediction?",
            "options": [
                "Forward Propagation",
                "Gradient Descent",
                "Backpropagation",
                "Loss Evaluation"
            ],
            "correct_index": 0,
            "explanation": "Forward Propagation (or forward pass) is the phase where inputs travel from the input layer, through hidden layers, to produce an output prediction."
        },
        {
            "question": "How does Backpropagation calculate the gradients of the loss function relative to weights?",
            "options": [
                "By picking random weight values and comparing losses",
                "Using the calculus chain rule, propagating derivatives backward from output to input",
                "Using linear regression to solve a system of linear equations",
                "By adjusting the learning rate continuously"
            ],
            "correct_index": 1,
            "explanation": "Backpropagation works backwards from the output error, computing gradients step-by-step using the chain rule to determine how much the error changes based on each individual weight."
        },
        {
            "question": "What is the consequence of choosing a learning rate that is too high during Gradient Descent?",
            "options": [
                "The training process will be extremely slow",
                "The activation functions will become strictly linear",
                "The algorithm might overshoot the minimum loss, causing instability or divergence",
                "Backpropagation will stop calculating weight derivatives entirely"
            ],
            "correct_index": 2,
            "explanation": "If the learning rate is too high, the updates to weights will be too large, causing the optimization process to overshoot the local minimum, oscillate, or completely diverge."
        }
    ]
    
    st.session_state.flashcards = [
        {
            "front": "What is an Artificial Neuron?",
            "back": "The basic building block of neural networks that processes inputs, multiplies them by weights, adds a bias, and applies an activation function."
        },
        {
            "front": "What is the purpose of an Activation Function?",
            "back": "To introduce non-linearity, allowing the network to learn complex relationships instead of just simple linear functions."
        },
        {
            "front": "Define Forward Propagation.",
            "back": "The process of input data passing forward through the network's layers to compute a prediction."
        },
        {
            "front": "What does a Loss Function measure?",
            "back": "The difference between the network's predicted output and the actual target values, showing how much error the prediction has."
        },
        {
            "front": "What is Backpropagation?",
            "back": "An algorithm that calculates gradients of the loss function using the calculus chain rule, moving backward from output to input layers."
        },
        {
            "front": "What is the Learning Rate?",
            "back": "A hyperparameter that controls the step size taken during gradient descent when updating weights."
        }
    ]
    
    st.session_state.personal_notes = (
        "Focus on these key points for midterm revision:\n"
        "- Sigmoid is active between 0 and 1, Tanh between -1 and 1, ReLU is max(0, x).\n"
        "- Chain rule is the mathematical foundation of backprop.\n"
        "- Underfitting might occur if the model doesn't have activation functions."
    )
    
    st.session_state.highlights = [
        {"text": "ReLU outputs the input directly if it is positive, and zero otherwise.", "category": "💡 Key Concept"},
        {"text": "Mathematically, the weighted sum is z = w1*x1 + w2*x2 + w3*x3 + bias.", "category": "💡 Key Concept"},
        {"text": "If the learning rate is too high, we might overshoot the minimum. If it is too low, training will be slow.", "category": "⚠️ Important"},
        {"text": "Backpropagation is an algorithm that calculates the gradient of the loss function with respect to weights and biases using the chain rule.", "category": "📝 Exam Tip"}
    ]
    
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.flashcard_index = 0
    st.session_state.demo_loaded = True

# --- API Integration Functions using google-generativeai ---

# Audio transcription using Gemini API (Gemini 1.5 Flash natively processes audio)
def transcribe_audio_api(audio_path, api_key, model_name):
    client = genai.Client(api_key=api_key)
    
    # Upload the file to the Gemini API
    audio_file = client.files.upload(file=audio_path)
    
    # Wait for the file to be processed
    state = getattr(audio_file.state, "name", audio_file.state)
    while state == "PROCESSING":
        time.sleep(1)
        audio_file = client.files.get(name=audio_file.name)
        state = getattr(audio_file.state, "name", audio_file.state)
        
    if state != "ACTIVE":
        raise Exception(f"Gemini failed to process audio: {state}")
        
    # Generate content using Gemini 1.5 Flash
    prompt = (
        "You are an expert academic transcriber. Transcribe the following lecture audio file accurately. "
        "Provide a clean verbatim transcription, maintaining all specific vocabulary, terminologies, and structure. "
        "Divide the text into logical paragraphs with correct capitalization and punctuation. "
        "Do not summarize or paraphrase, just output the transcription."
    )
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[audio_file, prompt]
        )
        transcript_text = response.text
    finally:
        # Delete file after transcription to clean up Gemini storage
        client.files.delete(name=audio_file.name)
        
    return transcript_text

# Structured Notes generator
def generate_notes_api(transcript, api_key, model_name):
    client = genai.Client(api_key=api_key)
    prompt = (
        f"You are a professional academic assistant. Based on this lecture transcript, create "
        f"comprehensive, high-quality, and structured study notes:\n\n{transcript}\n\n"
        f"Structure the notes as follows:\n"
        f"1. A Title with the topic\n"
        f"2. Lecture Summary (3-4 sentences in a callout block)\n"
        f"3. Core Terminology & Definitions (bulleted list of all critical terms mentioned)\n"
        f"4. Detailed Concept Breakdown (under logical subheadings, explaining key mechanisms)\n"
        f"5. Key Takeaways (bulleted bullet points highlighting the most crucial exam topics or conclusions)\n\n"
        f"Use clean Markdown formatting, professional language, and make it visually attractive."
    )
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    return response.text

# Quiz generator (outputs MCQ JSON)
def generate_quiz_api(transcript, api_key, model_name):
    client = genai.Client(api_key=api_key)
    prompt = (
        f"Based on the following lecture transcript, generate 5 challenging multiple-choice questions (MCQs) "
        f"to test comprehension:\n\n{transcript}\n\n"
        f"You must return ONLY a valid JSON array matching the structure below. "
        f"Do not include any markup, intro text, or markdown code blocks like ```json ... ```. Just return the raw JSON.\n\n"
        f"JSON Format Schema:\n"
        f"[\n"
        f"  {{\n"
        f"    \"question\": \"Question statement here?\",\n"
        f"    \"options\": [\"Option A text\", \"Option B text\", \"Option C text\", \"Option D text\"],\n"
        f"    \"correct_index\": 0,\n"
        f"    \"explanation\": \"Detailed explanation of why Option A is correct and why others are incorrect.\"\n"
        f"  }},\n"
        f"  ...\n"
        f"]"
    )
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    cleaned_res = clean_json_string(response.text)
    return json.loads(cleaned_res)

# Flashcard generator (outputs JSON)
def generate_flashcards_api(transcript, api_key, model_name):
    client = genai.Client(api_key=api_key)
    prompt = (
        f"Based on the following lecture transcript, extract 6-8 core terms, formulas, or major concepts "
        f"and create interactive flashcards. Provide direct, concise question/concept on the front, and explanation/answer on the back:\n\n{transcript}\n\n"
        f"You must return ONLY a valid JSON array matching the structure below. "
        f"Do not include any markup or markdown code blocks. Just return raw JSON.\n\n"
        f"JSON Format Schema:\n"
        f"[\n"
        f"  {{\n"
        f"    \"front\": \"Term, Question, or Formula\",\n"
        f"    \"back\": \"Concise definition, answer, or description (1-2 sentences maximum)\"\n"
        f"  }},\n"
        f"  ...\n"
        f"]"
    )
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    cleaned_res = clean_json_string(response.text)
    return json.loads(cleaned_res)


# --- APPLICATION INTERFACE LAYOUT ---

# Header block
st.markdown(
    """
    <div class="header-container">
        <div class="header-title">🎙️ Lecture Voice-to-Notes Generator</div>
        <div class="header-subtitle">
            An advanced AI-powered study companion that converts lecture recordings into accurate text transcripts, 
            generates structured summary notes, conducts interactive quizzes, and formats custom active-recall flashcards.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar configurations
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("🔑 API Setup")
    api_key_input = st.text_input(
        "Enter Gemini API Key:",
        type="password",
        placeholder="AIzaSy...",
        help="Get an API key from Google AI Studio"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Resolve the api key to use
    api_key = api_key_input or os.environ.get("GEMINI_API_KEY")
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("⚙️ Model Configuration")
    model_name = st.selectbox(
        "Select Generative Model:",
        options=["gemini-2.5-flash", "gemini-3.0-flash", "gemini-3.0-pro"],
        index=0,
        help="gemini-2.5-flash is faster and highly cost-efficient; gemini-3.0-pro is recommended for complex reasoning."
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("💡 Sandbox & Demos")
    st.markdown("No audio file on hand? Load our pre-configured college neural-network lecture to instantly try all features.")
    
    if st.button("🚀 Load Demo Lecture"):
        load_demo_data()
        st.success("Loaded neural network lecture demo!")
        st.rerun()
        
    if st.button("🗑️ Reset App State"):
        st.session_state.transcript = ""
        st.session_state.notes = ""
        st.session_state.quiz = []
        st.session_state.flashcards = []
        st.session_state.personal_notes = ""
        st.session_state.highlights = []
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False
        st.session_state.flashcard_index = 0
        st.session_state.demo_loaded = False
        st.success("Application state reset successfully!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown(
        """
        <div style="font-size: 11px; text-align: center; color: #64748b; margin-top: 30px;">
            Developed for Students & Educators • Powered by Gemini AI
        </div>
        """,
        unsafe_allow_html=True
    )

# Main Dashboard Layout
# Search Query (Global Search across transcript, notes, and personal notes)
st.markdown('<div class="feature-card">', unsafe_allow_html=True)
col_title, col_search = st.columns([2, 3])
with col_title:
    st.markdown("<h4 style='margin:0; padding-top:6px; color:#60a5fa;'>🔍 Study Material Search</h4>", unsafe_allow_html=True)
with col_search:
    search_query = st.text_input(
        "Search...",
        label_visibility="collapsed",
        placeholder="Type keyword to highlight across notes and transcripts...",
        key="global_search_input"
    )
st.markdown('</div>', unsafe_allow_html=True)

# Audio Upload and Recording Interface
st.markdown('<div class="feature-card">', unsafe_allow_html=True)
st.subheader("🎙️ Input Lecture Audio")
st.markdown("Provide an audio recording of your lecture. You can upload an audio file or record one live.")

col_upload, col_record = st.columns([3, 2])

audio_file_path = None

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload Audio File (MP3, WAV, M4A, OGG):",
        type=["mp3", "wav", "m4a", "ogg"],
        help="Maximum file size 200MB. Audio files are uploaded and processed using Gemini's native multimodal capabilities."
    )
    if uploaded_file is not None:
        # Save uploaded file to temp file to obtain paths for genai.upload_file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        audio_file_path = temp_path
        st.audio(uploaded_file)

with col_record:
    st.write("Record Live Lecture:")
    # Streamlit audio recorder component
    recorded_audio_bytes = audio_recorder(
        text="Click mic to record",
        recording_color="#ef4444",
        neutral_color="#3b82f6",
        icon_size="2x"
    )
    
    if recorded_audio_bytes:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "recorded_lecture.wav")
        with open(temp_path, "wb") as f:
            f.write(recorded_audio_bytes)
        audio_file_path = temp_path
        st.audio(recorded_audio_bytes, format="audio/wav")
        st.success("Audio recorded successfully!")

# Processing Action Button
if audio_file_path:
    # Tooltip warnings about keys
    if not api_key:
        st.warning("⚠️ A Gemini API Key is required. Please paste your key in the sidebar to run audio processing.")
        process_btn = st.button("Process Lecture Audio", disabled=True)
    else:
        process_btn = st.button("Process Lecture Audio")
        if process_btn:
            try:
                progress_bar = st.progress(0, "Initiating audio transcription...")
                
                # Step 1: Audio Transcription
                progress_bar.progress(15, "Transcribing lecture audio via Gemini...")
                transcript = transcribe_audio_api(audio_file_path, api_key, model_name)
                st.session_state.transcript = transcript
                
                # Step 2: Generate Structured Notes
                progress_bar.progress(45, "Generating AI Structured Notes...")
                notes = generate_notes_api(transcript, api_key, model_name)
                st.session_state.notes = notes
                
                # Step 3: Generate Quizzes
                progress_bar.progress(70, "Generating Interactive Quizzes...")
                try:
                    quiz = generate_quiz_api(transcript, api_key, model_name)
                    st.session_state.quiz = quiz
                except Exception as q_err:
                    st.error(f"Failed to generate Quiz JSON structure: {q_err}")
                    st.session_state.quiz = []
                
                # Step 4: Generate Flashcards
                progress_bar.progress(90, "Creating Active Recall Flashcards...")
                try:
                    flashcards = generate_flashcards_api(transcript, api_key, model_name)
                    st.session_state.flashcards = flashcards
                except Exception as f_err:
                    st.error(f"Failed to generate Flashcards JSON structure: {f_err}")
                    st.session_state.flashcards = []
                
                # Clean up local temporary file
                if os.path.exists(audio_file_path):
                    os.remove(audio_file_path)
                
                # Reset Quiz state
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.flashcard_index = 0
                st.session_state.highlights = []
                
                progress_bar.progress(100, "Processing complete! Access material below.")
                st.success("Lecture content generated successfully!")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"An error occurred during AI processing: {e}")
else:
    if not st.session_state.transcript:
        st.info("💡 Get started by uploading a file, recording live, or clicking 'Load Demo Lecture' in the sidebar.")

st.markdown('</div>', unsafe_allow_html=True)


# --- DASHBOARD CONTENT TAB PANELS ---
if st.session_state.transcript:
    tab_transcript, tab_notes, tab_quiz, tab_flashcards = st.tabs([
        "🎙️ Transcript & Student Highlights",
        "📝 AI Structured Notes",
        "🧠 Interactive Quiz Hub",
        "⚡ Study Flashcards"
    ])
    
    # ---------------- TAB 1: TRANSCRIPT & STUDENT HIGHLIGHTS ----------------
    with tab_transcript:
        col_t_left, col_t_right = st.columns([3, 2])
        
        with col_t_left:
            st.markdown("<h4 style='color:#3b82f6; border-bottom:1px solid #1f2937; padding-bottom:10px;'>Lecture Transcript</h4>", unsafe_allow_html=True)
            
            # Highlighting search keywords
            highlighted_transcript = highlight_search(st.session_state.transcript, search_query)
            
            # Use columns or details container for beautiful reading frame
            st.markdown(
                f"""
                <div style="background-color:#111827; border:1px solid #1f2937; border-radius:12px; padding:25px; line-height:1.7; font-size:15px; max-height:600px; overflow-y:auto; color:#cbd5e1; white-space: pre-wrap;">
{highlighted_transcript}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Transcript as Text",
                data=st.session_state.transcript,
                file_name="lecture_transcript.txt",
                mime="text/plain",
                key="download_transcript_btn"
            )
            
        with col_t_right:
            st.markdown("<h4 style='color:#3b82f6; border-bottom:1px solid #1f2937; padding-bottom:10px;'>✍️ Student Notebook & Tagging</h4>", unsafe_allow_html=True)
            
            # Personal Notes editor (Saves instantly on interaction)
            p_notes = st.text_area(
                "Personal Study Notes (edit as you study):",
                value=st.session_state.personal_notes,
                height=250,
                placeholder="Write down class dates, homework tasks, explanations in your own words...",
                key="personal_notes_editor"
            )
            if p_notes != st.session_state.personal_notes:
                st.session_state.personal_notes = p_notes
            
            st.markdown("<h5 style='color:#60a5fa; margin-top:20px;'>🏷️ Tag Crucial Points & Key Quotes</h5>", unsafe_allow_html=True)
            
            # Add highlight box
            with st.form("add_highlight_form", clear_on_submit=True):
                hl_text = st.text_area(
                    "Paste crucial text or enter key takeaways to bookmark:",
                    placeholder="Enter an important lecture quote or note here...",
                    height=90
                )
                hl_cat = st.selectbox(
                    "Tag category:",
                    options=["💡 Key Concept", "⚠️ Important", "📝 Exam Tip", "❓ Question to Ask"]
                )
                submit_hl = st.form_submit_button("➕ Save Highlight & Tag")
                
                if submit_hl and hl_text.strip():
                    st.session_state.highlights.append({
                        "text": hl_text.strip(),
                        "category": hl_cat
                    })
                    st.success("Highlight saved successfully!")
                    st.rerun()
            
            # Render Timeline / Card list of saved highlights
            if st.session_state.highlights:
                st.markdown("<h5 style='color:#94a3b8; margin-top:20px;'>Saved Highlights</h5>", unsafe_allow_html=True)
                
                for idx, hl in enumerate(st.session_state.highlights):
                    # Style class based on category
                    style_class = "highlight-card"
                    tag_class = "tag-badge"
                    if "Important" in hl["category"]:
                        style_class += " highlight-important"
                        tag_class += " tag-important"
                    elif "Exam" in hl["category"]:
                        style_class += " highlight-exam"
                        tag_class += " tag-exam"
                    elif "Question" in hl["category"]:
                        style_class += " highlight-question"
                        tag_class += " tag-question"
                    else:
                        tag_class += " tag-concept"
                        
                    highlighted_hl_text = highlight_search(hl["text"], search_query)
                    
                    st.markdown(
                        f"""
                        <div class="{style_class}">
                            <span class="{tag_class}">{hl['category']}</span>
                            <div style="font-size:14px; margin-top:8px; line-height:1.5; color:#f1f5f9;">{highlighted_hl_text}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Delete highlight button
                    if st.button("Remove Highlight", key=f"del_hl_{idx}"):
                        st.session_state.highlights.pop(idx)
                        st.rerun()
            else:
                st.info("No crucial highlights added yet. Use the form above to bookmark key quotes.")

    # ---------------- TAB 2: AI STRUCTURED NOTES ----------------
    with tab_notes:
        st.markdown("<h4 style='color:#3b82f6; border-bottom:1px solid #1f2937; padding-bottom:10px;'>📝 Generative Study Notes</h4>", unsafe_allow_html=True)
        
        if st.session_state.notes:
            # Highlight notes text
            highlighted_notes = highlight_search(st.session_state.notes, search_query)
            
            # Display notes beautifully
            st.markdown(
                f"""
                <div style="background-color:#111827; border:1px solid #1f2937; border-radius:12px; padding:35px; min-height:400px; line-height:1.7;">
{highlighted_notes}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.download_button(
                label="📥 Download Study Notes (Markdown)",
                data=st.session_state.notes,
                file_name="lecture_study_notes.md",
                mime="text/markdown",
                key="download_notes_btn"
            )
        else:
            st.warning("Notes could not be generated. Please make sure the transcription succeeded and try re-processing.")

    # ---------------- TAB 3: INTERACTIVE QUIZ HUB ----------------
    with tab_quiz:
        st.markdown("<h4 style='color:#3b82f6; border-bottom:1px solid #1f2937; padding-bottom:10px;'>🧠 Assessment Quiz</h4>", unsafe_allow_html=True)
        st.write("Test your retention and understanding of the lecture material. Answer all multiple-choice questions below.")
        
        if st.session_state.quiz:
            score = 0
            
            # Quiz grading workflow
            for idx, q in enumerate(st.session_state.quiz):
                st.markdown(f"<div class='feature-card'>", unsafe_allow_html=True)
                st.markdown(f"**Question {idx + 1}:** {q['question']}")
                
                # Check for existing state answers
                default_val = None
                saved_ans = st.session_state.quiz_answers.get(idx)
                if saved_ans is not None:
                    # Resolve to option string
                    default_val = q['options'][saved_ans]
                    
                selected_opt = st.radio(
                    f"Select your answer for Question {idx + 1}:",
                    options=q["options"],
                    index=None if saved_ans is None else saved_ans,
                    key=f"quiz_radio_{idx}",
                    label_visibility="collapsed"
                )
                
                # Save answer index in state
                if selected_opt is not None:
                    st.session_state.quiz_answers[idx] = q["options"].index(selected_opt)
                
                # Grading feedback layout
                if st.session_state.quiz_submitted:
                    chosen_idx = st.session_state.quiz_answers.get(idx)
                    correct_idx = q["correct_index"]
                    
                    if chosen_idx == correct_idx:
                        score += 1
                        st.markdown(f"<p style='color:#10b981; font-weight:700; margin-top:8px;'>✓ Correct Answer</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f"<p style='color:#ef4444; font-weight:700; margin-top:8px;'>✗ Incorrect</p>"
                            f"<p style='margin:0; font-size:14px; color:#94a3b8;'>Correct Answer: <b>{q['options'][correct_idx]}</b></p>",
                            unsafe_allow_html=True
                        )
                    
                    st.markdown(
                        f"<div style='background-color:#1e293b; padding:12px 15px; border-radius:8px; margin-top:8px; font-size:14px; line-height:1.5; color:#cbd5e1; border-left: 3px solid #60a5fa;'>"
                        f"<b>Explanation:</b> {q['explanation']}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                st.markdown(f"</div>", unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Quiz submission / reset controls
            if not st.session_state.quiz_submitted:
                # Disable submission if any question is unanswered
                all_answered = len(st.session_state.quiz_answers) == len(st.session_state.quiz)
                
                if not all_answered:
                    st.warning("Please select answers for all questions before submitting.")
                    submit_disabled = True
                else:
                    submit_disabled = False
                    
                if st.button("Submit Quiz for Grading", disabled=submit_disabled):
                    st.session_state.quiz_submitted = True
                    st.rerun()
            else:
                pct = int((score / len(st.session_state.quiz)) * 100)
                score_color = "#ef4444" if pct < 60 else ("#f59e0b" if pct < 80 else "#10b981")
                
                st.markdown(
                    f"""
                    <div class="feature-card" style="text-align:center; padding:30px;">
                        <h3 style="margin:0;">Quiz Performance Summary</h3>
                        <div style="font-size: 4rem; font-weight:800; color:{score_color}; margin: 15px 0;">
                            {score} / {len(st.session_state.quiz)}
                        </div>
                        <p style="font-size:16px; color:#cbd5e1;">You scored a <b>{pct}%</b> on this lecture assessment.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if st.button("🔄 Reset Quiz & Retry"):
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()
        else:
            st.warning("Quiz questions could not be generated. Please make sure the transcription succeeded and try re-processing.")

    # ---------------- TAB 4: ACTIVE RECALL FLASHCARDS ----------------
    with tab_flashcards:
        st.markdown("<h4 style='color:#3b82f6; border-bottom:1px solid #1f2937; padding-bottom:10px;'>⚡ Active Recall Flashcards</h4>", unsafe_allow_html=True)
        st.write("Click on the card structure to flip it back and forth. Use the buttons below to browse the deck.")
        
        if st.session_state.flashcards:
            total_cards = len(st.session_state.flashcards)
            curr_idx = st.session_state.flashcard_index
            
            # Fetch current card content
            card = st.session_state.flashcards[curr_idx]
            front_content = card.get("front", "")
            back_content = card.get("back", "")
            
            # Progress tracker
            progress_pct = (curr_idx + 1) / total_cards
            st.progress(progress_pct)
            st.markdown(
                f"<p style='text-align:center; font-size:14px; color:#94a3b8;'>Card <b>{curr_idx + 1}</b> of <b>{total_cards}</b></p>",
                unsafe_allow_html=True
            )
            
            # Pure CSS Flipping Flashcard via Markdown
            html_content = f"""
            <div style="display: flex; justify-content: center; align-items: center; min-height: 320px; padding: 20px;">
                <style>
                .flashcard-wrapper {{
                    width: 100%;
                    max-width: 480px;
                    height: 280px;
                    perspective: 1000px;
                    margin: 0 auto;
                }}
                .flashcard-inner {{
                    position: relative;
                    width: 100%;
                    height: 100%;
                    text-align: center;
                    transition: transform 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                    transform-style: preserve-3d;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
                    border-radius: 20px;
                }}
                .flashcard-wrapper:hover .flashcard-inner {{
                    transform: rotateY(180deg);
                }}
                .flashcard-front, .flashcard-back {{
                    position: absolute;
                    width: 100%;
                    height: 100%;
                    -webkit-backface-visibility: hidden;
                    backface-visibility: hidden;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    padding: 30px;
                    border-radius: 20px;
                    box-sizing: border-box;
                }}
                .flashcard-front {{
                    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    color: #f8fafc;
                    border: 2px solid #3b82f6;
                }}
                .flashcard-back {{
                    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
                    color: #f8fafc;
                    transform: rotateY(180deg);
                    border: 2px solid #60a5fa;
                }}
                .fc-label {{
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 2.5px;
                    color: #60a5fa;
                    margin-bottom: 20px;
                    font-weight: 700;
                }}
                .fc-text {{
                    font-size: 19px;
                    font-weight: 600;
                    line-height: 1.6;
                    color: #ffffff;
                }}
                .fc-hint {{
                    margin-top: 25px;
                    font-size: 11px;
                    color: #64748b;
                    letter-spacing: 0.5px;
                }}
                </style>
                <div class="flashcard-wrapper">
                    <div class="flashcard-inner">
                        <div class="flashcard-front">
                            <div class="fc-label">💡 Term / Question</div>
                            <div class="fc-text">{front_content}</div>
                            <div class="fc-hint">🖱️ Hover over card to reveal answer</div>
                        </div>
                        <div class="flashcard-back">
                            <div class="fc-label">✍️ Definition / Explanation</div>
                            <div class="fc-text">{back_content}</div>
                        </div>
                    </div>
                </div>
            </div>
            """
            
            # Embed flipping flashcard
            st.markdown(html_content, unsafe_allow_html=True)
            
            # Flashcard Navigation Buttons
            col_c_left, col_c_right = st.columns([1, 1])
            with col_c_left:
                if st.button("◀ Previous Card", disabled=curr_idx == 0):
                    st.session_state.flashcard_index = max(0, curr_idx - 1)
                    st.rerun()
            with col_c_right:
                if st.button("Next Card ▶", disabled=curr_idx == total_cards - 1):
                    st.session_state.flashcard_index = min(total_cards - 1, curr_idx + 1)
                    st.rerun()
        else:
            st.warning("Flashcards could not be generated. Please make sure the transcription succeeded and try re-processing.")
