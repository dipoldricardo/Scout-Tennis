import streamlit as st
import pandas as pd

# Configuração de Página Nível ATP - Marco "The Precision" Valente
st.set_page_config(
    page_title="Scout-Tennis Pro",
    page_icon="🎾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 70px;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
    }
    .main-score {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 15px;
        border: 2px solid #333;
        text-align: center;
        margin-bottom: 20px;
    }
    .player-name { color: #FFFFFF; font-size: 22px; font-weight: bold; }
    .score-value { color: #00FF00; font-size: 28px; font-weight: bold; }
    .server-icon { color: #DFFF00; font-size: 20px; margin-left: 10px; }
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

def format_pts(p):
    return {0: "0", 1: "15", 2: "30", 3: "40", 4: "AD"}.get(p, "40")

def register_point(winner, res, cat="Winner", golpe="Saque", dir_g="N/A", pos="N/A"):
    # Atualiza Placar
    if winner == st.session_state.setup['p1']: st.session_state.score["p1_pts"] += 1
    else: st.session_state.score["p2_pts"] += 1
    
    # Grava na Base
    sacador = st.session_state.setup['p1'] if st.session_state.setup['server'] == 1 else st.session_state.setup['p2']
    st.session_state.match_data.append({
        "Sacador": sacador, "Vencedor": winner, "Saque": f"{st.session_state.serve_num}º", 
        "Dir_Saque": st.session_state.temp_data.get('dir', "N/A"), "Resultado": res,
        "Categoria": cat, "Golpe": golpe, "Direcao": dir_g, "Posicao": pos
    })
    
    # Reset Total de Ciclo
    st.session_state.step = "SERVICE"
    st.session_state.serve_num = 1
    st.session_state.temp_data = {}

# --- 1. SETUP (SEM ST.FORM PARA EVITAR ERROS) ---
if not st.session_state.setup["active"]:
    st.title("🎾 Scout-Tennis Pro")
    st.subheader("Configuração da Partida")
    
    with st.container(border=True):
        p1_input = st.text_input("Atleta A", "Atleta 1")
        p2_input = st.text_input("Atleta B", "Atleta 2")
        server_choice = st.radio("Quem inicia sacando?", [p1_input, p2_input], horizontal=True)
        
        if st.button("🚀 INICIAR PARTIDA", type="primary"):
            srv_idx = 1 if server_choice == p1_input else 2
            st.session_state.setup.update({
                "active": True, 
                "p1": p1_input, 
                "p2": p2_input, 
                "server": srv_idx
            })
            st.rerun()

# --- 2. SCOUTING ---
else:
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    srv_idx = st.session_state.setup['server']
    sacador_atual = p1_n if srv_idx == 1 else p2_n
    recebedor_atual = p2_n if srv_idx == 1 else p1_n
    
    st.markdown(f"""
    <div class="main-score">
        <div class="player-name">{p1_n}{" 🎾" if srv_idx == 1 else ""}</div>
        <div class="score-value">{s['p1_sets']} | {s['p1_gms']} ({format_pts(s['p1_pts'])})</div>
        <hr style="border: 0.5px solid #444; margin: 10px 0;">
        <div class="player-name">{p2_n}{" 🎾" if srv_idx == 2 else ""}</div>
        <div class="score-value">{s['p2_sets']} | {s['p2_gms']} ({format_pts(s['p2_pts'])})</div>
    </div>
    """, unsafe_allow_html=True)

    # FASE 1: SERVIÇO
    if st.session_state.step == "SERVICE":
        st.markdown(f"<div class='step-title'>Saque: {sacador_atual} ({st.session_state.serve_num}º)</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button("WIDE ↙️"): st.session_state.temp_data['dir'] = "Wide"; st.session_state.step = "RESULT"; st.rerun()
        if c2.button("BODY 👤"): st.session_state.temp_data['dir'] = "Body"; st.session_state.step = "RESULT"; st.rerun()
        if c3.button("T ⬇️"): st.session_state.temp_data['dir'] = "T"; st.session_state.step = "RESULT"; st.rerun()
        if st.button("❌ FALTA / NET"):
            if st.session_state.serve_num == 1: st.session_state.serve_num = 2; st.rerun()
            else: register_point(recebedor_atual, "Dupla Falta", "Erro"); st.rerun()

    # FASE 2: DESFECHO
    elif st.session_state.step == "RESULT":
        st.markdown("<div class='step-title'>Desfecho do Ponto</div>", unsafe_allow_html=True)
        cr1, cr2 = st.columns(2)
        if cr1.button("🏆 WINNER (Rali)", type="primary"): 
            st.session_state.temp_data['res'] = "Winner"; st.session_state.temp_data['cat'] = "Winner"; st.session_state.step = "WINNER_PICK"; st.rerun()
        if cr2.button("📉 ERRO (Rali)"): 
            st.session_state.temp_data['res'] = "Erro"; st.session_state.step = "ERR_CAT"; st.rerun()
        
        st.divider()
        cs1, cs2 = st.columns(2)
        if cs1.button("🎯 ACE"): register_point(sacador_atual, "Ace"); st.rerun()
        if cs2.button("🎾 SERVICE WINNER"): register_point(sacador_atual, "Service Winner"); st.rerun()

    # FASE 3: TIPO DE ERRO
    elif st.session_state.step == "ERR_CAT":
        st.markdown("<div class='step-title'>Tipo de Erro</div>", unsafe_allow_html=True)
        ce1, ce2 = st.columns(2)
        if ce1.button("🐢 NÃO FORÇADO"): st.session_state.temp_data['cat'] = "Unforced"; st.session_state.step = "WINNER_PICK"; st.rerun()
        if ce2.button("💥 FORÇADO"): st.session_state.temp_data['cat'] = "Forced"; st.session_state.step = "WINNER_PICK"; st.rerun()

    # FASE 4: TÁTICA (RALI)
    elif st.session_state.step == "WINNER_PICK":
        st.markdown("<div class='step-title'>Finalização</div>", unsafe_allow_html=True)
        winner_choice = st.radio("Vencedor:", [p1_n, p2_n], horizontal=True)
        col1, col2 = st.columns(2)
        golpe_choice = col1.selectbox("Golpe", ["Forehand", "Backhand", "Voleio", "Smash", "Drop Shot"])
        
        # Trava de Voleio
        if golpe_choice == "Voleio":
            pos_choice = col2.radio("Posição", ["Rede"], index=0)
        else:
            pos_choice = col2.radio("Posição", ["Baseline", "Rede"])
            
        dir_choice = st.radio("Direção", ["Cruzada", "Paralela"], horizontal=True)
        
        if st.button("✅ REGISTRAR", type="primary"):
            register_point(winner_choice, st.session_state.temp_data['res'], st.session_state.temp_data['cat'], golpe_choice, dir_choice, pos_choice)
            st.rerun()

    st.divider()
    cf1, cf2 = st.columns(2)
    if cf1.button("🔄 UNDO"):
        if st.session_state.match_data: st.session_state.match_data.pop(); st.rerun()
    if cf2.button("🎾 ALTERNAR SAQUE"):
        st.session_state.setup['server'] = 2 if srv_idx == 1 else 1; st.rerun()
    
    if st.button("📥 EXPORTAR CSV"):
        df = pd.DataFrame(st.session_state.match_data)
        st.download_button("Baixar Dados", df.to_csv(index=False), "scout_pro.csv", "text/csv")