import streamlit as st
from pypdf import PdfReader
from groq import Groq

st.set_page_config(page_title="BacProf-AI v6.2", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI v6.2 – Choix par Chapitre + Temps pour répondre")

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
        st.success("✅ Clé sauvegardée ! Tu peux commencer.")
    else:
        st.error("La clé doit commencer par gsk_")

# ==================== MAÎTRISE (couleurs) ====================
if "mastery" not in st.session_state:
    st.session_state.mastery = {}  # "Chapitre 1 - Domaine": {"errors": 0}

def get_color(errors):
    if errors >= 4: return "🔴 Rouge (erreur répétée souvent)"
    elif errors >= 2: return "🟠 Orange"
    elif errors == 1: return "🟡 Jaune"
    else: return "🟢 Vert (maîtrisé)"

# ==================== CHAPITRES DU LIVRE (complet) ====================
chapitres = {
    "Chapitre 1 : Systèmes linéaires et matrices": [
        "Définir un système linéaire", "Opérations élémentaires sur les lignes",
        "Méthode de Gauss", "Systèmes triangulaires", "Cas particuliers (infini ou impossible)"
    ],
    "Chapitre 2 : Arithmétique": [
        "Divisibilité et critères", "PGCD et PPCM", "Décomposition en facteurs premiers",
        "Congruence", "Équations diophantiennes"
    ],
    "Chapitre 5 : Généralités sur les fonctions": [
        "Domaine de définition", "Calcul de f(a)", "Résoudre f(x)=0",
        "Signe de la fonction", "Tracer la courbe"
    ],
    "Chapitre 6 : Fonctions logarithme et exponentielle": [
        "Propriétés du ln", "Équations avec ln", "Fonction exponentielle e^x"
    ],
    "Chapitre 7 : Calcul intégral": ["Primitives", "Intégrale définie", "Aire sous la courbe"],
    # Tu peux ajouter les autres chapitres plus tard
}

# ==================== PROMPT ====================
SYSTEM_PROMPT = """Tu es un professeur de maths 7ème M (livre ITEM 062). 
Utilise EXACTEMENT la méthodologie du livre. Réponds avec LaTeX ($2x^2$, $\\frac{1}{2}$, etc.).
Quand tu analyses la réponse de l'élève, dis précisément où est l'erreur et propose un rappel simplifié + exercice plus facile si besoin."""

def ask_prof(prompt, full_context=""):
    if not st.session_state.client:
        return "❌ Sauvegarde ta clé d'abord."
    chat = st.session_state.client.chat.completions.create(
        messages=[{"role": "system", "content": SYSTEM_PROMPT + "\nContexte livre :\n" + full_context[:80000]},
                  {"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.6,
        max_tokens=2048
    )
    return chat.choices[0].message.content

# ==================== INTERFACE ====================
tab1, tab2, tab3 = st.tabs(["📚 Charger le livre", "💬 Exercices par Chapitre", "📊 Vision 360°"])

with tab1:
    uploaded = st.file_uploader("Charge ton livre complet (ITEM 062...pdf)", type="pdf", accept_multiple_files=True)
    if st.button("🚀 Indexer tout le livre"):
        with st.spinner("Lecture du livre de 199 pages..."):
            text = ""
            for f in uploaded:
                reader = PdfReader(f)
                if reader.is_encrypted: reader.decrypt("")
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
            st.session_state.full_context = text
            st.success("✅ Livre complet indexé ! Tu peux choisir n'importe quel chapitre.")

with tab2:
    st.subheader("Choisis le chapitre puis la partie précise")
    
    chapitre = st.selectbox("Chapitre du livre", list(chapitres.keys()))
    sous_partie = st.selectbox("Partie à travailler", chapitres[chapitre])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ Générer exercice"):
            exercice = ask_prof(f"Génère un exercice neuf sur : {sous_partie} (Chapitre {chapitre}). Donne seulement l'énoncé clair en LaTeX.")
            st.session_state.current_exercice = exercice
            st.session_state.current_competence = f"{chapitre} - {sous_partie}"
            st.success("Exercice généré ! Lis-le bien puis réponds ci-dessous.")
            st.markdown(exercice)
    
    with col2:
        st.subheader("Ta réponse")
        student_answer = st.text_area("Écris ta solution ici (prends ton temps)", height=150)
        
        if st.button("📤 Corriger ma réponse"):
            if "current_exercice" not in st.session_state:
                st.error("Génère d'abord un exercice")
            else:
                correction = ask_prof(
                    f"Analyse cette réponse de l'élève pour l'exercice sur {st.session_state.current_competence}. "
                    f"Dis précisément l'erreur (ou bravo). Propose un rappel simplifié + un exercice plus facile si besoin.",
                    student_answer=student_answer
                )
                st.markdown(correction)
                
                # Mise à jour couleurs
                comp = st.session_state.current_competence
                if comp not in st.session_state.mastery:
                    st.session_state.mastery[comp] = {"errors": 0}
                
                if any(word in correction.lower() for word in ["erreur", "faute", "incorrect", "mauvais"]):
                    st.session_state.mastery[comp]["errors"] += 1
                
                st.success(f"**{comp}** → {get_color(st.session_state.mastery[comp]['errors'])}")

with tab3:
    st.subheader("Vision 360° – Maîtrise par partie")
    if st.session_state.mastery:
        for comp, data in st.session_state.mastery.items():
            st.write(f"{get_color(data['errors'])} **{comp}**")
    else:
        st.info("Fais des exercices pour voir les couleurs apparaître")

st.caption("BacProf-AI v6.2 – Choix par chapitre + temps pour répondre + couleurs erreurs")
