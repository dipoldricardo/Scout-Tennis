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
        height: 80px;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        margin-bottom: 10px !important;
    }
    .main-score {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 20px;
        border: 2px solid #333;
        text-align: center;
        margin-bottom: 25px;
    }
    .player-name { color: #FFFFFF; font-size: 24px; font-weight: bold; }
    .score-value { color: #00FF00; font-size: 32px; font-weight: bold; }
    .step-title { color: #AAAAAA; text-transform: uppercase; letter-spacing: 2px; font-size: 14px; text-align: center;}
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'match_data' not in st.session_state:
    st.session_state.match_data = []
if 'score' not in st.session_state:
    st.session_state.score = {"p1_pts": 0, "p2_pts": 0, "p1_gms": 0, "p2_gms": 0, "p1_sets": 0, "p2_sets": 0}
if 'setup' not in st.session_state:
    st.session_state.setup = {"active": False, "p1": "Jogador A", "p2": "Jogador B", "fmt": ""}
if 'step' not in st.session_state:
    st.session_state.step = "SERVICE"
if 'serve_num' not in st.session_state:
    st.session_state.serve_num = 1
if 'temp_data' not in st.session_state:
    st.session_state.temp_data = {}

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

# --- 2. INTERFACE DE SCOUTING (MODERNA) ---
else:
    # PLACAR GIGANTE
    s = st.session_state.score
    st.markdown(f"""
    <div class="main-score">
        <div class="player-name">{st.session_state.setup['p1']}</div>
        <div class="score-value">{s['p1_sets']} | {s['p1_gms']} ({format_pts(s['p1_pts'])})</div>
        <hr style="border: 0.5px solid #444">
        <div class="player-name">{st.session_state.setup['p2']}</div>
        <div class="score-value">{s['p2_sets']} | {s['p2_gms']} ({format_pts(s['p2_pts'])})</div>
    </div>
    """, unsafe_allow_html=True)

    # --- FASE 1: SERVIÇO (MAPA DE SAQUE) ---
    if st.session_state.step == "SERVICE":
        st.markdown(f"<div class='step-title'>Fase 1: Direção do {st.session_state.serve_num}º Saque</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button("WIDE ↙️"): 
            st.session_state.temp_data['dir'] = "Wide"; st.session_state.step = "RESULT"; st.rerun()
        if c2.button("BODY 👤"): 
            st.session_state.temp_data['dir'] = "Body"; st.session_state.step = "RESULT"; st.rerun()
        if c3.button("T ⬇️"): 
            st.session_state.temp_data['dir'] = "T"; st.session_state.step = "RESULT"; st.rerun()
        
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
        st.markdown("<div class='step-title'>Fase 2: Desfecho do Rali</div>", unsafe_allow_html=True)
        cr1, cr2, cr3 = st.columns(3)
        if cr1.button("🏆 WINNER", type="primary"):
            st.session_state.temp_data['res'] = "Winner"; st.session_state.temp_data['cat'] = "Winner"
            st.session_state.step = "WINNER_PICK"; st.rerun()
        if cr2.button("📉 ERRO"):
            st.session_state.temp_data['res'] = "Erro"; st.session_state.step = "ERR_CAT"; st.rerun()
        if cr3.button("🎾 ACE"):
            st.session_state.temp_data['res'] = "Ace"; st.session_state.temp_data['cat'] = "Winner"
            st.session_state.step = "WINNER_PICK"; st.rerun()

    # --- FASE 3: QUALIFICAÇÃO DO ERRO ---
    elif st.session_state.step == "ERR_CAT":
        st.markdown("<div class='step-title'>Fase 3: Tipo de Erro</div>", unsafe_allow_html=True)
        ce1, ce2 = st.columns(2)
        if ce1.button("🐢 NÃO FORÇADO"):
            st.session_state.temp_data['cat'] = "Unforced"; st.session_state.step = "WINNER_PICK"; st.rerun()
        if ce2.button("💥 FORÇADO"):
            st.session_state.temp_state = "Forced"; st.session_state.temp_data['cat'] = "Forced"
            st.session_state.step = "WINNER_PICK"; st.rerun()

    # --- FASE 4: VENCEDOR E GOLPE ---
    elif st.session_state.step == "WINNER_PICK":
        st.markdown("<div class='step-title'>Fase 4: Atribuição e Detalhes</div>", unsafe_allow_html=True)
        winner = st.radio("Ponto para:", [st.session_state.setup['p1'], st.session_state.setup['p2']], horizontal=True)
        
        col_g1, col_g2 = st.columns(2)
        golpe = col_g1.selectbox("Golpe", ["Forehand 🎾", "Backhand 🎾", "Voleio 🧤", "Smash ⚡", "Drop Shot 💧", "Saque 🚀"])
        pos = col_g2.radio("Posição", ["Baseline 📏", "Rede 🕸️"])
        dir_g = st.radio("Direção", ["Cruzada ⚔️", "Paralela 🛤️"], horizontal=True)

        if st.button("✅ FINALIZAR PONTO", type="primary"):
            # Lógica de Placar
            if winner == st.session_state.setup['p1']: st.session_state.score["p1_pts"] += 1
            else: st.session_state.score["p2_pts"] += 1
            
            # Salvar na Base
            st.session_state.match_data.append({
                "Vencedor": winner, "Saque": f"{st.session_state.serve_num}º", 
                "Dir_Saque": st.session_state.temp_data.get('dir'), "Resultado": st.session_state.temp_data.get('res'),
                "Cat": st.session_state.temp_data.get('cat'), "Golpe": golpe, "Direcao": dir_g, "Posicao": pos
            })
            
            # Reset para próximo ponto
            st.session_state.step = "SERVICE"; st.session_state.serve_num = 1; st.rerun()

    # --- RODAPÉ DE GESTÃO ---
    st.divider()
    cf1, cf2 = st.columns(2)
    if cf1.button("🔄 DESFAZER (UNDO)"):
        if st.session_state.match_data:
            st.session_state.match_data.pop()
            st.rerun()
    if cf2.button("📥 EXPORTAR PDF/CSV"):
        df = pd.DataFrame(st.session_state.match_data)
        st.download_button("Clique para Baixar", df.to_csv(index=False), "scout_pro.csv", "text/csv")