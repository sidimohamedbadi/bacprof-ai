import streamlit as st
from pypdf import PdfReader
from groq import Groq

st.set_page_config(page_title="BacProf-AI", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI v5.1 – Ton vrai prof IA (Groq Llama-3.3-70B)")

# ==================== GESTION CLÉ GROQ (corrigé) ====================
if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""
if "client" not in st.session_state:
    st.session_state.client = None

groq_key = st.text_input(
    "🔑 Colle ta clé Groq (gratuite)",
    type="password",
    value=st.session_state.groq_key,
    help="https://console.groq.com/keys"
)

# Bouton pour sauvegarder la clé
if st.button("💾 Sauvegarder ma clé Groq"):
    if groq_key.startswith("gsk_"):
        st.session_state.groq_key = groq_key
        st.session_state.client = Groq(api_key=groq_key)
        st.success("✅ Clé sauvegardée ! Tu peux maintenant tester.")
    else:
        st.error("La clé doit commencer par gsk_")

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
        except:
            continue
    return text

SYSTEM_PROMPT = """Tu es un professeur agrégé de Terminale qui prépare le Bac depuis 20 ans.
Tu suis EXACTEMENT la méthodologie du cours et des annales que l'élève a uploadées.
Règles strictes : étapes numérotées, notations BAC, exercices 100% neufs.

Contexte complet :
{context}
"""

def ask_prof(prompt: str):
    if not st.session_state.client:
        return "❌ Clique d'abord sur 'Sauvegarder ma clé Groq'."
    
    try:
        context = st.session_state.get("full_context", "")[:90000]
        full_prompt = SYSTEM_PROMPT.format(context=context) + "\n\nDemande de l'élève : " + prompt
        
        chat = st.session_state.client.chat.completions.create(
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=2048
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur : {str(e)[:200]}"

# ==================== INTERFACE ====================
tab1, tab2, tab3 = st.tabs(["📚 Charger cours & annales", "💬 Chat avec mon prof", "📊 Vision 360°"])

with tab1:
    uploaded = st.file_uploader("Sélectionne tes PDFs", type="pdf", accept_multiple_files=True)
    if st.button("🚀 Indexer tout", type="primary") and uploaded:
        with st.spinner("Lecture des PDFs..."):
            st.session_state.full_context = extract_text_from_pdfs(uploaded)
            st.success(f"✅ {len(uploaded)} fichiers chargés !")

with tab2:
    st.subheader("Parle à ton prof IA")
    if st.button("🔍 Tester ma clé Groq"):
        if st.session_state.client:
            with st.spinner("Test en cours..."):
                test = ask_prof("Dis simplement 'Test Groq OK je suis prêt pour le Bac'.")
                st.write(test)
        else:
            st.warning("Sauvegarde ta clé d'abord !")

    user_input = st.chat_input("Exemple : Génère un exercice neuf sur les fonctions dérivées")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Ton prof réfléchit..."):
                answer = ask_prof(user_input)
                st.markdown(answer)

with tab3:
    st.info("Vision 360° + couleurs erreurs répétées + suivi lacunes arrive très bientôt.")

st.caption("BacProf-AI v5.1 – Clé sauvegardée correctement")
