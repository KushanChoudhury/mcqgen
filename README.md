  # 🧠 MCQ Generator using GROQ + Streamlit

A fully automated MCQ generator that extracts text from PDF/TXT files, generates multiple-choice questions using GROQ LLM (Llama-3.1-8B), evaluates question complexity, and displays the results in a clean Streamlit UI.

---

## ✨ Features

- ✔ Upload PDF or TXT files  
- ✔ Two-step LLM pipeline: generation + review  
- ✔ Human-readable MCQ preview  
- ✔ Table view of all questions  
- ✔ Full logging support  

---

## ⚙️ Installation

Clone the repository:

```bash[
git clone https://github.com/KushanChoudhury/mcqgen.git
cd mcqgen
```

## 💻 Create & activate virtual environment
```
python -m venv venv
source venv/Scripts/activate     # Windows
source venv/bin/activate         # Mac/Linux

```
## 🔧 Install project
```
pip install -r requirements.txt
```
## 🔑 Environment Variables

Create a .env file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```
Generate a key at: [GROQ Console](https://console.groq.com/keys)

## 🚀 Run the Application

Start the Streamlit app:

```
streamlit run streamlitapp.py
```
Access it in your browser at:
```
http://localhost:8501
```