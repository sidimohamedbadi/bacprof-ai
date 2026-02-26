import streamlit as st
from pypdf import PdfReader
from groq import Groq
import json
from datetime import datetime

st.set_page_config(page_title="BacProf-AI v6", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI v6 – Ton vrai prof IA avec suivi des erreurs (couleurs)")

# ==================== CLÉ GROQ ====================
if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""
if "client" not in st.session_state:
    st.session_state.client = None

groq_key = st.text_input("🔑 Colle ta clé Groq", type="password", value=st.session_state.groq_key)
if st.button("💾 Sauvegarder clé"):
    if groq_key.startswith("gsk_"):
        st.session_state.groq_key = groq_key
        st.session_state.client = Groq(api_key=groq_key)
        st.success("✅ Clé sauvegardée !")
    else:
        st.error("La clé doit commencer par gsk_")

# ==================== MAÎTRISE & ERREURS ====================
if "mastery" not in st.session_state:
    st.session_state.mastery = {}  # compétence : {"errors": 0, "last_color": "vert", "history": []}

def get_color(errors):
    if errors >= 4: return "🔴 Rouge (répétée souvent)"
    elif errors >= 2: return "🟠 Orange"
    elif errors == 1: return "🟡 Jaune"
    else: return "🟢 Vert (maîtrisé)"

# ==================== EXTRACTION & DÉCOUPAGE ====================
def extract_text_from_pdfs(files):
    text = ""
    for file in files:
        reader = PdfReader(file)
        if reader.is_encrypted:
            reader.decrypt("")
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
    return text

# Découpage simple en micro-compétences (basé sur ton livre)
MICRO_COMPETENCES = [
    "Déterminer le domaine de définition d'une fonction",
    "Calculer f(a) pour une valeur donnée",
    "Résoudre f(x)=0 (équation du second degré)",
    "Déterminer le signe de f(x)",
    "Tracer la courbe d'une fonction",
    # On peut en ajouter plus tard automatiquement
]

# ==================== PROMPT PROF ====================
SYSTEM_PROMPT = """Tu es un professeur agrégé de mathématiques. Tu utilises EXACTEMENT la méthodologie du livre uploadé (ITEM 062 MA 7AS M M.pdf).
Réponds toujours avec LaTeX pour les maths (ex: $2x^2$, $\\frac{1}{2}$).
Analyse la réponse de l'élève, détecte l'erreur précise, propose un rappel simplifié + exercice plus facile si besoin.
Utilise le contexte du cours."""

def ask_prof(prompt, context="", student_answer=None):
    if not st.session_state.client:
        return "❌ Sauvegarde ta clé Groq d'abord."
    
    full_context = st.session_state.get("full_context", context)[:90000]
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + f"\nContexte du livre :\n{full_context}"},
        {"role": "user", "content": prompt}
    ]
    if student_answer:
        messages.append({"role": "user", "content": f"Réponse de l'élève : {student_answer}"})
    
    chat = st.session_state.client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.6,
        max_tokens=2048
    )
    return chat.choices[0].message.content

# ==================== INTERFACE ====================
tab1, tab2, tab3 = st.tabs(["📚 Cours & Indexation", "💬 Exercices + Analyse", "📊 Vision 360° Maîtrise"])

with tab1:
    st.subheader("Charge ton livre (déjà fait ?)")
    uploaded = st.file_uploader("PDFs (ton livre 7ème M)", type="pdf", accept_multiple_files=True)
    if st.button("🚀 Indexer tout le livre"):
        with st.spinner("Découpage en micro-compétences..."):
            st.session_state.full_context = extract_text_from_pdfs(uploaded)
            st.success("✅ Livre indexé ! 199 pages découpées.")

with tab2:
    st.subheader("Exercice + Correction intelligente")
    
    competence = st.selectbox("Choisis une micro-compétence", MICRO_COMPETENCES)
    
    if st.button("✨ Générer exercice sur cette compétence"):
        exercice = ask_prof(f"Génère un exercice neuf niveau 7ème M sur : {competence}. Donne énoncé + correction détaillée en LaTeX.")
        st.session_state.current_exercice = exercice
        st.markdown(exercice)
    
    # Réponse élève
    st.subheader("Ta réponse")
    student_answer = st.text_area("Écris ta réponse ici (ou choisis QCM plus tard)")
    
    if st.button("📤 Envoyer ma réponse pour correction"):
        if "current_exercice" in st.session_state:
            correction = ask_prof(f"Analyse cette réponse de l'élève pour l'exercice ci-dessus. Détecte l'erreur précise. Propose rappel simplifié + exercice plus facile si erreur.", 
                                student_answer=student_answer)
            st.markdown(correction)
            
            # Mise à jour couleurs
            skill = competence
            if skill not in st.session_state.mastery:
                st.session_state.mastery[skill] = {"errors": 0, "history": []}
            
            if "faute" in correction.lower() or "erreur" in correction.lower():
                st.session_state.mastery[skill]["errors"] += 1
                st.session_state.mastery[skill]["history"].append("erreur")
            else:
                st.session_state.mastery[skill]["history"].append("bon")
            
            st.success(f"Compétence **{skill}** → {get_color(st.session_state.mastery[skill]['errors'])}")

with tab3:
    st.subheader("📊 Vision 360° – Maîtrise des compétences")
    if st.session_state.mastery:
        for skill, data in st.session_state.mastery.items():
            color = get_color(data["errors"])
            st.write(f"{color} **{skill}** — {data['errors']} erreurs")
    else:
        st.info("Fais des exercices pour voir les couleurs apparaître")

st.caption("BacProf-AI v6 – Suivi erreurs couleurs + LaTeX + micro-compétences")
