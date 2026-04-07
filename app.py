import streamlit as st
import pandas as pd

# Configuração de Página Nível ATP - Marco "The Precision" Valente
st.set_page_config(
    page_title="Scout-Tennis Pro",
    page_icon="🎾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO CUSTOMIZADA ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%; height: 70px; font-size: 18px !important;
        font-weight: bold !important; border-radius: 12px !important; margin-bottom: 8px !important;
    }
    .main-score {
        background-color: #1E1E1E; padding: 15px; border-radius: 15px;
        border: 2px solid #333; text-align: center; margin-bottom: 20px;
    }
    .player-name { color: #FFFFFF; font-size: 22px; font-weight: bold; }
    .score-value { color: #00FF00; font-size: 28px; font-weight: bold; }
    .step-title { color: #AAAAAA; text-transform: uppercase; letter-spacing: 1.5px; font-size: 12px; text-align: center; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'match_data' not in st.session_state:
    st.session_state.match_data = []
if 'score' not in st.session_state:
    st.session_state.score = {"p1_pts": 0, "p2_pts": 0, "p1_gms": 0, "p2_gms": 0, "p1_sets": 0, "p2_sets": 0}
if 'setup' not in st.session_state:
    st.session_state.setup = {"active": False, "p1": "Jogador A", "p2": "Jogador B", "server": 1}
if 'step' not in st.session_state:
    st.session_state.step = "SERVICE"
if 'serve_num' not in st.session_state:
    st.session_state.serve_num = 1
if 'temp_data' not in st.session_state:
    st.session_state.temp_data = {}

def format_pts(p1, p2):
    # Tradução de pontos internos para nomenclatura de tênis
    mapping = {0: "0", 1: "15", 2: "30", 3: "40"}
    if p1 <= 3 and p2 <= 3:
        if p1 == 3 and p2 == 3: return "40", "40"
        return mapping[p1], mapping[p2]
    
    # Lógica de Deuce / Vantagem
    if p1 == p2: return "40", "40"
    if p1 > p2: return "AD", "40"
    return "40", "AD"

def register_point(winner_name):
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    
    # Identifica quem ganhou o ponto numericamente
    if winner_name == p1_n:
        s["p1_pts"] += 1
    else:
        s["p2_pts"] += 1
        
    # --- SCORING ENGINE (Lógica de Fechamento de Game) ---
    p1, p2 = s["p1_pts"], s["p2_pts"]
    game_over = False
    
    if p1 >= 4 and (p1 - p2) >= 2:
        s["p1_gms"] += 1
        game_over = True
    elif p2 >= 4 and (p2 - p1) >= 2:
        s["p2_gms"] += 1
        game_over = True
        
    if game_over:
        s["p1_pts"], s["p2_pts"] = 0, 0
        # Alterna sacador automaticamente ao fechar o game
        st.session_state.setup['server'] = 2 if st.session_state.setup['server'] == 1 else 1
    
    # Grava na Base de Dados
    sacador = p1_n if st.session_state.setup['server'] == 1 else p2_n
    st.session_state.match_data.append({
        "Sacador": sacador, "Vencedor": winner_name, "Resultado": st.session_state.temp_data.get('res', 'Rali'),
        "P1_Score": f"{s['p1_gms']}({s['p1_pts']})", "P2_Score": f"{s['p2_gms']}({s['p2_pts']})"
    })
    
    # Reset de Ciclo de Ponto
    st.session_state.step = "SERVICE"
    st.session_state.serve_num = 1
    st.session_state.temp_data = {}

# --- 1. SETUP ---
if not st.session_state.setup["active"]:
    st.title("🎾 Scout-Tennis Pro")
    with st.container(border=True):
        p1_in = st.text_input("Atleta A", "Atleta 1")
        p2_in = st.text_input("Atleta B", "Atleta 2")
        srv_in = st.radio("Inicia sacando:", [p1_in, p2_in], horizontal=True)
        if st.button("🚀 INICIAR"):
            st.session_state.setup.update({"active": True, "p1": p1_in, "p2": p2_in, "server": 1 if srv_in == p1_in else 2})
            st.rerun()

# --- 2. SCOUTING ---
else:
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    srv = st.session_state.setup['server']
    sacador = p1_n if srv == 1 else p2_n
    recebedor = p2_n if srv == 1 else p1_n
    
    pt1, pt2 = format_pts(s["p1_pts"], s["p2_pts"])
    
    st.markdown(f"""
    <div class="main-score">
        <div class="player-name">{p1_n}{" 🎾" if srv == 1 else ""}</div>
        <div class="score-value">{s['p1_gms']} ({pt1})</div>
        <hr style="border: 0.5px solid #444; margin: 10px 0;">
        <div class="player-name">{p2_n}{" 🎾" if srv == 2 else ""}</div>
        <div class="score-value">{s['p2_gms']} ({pt2})</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.step == "SERVICE":
        st.markdown(f"<div class='step-title'>Saque: {sacador} ({st.session_state.serve_num}º)</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button("WIDE"): st.session_state.temp_data['res'] = "Wide"; st.session_state.step = "RESULT"; st.rerun()
        if c2.button("BODY"): st.session_state.temp_data['res'] = "Body"; st.session_state.step = "RESULT"; st.rerun()
        if c3.button("T"): st.session_state.temp_data['res'] = "T"; st.session_state.step = "RESULT"; st.rerun()
        if st.button("❌ FALTA"):
            if st.session_state.serve_num == 1: st.session_state.serve_num = 2; st.rerun()
            else: st.session_state.temp_data['res'] = "Dupla Falta"; register_point(recebedor); st.rerun()

    elif st.session_state.step == "RESULT":
        st.markdown("<div class='step-title'>Desfecho</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button("🏆 WINNER"): st.session_state.step = "WINNER_PICK"; st.rerun()
        if col2.button("📉 ERRO"): st.session_state.step = "WINNER_PICK"; st.rerun()
        st.divider()
        if st.button("🎯 ACE"): st.session_state.temp_data['res'] = "Ace"; register_point(sacador); st.rerun()
        if st.button("🎾 SERVICE WINNER"): st.session_state.temp_data['res'] = "S. Winner"; register_point(sacador); st.rerun()

    elif st.session_state.step == "WINNER_PICK":
        st.markdown("<div class='step-title'>Quem venceu o ponto?</div>", unsafe_allow_html=True)
        w = st.radio("Vencedor:", [p1_n, p2_n], horizontal=True)
        if st.button("✅ REGISTRAR"):
            register_point(w); st.rerun()

    st.divider()
    if st.button("🔄 DESFAZER ÚLTIMO PONTO"):
        if st.session_state.match_data: st.session_state.match_data.pop(); st.rerun()