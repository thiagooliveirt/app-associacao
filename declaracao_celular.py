import streamlit as st
from fpdf import FPDF
from datetime import datetime
import re
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Associação Alto Uruguai", page_icon="📄", layout="centered")

# --- ESTILO VISUAL (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #202b45; color: white; }
    h1, h2, h3, p { color: white !important; }
    label { color: white !important; font-weight: bold; }
    div.stButton > button { background-color: #ff6b6b; color: white; border: none; padding: 10px; width: 100%; }
    div.stButton > button:hover { background-color: #ff5252; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
def formatar_cpf(valor):
    v = re.sub(r'\D', '', str(valor))
    if len(v) == 11: return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
    return valor

def formatar_rg(valor):
    v = re.sub(r'\D', '', str(valor))
    if len(v) == 9: return f"{v[:2]}.{v[2:5]}.{v[5:8]}-{v[8:]}"
    if len(v) == 8: return f"{v[:2]}.{v[2:5]}.{v[5:]}"
    return valor

def formatar_cep(valor):
    v = re.sub(r'\D', '', str(valor))
    if len(v) == 8: return f"{v[:2]}.{v[2:5]}-{v[5:]}"
    return valor

# --- CLASSE PARA CRIAR O PDF ---
class PDF(FPDF):
    def header(self):
        # --- LOGO ---
        if os.path.exists("logoalto.jpg"):
            self.image("logoalto.jpg", x=80, y=5, w=50)
            self.ln(25) 
        else:
            self.ln(10)

        # Texto do Cabeçalho
        self.set_font('Arial', 'B', 14)
        self.cell(0, 6, 'A.M.A', 0, 1, 'C')  # <--- ALTERADO AQUI
        
        self.set_font('Arial', '', 8)
        self.cell(0, 4, 'ASSOCIACAO DE MORADORES E AMIGOS DO ALTO URUGUAI - MESQUITA', 0, 1, 'C')
        self.cell(0, 4, 'TRAVESSA TULIPA, 01 - ALTO URUGUAI', 0, 1, 'C')
        self.cell(0, 4, 'CEP: 26556-190  CNPJ: 30.193.254/0001-34', 0, 1, 'C')
        
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y()) 
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Documento gerado digitalmente', 0, 0, 'C')

def gerar_pdf_nativo(dados):
    pdf = PDF()
    pdf.set_margins(25, 25, 25)
    pdf.add_page()
    
    # Título
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'DECLARACAO', 0, 1, 'C')
    pdf.ln(10)

    # Texto Justificado
    pdf.set_font('Arial', '', 12)
    
    texto_completo = (
        f"Eu, Paulo Cesar de Souza, brasileiro, identidade 09.013.043-6 e CPF 016.015.967-90, "
        f"residente e domiciliado nesta cidade de Mesquita: Rua Jutai, 52 - Alto Uruguai "
        f"CEP: 26556-240, declaro para devidos fins de comprovacao de residencia que "
        f"{dados['nome']}, RG: {dados['rg']} e CPF: {dados['cpf']}, reside no endereco: "
        f"{dados['rua']}, {dados['numero']} - {dados['bairro']} - {dados['cidade']}, "
        f"RJ, CEP: {dados['cep']}."
    )
    
    pdf.multi_cell(0, 8, texto_completo, align='J')
    pdf.ln(20)

    # Data à esquerda
    pdf.cell(0, 10, f"Mesquita, {dados['dia']} de {dados['mes']} de {dados['ano']}", 0, 1, 'L')
    pdf.ln(30)
    
    # Assinatura
    pdf.cell(0, 5, "___________________________________________", 0, 1, 'C')
    pdf.cell(0, 5, "Paulo Cesar de Souza", 0, 1, 'C')
    pdf.cell(0, 5, "Presidente", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INTERFACE WEB ---
st.markdown("<h3 style='text-align: center; color: #ff6b6b;'>EMISSÃO - ALTO URUGUAI</h3>", unsafe_allow_html=True)

with st.form("form_pdf"):
    nome = st.text_input("Nome Completo")
    c1, c2 = st.columns(2)
    rg = c1.text_input("RG (só números)")
    cpf = c2.text_input("CPF (só números)")
    
    rua = st.text_input("Endereço (Rua)")
    c3, c4 = st.columns(2)
    num = c3.text_input("Número")
    bairro = c4.text_input("Bairro")
    
    c5, c6 = st.columns(2)
    cid = c5.text_input("Cidade")
    cep = c6.text_input("CEP (só números)")
    
    enviar = st.form_submit_button("BAIXAR PDF")

if enviar:
    if not nome:
        st.error("Preencha o nome!")
    else:
        meses = {1:'Janeiro', 2:'Fevereiro', 3:'Marco', 4:'Abril', 5:'Maio', 6:'Junho',
                 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
        hoje = datetime.now()
        
        dados = {
            'nome': nome.strip(),
            'rg': formatar_rg(rg),
            'cpf': formatar_cpf(cpf),
            'rua': rua.strip(),
            'numero': num.strip(),
            'bairro': bairro.strip(),
            'cidade': cid.strip(),
            'cep': formatar_cep(cep),
            'dia': hoje.strftime("%d"),
            'mes': meses[hoje.month],
            'ano': hoje.strftime("%Y")
        }
        
        arquivo_pdf = gerar_pdf_nativo(dados)
        
        st.success("✅ PDF Gerado!")
        st.download_button(
            label="⬇️ BAIXAR PDF",
            data=arquivo_pdf,
            file_name=f"Declaracao_{nome.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
