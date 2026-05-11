# PDF Extractor — build para macOS via GitHub Actions

Este pacote gera um aplicativo `.app` para macOS usando GitHub Actions.
A pessoa que receber o app não precisa instalar Python.

## Arquivos

- `pdf_extractor_gui.py`: programa com interface gráfica.
- `requirements.txt`: dependências do projeto.
- `.github/workflows/build-macos.yml`: automação para gerar o app no GitHub.

## Como usar

1. Crie um repositório novo no GitHub.
2. Envie estes arquivos para o repositório, mantendo a pasta `.github/workflows/`.
3. Entre no repositório no GitHub.
4. Vá em **Actions**.
5. Clique em **Build macOS App**.
6. Clique em **Run workflow**.
7. Aguarde finalizar.
8. Baixe os arquivos em **Artifacts**:
   - `PDF-Extractor-macOS-Apple-Silicon-arm64`
   - `PDF-Extractor-macOS-Intel-x64`

## Qual arquivo enviar?

- Mac com chip M1, M2, M3, M4 ou superior: envie o `Apple-Silicon-arm64`.
- Mac Intel antigo: envie o `Intel-x64`.

## Observação sobre segurança do macOS

Como o app não estará assinado/notarizado pela Apple, o macOS pode bloquear na primeira abertura.
A pessoa pode abrir com botão direito/control-click em cima do app e escolher **Abrir**.

Para distribuição profissional, o ideal é assinar e notarizar com Apple Developer.
