import streamlit as st
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# Configuração de Página - Marco "The Precision" Valente
st.set_page_config(
    page_title="Scout-Tennis Pro",
    page_icon="🎾",
    layout="centered"
)

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%; height: 60px; font-size: 16px !important;
        font-weight: bold !important; border-radius: 12px !important;
    }
    .main-score {
        background-color: #1E1E1E; padding: 15px; border-radius: 15px;
        border: 2px solid #333; text-align: center; margin-bottom: 20px;
    }
    .set-score-banner {
        background-color: #00FF00; color: #000000; font-weight: 900;
        font-size: 24px; border-radius: 8px; padding: 5px; margin-bottom: 15px;
    }
    .player-name { color: #FFFFFF; font-size: 22px; font-weight: bold; }
    .score-value { color: #00FF00; font-size: 28px; font-weight: 900; }
    .serve-badge {
        background-color: #DFFF00; color: #000; padding: 8px 15px;
        border-radius: 50px; font-weight: 900; font-size: 16px;
        display: inline-block; margin-bottom: 10px; border: 2px solid #000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO GERADORA DE PDF ---
def generate_pdf(data, p1, p2):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 10, f"Relatorio de Scout: {p1} vs {p2}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(200, 200, 200)
    cols = ["Vencedor", "Resultado", "Golpe", "Direcao", "Placar"]
    for col in cols: pdf.cell(38, 10, col, 1, 0, "C", True)
    pdf.ln()
    pdf.set_font("Helvetica", size=9)
    for row in data:
        for key in cols:
            val = "Score" if key == "Placar" else key
            pdf.cell(38, 10, str(row.get(val, "-")), 1)
        pdf.ln()
    return bytes(pdf.output())

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'match_data' not in st.session_state: st.session_state.match_data = []
if 'score' not in st.session_state: st.session_state.score = {"p1_pts": 0, "p2_pts": 0, "p1_gms": 0, "p2_gms": 0}
if 'setup' not in st.session_state: st.session_state.setup = {"active": False, "p1": "", "p2": "", "server": 1, "match_over": False}
if 'step' not in st.session_state: st.session_state.step = "SERVICE"
if 'serve_num' not in st.session_state: st.session_state.serve_num = 1
if 'temp_data' not in st.session_state: st.session_state.temp_data = {}

def format_pts(p1, p2):
    mapping = {0: "0", 1: "15", 2: "30", 3: "40"}
    if p1 <= 3 and p2 <= 3:
        if p1 == 3 and p2 == 3: return "40", "40"
        return mapping[p1], mapping[p2]
    if p1 == p2: return "40", "40"
    return ("AD", "40") if p1 > p2 else ("40", "AD")

def register_point(winner_name, res, cat="Winner", golpe="Saque", dir_g="N/A", pos="N/A"):
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    if winner_name == p1_n: s["p1_pts"] += 1
    else: s["p2_pts"] += 1
    p1_p, p2_p = s["p1_pts"], s["p2_pts"]
    if (p1_p >= 4 and p1_p - p2_p >= 2) or (p2_p >= 4 and p2_p - p1_p >= 2):
        if p1_p > p2_p: s["p1_gms"] += 1
        else: s["p2_gms"] += 1
        s["p1_pts"], s["p2_pts"] = 0, 0
        st.session_state.setup['server'] = 2 if st.session_state.setup['server'] == 1 else 1
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

# --- INTERFACE PRINCIPAL ---
if not st.session_state.setup["active"]:
    st.title("🎾 Scout-Tennis Pro")
    with st.container(border=True):
        p1_in = st.text_input("Atleta A", "Atleta 1")
        p2_in = st.text_input("Atleta B", "Atleta 2")
        srv_in = st.radio("Inicia sacando:", [p1_in, p2_in], horizontal=True)
        if st.button("🚀 INICIAR PARTIDA"):
            st.session_state.setup.update({"active": True, "p1": p1_in, "p2": p2_in, "server": 1 if srv_in == p1_in else 2})
            st.rerun()
else:
    # --- DASHBOARD (EXPANDER) ---
    with st.expander("📊 DASHBOARD ESTATÍSTICO", expanded=False):
        if st.session_state.match_data:
            df = pd.DataFrame(st.session_state.match_data)
            p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
            
            # Métricas Rápidas
            c1, c2, c3 = st.columns(3)
            c1.metric("Total de Pontos", len(df))
            c2.metric(f"Winners {p1_n}", len(df[(df['Vencedor'] == p1_n) & (df['Resultado'] == 'Winner')]))
            c3.metric(f"Winners {p2_n}", len(df[(df['Vencedor'] == p2_n) & (df['Resultado'] == 'Winner')]))
            
            # Gráfico de Distribuição de Golpes
            fig_golpes = px.pie(df[df['Golpe'] != 'Saque'], names='Golpe', title="Distribuição de Golpes (Rali)", hole=0.4)
            st.plotly_chart(fig_golpes, use_container_width=True)
            
            # Gráfico de Barras: Winners vs Erros por Jogador
            res_df = df.groupby(['Vencedor', 'Resultado']).size().reset_index(name='count')
            fig_res = px.bar(res_df, x='Vencedor', y='count', color='Resultado', barmode='group', title="Performance por Atleta")
            st.plotly_chart(fig_res, use_container_width=True)
        else:
            st.info("Aguardando dados para gerar o Dashboard...")

    # --- PLACAR ---
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    srv_idx = st.session_state.setup['server']
    sacador_at = p1_n if srv_idx == 1 else p2_n
    pt1, pt2 = format_pts(s["p1_pts"], s["p2_pts"])
    
    st.markdown(f"""
    <div class="main-score">
        <div class="set-score-banner">SET ÚNICO</div>
        <div class="player-name">{p1_n}{" 🎾" if srv_idx == 1 else ""}</div>
        <div class="score-value">{s['p1_gms']} ({pt1})</div>
        <hr style="border: 0.5px solid #444; margin: 10px 0;">
        <div class="player-name">{p2_n}{" 🎾" if srv_idx == 2 else ""}</div>
        <div class="score-value">{s['p2_gms']} ({pt2})</div>
    </div>
    """, unsafe_allow_html=True)

    # --- FLUXO DE SCOUTING ---
    if not st.session_state.setup["match_over"]:
        if st.session_state.step == "SERVICE":
            st.markdown(f"<div style='text-align: center;'><span class='serve-badge'>{st.session_state.serve_num}º SERVIÇO</span></div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            if c1.button("WIDE"): st.session_state.temp_data['dir_saque'] = "Wide"; st.session_state.step = "RESULT"; st.rerun()
            if c2.button("BODY"): st.session_state.temp_data['dir_saque'] = "Body"; st.session_state.step = "RESULT"; st.rerun()
            if c3.button("T"): st.session_state.temp_data['dir_saque'] = "T"; st.session_state.step = "RESULT"; st.rerun()
            if st.button("❌ FALTA"):
                if st.session_state.serve_num == 1: st.session_state.serve_num = 2; st.rerun()
                else: register_point(p2_n if srv_idx == 1 else p1_n, "Dupla Falta", "Erro"); st.rerun()

        elif st.session_state.step == "RESULT":
            cr1, cr2 = st.columns(2)
            if cr1.button("🏆 WINNER", type="primary"): 
                st.session_state.temp_data['res'] = "Winner"; st.session_state.temp_data['cat'] = "Winner"; st.session_state.step = "WINNER_PICK"; st.rerun()
            if cr2.button("📉 ERRO"): 
                st.session_state.temp_data['res'] = "Erro"; st.session_state.step = "ERR_CAT"; st.rerun()
            st.divider()
            if st.button("🎯 ACE"): register_point(sacador_at, "Ace"); st.rerun()
            if st.button("🎾 SERVICE WINNER"): register_point(sacador_at, "Service Winner"); st.rerun()

        elif st.session_state.step == "ERR_CAT":
            ce1, ce2 = st.columns(2)
            if ce1.button("🐢 NÃO FORÇADO"): st.session_state.temp_data['cat'] = "Unforced"; st.session_state.step = "WINNER_PICK"; st.rerun()
            if ce2.button("💥 FORÇADO"): st.session_state.temp_data['cat'] = "Forced"; st.session_state.step = "WINNER_PICK"; st.rerun()

        elif st.session_state.step == "WINNER_PICK":
            winner_choice = st.radio("Ponto para:", [p1_n, p2_n], horizontal=True)
            col1, col2 = st.columns(2)
            golpe_choice = col1.selectbox("Golpe", ["Forehand", "Backhand", "Voleio", "Smash", "Drop Shot"])
            dir_choice = st.radio("Direção", ["Cruzada", "Paralela"], horizontal=True)
            if st.button("✅ REGISTRAR"):
                register_point(winner_choice, st.session_state.temp_data['res'], st.session_state.temp_data['cat'], golpe_choice, dir_choice)
                st.rerun()
    else:
        st.success("PARTIDA FINALIZADA!")

    # --- RODAPÉ ---
    st.divider()
    bot_c1, bot_c2 = st.columns(2)
    with bot_c1:
        if st.button("🔄 UNDO"):
            if st.session_state.match_data: st.session_state.match_data.pop(); st.rerun()
    with bot_c2:
        if st.session_state.match_data:
            report_bytes = generate_pdf(st.session_state.match_data, st.session_state.setup['p1'], st.session_state.setup['p2'])
            st.download_button("📥 EXPORTAR PDF", data=report_bytes, file_name="scout.pdf", mime="application/pdf")
    
    if st.session_state.setup["match_over"]:
        if st.button("🆕 NOVA PARTIDA"): st.session_state.clear(); st.rerun()