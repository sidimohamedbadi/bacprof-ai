import streamlit as st
from pypdf import PdfReader
from groq import Groq
from datetime import datetime

st.set_page_config(page_title="BacProf-AI v7", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI v7 – Cœur de l'application (Matière → Chapitre → Photo → Correction)")

# ==================== CLÉ GROQ ====================
if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""
groq_key = st.text_input("🔑 Colle ta clé Groq", type="password", value=st.session_state.groq_key)
if st.button("💾 Sauvegarder clé"):
    if groq_key.startswith("gsk_"):
        st.session_state.groq_key = groq_key
        st.session_state.client = Groq(api_key=groq_key)
        st.success("✅ Clé sauvegardée !")
    else:
        st.error("La clé doit commencer par gsk_")

# ==================== MAÎTRISE & COULEURS ====================
if "mastery" not in st.session_state:
    st.session_state.mastery = {}  # "Maths - Chap5 - Domaine" : {"errors": 3, "progress": 40}

def get_color(errors):
    if errors >= 4: return "🔴 Rouge – priorité absolue"
    elif errors >= 2: return "🟠 Orange – à retravailler"
    elif errors == 1: return "🟡 Jaune – presque bon"
    else: return "🟢 Vert – maîtrisé"

# ==================== NAVIGATION MATIÈRE → CHAPITRE → PARTIE ====================
matieres = ["Mathématiques", "Physique", "Sciences"]
if "matiere" not in st.session_state:
    st.session_state.matiere = "Mathématiques"

matiere = st.selectbox("Matière", matieres, index=matieres.index(st.session_state.matiere))
st.session_state.matiere = matiere

# Chapitres complets (basés sur ton livre + structure générale)
chapitres_maths = {
    "Chapitre 1 : Systèmes linéaires et matrices": ["Définir un système", "Opérations élémentaires", "Méthode de Gauss", "Cas particuliers"],
    "Chapitre 5 : Généralités sur les fonctions": ["Domaine de définition", "Calcul de f(a)", "Résoudre f(x)=0", "Signe de f(x)", "Tracer la courbe"],
    "Chapitre 6 : Fonctions logarithme et exponentielle": ["Propriétés du ln", "Équations avec ln", "Fonction e^x"],
    "Chapitre 7 : Calcul intégral": ["Primitives", "Intégrale définie", "Aire sous la courbe"],
    # ... tu peux ajouter les 12 autres chapitres plus tard, j'ai mis les principaux pour commencer
}

chapitre = st.selectbox("Chapitre", list(chapitres_maths.keys()))
partie = st.selectbox("Partie précise", chapitres_maths[chapitre])

competence = f"{matiere} - {chapitre} - {partie}"

# ==================== EXERCICES ====================
tab_qcm, tab_papier = st.tabs(["📝 QCM rapide", "📸 Exercice sur papier (photo)"])

with tab_qcm:
    if st.button("Générer QCM sur cette partie"):
        qcm = ask_prof(f"Génère un QCM de 4 questions sur {partie} ({chapitre}). Format : Question + 4 choix (A B C D) + bonne réponse en fin.")
        st.session_state.current_qcm = qcm
        st.markdown(qcm)

with tab_papier:
    if st.button("Générer exercice sur papier"):
        exo = ask_prof(f"Génère un exercice ouvert niveau 7ème M sur {partie} ({chapitre}). Donne seulement l'énoncé clair.")
        st.session_state.current_exo = exo
        st.markdown(exo)

    st.subheader("📸 Prends une photo de ta copie et upload-la")
    photo = st.file_uploader("Photo de ta réponse manuscrite", type=["jpg", "png", "jpeg"])
    if photo:
        st.image(photo, caption="Ta copie uploadée", use_column_width=True)
    
    ocr_text = st.text_area("Corrige / tape ce que tu as écrit (validation manuelle)", height=150, placeholder="Écris ici le texte détecté ou ta réponse complète")

    if st.button("📤 Corriger ma réponse papier"):
        if not ocr_text:
            st.error("Tape ou corrige le texte de ta copie")
        else:
            correction = ask_prof(f"Analyse cette réponse manuscrite de l'élève pour l'exercice sur {competence}. Détecte les erreurs précises. Propose rappel simplifié + exercice plus facile si besoin.\nRéponse élève : {ocr_text}")
            st.markdown(correction)
            
            # Mise à jour maîtrise
            if competence not in st.session_state.mastery:
                st.session_state.mastery[competence] = {"errors": 0}
            if any(word in correction.lower() for word in ["erreur", "faute", "incorrect", "mauvais"]):
                st.session_state.mastery[competence]["errors"] += 1
            st.success(f"{competence} → {get_color(st.session_state.mastery[competence]['errors'])}")

# ==================== VISION 360° & RÉVISION ADAPTATIVE ====================
with st.expander("📊 Vision 360° + Révision adaptative"):
    st.subheader("Barres de progression")
    for comp, data in st.session_state.mastery.items():
        color = get_color(data["errors"])
        progress = max(0, 100 - data["errors"] * 15)
        st.write(f"{color} **{comp}**")
        st.progress(progress)
    
    if st.button("🔄 Proposer révision adaptative"):
        weak = [comp for comp, data in st.session_state.mastery.items() if data["errors"] >= 2]
        if weak:
            st.success("Points faibles détectés : " + ", ".join(weak))
            st.info("Aujourd’hui tu travailles prioritairement : " + weak[0])
        else:
            st.success("Tu maîtrises tout ! Bravo 🎉")

st.caption("BacProf-AI v7 – Cœur complet (photo + validation + couleurs + adaptatif)")
