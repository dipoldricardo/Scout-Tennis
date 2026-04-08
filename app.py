import streamlit as st
import pandas as pd
from fpdf import FPDF
import plotly.express as px
import plotly.graph_objects as go

# Configuração de Página Nível ATP
st.set_page_config(page_title="ATP Stats Pro", page_icon="🎾", layout="wide")

# --- ESTILIZAÇÃO ATP (Dark Mode & Gold Accents) ---
st.markdown("""
    <style>
    .main-score { background-color: #001e36; padding: 20px; border-radius: 15px; border-left: 10px solid #00feab; text-align: center; }
    .set-score-banner { background-color: #00feab; color: #001e36; font-weight: 900; font-size: 26px; border-radius: 5px; margin-bottom: 15px; }
    .player-name { color: #FFFFFF; font-size: 26px; font-weight: bold; font-family: 'Arial'; }
    .score-value { color: #00feab; font-size: 35px; font-weight: 900; }
    .metric-card { background-color: #002b4d; padding: 15px; border-radius: 10px; border: 1px solid #004080; text-align: center; }
    .serve-badge { background-color: #00feab; color: #000; padding: 10px 20px; border-radius: 5px; font-weight: 900; font-size: 20px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO GERADORA DE PDF (MODO RELATÓRIO TÉCNICO) ---
def generate_pdf(data, p1, p2):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 30, 54)
    pdf.cell(190, 15, "OFFICIAL MATCH STATS - ATP STYLE", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(190, 10, f"{p1} vs {p2}", ln=True, align="C")
    pdf.ln(10)
    
    # Tabela de Pontos
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(0, 254, 171) # Cor ATP
    cols = ["Sacador", "Vencedor", "Resultado", "Golpe", "Posicao", "Placar"]
    widths = [32, 32, 32, 32, 30, 32]
    for i, col in enumerate(cols): pdf.cell(widths[i], 10, col, 1, 0, "C", True)
    pdf.ln()
    
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(0, 0, 0)
    for row in data:
        for i, col in enumerate(cols):
            key = "Score" if col == "Placar" else col
            pdf.cell(widths[i], 8, str(row.get(key, "-")), 1, 0, "C")
        pdf.ln()
    return bytes(pdf.output())

# --- LÓGICA DE JOGO ---
if 'match_data' not in st.session_state: st.session_state.match_data = []
if 'score' not in st.session_state: st.session_state.score = {"p1_pts": 0, "p2_pts": 0, "p1_gms": 0, "p2_gms": 0}
if 'setup' not in st.session_state: st.session_state.setup = {"active": False, "p1": "", "p2": "", "server": 1, "match_over": False}
if 'step' not in st.session_state: st.session_state.step = "SERVICE"
if 'serve_num' not in st.session_state: st.session_state.serve_num = 1
if 'temp_data' not in st.session_state: st.session_state.temp_data = {}

def register_point(winner_name, res, cat="Winner", golpe="Saque", dir_g="N/A", pos="Baseline"):
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    if winner_name == p1_n: s["p1_pts"] += 1
    else: s["p2_pts"] += 1
    
    p1_p, p2_p = s["p1_pts"], s["p2_pts"]
    # Fechamento de Game
    if (p1_p >= 4 and p1_p - p2_p >= 2) or (p2_p >= 4 and p2_p - p1_p >= 2):
        if p1_p > p2_p: s["p1_gms"] += 1
        else: s["p2_gms"] += 1
        s["p1_pts"], s["p2_pts"] = 0, 0
        st.session_state.setup['server'] = 2 if st.session_state.setup['server'] == 1 else 1
        
        # Fechamento de Set Único
        g1, g2 = s["p1_gms"], s["p2_gms"]
        if (g1 >= 6 and g1 - g2 >= 2) or g1 == 7 or (g2 >= 6 and g2 - g1 >= 2) or g2 == 7:
            st.session_state.setup["match_over"] = True

    sacador = p1_n if st.session_state.setup['server'] == 1 else p2_n
    st.session_state.match_data.append({
        "Sacador": sacador, "Vencedor": winner_name, "Saque": f"{st.session_state.serve_num}º",
        "Resultado": res, "Categoria": cat, "Golpe": golpe, "Direcao": dir_g, "Posicao": pos,
        "Score": f"{s['p1_gms']}-{s['p2_gms']}"
    })
    st.session_state.step = "SERVICE"; st.session_state.serve_num = 1; st.session_state.temp_data = {}

# --- INTERFACE ---
if not st.session_state.setup["active"]:
    st.title("🎾 ATP Performance Tracker")
    with st.container(border=True):
        p1_in = st.text_input("Jogador 1 (Top Seed)", "Atleta A")
        p2_in = st.text_input("Jogador 2", "Atleta B")
        srv_in = st.radio("Saca Primeiro:", [p1_in, p2_in], horizontal=True)
        if st.button("🚀 START MATCH"):
            st.session_state.setup.update({"active": True, "p1": p1_in, "p2": p2_in, "server": 1 if srv_in == p1_in else 2})
            st.rerun()
else:
    # --- DASHBOARD ATP ---
    with st.expander("📊 OFFICIAL MATCH STATS (LIVE)", expanded=False):
        if st.session_state.match_data:
            df = pd.DataFrame(st.session_state.match_data)
            p1, p2 = st.session_state.setup['p1'], st.session_state.setup['p2']
            
            def get_stats(player):
                total_pts = len(df[df['Vencedor'] == player])
                winners = len(df[(df['Vencedor'] == player) & (df['Resultado'] == 'Winner')])
                unforced = len(df[(df['Vencedor'] != player) & (df['Categoria'] == 'Unforced')])
                aces = len(df[(df['Vencedor'] == player) & (df['Resultado'] == 'Ace')])
                return total_pts, winners, unforced, aces

            s1 = get_stats(p1)
            s2 = get_stats(p2)

            # Tabela Comparativa ATP Style
            st.markdown(f"""
            | {p1} | METRIC | {p2} |
            | :---: | :---: | :---: |
            | {s1[3]} | **ACES** | {s2[3]} |
            | {s1[1]} | **WINNERS** | {s2[1]} |
            | {s1[2]} | **UNFORCED ERRORS** | {s2[2]} |
            | {len(df[df['Posicao'] == 'Rede'])} | **NET POINTS WON** | - |
            """, unsafe_allow_html=True)

            # Gráfico de Momentum
            fig_momentum = px.line(df, y='Score', title="Match Momentum", markers=True, color_discrete_sequence=['#00feab'])
            st.plotly_chart(fig_momentum, use_container_width=True)
        else: st.info("Waiting for data points...")

    # --- SCOREBOARD ---
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    srv_idx = st.session_state.setup['server']
    sacador_at = p1_n if srv_idx == 1 else p2_n
    pt1, pt2 = (s["p1_pts"], s["p2_pts"]) # Simplificado para visualização técnica
    
    st.markdown(f"""
    <div class="main-score">
        <div class="set-score-banner">LIVE MATCH CENTER</div>
        <div class="player-name">{p1_n}{" 🎾" if srv_idx == 1 else ""}</div>
        <div class="score-value">{s['p1_gms']} <span style="font-size:20px; color:#fff;">({pt1})</span></div>
        <div style="margin: 15px 0; border-top: 1px solid #004080;"></div>
        <div class="player-name">{p2_n}{" 🎾" if srv_idx == 2 else ""}</div>
        <div class="score-value">{s['p2_gms']} <span style="font-size:20px; color:#fff;">({pt2})</span></div>
    </div>
    """, unsafe_allow_html=True)

    # --- ACTION CENTER ---
    if not st.session_state.setup["match_over"]:
        if st.session_state.step == "SERVICE":
            st.markdown(f"<div style='text-align: center;'><span class='serve-badge'>{st.session_state.serve_num}º SERVIÇO</span></div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            if c1.button("WIDE"): st.session_state.temp_data['dir_saque'] = "Wide"; st.session_state.step = "RESULT"; st.rerun()
            if c2.button("BODY"): st.session_state.temp_data['dir_saque'] = "Body"; st.session_state.step = "RESULT"; st.rerun()
            if c3.button("T"): st.session_state.temp_data['dir_saque'] = "T"; st.session_state.step = "RESULT"; st.rerun()
            if st.button("❌ DOUBLE FAULT / NET"):
                if st.session_state.serve_num == 1: st.session_state.serve_num = 2; st.rerun()
                else: register_point(p2_n if srv_idx == 1 else p1_n, "Double Fault", "Erro"); st.rerun()

        elif st.session_state.step == "RESULT":
            cr1, cr2, cr3 = st.columns(3)
            if cr1.button("🏆 WINNER", type="primary"): 
                st.session_state.temp_data['res'] = "Winner"; st.session_state.temp_data['cat'] = "Winner"; st.session_state.step = "WINNER_PICK"; st.rerun()
            if cr2.button("📉 UNFORCED"): 
                st.session_state.temp_data['res'] = "Erro"; st.session_state.temp_data['cat'] = "Unforced"; st.session_state.step = "WINNER_PICK"; st.rerun()
            if cr3.button("💥 FORCED"): 
                st.session_state.temp_data['res'] = "Erro"; st.session_state.temp_data['cat'] = "Forced"; st.session_state.step = "WINNER_PICK"; st.rerun()
            
            st.divider()
            if st.button("🎯 ACE"): register_point(sacador_at, "Ace"); st.rerun()
            if st.button("🎾 SERVICE WINNER"): register_point(sacador_at, "Service Winner"); st.rerun()

        elif st.session_state.step == "WINNER_PICK":
            st.markdown("<div class='step-title'>Point Detail</div>", unsafe_allow_html=True)
            winner_choice = st.radio("Point to:", [p1_n, p2_n], horizontal=True)
            c_pos1, c_pos2 = st.columns(2)
            pos_choice = c_pos1.radio("Zone:", ["Baseline", "Net"], horizontal=True)
            golpe_choice = c_pos2.selectbox("Stroke:", ["Forehand", "Backhand", "Volley", "Smash", "Slice"])
            dir_choice = st.radio("Direction:", ["Crosscourt", "Down the line", "N/A"], horizontal=True)
            
            if st.button("✅ LOG POINT"):
                register_point(winner_choice, st.session_state.temp_data['res'], st.session_state.temp_data['cat'], golpe_choice, dir_choice, pos_choice)
                st.rerun()
    else:
        st.balloons()
        st.success("MATCH COMPLETED")

    # --- FOOTER ---
    st.divider()
    bot_c1, bot_c2 = st.columns(2)
    with bot_c1:
        if st.button("🔄 UNDO LAST"):
            if st.session_state.match_data: st.session_state.match_data.pop(); st.rerun()
    with bot_c2:
        if st.session_state.match_data:
            report_bytes = generate_pdf(st.session_state.match_data, st.session_state.setup['p1'], st.session_state.setup['p2'])
            st.download_button("📥 DOWNLOAD ATP REPORT (PDF)", data=report_bytes, file_name="match_stats_pro.pdf", mime="application/pdf")
    
    if st.session_state.setup["match_over"]:
        if st.button("🆕 RESET MATCH"): st.session_state.clear(); st.rerun()