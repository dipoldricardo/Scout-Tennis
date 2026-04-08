import streamlit as st
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- CONFIGURAÇÃO DE PÁGINA MASTER ---
st.set_page_config(page_title="ATP Scout Pro: Marco Valente Edition", page_icon="🎾", layout="wide")

# --- BLOCO DE ESTILIZAÇÃO CSS (INTERFACE PROFISSIONAL) ---
st.markdown("""
    <style>
    .main-score { background-color: #001e36; padding: 30px; border-radius: 15px; border-left: 10px solid #00feab; text-align: center; margin-bottom: 25px;}
    .set-score-banner { background-color: #00feab; color: #001e36; font-weight: 900; font-size: 24px; border-radius: 5px; padding: 8px; margin-bottom: 20px; text-transform: uppercase;}
    .player-name { color: #FFFFFF; font-size: 28px; font-weight: bold; }
    .score-value { color: #00feab; font-size: 40px; font-weight: 900; }
    .serve-badge { background-color: #DFFF00; color: #000; padding: 12px 35px; border-radius: 50px; font-weight: 900; font-size: 22px; display: inline-block; margin-bottom: 20px; border: 3px solid #000; }
    .step-label { color: #AAAAAA; text-transform: uppercase; font-size: 14px; font-weight: bold; margin-bottom: 8px; display: block;}
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DE GERAÇÃO DE RELATÓRIO PDF COMPLETO ---
def generate_pdf(data, p1, p2, score_final):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(190, 15, "OFFICIAL ATP SCOUT REPORT", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(190, 10, f"Match: {p1} vs {p2}", ln=True, align="C")
    pdf.cell(190, 10, f"Placar Final: {score_final}", ln=True, align="C")
    pdf.ln(10)
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(0, 254, 171)
    pdf.set_font("Helvetica", "B", 10)
    cols = ["Vencedor", "Resultado", "Golpe", "Zona", "Direção", "Placar"]
    widths = [32, 32, 32, 30, 32, 32]
    for i, col in enumerate(cols): pdf.cell(widths[i], 12, col, 1, 0, "C", True)
    pdf.ln()
    
    # Preenchimento de Dados
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

# --- LÓGICA DE PONTUAÇÃO ATP (TRADICIONAL) ---
def format_pts(p1, p2):
    mapping = {0: "0", 1: "15", 2: "30", 3: "40"}
    if p1 <= 3 and p2 <= 3:
        if p1 == 3 and p2 == 3: return "40", "40"
        return mapping[p1], mapping[p2]
    if p1 == p2: return "40", "40"
    return ("AD", "40") if p1 > p2 else ("40", "AD")

# --- INICIALIZAÇÃO E GESTÃO DE ESTADOS (SESSION STATE) ---
if 'match_data' not in st.session_state: st.session_state.match_data = []
if 'score' not in st.session_state: 
    st.session_state.score = {"p1_pts": 0, "p2_pts": 0, "p1_gms": 0, "p2_gms": 0, "p1_sets": 0, "p2_sets": 0, "history": []}
if 'setup' not in st.session_state: 
    st.session_state.setup = {"active": False, "p1": "", "p2": "", "server": 1, "match_over": False, "format": "Melhor de 3"}
if 'step' not in st.session_state: st.session_state.step = "SERVICE"
if 'serve_num' not in st.session_state: st.session_state.serve_num = 1
if 'temp_data' not in st.session_state: st.session_state.temp_data = {}

# --- FUNÇÃO PRINCIPAL: REGISTRO E CÁLCULO DE PONTOS ---
def register_point(winner_name, res, cat="Winner", golpe="Saque", dir_g="N/A", pos="Baseline"):
    s = st.session_state.score
    setup = st.session_state.setup
    
    # Incremento de Pontos
    if winner_name == setup['p1']: s["p1_pts"] += 1
    else: s["p2_pts"] += 1
    
    # Fechamento de Game
    if (s["p1_pts"] >= 4 and s["p1_pts"] - s["p2_pts"] >= 2) or (s["p2_pts"] >= 4 and s["p2_pts"] - s["p1_pts"] >= 2):
        if s["p1_pts"] > s["p2_pts"]: s["p1_gms"] += 1
        else: s["p2_gms"] += 1
        s["p1_pts"], s["p2_pts"] = 0, 0
        setup['server'] = 2 if setup['server'] == 1 else 1
        
        # Fechamento de Set
        g1, g2 = s["p1_gms"], s["p2_gms"]
        if (g1 >= 6 and g1 - g2 >= 2) or g1 == 7 or (g2 >= 6 and g2 - g1 >= 2) or g2 == 7:
            if g1 > g2: s["p1_sets"] += 1
            else: s["p2_sets"] += 1
            s["history"].append(f"{g1}-{g2}")
            s["p1_gms"], s["p2_gms"] = 0, 0
            
            # Fim da Partida
            target = {"Set Único": 1, "Melhor de 3": 2, "Melhor de 5": 3}[setup["format"]]
            if s["p1_sets"] == target or s["p2_sets"] == target:
                setup["match_over"] = True

    # Armazenamento no Histórico
    st.session_state.match_data.append({
        "Vencedor": winner_name, "Resultado": res, "Categoria": cat, "Golpe": golpe, "Direcao": dir_g, "Posicao": pos,
        "Score": f"{s['p1_sets']}-{s['p2_sets']} ({s['p1_gms']}-{s['p2_gms']})"
    })
    
    # Reset de Fluxo
    st.session_state.step = "SERVICE"
    st.session_state.serve_num = 1
    st.session_state.temp_data = {}

# --- INTERFACE DE SETUP INICIAL ---
if not st.session_state.setup["active"]:
    st.title("🎾 Scout-Tennis Pro: Elite Management")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        p1_in = c1.text_input("Jogador A (Mandante)", "Atleta 1")
        p2_in = c2.text_input("Jogador B (Visitante)", "Atleta 2")
        
        c3, c4 = st.columns(2)
        format_in = c3.selectbox("Formato da Partida:", ["Set Único", "Melhor de 3", "Melhor de 5"], index=1)
        srv_in = c4.radio("Quem inicia sacando?", [p1_in, p2_in], horizontal=True)
        
        if st.button("🚀 INICIAR PARTIDA E ABRIR SCOUT"):
            st.session_state.setup.update({"active": True, "p1": p1_in, "p2": p2_in, "server": 1 if srv_in == p1_in else 2, "format": format_in})
            st.rerun()

else:
    # --- SIDEBAR DE ESTATÍSTICAS EM TEMPO REAL ---
    with st.sidebar:
        st.header("📊 Análise de Dados")
        if st.session_state.match_data:
            df_stats = pd.DataFrame(st.session_state.match_data)
            st.plotly_chart(px.pie(df_stats, names='Vencedor', hole=0.4, title="Domínio de Pontos"), use_container_width=True)
            st.write(f"Pontos registrados: {len(df_stats)}")
            st.divider()
            st.markdown("**Último Ponto:**")
            st.json(st.session_state.match_data[-1])
        if st.button("🚨 RESET TOTAL"): st.session_state.clear(); st.rerun()

    # --- PLACAR CENTRAL ---
    s = st.session_state.score
    p1_n, p2_n = st.session_state.setup['p1'], st.session_state.setup['p2']
    srv_idx = st.session_state.setup['server']
    pt1, pt2 = format_pts(s["p1_pts"], s["p2_pts"])
    
    st.markdown(f"""
    <div class="main-score">
        <div class="set-score-banner">{st.session_state.setup['format'].upper()} | Sets Finalizados: {", ".join(s['history']) if s['history'] else "0-0"}</div>
        <div class="player-name">{p1_n}{" 🎾" if srv_idx == 1 else ""}</div>
        <div class="score-value">SETS: {s['p1_sets']} | GAMES: {s['p1_gms']} | <span style='color:white;'>({pt1})</span></div>
        <hr style="border: 0.5px solid #004080; margin: 15px 0;">
        <div class="player-name">{p2_n}{" 🎾" if srv_idx == 2 else ""}</div>
        <div class="score-value">SETS: {s['p2_sets']} | GAMES: {s['p2_gms']} | <span style='color:white;'>({pt2})</span></div>
    </div>
    """, unsafe_allow_html=True)

    # --- INTERFACE DE SCOUTING (ETAPAS) ---
    if not st.session_state.setup["match_over"]:
        
        # PASSO 1: O SAQUE
        if st.session_state.step == "SERVICE":
            st.markdown(f"<div style='text-align:center'><span class='serve-badge'>{st.session_state.serve_num}º SERVIÇO</span></div>", unsafe_allow_html=True)
            st.markdown("<span class='step-label'>1. Direção do Saque:</span>", unsafe_allow_html=True)
            cs1, cs2, cs3 = st.columns(3)
            if cs1.button("WIDE (Aberto)"): st.session_state.temp_data['dir_saque'] = "Wide"; st.session_state.step = "RESULT"; st.rerun()
            if cs2.button("BODY (Corpo)"): st.session_state.temp_data['dir_saque'] = "Body"; st.session_state.step = "RESULT"; st.rerun()
            if cs3.button("T (Centro)"): st.session_state.temp_data['dir_saque'] = "T"; st.session_state.step = "RESULT"; st.rerun()
            
            st.divider()
            if st.button("❌ FALTA / NET"):
                if st.session_state.serve_num == 1: st.session_state.serve_num = 2; st.rerun()
                else: register_point(p2_n if srv_idx == 1 else p1_n, "Dupla Falta", "Erro", "Saque"); st.rerun()

        # PASSO 2: O RESULTADO DO PONTO
        elif st.session_state.step == "RESULT":
            st.markdown("<span class='step-label'>2. Desfecho do Ponto:</span>", unsafe_allow_html=True)
            cr1, cr2, cr3 = st.columns(3)
            if cr1.button("🏆 WINNER", type="primary"): 
                st.session_state.temp_data.update({'res':'Winner','cat':'Winner'}); st.session_state.step = "DETAIL"; st.rerun()
            if cr2.button("📉 ERRO NÃO FORÇADO"): 
                st.session_state.temp_data.update({'res':'Erro','cat':'Unforced'}); st.session_state.step = "DETAIL"; st.rerun()
            if cr3.button("💥 ERRO FORÇADO"): 
                st.session_state.temp_data.update({'res':'Erro','cat':'Forced'}); st.session_state.step = "DETAIL"; st.rerun()
            
            st.divider()
            if st.button("🎯 ACE"): register_point(p1_n if srv_idx == 1 else p2_n, "Ace", "Winner", "Saque", st.session_state.temp_data['dir_saque']); st.rerun()
            if st.button("🎾 SERVICE WINNER"): register_point(p1_n if srv_idx == 1 else p2_n, "Service Winner", "Winner", "Saque", st.session_state.temp_data['dir_saque']); st.rerun()

        # PASSO 3: O RIGOR TÉCNICO (DETALHAMENTO)
        elif st.session_state.step == "DETAIL":
            st.markdown("<span class='step-label'>3. Detalhamento Técnico Final:</span>", unsafe_allow_html=True)
            winner_choice = st.radio("Ponto registrado para:", [p1_n, p2_n], horizontal=True)
            
            col_g, col_z = st.columns(2)
            golpe = col_g.selectbox("Golpe Definidor:", ["Forehand", "Backhand", "Voleio", "Smash", "Drop Shot", "Slice"])
            
            # --- LÓGICA DE RIGOR TÉCNICO MARCO VALENTE ---
            if golpe == "Voleio":
                # Voleio obrigatoriamente na rede
                zona = col_z.radio("Zona da Quadra:", ["Rede"], index=0)
                st.warning("⚠️ Voleio: Zona travada em 'Rede' por impossibilidade técnica de fundo.")
            elif golpe == "Smash":
                # Smash pode ser fundo (back-court overhead)
                zona = col_z.radio("Zona da Quadra:", ["Rede", "Baseline"], index=0)
                st.info("ℹ️ Smash: Zona flexível para permitir smashes de fundo de quadra.")
            else:
                # Padrão
                zona = col_z.radio("Zona da Quadra:", ["Baseline", "Rede"], index=0)
            
            # Direções Táticas (Drop Shot é a própria definição de curta, por isso removida como direção)
            direcao = st.radio("Direção da Bola:", ["Cruzada", "Paralela", "No Corpo"], horizontal=True)
            
            if st.button("✅ REGISTRAR NO SCOUT"):
                register_point(winner_choice, st.session_state.temp_data['res'], st.session_state.temp_data['cat'], golpe, direcao, zona)
                st.rerun()
    else:
        st.balloons()
        st.success("🏆 PARTIDA FINALIZADA!")

    # --- RODAPÉ, DESFAZER E DOWNLOAD ---
    st.divider()
    bot1, bot2, bot3 = st.columns([1, 1, 2])
    with bot1:
        if st.button("🔄 DESFAZER ÚLTIMO"):
            if st.session_state.match_data: st.session_state.match_data.pop(); st.rerun()
    with bot2:
        if st.button("🆕 NOVA PARTIDA"): st.session_state.clear(); st.rerun()
    with bot3:
        if st.session_state.match_data:
            score_final_str = f"{s['p1_sets']}-{s['p2_sets']} ({', '.join(s['history'])})"
            pdf_bytes = generate_pdf(st.session_state.match_data, p1_n, p2_n, score_final_str)
            st.download_button("📥 EXPORTAR PDF COMPLETO", data=pdf_bytes, file_name="scout_atp_completo.pdf", mime="application/pdf")