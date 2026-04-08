import streamlit as st
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- CONFIGURAÇÃO MASTER ---
st.set_page_config(page_title="ATP Scout Pro: Marco Valente Edition", page_icon="🎾", layout="wide")

# --- ESTILIZAÇÃO DASHBOARD PROFISSIONAL ---
st.markdown("""
    <style>
    .main-score { background-color: #001e36; padding: 25px; border-radius: 15px; border-left: 10px solid #00feab; text-align: center; margin-bottom: 20px;}
    .set-score-banner { background-color: #00feab; color: #001e36; font-weight: 900; font-size: 22px; border-radius: 5px; padding: 5px; margin-bottom: 15px; }
    .player-name { color: #FFFFFF; font-size: 24px; font-weight: bold; }
    .score-value { color: #00feab; font-size: 38px; font-weight: 900; }
    .serve-badge { background-color: #DFFF00; color: #000; padding: 10px 25px; border-radius: 50px; font-weight: 900; border: 2px solid #000; display: inline-block; margin-bottom: 15px; }
    .stats-table { width: 100%; border-collapse: collapse; margin-top: 20px; color: white; background: #001e36; border-radius: 10px; overflow: hidden; border: 1px solid #004080; }
    .stats-header { background: #00feab; color: #001e36; font-weight: 900; padding: 12px; text-align: center; font-size: 18px; }
    .stats-row { border-bottom: 1px solid #004080; }
    .stats-cell { padding: 15px; text-align: center; font-family: 'Courier New', monospace; font-size: 16px; }
    .stats-label { color: #AAAAAA; font-size: 13px; font-weight: bold; text-transform: uppercase; }
    .step-label { color: #AAAAAA; text-transform: uppercase; font-size: 13px; font-weight: bold; margin-bottom: 5px; display: block;}
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DE CÁLCULO ESTATÍSTICO AVANÇADO ---
def calculate_match_stats(df, p1, p2):
    stats = []
    total_pts_match = len(df)
    for p in [p1, p2]:
        p_pts_won = len(df[df['Vencedor'] == p])
        opp_pts_won = len(df[df['Vencedor'] != p])
        
        # Aces e Duplas Faltas
        aces = len(df[(df['Vencedor'] == p) & (df['Resultado'] == 'Ace')])
        df_faults = len(df[(df['Vencedor'] != p) & (df['Resultado'] == 'Dupla Falta')])
        
        # Winners e Erros
        winners = len(df[(df['Vencedor'] == p) & (df['Categoria'] == 'Winner')])
        ue = len(df[(df['Vencedor'] != p) & (df['Categoria'] == 'Unforced')])
        forced = len(df[(df['Vencedor'] != p) & (df['Categoria'] == 'Forced')])
        
        # Aproveitamento de Rede (Rigor Marco Valente)
        net_pts_p = df[df['Posicao'] == 'Rede']
        net_won = len(net_pts_p[net_pts_p['Vencedor'] == p])
        net_total = len(net_pts_p)
        net_pct = (net_won / net_total * 100) if net_total > 0 else 0

        # Percentual de Pontos Totais
        total_pct = (p_pts_won / total_pts_match * 100) if total_pts_match > 0 else 0

        stats.append({
            "Player": p, "Aces": aces, "DF": df_faults, 
            "Winners": winners, "UE": len(df[(df['Vencedor'] != p) & (df['Categoria'] == 'Unforced')]),
            "Net": f"{net_won}/{net_total} ({net_pct:.1f}%)",
            "Total": f"{p_pts_won} ({total_pct:.1f}%)"
        })
    return stats

# --- ENGINE PDF ---
def generate_pdf(data, p1, p2, score_f):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20); pdf.cell(190, 15, "OFFICIAL SCOUT REPORT", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12); pdf.cell(190, 10, f"{p1} vs {p2} | {score_f}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_fill_color(0, 254, 171); pdf.set_font("Helvetica", "B", 10)
    cols = ["Vencedor", "Resultado", "Golpe", "Zona", "Direção", "Placar"]
    for i, col in enumerate(cols): pdf.cell(31, 10, col, 1, 0, "C", True)
    pdf.ln()
    pdf.set_font("Helvetica", size=8)
    for row in data:
        for key in ["Vencedor", "Resultado", "Golpe", "Posicao", "Direcao", "Score"]:
            pdf.cell(31, 8, str(row.get(key, "-")), 1)
        pdf.ln()
    return bytes(pdf.output())

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'match_data' not in st.session_state: st.session_state.match_data = []
if 'score' not in st.session_state: 
    st.session_state.score = {"p1_pts": 0, "p2_pts": 0, "p1_gms": 0, "p2_gms": 0, "p1_sets": 0, "p2_sets": 0, "history": []}
if 'setup' not in st.session_state: 
    st.session_state.setup = {"active": False, "p1": "", "p2": "", "server": 1, "match_over": False, "format": "Melhor de 3"}
if 'step' not in st.session_state: st.session_state.step = "SERVICE"
if 'serve_num' not in st.session_state: st.session_state.serve_num = 1
if 'temp_data' not in st.session_state: st.session_state.temp_data = {}

def register_point(winner_name, res, cat="Winner", golpe="Saque", dir_g="N/A", pos="Baseline"):
    s = st.session_state.score
    setup = st.session_state.setup
    if winner_name == setup['p1']: s["p1_pts"] += 1
    else: s["p2_pts"] += 1
    
    if (s["p1_pts"] >= 4 and s["p1_pts"] - s["p2_pts"] >= 2) or (s["p2_pts"] >= 4 and s["p2_pts"] - s["p1_pts"] >= 2):
        if s["p1_pts"] > s["p2_pts"]: s["p1_gms"] += 1
        else: s["p2_gms"] += 1
        s["p1_pts"], s["p2_pts"] = 0, 0
        setup['server'] = 2 if setup['server'] == 1 else 1
        g1, g2 = s["p1_gms"], s["p2_gms"]
        if (g1 >= 6 and g1 - g2 >= 2) or g1 == 7 or (g2 >= 6 and g2 - g1 >= 2) or g2 == 7:
            if g1 > g2: s["p1_sets"] += 1
            else: s["p2_sets"] += 1
            s["history"].append(f"{g1}-{g2}"); s["p1_gms"], s["p2_gms"] = 0, 0
            target = {"Set Único": 1, "Melhor de 3": 2, "Melhor de 5": 3}[setup["format"]]
            if s["p1_sets"] == target or s["p2_sets"] == target: setup["match_over"] = True

    st.session_state.match_data.append({
        "Vencedor": winner_name, "Resultado": res, "Categoria": cat, "Golpe": golpe, "Direcao": dir_g, "Posicao": pos,
        "Score": f"{s['p1_sets']}-{s['p2_sets']} ({s['p1_gms']}-{s['p2_gms']})"
    })
    st.session_state.step = "SERVICE"; st.session_state.serve_num = 1; st.session_state.temp_data = {}

# --- INTERFACE ---
if not st.session_state.setup["active"]:
    st.title("🎾 Scout-Tennis Pro: Marco Valente Edition")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        p1_in = c1.text_input("Atleta A", "Jogador 1")
        p2_in = c2.text_input("Atleta B", "Jogador 2")
        fmt = st.selectbox("Formato:", ["Set Único", "Melhor de 3", "Melhor de 5"], index=1)
        srv = st.radio("Sacador Inicial:", [p1_in, p2_in], horizontal=True)
        if st.button("🚀 INICIAR SCOUT"):
            st.session_state.setup.update({"active": True, "p1": p1_in, "p2": p2_in, "server": 1 if srv == p1_in else 2, "format": fmt})
            st.rerun()
else:
    # --- PLACAR CENTRAL (TOPO) ---
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    srv_idx = st.session_state.setup['server']
    
    def get_atp_pt(p_pts, opp_pts):
        m = {0: "0", 1: "15", 2: "30", 3: "40"}
        if p_pts <= 3 and opp_pts <= 3: return m[p_pts]
        if p_pts == opp_pts: return "40"
        return "AD" if p_pts > opp_pts else "40"

    pt1 = get_atp_pt(s["p1_pts"], s["p2_pts"])
    pt2 = get_atp_pt(s["p2_pts"], s["p1_pts"])
    
    st.markdown(f"""
    <div class="main-score">
        <div class="set-score-banner">{st.session_state.setup['format']} | Sets: {", ".join(s['history']) if s['history'] else "0-0"}</div>
        <div class="player-name">{p1_n}{" 🎾" if srv_idx == 1 else ""}</div>
        <div class="score-value">{s['p1_sets']} | {s['p1_gms']} | <span style="color:white">{pt1}</span></div>
        <hr style="border:0.5px solid #004080; margin:10px 0;">
        <div class="player-name">{p2_n}{" 🎾" if srv_idx == 2 else ""}</div>
        <div class="score-value">{s['p2_sets']} | {s['p2_gms']} | <span style="color:white">{pt2}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # --- ÁREA DE INPUT (SCOUTING) ---
    if not st.session_state.setup["match_over"]:
        if st.session_state.step == "SERVICE":
            st.markdown(f"<center><span class='serve-badge'>{st.session_state.serve_num}º SERVIÇO</span></center>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            if c1.button("WIDE"): st.session_state.temp_data['dir'] = "Wide"; st.session_state.step = "RESULT"; st.rerun()
            if c2.button("BODY"): st.session_state.temp_data['dir'] = "Body"; st.session_state.step = "RESULT"; st.rerun()
            if c3.button("T"): st.session_state.temp_data['dir'] = "T"; st.session_state.step = "RESULT"; st.rerun()
            if st.button("❌ FALTA / NET"):
                if st.session_state.serve_num == 1: st.session_state.serve_num = 2; st.rerun()
                else: register_point(p2_n if srv_idx == 1 else p1_n, "Dupla Falta", "Erro", "Saque"); st.rerun()

        elif st.session_state.step == "RESULT":
            cr1, cr2, cr3 = st.columns(3)
            if cr1.button("🏆 WINNER"): st.session_state.temp_data.update({'res':'Winner','cat':'Winner'}); st.session_state.step = "DETAIL"; st.rerun()
            if cr2.button("📉 N. FORÇADO"): st.session_state.temp_data.update({'res':'Erro','cat':'Unforced'}); st.session_state.step = "DETAIL"; st.rerun()
            if cr3.button("💥 FORÇADO"): st.session_state.temp_data.update({'res':'Erro','cat':'Forced'}); st.session_state.step = "DETAIL"; st.rerun()
            st.divider()
            if st.button("🎯 ACE"): register_point(p1_n if srv_idx == 1 else p2_n, "Ace", "Winner", "Saque", st.session_state.temp_data['dir']); st.rerun()
            if st.button("🎾 SERVICE WINNER"): register_point(p1_n if srv_idx == 1 else p2_n, "Service Winner", "Winner", "Saque", st.session_state.temp_data['dir']); st.rerun()

        elif st.session_state.step == "DETAIL":
            winner = st.radio("Ponto para:", [p1_n, p2_n], horizontal=True)
            cg, cz = st.columns(2)
            golpe = cg.selectbox("Golpe:", ["Forehand", "Backhand", "Voleio", "Smash", "Drop Shot", "Slice"])
            
            if golpe == "Voleio": zona = cz.radio("Zona:", ["Rede"], index=0)
            elif golpe == "Smash": zona = cz.radio("Zona:", ["Rede", "Baseline"], index=0)
            else: zona = cz.radio("Zona:", ["Baseline", "Rede"], index=0)
            
            direcao = st.radio("Direção:", ["Cruzada", "Paralela", "No Corpo"], horizontal=True)
            if st.button("✅ REGISTRAR"):
                register_point(winner, st.session_state.temp_data['res'], st.session_state.temp_data['cat'], golpe, direcao, zona); st.rerun()
    else:
        st.success("FIM DE JOGO!")

    # --- MATCH STATS (FINAL DA PÁGINA) ---
    st.divider()
    st.subheader("📊 Estatísticas da Partida (Broadcasting Standard)")
    if st.session_state.match_data:
        df_stats = pd.DataFrame(st.session_state.match_data)
        ms = calculate_match_stats(df_stats, p1_n, p2_n)
        
        st.markdown(f"""
        <table class="stats-table">
            <tr class="stats-header">
                <th style="width:30%">{p1_n}</th>
                <th style="width:40%">ESTATÍSTICA</th>
                <th style="width:30%">{p2_n}</th>
            </tr>
            <tr class="stats-row">
                <td class="stats-cell">{ms[0]['Aces']}</td>
                <td class="stats-cell stats-label">ACES</td>
                <td class="stats-cell">{ms[1]['Aces']}</td>
            </tr>
            <tr class="stats-row">
                <td class="stats-cell">{ms[0]['DF']}</td>
                <td class="stats-cell stats-label">DUPLAS FALTAS</td>
                <td class="stats-cell">{ms[1]['DF']}</td>
            </tr>
            <tr class="stats-row">
                <td class="stats-cell">{ms[0]['Winners']}</td>
                <td class="stats-cell stats-label">WINNERS</td>
                <td class="stats-cell">{ms[1]['Winners']}</td>
            </tr>
            <tr class="stats-row">
                <td class="stats-cell">{ms[0]['UE']}</td>
                <td class="stats-cell stats-label">ERROS NÃO FORÇADOS</td>
                <td class="stats-cell">{ms[1]['UE']}</td>
            </tr>
            <tr class="stats-row">
                <td class="stats-cell">{ms[0]['Net']}</td>
                <td class="stats-cell stats-label">EFICIÊNCIA NA REDE</td>
                <td class="stats-cell">{ms[1]['Net']}</td>
            </tr>
            <tr class="stats-row">
                <td class="stats-cell" style="color:#00feab; font-weight:bold;">{ms[0]['Total']}</td>
                <td class="stats-cell stats-label">TOTAL DE PONTOS (% GANHOS)</td>
                <td class="stats-cell" style="color:#00feab; font-weight:bold;">{ms[1]['Total']}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
    else:
        st.info("Aguardando dados para consolidar estatísticas.")

    # --- CONTROLES DE RODAPÉ ---
    st.divider()
    f1, f2, f3 = st.columns([1,1,2])
    if f1.button("🔄 DESFAZER"): 
        if st.session_state.match_data: st.session_state.match_data.pop(); st.rerun()
    if f2.button("🆕 NOVO JOGO"): st.session_state.clear(); st.rerun()
    if st.session_state.match_data:
        score_f = f"{s['p1_sets']}-{s['p2_sets']} ({', '.join(s['history'])})"
        st.download_button("📥 EXPORTAR PDF", generate_pdf(st.session_state.match_data, p1_n, p2_n, score_f), "scout.pdf")