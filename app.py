
import streamlit as st
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter
import tempfile

st.set_page_config(page_title="Organizador de Etiquetas - Renova Pisos")
st.title("📦 Organizador de Etiquetas - Renova Pisos")
st.markdown("Organize automaticamente suas etiquetas em PDF por nome do destinatário.")

uploaded_file = st.file_uploader("Envie seu arquivo PDF com etiquetas", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    doc = fitz.open(tmp_path)
    pages_info = []

    for i in range(len(doc)):
        lines = doc[i].get_text().split("\n")
        destinatario = None
        for idx, line in enumerate(lines):
            if "destinatário" in line.lower():
                if ":" in line:
                    partes = line.split(":", 1)
                    if partes[1].strip():
                        destinatario = partes[1].strip()
                    elif idx + 1 < len(lines):
                        proxima = lines[idx + 1].strip()
                        if proxima:
                            destinatario = proxima
                elif idx + 1 < len(lines):
                    proxima = lines[idx + 1].strip()
                    if proxima:
                        destinatario = proxima
                break
        if destinatario:
            pages_info.append((destinatario, i))

    total_paginas = len(doc)
    paginas_com_dest = [i for _, i in pages_info]
    paginas_sem_dest = [i for i in range(total_paginas) if i not in paginas_com_dest]

    st.info(f"Total de páginas: {total_paginas}")
    st.success(f"Com destinatário: {len(paginas_com_dest)}")
    if paginas_sem_dest:
        st.warning(f"Sem destinatário: {len(paginas_sem_dest)}")
        with st.expander("Ver páginas sem destinatário"):
            st.write([p+1 for p in paginas_sem_dest])

    if st.button("📥 Gerar PDF ordenado"):
        pages_info.sort(key=lambda x: x[0].lower())
        reader = PdfReader(tmp_path)
        writer = PdfWriter()

        for _, p in pages_info:
            writer.add_page(reader.pages[p])
        for p in paginas_sem_dest:
            writer.add_page(reader.pages[p])

        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        with open(output_temp.name, "wb") as f:
            writer.write(f)

        with open(output_temp.name, "rb") as f:
            st.download_button(
                label="📎 Baixar PDF Ordenado",
                data=f.read(),
                file_name="arquivo_ordenado.pdf",
                mime="application/pdf"
            )
