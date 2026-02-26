import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

st.set_page_config(page_title="BacProf-AI", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI v4 – Ton vrai prof IA pour le Bac Terminale")

# ==================== CLÉ API ====================
api_key = st.text_input("🔑 Colle ta clé API Gemini (gratuite)", type="password", help="Crée-la sur https://aistudio.google.com/app/apikey")

if api_key:
    genai.configure(api_key=api_key)

# ==================== FONCTIONS ====================
def extract_text_from_pdfs(files):
    text = ""
    for file in files:
        try:
            reader = PdfReader(file)
            if reader.is_encrypted:
                reader.decrypt("")
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
        except Exception as e:
            st.warning(f"⚠️ {file.name} : {str(e)[:80]}")
            continue
    return text

SYSTEM_PROMPT = """Tu es un professeur agrégé de Terminale qui prépare le Bac depuis 20 ans.
Tu suis EXACTEMENT la méthodologie du cours et des annales que l'élève a uploadées.
Donne toujours étapes numérotées, notations BAC, et exercices 100% neufs dans le même style.

Contexte complet du cours :
{context}
"""

def ask_prof(prompt: str):
    if not api_key:
        return "❌ Colle d'abord ta clé Gemini."
    
    try:
        # Test avec plusieurs modèles en fallback
        models = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro']
        context = st.session_state.get("full_context", "")[:80000]
        
        for model_name in models:
            try:
                model = genai.GenerativeModel(model_name)
                full_prompt = SYSTEM_PROMPT.format(context=context) + "\n\nDemande de l'élève : " + prompt
                response = model.generate_content(full_prompt)
                return response.text
            except Exception:
                continue  # Essaie le modèle suivant
        
        return "❌ Aucun modèle Gemini n'a répondu. Essaie de créer une nouvelle clé API."
    
    except Exception as e:
        return f"❌ Erreur Gemini : {str(e)}\n\nCrée une nouvelle clé API sur Google AI Studio."

# ==================== INTERFACE ====================
tab1, tab2, tab3 = st.tabs(["📚 Charger cours & annales", "💬 Chat avec mon prof", "📊 Vision 360°"])

with tab1:
    st.subheader("Charge tes PDFs")
    uploaded = st.file_uploader("Sélectionne tes fichiers PDF", type="pdf", accept_multiple_files=True)
    if st.button("🚀 Indexer tout", type="primary") and uploaded:
        with st.spinner("Lecture des PDFs..."):
            st.session_state.full_context = extract_text_from_pdfs(uploaded)
            st.success(f"✅ {len(uploaded)} fichiers chargés !")

with tab2:
    st.subheader("Parle à ton prof IA")
    
    # Bouton de test de clé
    if st.button("🔍 Tester ma clé API"):
        with st.spinner("Test en cours..."):
            test = ask_prof("Dis-moi simplement 'Test OK' si tu fonctionnes.")
            st.write(test)
    
    user_input = st.chat_input("Exemple : Génère un exercice neuf sur les fonctions dérivées")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Ton prof réfléchit..."):
                answer = ask_prof(user_input)
                st.markdown(answer)

with tab3:
    st.info("Vision 360° avec couleurs et suivi des erreurs → arrive dans la prochaine version")

st.caption("BacProf-AI v4 – Test clé + fallback modèles")
