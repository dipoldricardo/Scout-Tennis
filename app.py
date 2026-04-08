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
    mapping = {0: "0", 1: "15", 2: "30", 3: "40"}
    if p1 <= 3 and p2 <= 3:
        if p1 == 3 and p2 == 3: return "40", "40"
        return mapping[p1], mapping[p2]
    if p1 == p2: return "40", "40"
    return ("AD", "40") if p1 > p2 else ("40", "AD")

def register_point(winner_name, res, cat="Winner", golpe="Saque", dir_g="N/A", pos="N/A"):
    s = st.session_state.score
    p1_n = st.session_state.setup['p1']
    p2_n = st.session_state.setup['p2']
    
    # 1. Atualiza Pontos do Game
    if winner_name == p1_n: s["p1_pts"] += 1
    else: s["p2_pts"] += 1
        
    # 2. Checa Fechamento de Game
    p1_p, p2_p = s["p1_pts"], s["p2_pts"]
    if (p1_p >= 4 and p1_p - p2_p >= 2) or (p2_p >= 4 and p2_p - p1_p >= 2):
        if p1_p > p2_p: s["p1_gms"] += 1
        else: s["p2_gms"] += 1
        s["p1_pts"], s["p2_pts"] = 0, 0 # Reseta pontos
        st.session_state.setup['server'] = 2 if st.session_state.setup['server'] == 1 else 1 # Alterna saque
        
        # 3. Checa Fechamento de Set (ex: 6-2 ou 7-5 ou 7-6)
        g1, g2 = s["p1_gms"], s["p2_gms"]
        set_won = False
        if (g1 >= 6 and g1 - g2 >= 2) or (g1 == 7):
            s["p1_sets"] += 1
            set_won = True
        elif (g2 >= 6 and g2 - g1 >= 2) or (g2 == 7):
            s["p2_sets"] += 1
            set_won = True
            
        if set_won:
            s["p1_gms"], s["p2_gms"] = 0, 0 # Reseta games para o novo set

    # 4. Grava Dados
    sacador = p1_n if st.session_state.setup['server'] == 1 else p2_n
    st.session_state.match_data.append({
        "Sacador": sacador, "Vencedor": winner_name, "Saque": f"{st.session_state.serve_num}º",
        "Resultado": res, "Categoria": cat, "Golpe": golpe, "Direcao": dir_g, "Posicao": pos,
        "Placar": f"S:{s['p1_sets']}-{s['p2_sets']} G:{s['p1_gms']}-{s['p2_gms']}"
    })
    
    # Reset Fluxo UI
    st.session_state.step = "SERVICE"
    st.session_state.serve_num = 1
    st.session_state.temp_data = {}

# --- SETUP E INTERFACE ---
if not st.session_state.setup["active"]:
    st.title("🎾 Scout-Tennis Pro")
    with st.container(border=True):
        p1_in = st.text_input("Atleta A", "Atleta 1")
        p2_in = st.text_input("Atleta B", "Atleta 2")
        srv_in = st.radio("Inicia sacando:", [p1_in, p2_in], horizontal=True)
        if st.button("🚀 INICIAR"):
            st.session_state.setup.update({"active": True, "p1": p1_in, "p2": p2_in, "server": 1 if srv_in == p1_in else 2})
            st.rerun()
else:
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    srv_idx = st.session_state.setup['server']
    sacador_at = p1_n if srv_idx == 1 else p2_n
    recebedor_at = p2_n if srv_idx == 1 else p1_n
    pt1, pt2 = format_pts(s["p1_pts"], s["p2_pts"])
    
    st.markdown(f"""<div class="main-score">
        <div style="color:#AAAAAA; font-size:12px;">SETS: {s['p1_sets']} - {s['p2_sets']}</div>
        <div class="player-name">{p1_n}{" 🎾" if srv_idx == 1 else ""}</div>
        <div class="score-value">{s['p1_gms']} ({pt1})</div>
        <hr style="border: 0.5px solid #444; margin: 10px 0;">
        <div class="player-name">{p2_n}{" 🎾" if srv_idx == 2 else ""}</div>
        <div class="score-value">{s['p2_gms']} ({pt2})</div>
    </div>""", unsafe_allow_html=True)

    if st.session_state.step == "SERVICE":
        st.markdown(f"<div class='step-title'>Saque: {sacador_at} ({st.session_state.serve_num}º)</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button("WIDE"): st.session_state.temp_data['dir_saque'] = "Wide"; st.session_state.step = "RESULT"; st.rerun()
        if c2.button("BODY"): st.session_state.temp_data['dir_saque'] = "Body"; st.session_state.step = "RESULT"; st.rerun()
        if c3.button("T"): st.session_state.temp_data['dir_saque'] = "T"; st.session_state.step = "RESULT"; st.rerun()
        if st.button("❌ FALTA"):
            if st.session_state.serve_num == 1: st.session_state.serve_num = 2; st.rerun()
            else: register_point(recebedor_at, "Dupla Falta", "Erro"); st.rerun()

    elif st.session_state.step == "RESULT":
        st.markdown("<div class='step-title'>Desfecho</div>", unsafe_allow_html=True)
        cr1, cr2 = st.columns(2)
        if cr1.button("🏆 WINNER", type="primary"): 
            st.session_state.temp_data['res'] = "Winner"; st.session_state.temp_data['cat'] = "Winner"; st.session_state.step = "WINNER_PICK"; st.rerun()
        if cr2.button("📉 ERRO"): 
            st.session_state.temp_data['res'] = "Erro"; st.session_state.step = "ERR_CAT"; st.rerun()
        st.divider()
        if st.button("🎯 ACE"): register_point(sacador_at, "Ace"); st.rerun()
        if st.button("🎾 S. WINNER"): register_point(sacador_at, "Service Winner"); st.rerun()

    elif st.session_state.step == "ERR_CAT":
        ce1, ce2 = st.columns(2)
        if ce1.button("🐢 NÃO FORÇADO"): st.session_state.temp_data['cat'] = "Unforced"; st.session_state.step = "WINNER_PICK"; st.rerun()
        if ce2.button("💥 FORÇADO"): st.session_state.temp_data['cat'] = "Forced"; st.session_state.step = "WINNER_PICK"; st.rerun()

    elif st.session_state.step == "WINNER_PICK":
        winner_choice = st.radio("Vencedor:", [p1_n, p2_n], horizontal=True)
        col1, col2 = st.columns(2)
        golpe_choice = col1.selectbox("Golpe", ["Forehand", "Backhand", "Voleio", "Smash", "Drop Shot"])
        pos_choice = col2.radio("Posição", ["Rede"] if golpe_choice == "Voleio" else ["Baseline", "Rede"])
        dir_choice = st.radio("Direção", ["Cruzada", "Paralela"], horizontal=True)
        if st.button("✅ REGISTRAR"):
            register_point(winner_choice, st.session_state.temp_data['res'], st.session_state.temp_data['cat'], golpe_choice, dir_choice, pos_choice)
            st.rerun()

    st.divider()
    cf1, cf2 = st.columns(2)
    if cf1.button("🔄 UNDO"):
        if st.session_state.match_data: st.session_state.match_data.pop(); st.rerun()
    if cf2.button("📥 EXPORTAR CSV"):
        df = pd.DataFrame(st.session_state.match_data)
        st.download_button("Baixar", df.to_csv(index=False), "scout.csv", "text/csv")