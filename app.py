import streamlit as st

st.set_page_config(page_title="BacProf-AI", page_icon="🎓", layout="wide")

# CSS moderne propre
st.markdown("""
<style>
    .main {background-color: #0a0f1c; color: #e2e8f0;}
    .card {background-color: #1e2937; padding: 24px; border-radius: 16px; margin: 16px 0; border: 1px solid #334155;}
    .bar-container {margin: 12px 0;}
    .progress-bar {height: 10px; background: #334155; border-radius: 9999px; overflow: hidden;}
    .progress-fill {height: 100%; background: #60a5fa;}
    .mastery-bar {height: 10px; border-radius: 9999px; margin-top: 6px;}
    h3 {color: #f1f5f9;}
</style>
""", unsafe_allow_html=True)

st.title("🎓 BacProf-AI")
st.caption("Ton coach personnel pour le Bac – Design 2026")

if "current_matiere" not in st.session_state:
    st.session_state.current_matiere = None

if not st.session_state.current_matiere:
    st.subheader("Choisis ta matière")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📐 Mathématiques", use_container_width=True):
            st.session_state.current_matiere = "Mathématiques"
            st.rerun()
    with col2:
        if st.button("⚡ Physique", use_container_width=True):
            st.session_state.current_matiere = "Physique"
            st.rerun()
    with col3:
        if st.button("🧪 Sciences", use_container_width=True):
            st.session_state.current_matiere = "Sciences"
            st.rerun()
else:
    if st.button("← Retour aux matières"):
        st.session_state.current_matiere = None
        st.rerun()
    
    st.subheader(f"📚 {st.session_state.current_matiere}")

    # Exemple de chapitres (tu peux ajouter tous les 15)
    chapitres = {
        "Chapitre 1 : Systèmes linéaires": {"progress": 85, "mastery": 1},   # 1 = vert
        "Chapitre 5 : Généralités sur les fonctions": {"progress": 45, "mastery": 4}, # 4 = rouge
        "Chapitre 6 : Logarithme & Exponentielle": {"progress": 70, "mastery": 2},
        "Chapitre 7 : Calcul intégral": {"progress": 30, "mastery": 3},
    }
    
    colors = ["#22c55e", "#eab308", "#f97316", "#ef4444"]  # vert, jaune, orange, rouge

    for ch, data in chapitres.items():
        mastery_color = colors[data["mastery"]-1]
        mastery_width = 100 - (data["mastery"] * 20)   # plus d'erreurs = barre plus courte
        
        st.markdown(f"""
        <div class="card">
            <h3>{ch}</h3>
            
            <div class="bar-container">
                Progression du chapitre : <strong>{data["progress"]}%</strong>
                <div class="progress-bar"><div class="progress-fill" style="width:{data['progress']}%;"></div></div>
            </div>
            
            <div class="bar-container">
                Niveau de maîtrise :
                <div class="mastery-bar" style="background:{mastery_color}; width:{mastery_width}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.caption("BacProf-AI v9.2 – Design moderne & lisible | Développé avec toi")
