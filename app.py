import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

st.set_page_config(page_title="BacProf-AI", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI – Ton vrai prof IA pour le Bac Terminale")

# Clé API
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("🔑 Colle ta clé API Gemini (gratuite)", value=st.session_state.api_key, type="password")
if api_key:
    st.session_state.api_key = api_key
    genai.configure(api_key=api_key)

# Stockage
if "full_context" not in st.session_state:
    st.session_state.full_context = ""
if "mastery" not in st.session_state:
    st.session_state.mastery = {}

# Fonctions
def extract_text_from_pdfs(files):
    text = ""
    for file in files:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
    return text

SYSTEM_PROMPT = """Tu es un professeur agrégé de Terminale qui prépare le Bac depuis 20 ans.
Tu suis EXACTEMENT la méthodologie des cours et annales que l'élève a uploadés.
Règles : utilise uniquement les méthodes présentes dans le contexte ci-dessous.
Donne toujours étapes numérotées, notations BAC, et exercices neufs dans le même style.

Contexte complet des cours et annales :
{context}
"""

def ask_prof(prompt: str):
    if not st.session_state.api_key:
        return "❌ Colle ta clé Gemini d'abord."
    context = st.session_state.full_context[:80000]  # Gemini gère très bien
    full_prompt = SYSTEM_PROMPT.format(context=context) + "\n\nQuestion : " + prompt
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(full_prompt)
    return response.text

# Interface
tab1, tab2, tab3 = st.tabs(["📚 Charger cours & annales", "💬 Chat avec mon prof", "📊 Vision 360°"])

with tab1:
    st.subheader("Charge tes PDFs (cours + annales corrigées)")
    uploaded = st.file_uploader("Sélectionne plusieurs PDFs", type="pdf", accept_multiple_files=True)
    if st.button("🚀 Indexer tout", type="primary") and uploaded:
        with st.spinner("Lecture des PDFs..."):
            st.session_state.full_context = extract_text_from_pdfs(uploaded)
            st.success(f"✅ {len(uploaded)} fichiers chargés ! Ton prof connaît maintenant tout.")

with tab2:
    st.subheader("Demande un exercice ou analyse une erreur")
    user_input = st.chat_input("Exemple : Génère un exercice neuf sur les probabilités")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Ton prof réfléchit..."):
                answer = ask_prof(user_input)
                st.markdown(answer)

with tab3:
    st.subheader("Ma vision 360°")
    st.info("Fais quelques exercices → les couleurs apparaîtront ici (prochaine mise à jour)")

st.caption("BacProf-AI v2 Léger – Parfait pour commencer à réviser tout de suite")
