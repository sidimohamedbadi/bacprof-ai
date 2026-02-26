import streamlit as st

st.set_page_config(page_title="BacProf-AI", page_icon="🎓", layout="wide")

# CSS moderne 2026
st.markdown("""
<style>
    .main {background-color: #0a0e17;}
    .card {background: linear-gradient(135deg, #1e2538, #161d2e); padding: 24px; border-radius: 20px; margin: 12px 0; border: 1px solid #2a3550;}
    .matiere-card {background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; border-radius: 20px; text-align: center; cursor: pointer;}
    .progress-container {margin: 12px 0;}
    .mastery-bar {height: 12px; border-radius: 9999px; margin-top: 6px;}
</style>
""", unsafe_allow_html=True)

st.title("🎓 BacProf-AI")
st.markdown("**Ton coach personnel pour le Bac**")

# Navigation Matière
if "current_matiere" not in st.session_state:
    st.session_state.current_matiere = None

if not st.session_state.current_matiere:
    st.subheader("Choisis ta matière")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📐 Mathématiques", key="maths_btn"):
            st.session_state.current_matiere = "Mathématiques"
            st.rerun()
    with col2:
        if st.button("⚡ Physique", key="phys_btn"):
            st.session_state.current_matiere = "Physique"
            st.rerun()
    with col3:
        if st.button("🧪 Sciences", key="sci_btn"):
            st.session_state.current_matiere = "Sciences"
            st.rerun()

else:
    st.button("← Retour aux matières", on_click=lambda: setattr(st.session_state, 'current_matiere', None))
    
    st.subheader(f"📚 {st.session_state.current_matiere}")
    
    # Exemple de chapitres pour Maths (tu peux compléter pour Physique et Sciences)
    chapitres = {
        "Chapitre 1 : Systèmes linéaires": {"progress": 85, "mastery": 3},
        "Chapitre 5 : Généralités sur les fonctions": {"progress": 45, "mastery": 4},
        "Chapitre 6 : Logarithme & Exponentielle": {"progress": 70, "mastery": 2},
        "Chapitre 7 : Calcul intégral": {"progress": 30, "mastery": 4},
        "Chapitre 14 : Coniques": {"progress": 60, "mastery": 1},
    }
    
    for ch, data in chapitres.items():
        color = ["#22c55e", "#eab308", "#f97316", "#ef4444"][data["mastery"]-1]
        
        st.markdown(f"""
        <div class="card">
            <h3>{ch}</h3>
            <div class="progress-container">
                Progression du chapitre : {data["progress"]}%
                <div style="height:8px; background:#334155; border-radius:9999px; margin:8px 0;">
                    <div style="width:{data['progress']}%; height:100%; background:#60a5fa; border-radius:9999px;"></div>
                </div>
            </div>
            <div>Niveau de maîtrise :</div>
            <div class="mastery-bar" style="background:{color}; width:{100 - data['mastery']*20}%;"></div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.caption("BacProf-AI v9 – Design moderne 2026 | Développé avec toi")
