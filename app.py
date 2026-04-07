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
if 'serve_attempt' not in st.session_state:
    st.session_state.serve_attempt = 1  # 1 para 1º Saque, 2 para 2º Saque
if 'last_serve_dir' not in st.session_state:
    st.session_state.last_serve_dir = ""
if 'last_res' not in st.session_state:
    st.session_state.last_res = ""
if 'err_cat' not in st.session_state:
    st.session_state.err_cat = ""

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
    
    st.markdown(f"""
    <div style="background-color: #0e1117; padding: 15px; border-radius: 10px; border: 1px solid #31333f; text-align: center;">
        <h3 style="margin:0; color: #00ff00;">{p1}: {s['p1_sets']} sets | {s['p1_games']} ({format_tennis_score(s['p1_points'])})</h3>
        <h3 style="margin:0; color: #00ff00;">{p2}: {s['p2_sets']} sets | {s['p2_games']} ({format_tennis_score(s['p2_points'])})</h3>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # FASE 1: DIREÇÃO DO SAQUE (COM LÓGICA DE 1º E 2º)
    if st.session_state.step == "Service":
        st.subheader(f"📍 Direção do {st.session_state.serve_attempt}º Saque")
        c1, c2, c3 = st.columns(3)
        if c1.button("WIDE", use_container_width=True): 
            st.session_state.last_serve_dir = "Wide"
            st.session_state.step = "Result"
            st.rerun()
        if c2.button("BODY", use_container_width=True): 
            st.session_state.last_serve_dir = "Body"
            st.session_state.step = "Result"
            st.rerun()
        if c3.button("T", use_container_width=True): 
            st.session_state.last_serve_dir = "T"
            st.session_state.step = "Result"
            st.rerun()
        
        # Botão de Falta
        if st.button("❌ FALTA (NET / OUT)", use_container_width=True):
            if st.session_state.serve_attempt == 1:
                st.session_state.serve_attempt = 2
                st.warning("1º Saque fora. Preparar 2º Saque.")
                st.rerun()
            else:
                st.error("DUPLA FALTA!")
                st.session_state.last_res = "Double Fault"
                st.session_state.step = "Context" # Pula direto para o registro do vencedor
                st.rerun()

    # FASE 2: RESULTADO DO PONTO
    elif st.session_state.step == "Result":
        st.subheader(f"🎯 Desfecho do Ponto ({st.session_state.serve_attempt}º Saque)")
        res_c1, res_c2, res_c3 = st.columns(3)
        if res_c1.button("🏆 WINNER", type="primary", use_container_width=True):
            st.session_state.last_res = "Winner"
            st.session_state.err_cat = "N/A"
            st.session_state.step = "Context"
            st.rerun()
        if res_c2.button("📉 ERRO", type="secondary", use_container_width=True):
            st.session_state.last_res = "Erro"
            st.session_state.step = "ErrorType"
            st.rerun()
        if res_c3.button("🎾 ACE / SERVE WINNER", use_container_width=True):
            st.session_state.last_res = "Ace/Service Winner"
            st.session_state.err_cat = "N/A"
            st.session_state.step = "Context"
            st.rerun()

    # FASE 3: QUALIFICAÇÃO DO ERRO
    elif st.session_state.step == "ErrorType":
        st.subheader("❌ Qualificação do Erro")
        e1, e2 = st.columns(2)
        if e1.button("NÃO FORÇADO", use_container_width=True):
            st.session_state.err_cat = "Unforced"
            st.session_state.step = "Context"
            st.rerun()
        if e2.button("FORÇADO", use_container_width=True):
            st.session_state.err_cat = "Forced"
            st.session_state.step = "Context"
            st.rerun()

    # FASE 4: CONTEXTO TÁTICO FINAL
    elif st.session_state.step == "Context":
        st.subheader("📊 Detalhes Finais")
        winner_pt = st.radio("Ponto para:", [p1, p2], horizontal=True)
        
        # Se for Dupla Falta ou Ace, os detalhes de golpe são automáticos
        if st.session_state.last_res in ["Double Fault", "Ace/Service Winner"]:
            golpe, dir_g, pos = "Saque", "N/A", "N/A"
            st.info(f"Ponto por {st.session_state.last_res}")
        else:
            golpe = st.selectbox("Tipo de Golpe", ["Forehand", "Backhand", "Voleio", "Smash", "Drop Shot"])
            dir_g = st.radio("Direção do Golpe", ["Cruzada", "Paralela"], horizontal=True)
            pos = st.radio("Posição do Jogador", ["Baseline", "Rede"], horizontal=True)
        
        if st.button("CONFIRMAR PONTO", use_container_width=True, type="primary"):
            # Atualização de placar
            if winner_pt == p1: st.session_state.score["p1_points"] += 1
            else: st.session_state.score["p2_points"] += 1
            
            # Registro na Base com distinção de saque
            st.session_state.match_data.append({
                "Vencedor": winner_pt, 
                "Tentativa_Saque": f"{st.session_state.serve_attempt}º",
                "Dir_Saque": st.session_state.last_serve_dir, 
                "Resultado": st.session_state.last_res, 
                "Cat_Erro": st.session_state.err_cat,
                "Golpe": golpe, "Direção": dir_g, "Posição": pos
            })
            
            # Reset Total para o próximo ponto
            st.session_state.step = "Service"
            st.session_state.serve_attempt = 1
            st.session_state.last_serve_dir = ""
            st.rerun()

    st.divider()
    
    # RODAPÉ DE GESTÃO
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if st.button("🔄 DESFAZER ÚLTIMO"):
            if st.session_state.match_data:
                st.session_state.match_data.pop()
                st.session_state.step = "Service"
                st.session_state.serve_attempt = 1
                st.rerun()
    with col_f2:
        if st.button("📥 EXPORTAR SCOUT"):
            if st.session_state.match_data:
                df = pd.DataFrame(st.session_state.match_data)
                st.download_button("Baixar CSV", df.to_csv(index=False), "scout-tennis.csv", "text/csv")