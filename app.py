import streamlit as st
import time
from groq import Groq

st.set_page_config(page_title="BacProf-AI", page_icon="🎓", layout="centered")

# CSS moderne 2026
st.markdown("""
<style>
    .main {background-color: #0f1117;}
    .stButton>button {width: 100%; height: 55px; font-size: 18px; border-radius: 12px;}
    .card {background-color: #1a1f2e; padding: 25px; border-radius: 16px; margin: 15px 0;}
    .question {font-size: 20px; font-weight: 600; color: #e0e0e0;}
    .timer {font-size: 28px; color: #ff4d4d; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("🎓 BacProf-AI")
st.markdown("**L'application moderne que tu mérites**")

# Clé Groq
if "client" not in st.session_state:
    groq_key = st.text_input("🔑 Ta clé Groq", type="password")
    if st.button("Sauvegarder clé"):
        if groq_key.startswith("gsk_"):
            st.session_state.client = Groq(api_key=groq_key)
            st.success("✅ Connecté")
        else:
            st.error("Clé invalide")

# Navigation moderne
col1, col2, col3 = st.columns(3)
with col1:
    matiere = st.selectbox("Matière", ["Mathématiques", "Physique", "Sciences"])
with col2:
    chapitre = st.selectbox("Chapitre", ["Chapitre 5 : Généralités sur les fonctions", "Chapitre 7 : Calcul intégral", "Chapitre 1 : Systèmes linéaires"])
with col3:
    partie = st.selectbox("Partie", ["Domaine de définition", "Calcul de f(a)", "Résoudre f(x)=0", "Signe de la fonction"])

competence = f"{matiere} - {chapitre} - {partie}"

tab1, tab2 = st.tabs(["📝 QCM Moderne", "📸 Exercice sur papier"])

with tab1:
    if st.button("🚀 Commencer le QCM", type="primary"):
        st.session_state.qcm_questions = [
            {"q": "Qu'est-ce que le domaine de définition ?", "options": ["A) Ensemble des x possibles", "B) Ensemble des y", "C) La courbe", "D) L'équation"], "correct": 0},
            {"q": "f(x) = 1/(x-2) a un domaine qui exclut ?", "options": ["A) x=0", "B) x=2", "C) x=1", "D) Tous les réels"], "correct": 1},
            # On peut en ajouter plus
        ]
        st.session_state.qcm_index = 0
        st.session_state.qcm_score = 0
        st.session_state.qcm_start_time = time.time()

    if "qcm_index" in st.session_state:
        q = st.session_state.qcm_questions[st.session_state.qcm_index]
        st.markdown(f"<div class='card'><div class='question'>Question {st.session_state.qcm_index + 1}</div><p>{q['q']}</p></div>", unsafe_allow_html=True)
        
        choix = st.radio("Choisis ta réponse", q["options"], key=f"q{st.session_state.qcm_index}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Valider réponse", type="primary"):
                if choix == q["options"][q["correct"]]:
                    st.success("✅ Correct !")
                    st.session_state.qcm_score += 1
                else:
                    st.error(f"❌ Mauvaise réponse. La bonne était : {q['options'][q['correct']]}")
                
                if st.session_state.qcm_index < len(st.session_state.qcm_questions) - 1:
                    st.session_state.qcm_index += 1
                    st.rerun()
                else:
                    st.balloons()
                    st.success(f"QCM terminé ! Score : {st.session_state.qcm_score}/{len(st.session_state.qcm_questions)}")
                    del st.session_state.qcm_index

with tab2:
    st.markdown("**Exercice sur papier**")
    exo = st.text_area("Énoncé de l'exercice", "Soit f(x) = 2x² - 3x + 1. Détermine son domaine de définition et résous f(x) = 0.")
    
    photo = st.camera_input("Prends une photo de ta copie avec ton téléphone") or st.file_uploader("Ou upload une photo", type=["jpg","png"])
    if photo:
        st.image(photo, width=400)
    
    reponse_eleve = st.text_area("Tape ou corrige ce que tu as écrit sur la feuille", height=180)
    
    if st.button("📤 Corriger avec l'IA", type="primary"):
        correction = "Analyse en cours..."  # Ici on mettra ask_prof plus tard
        st.info("Correction IA : " + correction)

# Vision 360° moderne
with st.expander("📊 Ma progression globale"):
    st.progress(65, text="65% du programme maîtrisé")
    st.metric("Points faibles", "3 chapitres en rouge")

st.caption("BacProf-AI v8 – Design moderne 2026 | Développé avec toi")
