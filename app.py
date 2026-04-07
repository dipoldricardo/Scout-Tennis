import streamlit as st
import pandas as pd

# Configuração de Página Nível ATP - Marco "The Precision" Valente
st.set_page_config(page_title="Scout-Tennis | High Performance", layout="centered")

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'match_data' not in st.session_state:
    st.session_state.match_data = []
if 'score' not in st.session_state:
    st.session_state.score = {
        "p1_points": 0, "p2_points": 0, 
        "p1_games": 0, "p2_games": 0, 
        "p1_sets": 0, "p2_sets": 0
    }
if 'setup' not in st.session_state:
    st.session_state.setup = {"active": False, "p1_name": "", "p2_name": "", "format": ""}
if 'step' not in st.session_state:
    st.session_state.step = "Service"

def format_tennis_score(pts):
    labels = {0: "0", 1: "15", 2: "30", 3: "40", 4: "AD"}
    return labels.get(pts, "40")

# --- INTERFACE DE SETUP ---
if not st.session_state.setup["active"]:
    st.title("🎾 Scout-Tennis: Painel de Controle")
    with st.form("setup_form"):
        p1 = st.text_input("Nome Jogador/Dupla A", "Atleta 1")
        p2 = st.text_input("Nome Jogador/Dupla B", "Atleta 2")
        fmt = st.selectbox("Formato", ["Set Único", "Melhor de 3", "Melhor de 5"])
        if st.form_submit_button("INICIAR PARTIDA"):
            st.session_state.setup.update({"active": True, "p1_name": p1, "p2_name": p2, "format": fmt})
            st.rerun()

# --- INTERFACE DE SCOUTING ---
else:
    s = st.session_state.score
    p1 = st.session_state.setup["p1_name"]
    p2 = st.session_state.setup["p2_name"]
    
    # Placar Visual
    st.markdown(f"""
    <div style="background-color: #0e1117; padding: 15px; border-radius: 10px; border: 1px solid #31333f; text-align: center;">
        <h3 style="margin:0;">{p1}: {s['p1_sets']} sets | {s['p1_games']} ({format_tennis_score(s['p1_points'])})</h3>
        <h3 style="margin:0;">{p2}: {s['p2_sets']} sets | {s['p2_games']} ({format_tennis_score(s['p2_points'])})</h3>
    </div>
    """, unsafe_allow_html=True)

    # FLUXO DE SCOUT
    if st.session_state.step == "Service":
        st.subheader("📍 Direção do Saque")
        c1, c2, c3 = st.columns(3)
        if c1.button("WIDE", use_container_width=True): 
            st.session_state.last_serve, st.session_state.step = "Wide", "Result"
            st.rerun()
        if c2.button("BODY", use_container_width=True): 
            st.session_state.last_serve, st.session_state.step = "Body", "Result"
            st.rerun()
        if c3.button("T", use_container_width=True): 
            st.session_state.last_serve, st.session_state.step = "T", "Result"
            st.rerun()

    elif st.session_state.step == "Result":
        st.subheader("🎯 Desfecho")
        res_c1, res_c2 = st.columns(2)
        if res_c1.button("🏆 WINNER", type="primary", use_container_width=True):
            st.session_state.last_res, st.session_state.step = "Winner", "Context"
            st.rerun()
        if res_c2.button("📉 ERRO", type="secondary", use_container_width=True):
            st.session_state.last_res, st.session_state.step = "ErrorType"
            st.rerun()

    elif st.session_state.step == "ErrorType":
        st.subheader("❌ Qualificação do Erro")
        e1, e2 = st.columns(2)
        if e1.button("NÃO FORÇADO", use_container_width=True):
            st.session_state.err_cat, st.session_state.step = "Unforced", "Context"
            st.rerun()
        if e2.button("FORÇADO", use_container_width=True):
            st.session_state.err_cat, st.session_state.step = "Forced", "Context"
            st.rerun()

    elif st.session_state.step == "Context":
        st.subheader("📊 Detalhes Finais")
        winner_pt = st.radio("Ponto para:", [p1, p2], horizontal=True)
        golpe = st.selectbox("Golpe", ["Forehand", "Backhand", "Voleio", "Smash", "Drop Shot"])
        dir_g = st.radio("Direção", ["Cruzada", "Paralela"], horizontal=True)
        pos = st.radio("Posição", ["Baseline", "Rede"], horizontal=True)
        
        if st.button("REGISTRAR PONTO", use_container_width=True, type="primary"):
            # Atualiza Placar (Simplificado)
            if winner_pt == p1: st.session_state.score["p1_points"] += 1
            else: st.session_state.score["p2_points"] += 1
            
            st.session_state.match_data.append({
                "Vencedor": winner_pt, "Saque": st.session_state.last_serve, 
                "Tipo": st.session_state.last_res, "Golpe": golpe, "Direção": dir_g, "Posição": pos
            })
            st.session_state.step = "Service"
            st.rerun()

    st.divider()
    if st.button("📥 BAIXAR SCOUT (CSV/PDF)"):
        df = pd.DataFrame(st.session_state.match_data)
        st.download_button("Clique para Download", df.to_csv(index=False), "scout-tennis-report.csv", "text/csv")