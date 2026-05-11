"""
pdf_extractor_gui.py
--------------------
Interface gráfica para extrair texto de todos os PDFs de uma pasta
e consolidar o resultado em um arquivo .txt.

Requisitos:
    pip install pdfplumber

Uso:
    python pdf_extractor_gui.py
"""

import logging
import queue
import threading
from pathlib import Path
from collections import Counter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pdfplumber


# ---------------------------------------------------------------------------
# Funções originais / lógica de extração
# ---------------------------------------------------------------------------

def get_pdf_files(directory: Path) -> list[Path]:
    """Retorna lista ordenada de arquivos .pdf no diretório informado."""
    return sorted(directory.glob("*.pdf"))


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Abre um PDF com pdfplumber e extrai o texto de todas as páginas.
    Retorna string vazia se o PDF não tiver texto.
    """
    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

        if total_pages == 0:
            return ""

        for page_num, page in enumerate(pdf.pages, start=1):
            try:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            except Exception as e:
                pages_text.append(f"[ERRO ao processar página {page_num}: {e}]")

    return "\n".join(pages_text)


def deduplicate_headers_footers(text: str, threshold: int = 3) -> str:
    """
    Remove linhas que aparecem repetidamente, úteis para cabeçalhos/rodapés.
    """
    lines = text.splitlines()
    non_empty = [line.strip() for line in lines if line.strip()]
    freq = Counter(non_empty)
    repeated = {line for line, count in freq.items() if count >= threshold}
    cleaned = [line for line in lines if line.strip() not in repeated]
    return "\n".join(cleaned)


def format_pdf_block(filename: str, text: str) -> str:
    """Formata o bloco de texto de um PDF com cabeçalho e separadores."""
    header = f"\n{'=' * 60}\n==== {filename} ====\n{'=' * 60}\n"
    body = text.strip() if text.strip() else "[PDF vazio ou sem texto extraível]"
    return header + "\n" + body + "\n"


def process_directory(
    input_dir: Path,
    output_file: Path,
    progress_callback=None,
    deduplicate: bool = True,
) -> dict:
    """
    Processa todos os PDFs de uma pasta e grava o resultado no arquivo de saída.

    progress_callback recebe:
        progress_callback(indice_atual, total, mensagem)
    """
    pdf_files = get_pdf_files(input_dir)

    if not pdf_files:
        return {
            "ok": 0,
            "empty": 0,
            "error": 0,
            "total": 0,
            "output_file": str(output_file),
        }

    stats = {"ok": 0, "empty": 0, "error": 0, "total": len(pdf_files)}

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write("PDF Extraction Report\n")
        out_f.write(f"Diretório: {input_dir.resolve()}\n")
        out_f.write(f"Total de PDFs: {len(pdf_files)}\n")
        out_f.write("=" * 60 + "\n")

        for idx, pdf_path in enumerate(pdf_files, start=1):
            if progress_callback:
                progress_callback(idx, len(pdf_files), f"Processando: {pdf_path.name}")

            try:
                raw_text = extract_text_from_pdf(pdf_path)

                if not raw_text.strip():
                    stats["empty"] += 1
                else:
                    if deduplicate:
                        raw_text = deduplicate_headers_footers(raw_text)
                    stats["ok"] += 1

                out_f.write(format_pdf_block(pdf_path.name, raw_text))

            except Exception as e:
                stats["error"] += 1
                out_f.write(format_pdf_block(pdf_path.name, f"[ERRO: {e}]"))

    stats["output_file"] = str(output_file)
    return stats


# ---------------------------------------------------------------------------
# Interface gráfica
# ---------------------------------------------------------------------------

class PdfExtractorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Extrator de Texto de PDFs")
        self.root.geometry("760x500")
        self.root.minsize(700, 460)

        self.input_dir_var = tk.StringVar()
        self.output_file_var = tk.StringVar(value=str(Path.cwd() / "output_extracted.txt"))
        self.deduplicate_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Selecione uma pasta com PDFs para começar.")

        self.log_queue = queue.Queue()
        self.worker_thread = None

        self._build_ui()
        self._poll_log_queue()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)

        title = ttk.Label(
            container,
            text="Extrator de Texto de PDFs",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(anchor="w", pady=(0, 12))

        input_frame = ttk.LabelFrame(container, text="1. Pasta de entrada")
        input_frame.pack(fill="x", pady=(0, 10))

        ttk.Entry(input_frame, textvariable=self.input_dir_var).pack(
            side="left", fill="x", expand=True, padx=(10, 6), pady=10
        )
        ttk.Button(input_frame, text="Selecionar pasta", command=self.select_input_dir).pack(
            side="right", padx=(0, 10), pady=10
        )

        output_frame = ttk.LabelFrame(container, text="2. Arquivo de saída")
        output_frame.pack(fill="x", pady=(0, 10))

        ttk.Entry(output_frame, textvariable=self.output_file_var).pack(
            side="left", fill="x", expand=True, padx=(10, 6), pady=10
        )
        ttk.Button(output_frame, text="Escolher destino", command=self.select_output_file).pack(
            side="right", padx=(0, 10), pady=10
        )

        options_frame = ttk.Frame(container)
        options_frame.pack(fill="x", pady=(0, 10))

        ttk.Checkbutton(
            options_frame,
            text="Remover cabeçalhos/rodapés repetidos",
            variable=self.deduplicate_var,
        ).pack(side="left")

        self.run_button = ttk.Button(
            options_frame,
            text="Executar extração",
            command=self.run_extraction,
        )
        self.run_button.pack(side="right")

        progress_frame = ttk.LabelFrame(container, text="Progresso")
        progress_frame.pack(fill="x", pady=(0, 10))

        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=(10, 4))

        ttk.Label(progress_frame, textvariable=self.status_var).pack(
            anchor="w", padx=10, pady=(0, 10)
        )

        log_frame = ttk.LabelFrame(container, text="Log")
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_frame, height=10, wrap="word", state="disabled")
        self.log_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def select_input_dir(self):
        selected_dir = filedialog.askdirectory(title="Selecione a pasta com PDFs")
        if selected_dir:
            self.input_dir_var.set(selected_dir)
            default_output = Path(selected_dir) / "output_extracted.txt"
            self.output_file_var.set(str(default_output))
            self._log(f"Pasta selecionada: {selected_dir}")

    def select_output_file(self):
        selected_file = filedialog.asksaveasfilename(
            title="Escolha onde salvar o TXT",
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            initialfile="output_extracted.txt",
        )
        if selected_file:
            self.output_file_var.set(selected_file)
            self._log(f"Arquivo de saída definido: {selected_file}")

    def run_extraction(self):
        input_dir = Path(self.input_dir_var.get().strip())
        output_file = Path(self.output_file_var.get().strip())

        if not input_dir:
            messagebox.showerror("Erro", "Selecione a pasta de entrada.")
            return

        if not input_dir.exists() or not input_dir.is_dir():
            messagebox.showerror("Erro", "A pasta de entrada não existe ou não é válida.")
            return

        if not output_file.name:
            messagebox.showerror("Erro", "Escolha um arquivo de saída válido.")
            return

        pdf_files = get_pdf_files(input_dir)
        if not pdf_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo PDF foi encontrado nessa pasta.")
            return

        self.progress["value"] = 0
        self.progress["maximum"] = len(pdf_files)
        self.status_var.set("Iniciando extração...")
        self.run_button.config(state="disabled")
        self._log(f"Iniciando. PDFs encontrados: {len(pdf_files)}")

        self.worker_thread = threading.Thread(
            target=self._worker,
            args=(input_dir, output_file, self.deduplicate_var.get()),
            daemon=True,
        )
        self.worker_thread.start()

    def _worker(self, input_dir: Path, output_file: Path, deduplicate: bool):
        def progress_callback(current, total, message):
            self.log_queue.put(("progress", current, total, message))

        try:
            stats = process_directory(
                input_dir=input_dir,
                output_file=output_file,
                progress_callback=progress_callback,
                deduplicate=deduplicate,
            )
            self.log_queue.put(("done", stats))
        except Exception as e:
            self.log_queue.put(("error", str(e)))

    def _poll_log_queue(self):
        try:
            while True:
                item = self.log_queue.get_nowait()
                kind = item[0]

                if kind == "progress":
                    _, current, total, message = item
                    self.progress["maximum"] = total
                    self.progress["value"] = current
                    self.status_var.set(f"{current}/{total} — {message}")
                    self._log(message)

                elif kind == "done":
                    _, stats = item
                    self.run_button.config(state="normal")
                    self.status_var.set("Extração concluída.")
                    self._log("=" * 50)
                    self._log(f"Concluído! Arquivo gerado: {stats['output_file']}")
                    self._log(f"Com texto: {stats['ok']}")
                    self._log(f"Vazios: {stats['empty']}")
                    self._log(f"Com erro: {stats['error']}")

                    messagebox.showinfo(
                        "Concluído",
                        "Extração finalizada!\n\n"
                        f"Arquivo gerado:\n{stats['output_file']}\n\n"
                        f"Com texto: {stats['ok']}\n"
                        f"Vazios: {stats['empty']}\n"
                        f"Com erro: {stats['error']}",
                    )

                elif kind == "error":
                    _, error_message = item
                    self.run_button.config(state="normal")
                    self.status_var.set("Erro durante a extração.")
                    self._log(f"ERRO: {error_message}")
                    messagebox.showerror("Erro", error_message)

        except queue.Empty:
            pass

        self.root.after(100, self._poll_log_queue)

    def _log(self, message: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")


def main():
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    app = PdfExtractorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
