import streamlit as st
from pypdf import PdfReader
from groq import Groq

st.set_page_config(page_title="BacProf-AI", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI v5 – Ton vrai prof IA (Groq Llama-3.3-70B)")

# ==================== CLÉ GROQ ====================
groq_key = st.text_input("🔑 Colle ta clé Groq (gratuite)", type="password", help="Obtiens-la sur https://console.groq.com/keys")

if groq_key:
    client = Groq(api_key=groq_key)

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
Tu suis EXACTEMENT la méthodologie du cours et des annales corrigées que l'élève a uploadées.
Règles strictes :
- Utilise uniquement les méthodes présentes dans le contexte.
- Réponds avec étapes numérotées, notations BAC précises.
- Crée des exercices 100% neufs dans le même style que les sujets BAC.

Contexte complet du cours et annales :
{context}
"""

def ask_prof(prompt: str):
    if not groq_key:
        return "❌ Colle d'abord ta clé Groq."
    
    try:
        context = st.session_state.get("full_context", "")[:90000]
        full_prompt = SYSTEM_PROMPT.format(context=context) + "\n\nDemande de l'élève : " + prompt
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": full_prompt}, {"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=2048
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur : {str(e)}\nVérifie que ta clé Groq est correcte."

# ==================== INTERFACE ====================
tab1, tab2, tab3 = st.tabs(["📚 Charger cours & annales", "💬 Chat avec mon prof", "📊 Vision 360°"])

with tab1:
    st.subheader("Charge tes PDFs")
    uploaded = st.file_uploader("Sélectionne tes fichiers PDF", type="pdf", accept_multiple_files=True)
    if st.button("🚀 Indexer tout", type="primary") and uploaded:
        with st.spinner("Lecture des PDFs..."):
            st.session_state.full_context = extract_text_from_pdfs(uploaded)
            st.success(f"✅ {len(uploaded)} fichiers chargés ! Ton prof connaît tout.")

with tab2:
    st.subheader("Parle à ton prof IA")
    if st.button("🔍 Tester ma clé Groq"):
        with st.spinner("Test..."):
            test = ask_prof("Dis simplement 'Test Groq OK' si tu es prêt.")
            st.write(test)
    
    user_input = st.chat_input("Exemple : Génère un exercice neuf sur les fonctions dérivées")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Ton prof réfléchit (très rapide avec Groq)..."):
                answer = ask_prof(user_input)
                st.markdown(answer)

with tab3:
    st.info("Vision 360° + couleurs erreurs répétées arrive dans 2 jours.")

st.caption("BacProf-AI v5 – Groq Llama-3.3-70B (ultra-rapide et fiable partout)")
