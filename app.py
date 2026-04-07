import streamlit as st
import pandas as pd
import base64

# Configuração de Página Nível ATP
st.set_page_config(page_title="MatchScout Pro | The Precision", layout="centered")

# --- INICIALIZAÇÃO DE ESTADOS (MEMÓRIA DO JOGO) ---
if 'match_data' not in st.session_state:
    st.session_state.match_data = []
if 'score' not in st.session_state:
    st.session_state.score = {
        "p1_points": 0, "p2_points": 0, 
        "p1_games": 0, "p2_games": 0, 
        "p1_sets": 0, "p2_sets": 0,
        "server": 1
    }
if 'setup' not in st.session_state:
    st.session_state.setup = {"active": False, "p1_name": "Jogador A", "p2_name": "Jogador B", "format": "Melhor de 3"}
if 'step' not in st.session_state:
    st.session_state.step = "Service"

def format_tennis_score(pts, other_pts):
    labels = {0: "0", 1: "15", 2: "30", 3: "40", 4: "AD"}
    return labels.get(pts, "40")

# --- INTERFACE DE SETUP ---
if not st.session_state.setup["active"]:
    st.title("🎾 MatchScout Pro Setup")
    with st.container():
        p1 = st.text_input("Nome do Jogador/Dupla A", "Atleta 1")
        p2 = st.text_input("Nome do Jogador/Dupla B", "Atleta 2")
        fmt = st.selectbox("Formato da Partida", ["Set Único", "Melhor de 3", "Melhor de 5", "Set Profissional (8 games)"])
        adv = st.radio("Regra de Vantagem", ["Com Vantagem (Deuce)", "No-Ad (Ponto Decisivo)"], horizontal=True)
        
        if st.button("INICIAR TORNEIO", use_container_width=True):
            st.session_state.setup.update({"active": True, "p1_name": p1, "p2_name": p2, "format": fmt, "adv": adv})
            st.rerun()

# --- INTERFACE DE SCOUTING ---
else:
    # Placar Dinâmico
    s = st.session_state.score
    p1_name = st.session_state.setup["p1_name"]
    p2_name = st.session_state.setup["p2_name"]
    
    st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #333; text-align: center;">
        <h2 style="color: white; margin: 0;">{p1_name} <span style="color: #00ff00;">{s['p1_sets']}</span> | {s['p1_games']} ({format_tennis_score(s['p1_points'], s['p2_points'])})</h2>
        <h2 style="color: white; margin: 0;">{p2_name} <span style="color: #00ff00;">{s['p2_sets']}</span> | {s['p2_games']} ({format_tennis_score(s['p2_points'], s['p1_points'])})</h2>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # FASE 1: SAQUE
    if st.session_state.step == "Service":
        st.subheader("📍 Registro de Saque")
        col_s1, col_s2, col_s3 = st.columns(3)
        directions = ["Wide", "Body", "T"]
        for i, col in enumerate([col_s1, col_s2, col_s3]):
            if col.button(directions[i], key=f"serve_{directions[i]}", use_container_width=True):
                st.session_state.last_serve = directions[i]
                st.session_state.step = "Rally"
                st.rerun()
        
        if st.button("ACE / SERVICE WINNER", type="primary", use_container_width=True):
            st.session_state.last_serve = "Ace/Winner"
            st.session_state.last_result = "Winner"
            st.session_state.step = "Context"
            st.rerun()

    # FASE 2: DESFECHO
    elif st.session_state.step == "Rally":
        st.subheader("🎯 Resultado do Ponto")
        c1, c2 = st.columns(2)
        if c1.button("🏆 WINNER", type="primary", use_container_width=True):
            st.session_state.last_result = "Winner"
            st.session_state.step = "Context"
            st.rerun()
        if c2.button("📉 ERRO", type="secondary", use_container_width=True):
            st.session_state.last_result = "Erro"
            st.session_state.step = "ErrorType"
            st.rerun()

    # FASE 2.1: TIPO DE ERRO
    elif st.session_state.step == "ErrorType":
        st.subheader("❌ Qualificação do Erro")
        ce1, ce2 = st.columns(2)
        if ce1.button("NÃO FORÇADO", use_container_width=True):
            st.session_state.error_cat = "Unforced"
            st.session_state.step = "Context"
            st.rerun()
        if ce2.button("FORÇADO", use_container_width=True):
            st.session_state.error_cat = "Forced"
            st.session_state.step = "Context"
            st.rerun()

    # FASE 3: CONTEXTO FINAL
    elif st.session_state.step == "Context":
        st.subheader("📊 Detalhes do Golpe")
        col_p1, col_p2 = st.columns(2)
        
        # Seleção de quem fez o ponto (Individual para Duplas)
        winner_of_point = st.radio("Ponto para:", [p1_name, p2_name], horizontal=True)
        
        tipo = st.selectbox("Tipo de Golpe", ["Forehand", "Backhand", "Voleio", "Smash", "Drop Shot"])
        direcao = st.radio("Direção", ["Cruzada", "Paralela"], horizontal=True)
        contexto = st.radio("Posição em Quadra", ["Baseline", "Net Point (Rede)"], horizontal=True)
        
        if st.button("REGISTRAR PONTO E ATUALIZAR PLACAR", use_container_width=True, type="primary"):
            # Lógica Simples de Incremento (Simplificada para Scout)
            if winner_of_point == p1_name:
                st.session_state.score["p1_points"] += 1
            else:
                st.session_state.score["p2_points"] += 1
            
            # Reset para próximo ponto
            st.session_state.match_data.append({
                "Vencedor": winner_of_point,
                "Saque": st.session_state.last_serve,
                "Golpe": tipo,
                "Direção": direcao,
                "Posição": contexto
            })
            st.session_state.step = "Service"
            st.rerun()

    st.divider()
    if st.button("📥 EXPORTAR PDF (RESUMO DIGITAL)", use_container_width=True):
        df = pd.DataFrame(st.session_state.match_data)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Clique aqui para baixar o PDF/CSV do Scout", csv, "scout_precision.csv", "text/csv")