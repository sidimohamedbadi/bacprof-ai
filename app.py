import streamlit as st
from pypdf import PdfReader
from groq import Groq

st.set_page_config(page_title="BacProf-AI v6.3", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI v6.3 – Choix par Chapitre + Temps pour répondre")

# Clé Groq
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

# Maîtrise avec couleurs
if "mastery" not in st.session_state:
    st.session_state.mastery = {}

def get_color(errors):
    if errors >= 4: return "🔴 Rouge – à revoir en priorité"
    elif errors >= 2: return "🟠 Orange – à retravailler"
    elif errors == 1: return "🟡 Jaune – presque bon"
    else: return "🟢 Vert – maîtrisé"

# Tous les 15 chapitres de ton livre
chapitres = {
    "Chapitre 1 : Systèmes linéaires et matrices": ["Définir un système linéaire", "Opérations élémentaires", "Méthode de Gauss", "Systèmes triangulaires", "Cas particuliers"],
    "Chapitre 2 : Arithmétique": ["Divisibilité et critères", "PGCD – PPCM", "Décomposition en facteurs premiers", "Congruence", "Équations diophantiennes"],
    "Chapitre 3 : Nombres complexes 1": ["Forme algébrique", "Représentation géométrique", "Conjugué et module", "Argument"],
    "Chapitre 4 : Nombres complexes 2": ["Forme trigonométrique", "Forme exponentielle", "Formule de Moivre", "Racines n-ièmes"],
    "Chapitre 5 : Généralités sur les fonctions": ["Domaine de définition", "Calcul de f(a)", "Résoudre f(x)=0", "Signe de f(x)", "Tracer la courbe"],
    "Chapitre 6 : Fonctions logarithme et exponentielle": ["Propriétés du ln", "Équations avec ln", "Fonction exponentielle", "Limites et dérivées"],
    "Chapitre 7 : Calcul intégral": ["Primitives", "Intégrale définie", "Aire sous la courbe", "Intégration par parties"],
    "Chapitre 8 : Equations différentielles": ["Équations du 1er ordre", "Équations linéaires"],
    "Chapitre 9 : Calcul vectoriel 1": ["Vecteurs", "Produit scalaire"],
    "Chapitre 10 : Calcul vectoriel 2": ["Produit vectoriel", "Applications géométriques"],
    "Chapitre 11 : Transformations 1": ["Translation", "Homothétie"],
    "Chapitre 12 : Transformations 2": ["Rotation", "Similitude directe"],
    "Chapitre 13 : Courbes paramétrées": ["Paramétrage", "Vitesse et accélération"],
    "Chapitre 14 : Coniques": ["Parabole", "Ellipse", "Hyperbole"],
    "Chapitre 15 : Probabilités et échantillonnage": ["Dénombrement", "Loi binomiale", "Intervalle de fluctuation"]
}

# Prompt
SYSTEM_PROMPT = "Tu es un professeur de maths 7ème M. Utilise la méthodologie exacte du livre ITEM 062. Réponds avec LaTeX."

def ask_prof(prompt):
    if "client" not in st.session_state:
        return "❌ Sauvegarde ta clé Groq d'abord."
    chat = st.session_state.client.chat.completions.create(
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.6,
        max_tokens=2048
    )
    return chat.choices[0].message.content

# Interface
tab1, tab2, tab3 = st.tabs(["📚 Charger livre", "💬 Exercices par Chapitre", "📊 Vision 360°"])

with tab1:
    uploaded = st.file_uploader("Ton livre complet (ITEM 062...pdf)", type="pdf", accept_multiple_files=True)
    if st.button("🚀 Indexer le livre"):
        text = ""
        for f in uploaded:
            reader = PdfReader(f)
            if reader.is_encrypted: reader.decrypt("")
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
        st.session_state.full_context = text
        st.success("✅ Livre complet indexé (199 pages) !")

with tab2:
    chapitre = st.selectbox("Choisis le chapitre", list(chapitres.keys()))
    partie = st.selectbox("Choisis la partie précise", chapitres[chapitre])
    
    if st.button("✨ Générer exercice"):
        prompt = f"Génère un exercice neuf clair sur : {partie} ({chapitre}). Donne seulement l'énoncé en LaTeX."
        exercice = ask_prof(prompt)
        st.session_state.current_exercice = exercice
        st.session_state.current_competence = f"{chapitre} - {partie}"
        st.markdown(exercice)
    
    st.subheader("Ta réponse (prends ton temps)")
    student_answer = st.text_area("Écris ta solution ici", height=200)
    
    if st.button("📤 Corriger ma réponse"):
        if "current_exercice" not in st.session_state:
            st.error("Génère d'abord un exercice")
        else:
            prompt = f"Analyse cette réponse de l'élève pour l'exercice sur {st.session_state.current_competence}. Dis précisément où est l'erreur ou bravo. Propose un rappel simplifié + un exercice plus facile si besoin."
            correction = ask_prof(prompt + "\nRéponse élève : " + student_answer)
            st.markdown(correction)
            
            comp = st.session_state.current_competence
            if comp not in st.session_state.mastery:
                st.session_state.mastery[comp] = {"errors": 0}
            if any(word in correction.lower() for word in ["erreur", "faute", "incorrect", "mauvais"]):
                st.session_state.mastery[comp]["errors"] += 1
            st.success(f"{comp} → {get_color(st.session_state.mastery[comp]['errors'])}")

with tab3:
    st.subheader("Vision 360° – Maîtrise")
    if st.session_state.mastery:
        for comp, data in st.session_state.mastery.items():
            color = get_color(data["errors"])
            progress = min(100, 100 - data["errors"]*10)
            st.write(f"{color} **{comp}**")
            st.progress(progress)
    else:
        st.info("Fais des exercices pour voir les barres de progression colorées")

st.caption("BacProf-AI v6.3 – Tous les chapitres + temps pour répondre + barres de progression")
