import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
from typing import List, Dict

st.set_page_config(page_title="BacProf-AI", page_icon="🎓", layout="wide")
st.title("🎓 BacProf-AI – Ton vrai prof IA pour le Bac Terminale")

# ==================== CONFIGURATION ====================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input(
    "🔑 Colle ta clé API Gemini (gratuite)",
    value=st.session_state.api_key,
    type="password",
    help="Va sur https://aistudio.google.com/app/apikey → Create API key"
)

if api_key:
    st.session_state.api_key = api_key
    genai.configure(api_key=api_key)

# Modèle embeddings (très rapide)
@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

embedder = get_embedding_model()

# ==================== STOCKAGE SESSION ====================
if "documents" not in st.session_state:
    st.session_state.documents = []
if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "mastery" not in st.session_state:  # Vision 360°
    st.session_state.mastery = {}  # {"compétence": {"color": "vert", "errors": 0}}
if "history" not in st.session_state:
    st.session_state.history = []

# ==================== FONCTIONS ====================
def extract_text_from_pdfs(files):
    text = ""
    for file in files:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
    return text

def split_text(text: str) -> List[str]:
    # Découpage intelligent
    splitter = text.split("\n\n")
    chunks = [c.strip() for c in splitter if len(c.strip()) > 50]
    return chunks

def build_faiss_index(chunks):
    embeddings = embedder.encode(chunks, show_progress_bar=False)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    return index, embeddings

def retrieve_context(query: str, k=5) -> str:
    if st.session_state.faiss_index is None:
        return "Aucun cours chargé pour l'instant."
    query_emb = embedder.encode([query])
    D, I = st.session_state.faiss_index.search(query_emb.astype('float32'), k)
    context = "\n\n".join([st.session_state.chunks[i] for i in I[0]])
    return context

# Prompt système ultra-puissant (le "vrai prof agrégé")
SYSTEM_PROMPT = """Tu es un professeur agrégé de Terminale qui prépare le Bac depuis 20 ans.
Tu suis EXACTEMENT la méthodologie des cours et des annales corrigées que l'élève a uploadées.
Règles strictes :
- Utilise uniquement les méthodes présentes dans les documents fournis.
- Réponds toujours avec les mêmes étapes numérotées, les mêmes notations et phrases que dans les corrigés officiels.
- Quand tu crées un exercice, il doit être 100% neuf mais dans le même style BAC.
- Analyse les erreurs de l'élève et dis-lui précisément quel point il n'a pas maîtrisé.
- Utilise le contexte ci-dessous pour répondre.

Contexte des cours et annales :
{context}
"""

def ask_prof(prompt: str, exercice_mode=False):
    if not api_key:
        return "❌ Mets ta clé Gemini d'abord."
    
    context = retrieve_context(prompt)
    full_prompt = SYSTEM_PROMPT.format(context=context) + "\n\nQuestion de l'élève : " + prompt
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(full_prompt)
    return response.text

# ==================== INTERFACE ====================
tab1, tab2, tab3 = st.tabs(["📚 Charger mes cours & annales", "💬 Chat avec mon prof IA", "📊 Ma vision 360°"])

with tab1:
    st.subheader("Charge tous tes PDFs (cours + annales corrigées)")
    uploaded_files = st.file_uploader("Sélectionne tous tes fichiers PDF", type="pdf", accept_multiple_files=True)
    
    if st.button("🚀 Indexer tout le programme", type="primary"):
        if uploaded_files:
            with st.spinner("Lecture des PDFs + création de la base de connaissance..."):
                full_text = extract_text_from_pdfs(uploaded_files)
                st.session_state.chunks = split_text(full_text)
                st.session_state.faiss_index, _ = build_faiss_index(st.session_state.chunks)
                st.success(f"✅ {len(st.session_state.chunks)} morceaux de cours indexés ! Tu peux maintenant discuter avec ton prof.")
        else:
            st.error("Charge au moins un PDF")

with tab2:
    st.subheader("Pose n'importe quelle question ou demande un exercice")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ Génère un exercice sur..."):
            sujet = st.text_input("Sur quel chapitre / notion ?", "dérivées fonctions", key="sujet")
            if sujet:
                response = ask_prof(f"Génère un exercice complet NEUF sur : {sujet}. Donne l'énoncé puis la correction détaillée avec la méthodologie exacte du cours.", exercice_mode=True)
                st.write(response)
    
    with col2:
        if st.button("📝 Analyse mon erreur"):
            erreur = st.text_area("Colle ici ta réponse ou ton erreur", height=100)
            if erreur:
                response = ask_prof(f"Analyse cette réponse de l'élève et dis-moi précisément les lacunes et comment corriger avec la méthode du cours : {erreur}")
                st.write(response)
                # Mise à jour couleurs erreurs (prototype simple)
                st.session_state.mastery["Exemple compétence"] = {"color": "orange", "errors": 2}

    # Chat classique
    user_input = st.chat_input("Demande un exercice, une explication, etc.")
    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Ton prof réfléchit..."):
                answer = ask_prof(user_input)
                st.markdown(answer)
        
        st.session_state.history.append({"role": "assistant", "content": answer})

with tab3:
    st.subheader("📊 Ma vision 360° – Ce que je maîtrise vraiment")
    if not st.session_state.mastery:
        st.info("Commence à faire des exercices pour voir les couleurs apparaître")
    else:
        for comp, data in st.session_state.mastery.items():
            color = data["color"]
            emoji = "🟢" if color == "vert" else "🟠" if color == "orange" else "🔴"
            st.write(f"{emoji} **{comp}** — {data['errors']} erreurs détectées")

st.caption("BacProf-AI Prototype v1 – Créé avec ❤️ pour les Terminales 2026")
