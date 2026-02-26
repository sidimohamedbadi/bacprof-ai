import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai

st.set_page_config(page_title="BacProf-AI", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI – Ton vrai prof IA pour le Bac Terminale")

# Clé API Gemini
api_key = st.text_input("🔑 Colle ta clé API Gemini (gratuite)", type="password")
if api_key:
    genai.configure(api_key=api_key)

# Stockage
if "full_context" not in st.session_state:
    st.session_state.full_context = ""

def extract_text_from_pdfs(files):
    text = ""
    for uploaded_file in files:
        try:
            reader = PdfReader(uploaded_file)
            if reader.is_encrypted:
                # Essaie le mot de passe vide (très souvent ça marche)
                reader.decrypt("")
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
        except Exception as e:
            st.error(f"Impossible de lire {uploaded_file.name} → {str(e)[:100]}")
            continue
    return text

SYSTEM_PROMPT = """Tu es un professeur agrégé de Terminale qui prépare le Bac depuis 20 ans.
Tu suis EXACTEMENT la méthodologie des cours et annales que l'élève a uploadées.
Utilise uniquement les méthodes présentes dans le contexte.
Donne toujours les étapes numérotées, notations BAC, et crée des exercices neufs dans le même style.

Contexte complet :
{context}
"""

def ask_prof(prompt: str):
    if not api_key:
        return "❌ Colle ta clé Gemini d'abord."
    context = st.session_state.full_context[:80000]
    full_prompt = SYSTEM_PROMPT.format(context=context) + "\n\nDemande : " + prompt
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(full_prompt)
    return response.text

# Interface
tab1, tab2, tab3 = st.tabs(["📚 Charger cours & annales", "💬 Chat avec mon prof", "📊 Vision 360°"])

with tab1:
    st.subheader("Charge tes PDFs (cours + annales corrigées)")
    uploaded = st.file_uploader("Sélectionne tes fichiers", type="pdf", accept_multiple_files=True)
    if st.button("🚀 Indexer tout", type="primary") and uploaded:
        with st.spinner("Lecture des PDFs (même ceux protégés)..."):
            st.session_state.full_context = extract_text_from_pdfs(uploaded)
            st.success(f"✅ Tous les fichiers sont chargés ! Ton prof connaît maintenant tout ton cours.")

with tab2:
    st.subheader("Parle à ton prof IA")
    user_input = st.chat_input("Exemple : Génère un exercice neuf sur les fonctions dérivées")
    if user_input:
        with st.chat_message("assistant"):
            with st.spinner("Ton prof réfléchit..."):
                answer = ask_prof(user_input)
                st.markdown(answer)

with tab3:
    st.subheader("📊 Ma vision 360°")
    st.info("Fais des exercices → les couleurs et le suivi arriveront dans la prochaine mise à jour")

st.caption("BacProf-AI v3 – Gère les PDFs protégés")
