# 📄 PDF Extractor

**Junta o texto de uma pasta inteira de PDFs num único arquivo `.txt` em poucos cliques, sem precisar instalar nada.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Interface-Tkinter-555?style=flat-square)
![GitHub Actions](https://img.shields.io/badge/Build-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-.app-000?style=flat-square&logo=apple&logoColor=white)

<!-- 📸 Coloque aqui um print ou GIF do app rodando: ![PDF Extractor em ação](docs/demo.gif) -->

---

## O problema

Ler dezenas de PDFs um por um, copiar o texto e colar num documento é lento e cheio de erro. Ferramentas prontas costumam pedir instalação de Python, linha de comando ou conhecimento técnico, e quem precisa do resultado geralmente não tem nada disso.

## A solução

Um aplicativo de janela simples: a pessoa escolhe a pasta, clica em **Executar** e recebe um relatório `.txt` com o texto de todos os PDFs, separado por arquivo.

- 📁 **Processa a pasta inteira de uma vez**, em ordem alfabética.
- 🧹 **Limpa cabeçalhos e rodapés repetidos**, que costumam poluir o texto extraído (opcional).
- 📊 **Mostra o progresso e um log em tempo real**, sem travar a janela, porque a extração roda em segundo plano.
- 🧾 **Gera um resumo no final**: quantos PDFs tinham texto, quantos estavam vazios e quantos deram erro.
- 🛡️ **Não para no primeiro erro**: uma página ou um PDF com problema é registrado no relatório, e o resto continua sendo processado.

## A automação por trás

O usuário final usa Mac e não tem Python. Em vez de pedir que ele instale qualquer coisa, o próprio GitHub gera o aplicativo:

```
Botão "Run workflow" → máquina macOS do GitHub → instala Python e dependências
→ PyInstaller empacota o app → .zip pronto para baixar em "Artifacts"
```

Basta enviar o `.zip` para a pessoa. Ela descompacta e abre o **PDF Extractor.app**.

## Como gerar o app

1. Vá na aba **Actions** deste repositório.
2. Escolha **Build macOS App** e clique em **Run workflow**.
3. Quando terminar, baixe o artifact **PDF-Extractor-macOS**.

> ⚠️ O app não é assinado pela Apple, então o macOS pode bloquear a primeira abertura. Para liberar, clique com o botão direito no app e escolha **Abrir**. Para distribuição profissional, o ideal é assinar e notarizar com uma conta Apple Developer.

## Rodar direto pelo Python (Windows, Linux ou Mac)

```bash
pip install -r requirements.txt
python pdf_extractor_gui.py
```

## Stack

- **Python 3.11** com **pdfplumber** para extrair o texto
- **Tkinter** para a interface, com `threading` e `queue` para não travar a janela
- **PyInstaller** para empacotar o app
- **GitHub Actions** (runner macOS) para o build automático

---

Feito por [Jerônimo](https://github.com/jjlosmak) · automação de processos e IA aplicada
