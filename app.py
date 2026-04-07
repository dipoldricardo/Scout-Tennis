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
    .step-title { color: #AAAAAA; text-transform: uppercase; letter-spacing: 1.5px; font-size: 12px; text-align: center; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
states = {
    'match_data': [],
    'score': {"p1_pts": 0, "p2_pts": 0, "p1_gms": 0, "p2_gms": 0, "p1_sets": 0, "p2_sets": 0},
    'setup': {"active": False, "p1": "Jogador A", "p2": "Jogador B", "fmt": ""},
    'step': "SERVICE",
    'serve_num': 1,
    'temp_data': {}
}

for key, value in states.items():
    if key not in st.session_state:
        st.session_state[key] = value

def format_pts(p):
    return {0: "0", 1: "15", 2: "30", 3: "40", 4: "AD"}.get(p, "40")

# --- 1. SETUP DA PARTIDA ---
if not st.session_state.setup["active"]:
    st.title("🎾 Scout-Tennis Pro")
    st.subheader("Configuração Metodológica")
    
    with st.container(border=True):
        col_a, col_b = st.columns(2)
        p1 = col_a.text_input("Atleta/Dupla A", "Atleta 1")
        p2 = col_b.text_input("Atleta/Dupla B", "Atleta 2")
        
        fmt = st.selectbox("Formato da Disputa", 
                          ["Melhor de 3 Sets", "Melhor de 5 Sets", "Set Único (6 games)", "Pro-Set (8 games)"])
        adv = st.radio("Regra de Vantagem", ["Com Vantagem", "No-Ad (Ponto Decisivo)"], horizontal=True)
        
        if st.button("🚀 INICIAR PARTIDA", type="primary"):
            st.session_state.setup.update({"active": True, "p1": p1, "p2": p2, "fmt": fmt, "adv": adv})
            st.rerun()

# --- 2. INTERFACE DE SCOUTING ---
else:
    s = st.session_state.score
    p1_n = st.session_state.setup['p1']
    p2_n = st.session_state.setup['p2']
    
    st.markdown(f"""
    <div class="main-score">
        <div class="player-name">{p1_n}</div>
        <div class="score-value">{s['p1_sets']} | {s['p1_gms']} ({format_pts(s['p1_pts'])})</div>
        <hr style="border: 0.5px solid #444; margin: 10px 0;">
        <div class="player-name">{p2_n}</div>
        <div class="score-value">{s['p2_sets']} | {s['p2_gms']} ({format_pts(s['p2_pts'])})</div>
    </div>
    """, unsafe_allow_html=True)

    # --- FASE 1: SERVIÇO ---
    if st.session_state.step == "SERVICE":
        st.markdown(f"<div class='step-title'>Fase 1: Direção do {st.session_state.serve_num}º Saque</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        dirs = ["Wide ↙️", "Body 👤", "T ⬇️"]
        val_dirs = ["Wide", "Body", "T"]
        
        for idx, col in enumerate([c1, c2, c3]):
            if col.button(dirs[idx]):
                st.session_state.temp_data['dir'] = val_dirs[idx]
                st.session_state.step = "RESULT"
                st.rerun()
        
        if st.button("❌ FALTA / NET", type="secondary"):
            if st.session_state.serve_num == 1:
                st.session_state.serve_num = 2
                st.rerun()
            else:
                st.session_state.temp_data.update({'res': "Dupla Falta", 'dir': "N/A", 'cat': "Erro"})
                st.session_state.step = "WINNER_PICK"
                st.rerun()

    # --- FASE 2: DESFECHO ---
    elif st.session_state.step == "RESULT":
        st.markdown("<div class='step-title'>Fase 2: Desfecho do Ponto</div>", unsafe_allow_html=True)
        cr1, cr2 = st.columns(2)
        if cr1.button("🏆 WINNER (Rali)", type="primary"):
            st.session_state.temp_data['res'] = "Winner"; st.session_state.temp_data['cat'] = "Winner"
            st.session_state.step = "WINNER_PICK"; st.rerun()
        if cr2.button("📉 ERRO (Rali)"):
            st.session_state.temp_data['res'] = "Erro"; st.session_state.step = "ERR_CAT"; st.rerun()
        
        st.divider()
        st.markdown("<div class='step-title'>Desfecho de Saque</div>", unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        if cs1.button("🎯 ACE (Direto)"):
            st.session_state.temp_data['res'] = "Ace"; st.session_state.temp_data['cat'] = "Winner"
            st.session_state.step = "WINNER_PICK"; st.rerun()
        if cs2.button("🎾 SERVICE WINNER"):
            st.session_state.temp_data['res'] = "Service Winner"; st.session_state.temp_data['cat'] = "Winner"
            st.session_state.step = "WINNER_PICK"; st.rerun()

    # --- FASE 3: QUALIFICAÇÃO DO ERRO ---
    elif st.session_state.step == "ERR_CAT":
        st.markdown("<div class='step-title'>Fase 3: Tipo de Erro</div>", unsafe_allow_html=True)
        ce1, ce2 = st.columns(2)
        if ce1.button("🐢 NÃO FORÇADO"):
            st.session_state.temp_data['cat'] = "Unforced"; st.session_state.step = "WINNER_PICK"; st.rerun()
        if ce2.button("💥 FORÇADO"):
            st.session_state.temp_data['cat'] = "Forced"; st.session_state.step = "WINNER_PICK"; st.rerun()

    # --- FASE 4: VENCEDOR E GOLPE ---
    elif st.session_state.step == "WINNER_PICK":
        st.markdown("<div class='step-title'>Fase 4: Finalização do Ponto</div>", unsafe_allow_html=True)
        winner = st.radio("Ponto para:", [p1_n, p2_n], horizontal=True)
        
        # Lógica inteligente para Ace/Double Fault
        res_tipo = st.session_state.temp_data.get('res')
        if res_tipo in ["Ace", "Service Winner", "Dupla Falta"]:
            golpe, pos, dir_g = "Saque 🚀", "N/A", "N/A"
            st.info(f"Ponto encerrado por {res_tipo}")
        else:
            col_g1, col_g2 = st.columns(2)
            golpe = col_g1.selectbox("Golpe", ["Forehand 🎾", "Backhand 🎾", "Voleio 🧤", "Smash ⚡", "Drop Shot 💧"])
            pos = col_g2.radio("Posição", ["Baseline 📏", "Rede 🕸️"])
            dir_g = st.radio("Direção", ["Cruzada ⚔️", "Paralela 🛤️"], horizontal=True)

        if st.button("✅ REGISTRAR PONTO", type="primary"):
            if winner == p1_n: st.session_state.score["p1_pts"] += 1
            else: st.session_state.score["p2_pts"] += 1
            
            st.session_state.match_data.append({
                "Vencedor": winner, "Saque": f"{st.session_state.serve_num}º", 
                "Direcao_Saque": st.session_state.temp_data.get('dir'), 
                "Resultado": res_tipo, "Categoria": st.session_state.temp_data.get('cat'), 
                "Golpe": golpe, "Direcao_Golpe": dir_g, "Posicao": pos
            })
            st.session_state.step = "SERVICE"; st.session_state.serve_num = 1; st.rerun()

    # --- RODAPÉ DE GESTÃO ---
    st.divider()
    cf1, cf2 = st.columns(2)
    with cf1:
        if st.button("🔄 DESFAZER (UNDO)"):
            if st.session_state.match_data:
                st.session_state.match_data.pop()
                st.session_state.step = "SERVICE"; st.session_state.serve_num = 1; st.rerun()
    with cf2:
        if st.button("📥 EXPORTAR SCOUT"):
            if st.session_state.match_data:
                df = pd.DataFrame(st.session_state.match_data)
                st.download_button("Baixar CSV", df.to_csv(index=False), "scout_pro.csv", "text/csv")