import streamlit as st
from pypdf import PdfReader
from groq import Groq

st.set_page_config(page_title="BacProf-AI v7.1", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI v7.1 – Cœur complet (Matière → Chapitre → Photo → Correction)")

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

# ==================== FONCTION ASK_PROF (obligatoire) ====================
def ask_prof(prompt):
    if not st.session_state.client:
        return "❌ Sauvegarde ta clé Groq d'abord."
    try:
        chat = st.session_state.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=2048
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur Groq : {str(e)}"

# ==================== MAÎTRISE & COULEURS ====================
if "mastery" not in st.session_state:
    st.session_state.mastery = {}

def get_color(errors):
    if errors >= 4: return "🔴 Rouge – priorité absolue"
    elif errors >= 2: return "🟠 Orange"
    elif errors == 1: return "🟡 Jaune"
    else: return "🟢 Vert – maîtrisé"

# ==================== NAVIGATION ====================
matiere = st.selectbox("Matière", ["Mathématiques", "Physique", "Sciences"])
chapitres = {
    "Chapitre 1 : Systèmes linéaires et matrices": ["Définir un système", "Opérations élémentaires", "Méthode de Gauss"],
    "Chapitre 5 : Généralités sur les fonctions": ["Domaine de définition", "Calcul de f(a)", "Résoudre f(x)=0", "Signe de f(x)", "Tracer la courbe"],
    "Chapitre 6 : Fonctions logarithme et exponentielle": ["Propriétés du ln", "Équations avec ln", "Fonction e^x"],
    "Chapitre 7 : Calcul intégral": ["Primitives", "Intégrale définie", "Aire sous la courbe"],
    # Ajoute les autres chapitres ici plus tard
}
chapitre = st.selectbox("Chapitre", list(chapitres.keys()))
partie = st.selectbox("Partie précise", chapitres[chapitre])
competence = f"{matiere} - {chapitre} - {partie}"

# ==================== EXERCICES ====================
tab_qcm, tab_papier = st.tabs(["📝 QCM rapide", "📸 Exercice sur papier (photo)"])

with tab_qcm:
    if st.button("Générer QCM"):
        qcm = ask_prof(f"Génère un QCM de 4 questions sur {partie} dans {chapitre}. Format clair : Question + 4 choix (A B C D) + bonne réponse à la fin.")
        st.session_state.current_qcm = qcm
        st.markdown(qcm)

with tab_papier:
    if st.button("Générer exercice sur papier"):
        exo = ask_prof(f"Génère un exercice ouvert clair sur {partie} ({chapitre}). Donne seulement l'énoncé.")
        st.session_state.current_exo = exo
        st.markdown(exo)

    st.subheader("📸 Photo de ta copie")
    photo = st.file_uploader("Upload photo de ta réponse manuscrite", type=["jpg", "png", "jpeg"])
    if photo:
        st.image(photo, use_column_width=True)

    ocr_text = st.text_area("Corrige / tape ce que tu as écrit sur la feuille", height=200, placeholder="Écris ici ta réponse complète")

    if st.button("📤 Corriger ma réponse papier"):
        if not ocr_text:
            st.error("Tape le texte de ta copie")
        else:
            correction = ask_prof(f"Analyse cette réponse manuscrite pour {competence}. Détecte les erreurs précises. Propose rappel simplifié + exercice plus facile si besoin.\nRéponse élève : {ocr_text}")
            st.markdown(correction)
            
            if competence not in st.session_state.mastery:
                st.session_state.mastery[competence] = {"errors": 0}
            if any(word in correction.lower() for word in ["erreur", "faute", "incorrect"]):
                st.session_state.mastery[competence]["errors"] += 1
            st.success(f"{competence} → {get_color(st.session_state.mastery[competence]['errors'])}")

# Vision 360°
with st.expander("📊 Vision 360° + Progression"):
    for comp, data in st.session_state.mastery.items():
        color = get_color(data["errors"])
        st.write(f"{color} **{comp}**")

st.caption("BacProf-AI v7.1 – Correction complète (photo + validation + couleurs)")
