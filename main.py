import streamlit as st
import requests
import pandas as pd
import re
from streamlit_agraph import agraph, Node, Edge, Config

# Configuração da página
st.set_page_config(page_title="OSINT Corporate | Private", page_icon="👁️‍🗨️", layout="wide")

# Estilização CSS customizada
st.markdown("""
    <style>
    /* Ajuste fino de margens e fontes */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; color: #E0E0E0; }
    .stTextInput>div>div>input { background-color: #1E1E1E; color: #FFF; }
    </style>
""", unsafe_allow_html=True)

# Sistema de autenticação (Portão de Acesso)
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("password", "admin123"): # Fallback para testes
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("👁️‍🗨️ OSINT Access Gateway")
        st.text_input("Insira a chave de liberação", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("👁️‍🗨️ OSINT Access Gateway")
        st.text_input("Insira a chave de liberação", type="password", on_change=password_entered, key="password")
        st.error("❌ Credencial revogada ou inválida.")
        return False
    return True

# Funções de busca e integração com APIs públicas
@st.cache_data(ttl=3600) # Cache para evitar requisições repetidas
def buscar_dados(cnpj):
    cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj_limpo) != 14: return None, "Formato de CNPJ inválido."
    
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200: return res.json(), None
        return None, f"Erro {res.status_code}: CNPJ não localizado na base pública."
    except Exception as e:
        return None, f"Falha de comunicação: {e}"

def gerar_url_osint(termo, motor):
    termo_url = requests.utils.quote(termo)
    if motor == "linkedin": return f"https://www.google.com/search?q=site:linkedin.com/in/+%22{termo_url}%22"
    if motor == "jusbrasil": return f"https://www.jusbrasil.com.br/consulta-processual/busca?q={termo_url}"
    if motor == "transparencia": return f"https://portaldatransparencia.gov.br/busca?termo={termo_url}"
    if motor == "docs": return f"https://www.google.com/search?q=%22{termo_url}%22+ext:pdf+OR+ext:doc"
    return ""

# Execução da aplicação principal
if check_password():
    st.title("🔍 Sistema de Inteligência Corporativa")
    st.markdown("Extração estruturada de dados fiscais, societários e vetores de investigação paralela.")
    
    with st.container(border=True):
        col_busca, col_btn = st.columns([4, 1], vertical_alignment="bottom")
        with col_busca:
            cnpj_input = st.text_input("Target CNPJ:", placeholder="Digite apenas números ou com pontuação...")
        with col_btn:
            run_btn = st.button("Iniciar Varredura 🚀", use_container_width=True, type="primary")

    if run_btn and cnpj_input:
        with st.spinner("Interceptando dados da Receita Federal..."):
            dados, erro = buscar_dados(cnpj_input)
            
            if erro:
                st.error(erro)
            else:
                # Setup das abas para limpar o visual
                aba_resumo, aba_qsa, aba_grafo = st.tabs(["📄 Dossiê Principal", "👥 QSA & OSINT", "🕸️ Topologia Societária"])
                
                razao_social = dados.get('razao_social', 'N/D')
                nome_fantasia = dados.get('nome_fantasia', razao_social)
                socios = dados.get('qsa', [])

                # Aba 1: Exibição do Dossiê Cadastral
                with aba_resumo:
                    st.subheader(f"🏢 {nome_fantasia}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Situação Cadastral", dados.get('descricao_situacao_cadastral', 'N/D'))
                    c2.metric("Data de Abertura", dados.get('data_inicio_atividade', 'N/D'))
                    c3.metric("Capital Social", f"R$ {dados.get('capital_social', 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    
                    st.divider()
                    
                    col_dados1, col_dados2 = st.columns(2)
                    with col_dados1:
                        with st.container(border=True):
                            st.markdown("**📌 Informações Fiscais**")
                            st.text_input("Razão Social", razao_social, disabled=True)
                            st.text_input("Natureza Jurídica", dados.get('natureza_juridica', ''), disabled=True)
                            st.text_input("CNAE Principal", f"{dados.get('cnae_fiscal', '')} - {dados.get('cnae_fiscal_descricao', '')}", disabled=True)
                    
                    with col_dados2:
                        with st.container(border=True):
                            st.markdown("**📍 Contato e Localização**")
                            st.text_input("Endereço Completo", f"{dados.get('logradouro')}, {dados.get('numero')} - {dados.get('bairro')}, {dados.get('municipio')}/{dados.get('uf')}", disabled=True)
                            st.text_input("E-mails Registrados", dados.get('email', 'Não consta'), disabled=True)
                            st.text_input("Telefones", f"{dados.get('ddd_telefone_1', '')} / {dados.get('ddd_telefone_2', '')}", disabled=True)

                # Aba 2: Sócios e links externos para OSINT
                with aba_qsa:
                    st.subheader("Quadro de Sócios e Ferramentas de Rastreio")
                    if not socios:
                        st.info("Nenhum sócio registrado na base pública para este CNPJ.")
                    else:
                        # Exibir dataframe cru completo para não ocultar nada
                        st.markdown("**📋 Dados Brutos do QSA (Inclui CPFs mascarados e Representantes)**")
                        df_socios = pd.DataFrame(socios)
                        st.dataframe(df_socios, use_container_width=True)

                        st.divider()
                        st.markdown("**🎯 Painel de Ações de Investigação (Por Sócio)**")
                        
                        # Cria um "card" expansível para cada sócio com links de investigação
                        for socio in socios:
                            nome_socio = socio.get('nome_socio', 'Desconhecido')
                            doc_socio = socio.get('cnpj_cpf_do_socio', 'Doc Indisponível')
                            qualificacao = socio.get('qualificacao_socio', '')

                            with st.expander(f"👤 {nome_socio} | {qualificacao} ({doc_socio})"):
                                st.markdown(f"**Investigar Ativos e Histórico de `{nome_socio}`:**")
                                
                                btn_c1, btn_c2, btn_c3, btn_c4 = st.columns(4)
                                with btn_c1:
                                    st.link_button("🌐 Rastrear no LinkedIn", gerar_url_osint(nome_socio, "linkedin"), use_container_width=True)
                                with btn_c2:
                                    st.link_button("⚖️ Processos Jusbrasil", gerar_url_osint(nome_socio, "jusbrasil"), use_container_width=True)
                                with btn_c3:
                                    st.link_button("🏛️ Gov. Transparência", gerar_url_osint(nome_socio, "transparencia"), use_container_width=True)
                                with btn_c4:
                                    st.link_button("📄 Vazamentos (PDF/DOC)", gerar_url_osint(nome_socio, "docs"), use_container_width=True)

                # Aba 3: Mapeamento de conexões societárias
                with aba_grafo:
                    st.subheader("Topologia de Conexões Diretas")
                    st.caption("Nota: A API gratuita não mapeia conexões de 2º grau (outras empresas dos mesmos sócios).")
                    
                    if socios:
                        nodes, edges = [], []
                        # Empresa
                        nodes.append(Node(id=razao_social, label=nome_fantasia, size=40, shape="hexagon", color="#8B0000"))
                        
                        for socio in socios:
                            nome_socio = socio.get('nome_socio')
                            qual = socio.get('qualificacao_socio')
                            # Sócios
                            nodes.append(Node(id=nome_socio, label=nome_socio, size=25, color="#1f77b4"))
                            edges.append(Edge(source=razao_social, target=nome_socio, label=qual, color="#888888"))
                        
                        config = Config(width="100%", height=500, directed=True, physics=True, hierarchical=False)
                        agraph(nodes=nodes, edges=edges, config=config)
