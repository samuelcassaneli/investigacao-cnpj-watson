# Investigação de CNPJ & Inteligência Corporativa (OSINT)

Ferramenta em Python projetada para automação, análise e enriquecimento de dados cadastrais e societários de CNPJs a partir de fontes públicas (BrasilAPI). O projeto fornece uma interface intuitiva para análise de risco, mapeamento de vínculos corporativos e auditoria de parceiros comerciais.

---

## Recursos Principais

* **Dossiê Cadastral**: Consulta em tempo real de informações cadastrais, situação fiscal e dados de localização direto da Receita Federal.
* **Quadro de Sócios e Administradores (QSA)**: Extração automatizada e formatação estruturada de dados de relacionamento e participações.
* **Integração OSINT**: Geração automática de chaves de pesquisa avançadas para motores externos (LinkedIn, Jusbrasil, Portal da Transparência, e busca por documentos vazados/PDF).
* **Mapeamento de Vínculos Societários**: Representação topológica das conexões de primeiro grau através de grafos interativos (`streamlit-agraph`).
* **Segurança de Acesso**: Proteção por gateway de autenticação simples na interface.

---

## Tecnologias e Dependências

* **Backend**: Python 3.x
* **Interface Web**: Streamlit
* **Modelagem de Grafos**: Streamlit AGraph
* **Processamento de Dados**: Pandas

---

## Instalação e Execução

### Via Dev Container (Recomendado)

O projeto inclui suporte completo a **Dev Containers**, isolando o ambiente em um container Docker para evitar problemas de dependências.

1. Instale o Docker e a extensão **Dev Containers** no VS Code.
2. Abra este diretório no VS Code.
3. Clique em **Reopen in Container** quando notificado.
4. O ambiente e os pacotes necessários serão instalados e configurados automaticamente.
5. Inicie o Streamlit no terminal do container:
   ```bash
   streamlit run main.py
   ```

### Instalação Local

Caso queira rodar localmente sem usar Docker:

1. Clone o repositório.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o aplicativo:
   ```bash
   streamlit run main.py
   ```
