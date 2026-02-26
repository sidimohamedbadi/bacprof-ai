import streamlit as st

st.set_page_config(page_title="BacProf-AI", page_icon="🎓", layout="wide")

# Thème sombre moderne
st.markdown("""
<style>
    .main {background-color: #0a0f1c;}
    .card {background-color: #1e2937; padding: 24px; border-radius: 16px; margin: 16px 0;}
    .title {font-size: 28px; font-weight: 700; color: #e2e8f0;}
    .bar-label {font-size: 15px; color: #94a3b8; margin-bottom: 6px;}
</style>
""", unsafe_allow_html=True)

st.title("🎓 BacProf-AI")
st.caption("Ton coach personnel pour le Bac – Design 2026")

# Retour aux matières
if st.button("← Retour aux matières"):
    if "current_matiere" in st.session_state:
        st.session_state.current_matiere = None

# Choix matière
if "current_matiere" not in st.session_state or st.session_state.current_matiere is None:
    st.subheader("Choisis ta matière")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📐 Mathématiques", use_container_width=True, type="primary"):
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
    st.subheader(f"📚 {st.session_state.current_matiere}")

    # Chapitres avec 2 barres courtes et propres
    chapitres = {
        "Chapitre 1 : Systèmes linéaires": {"progress": 85, "mastery": 1},   # 1=vert
        "Chapitre 5 : Généralités sur les fonctions": {"progress": 45, "mastery": 4}, # 4=rouge
        "Chapitre 6 : Logarithme & Exponentielle": {"progress": 70, "mastery": 2},
        "Chapitre 7 : Calcul intégral": {"progress": 30, "mastery": 3},
        "Chapitre 14 : Coniques": {"progress": 60, "mastery": 1},
    }

    mastery_colors = ["#22c55e", "#eab308", "#f97316", "#ef4444"]  # vert, jaune, orange, rouge

    for ch, data in chapitres.items():
        mastery_color = mastery_colors[data["mastery"]-1]
        mastery_width = max(15, 100 - data["mastery"] * 22)   # barre courte quand faible

        with st.container():
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"**{ch}**")
            
            st.caption("Progression du chapitre")
            st.progress(data["progress"]/100)
            
            st.caption("Niveau de maîtrise")
            st.progress(mastery_width/100, text=f"{mastery_color.replace('#','')}")

            st.markdown("</div>", unsafe_allow_html=True)

st.caption("BacProf-AI v9.3 – Design propre & lisible")
