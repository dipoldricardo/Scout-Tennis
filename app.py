import streamlit as st
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# Configuração de Página Nível Master
st.set_page_config(page_title="ATP Scout Pro: Marco Valente Edition", page_icon="🎾", layout="wide")

# --- ESTILIZAÇÃO CUSTOMIZADA ---
st.markdown("""
    <style>
    .main-score { background-color: #001e36; padding: 25px; border-radius: 15px; border-left: 10px solid #00feab; text-align: center; margin-bottom: 20px;}
    .set-score-banner { background-color: #00feab; color: #001e36; font-weight: 900; font-size: 22px; border-radius: 5px; padding: 5px; margin-bottom: 15px; }
    .player-name { color: #FFFFFF; font-size: 26px; font-weight: bold; }
    .score-value { color: #00feab; font-size: 35px; font-weight: 900; }
    .serve-badge { background-color: #DFFF00; color: #000; padding: 10px 25px; border-radius: 50px; font-weight: 900; font-size: 20px; display: inline-block; margin-bottom: 15px; border: 2px solid #000; }
    .step-label { color: #AAAAAA; text-transform: uppercase; font-size: 13px; font-weight: bold; margin-bottom: 5px; display: block;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO GERADORA DE PDF (DADOS BRUTOS) ---
def generate_pdf(data, p1, p2, score_final):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(190, 10, "OFFICIAL SCOUT REPORT - ATP STANDARD", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, f"{p1} vs {p2} | Placar Final: {score_final}", ln=True, align="C")
    pdf.ln(10)
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(0, 254, 171)
    pdf.set_font("Helvetica", "B", 10)
    cols = ["Vencedor", "Resultado", "Golpe", "Zona", "Direção", "Placar"]
    widths = [32, 32, 32, 30, 32, 32]
    for i, col in enumerate(cols): pdf.cell(widths[i], 10, col, 1, 0, "C", True)
    pdf.ln()
    
    # Dados
    pdf.set_font("Helvetica", size=9)
    for row in data:
        pdf.cell(widths[0], 10, str(row.get("Vencedor", "-")), 1)
        pdf.cell(widths[1], 10, str(row.get("Resultado", "-")), 1)
        pdf.cell(widths[2], 10, str(row.get("Golpe", "-")), 1)
        pdf.cell(widths[3], 10, str(row.get("Posicao", "-")), 1)
        pdf.cell(widths[4], 10, str(row.get("Direcao", "-")), 1)
        pdf.cell(widths[5], 10, str(row.get("Score", "-")), 1)
        pdf.ln()
    return bytes(pdf.output())

# --- LÓGICA DE PONTUAÇÃO ATP ---
def format_pts(p1, p2):
    mapping = {0: "0", 1: "15", 2: "30", 3: "40"}
    if p1 <= 3 and p2 <= 3:
        if p1 == 3 and p2 == 3: return "40", "40"
        return mapping[p1], mapping[p2]
    if p1 == p2: return "40", "40"
    return ("AD", "40") if p1 > p2 else ("40", "AD")

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
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    
    if winner_name == p1_n: s["p1_pts"] += 1
    else: s["p2_pts"] += 1
    
    # Lógica de Game
    if (s["p1_pts"] >= 4 and s["p1_pts"] - s["p2_pts"] >= 2) or (s["p2_pts"] >= 4 and s["p2_pts"] - s["p1_pts"] >= 2):
        if s["p1_pts"] > s["p2_pts"]: s["p1_gms"] += 1
        else: s["p2_gms"] += 1
        s["p1_pts"], s["p2_pts"] = 0, 0
        st.session_state.setup['server'] = 2 if st.session_state.setup['server'] == 1 else 1
        
        # Lógica de Set
        g1, g2 = s["p1_gms"], s["p2_gms"]
        if (g1 >= 6 and g1 - g2 >= 2) or g1 == 7 or (g2 >= 6 and g2 - g1 >= 2) or g2 == 7:
            if g1 > g2: s["p1_sets"] += 1
            else: s["p2_sets"] += 1
            s["history"].append(f"{g1}-{g2}")
            s["p1_gms"], s["p2_gms"] = 0, 0
            
            # Fim da Partida
            target = {"Set Único": 1, "Melhor de 3": 2, "Melhor de 5": 3}[st.session_state.setup["format"]]
            if s["p1_sets"] == target or s["p2_sets"] == target:
                st.session_state.setup["match_over"] = True

    st.session_state.match_data.append({
        "Vencedor": winner_name, "Resultado": res, "Categoria": cat, "Golpe": golpe, "Direcao": dir_g, "Posicao": pos,
        "Score": f"{s['p1_sets']}-{s['p2_sets']} ({s['p1_gms']}-{s['p2_gms']})"
    })
    st.session_state.step = "SERVICE"; st.session_state.serve_num = 1; st.session_state.temp_data = {}

# --- INTERFACE DE SETUP ---
if not st.session_state.setup["active"]:
    st.title("🎾 Scout-Tennis Pro: Elite Edition")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        p1_in = c1.text_input("Jogador A", "Atleta 1")
        p2_in = c2.text_input("Jogador B", "Atleta 2")
        
        c3, c4 = st.columns(2)
        format_in = c3.selectbox("Formato da Partida:", ["Set Único", "Melhor de 3", "Melhor de 5"], index=1)
        srv_in = c4.radio("Inicia Sacando:", [p1_in, p2_in], horizontal=True)
        
        if st.button("🚀 INICIAR PARTIDA PROFISSIONAL"):
            st.session_state.setup.update({"active": True, "p1": p1_in, "p2": p2_in, "server": 1 if srv_in == p1_in else 2, "format": format_in})
            st.rerun()

else:
    # --- DASHBOARD ---
    with st.sidebar:
        st.header("📊 Resumo Live")
        if st.session_state.match_data:
            df = pd.DataFrame(st.session_state.match_data)
            st.write(f"Total de Pontos: {len(df)}")
            st.plotly_chart(px.pie(df, names='Vencedor', hole=0.4, color_discrete_sequence=['#00feab', '#004080']), use_container_width=True)
        if st.button("🚨 RESET TOTAL"): st.session_state.clear(); st.rerun()

    # --- PLACAR CENTRAL ---
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    srv_idx = st.session_state.setup['server']
    pt1, pt2 = format_pts(s["p1_pts"], s["p2_pts"])
    
    st.markdown(f"""
    <div class="main-score">
        <div class="set-score-banner">{st.session_state.setup['format'].upper()} | Sets: {", ".join(s['history']) if s['history'] else "0-0"}</div>
        <div class="player-name">{p1_n}{" 🎾" if srv_idx == 1 else ""}</div>
        <div class="score-value">SETS: {s['p1_sets']} | GMS: {s['p1_gms']} | <span style='color:white;'>({pt1})</span></div>
        <hr style="border: 0.5px solid #004080; margin: 15px 0;">
        <div class="player-name">{p2_n}{" 🎾" if srv_idx == 2 else ""}</div>
        <div class="score-value">SETS: {s['p2_sets']} | GMS: {s['p2_gms']} | <span style='color:white;'>({pt2})</span></div>
    </div>
    """, unsafe_allow_html=True)

    # --- ÁREA DE SCOUT ---
    if not st.session_state.setup["match_over"]:
        
        # PASSO 1: O SERVIÇO
        if st.session_state.step == "SERVICE":
            st.markdown(f"<div style='text-align:center'><span class='serve-badge'>{st.session_state.serve_num}º SERVIÇO</span></div>", unsafe_allow_html=True)
            st.markdown("<span class='step-label'>Direção do Saque:</span>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            if c1.button("WIDE (Aberto)"): st.session_state.temp_data['dir_saque'] = "Wide"; st.session_state.step = "RESULT"; st.rerun()
            if c2.button("BODY (Corpo)"): st.session_state.temp_data['dir_saque'] = "Body"; st.session_state.step = "RESULT"; st.rerun()
            if c3.button("T (Centro)"): st.session_state.temp_data['dir_saque'] = "T"; st.session_state.step = "RESULT"; st.rerun()
            
            st.divider()
            if st.button("❌ FALTA / NET"):
                if st.session_state.serve_num == 1: st.session_state.serve_num = 2; st.rerun()
                else: register_point(p2_n if srv_idx == 1 else p1_n, "Dupla Falta", "Erro", "Saque"); st.rerun()

        # PASSO 2: O RESULTADO DO PONTO
        elif st.session_state.step == "RESULT":
            st.markdown("<span class='step-label'>Finalização do Ponto:</span>", unsafe_allow_html=True)
            cr1, cr2, cr3 = st.columns(3)
            if cr1.button("🏆 WINNER", type="primary"): 
                st.session_state.temp_data.update({'res':'Winner','cat':'Winner'}); st.session_state.step = "DETAIL"; st.rerun()
            if cr2.button("📉 N. FORÇADO"): 
                st.session_state.temp_data.update({'res':'Erro','cat':'Unforced'}); st.session_state.step = "DETAIL"; st.rerun()
            if cr3.button("💥 FORÇADO"): 
                st.session_state.temp_data.update({'res':'Erro','cat':'Forced'}); st.session_state.step = "DETAIL"; st.rerun()
            
            st.divider()
            if st.button("🎯 ACE"): register_point(p1_n if srv_idx == 1 else p2_n, "Ace", "Winner", "Saque", st.session_state.temp_data['dir_saque']); st.rerun()
            if st.button("🎾 SERVICE WINNER"): register_point(p1_n if srv_idx == 1 else p2_n, "Service Winner", "Winner", "Saque", st.session_state.temp_data['dir_saque']); st.rerun()

        # PASSO 3: DETALHAMENTO TÉCNICO (Onde a mágica acontece)
        elif st.session_state.step == "DETAIL":
            st.markdown("<span class='step-label'>Detalhamento Técnico:</span>", unsafe_allow_html=True)
            winner_choice = st.radio("Ponto para:", [p1_n, p2_n], horizontal=True)
            
            col_g, col_z = st.columns(2)
            golpe = col_g.selectbox("Golpe de Definição:", ["Forehand", "Backhand", "Voleio", "Smash", "Drop Shot", "Slice"])
            
            # --- LÓGICA DE RIGOR TÉCNICO MARCO VALENTE ---
            if golpe == "Voleio":
                zona = col_z.radio("Zona da Quadra:", ["Rede"], index=0) # BLOQUEADO
                st.warning("Voleio detectado: Zona obrigatoriamente definida como Rede.")
            elif golpe == "Smash":
                zona = col_z.radio("Zona da Quadra:", ["Rede", "Baseline"], index=0) # FLEXÍVEL
            else:
                zona = col_z.radio("Zona da Quadra:", ["Baseline", "Rede"], index=0)
            
            direcao = st.radio("Direção da Bola:", ["Cruzada", "Paralela", "No Corpo", "Curta"], horizontal=True)
            
            if st.button("✅ REGISTRAR PONTO NO SCOUT"):
                register_point(winner_choice, st.session_state.temp_data['res'], st.session_state.temp_data['cat'], golpe, direcao, zona)
                st.rerun()
    else:
        st.balloons()
        st.success("PARTIDA FINALIZADA!")

    # --- RODAPÉ E DOWNLOAD ---
    st.divider()
    bot_c1, bot_c2, bot_c3 = st.columns([1, 1, 2])
    with bot_c1:
        if st.button("🔄 DESFAZER ÚLTIMO"):
            if st.session_state.match_data: st.session_state.match_data.pop(); st.rerun()
    with bot_c2:
        if st.button("🆕 NOVA PARTIDA"): st.session_state.clear(); st.rerun()
    with bot_c3:
        if st.session_state.match_data:
            score_final_str = f"{s['p1_sets']}-{s['p2_sets']} ({', '.join(s['history'])})"
            pdf_bytes = generate_pdf(st.session_state.match_data, p1_n, p2_n, score_final_str)
            st.download_button("📥 EXPORTAR RELATÓRIO PDF PROFISSIONAL", data=pdf_bytes, file_name="scout_atp_pro.pdf", mime="application/pdf")