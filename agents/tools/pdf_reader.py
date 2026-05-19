"""
Agent    : pdf_reader.py
Catégorie: tools
Contrat  : stdout = résultat | stderr = erreurs | exit 0 = succès

Usage CLI:
  python pdf_reader.py <chemin_pdf>           # chemin explicite
  python pdf_reader.py                         # utilise data/test.pdf par défaut
"""

import os
import sys


def read_pdf(file_path: str, max_chars: int = 3000) -> str:
    try:
        import fitz  # PyMuPDF # type: ignore
    except ImportError:
        print("Module 'fitz' manquant. Installez-le : pip install PyMuPDF", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(file_path):
        print(f"Fichier introuvable : {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        doc  = fitz.open(file_path)
        text = ""
        for i, page in enumerate(doc, start=1):
            page_text = page.get_text().strip()
            if page_text:
                text += f"\n[Page {i}]\n{page_text}\n"
        doc.close()
    except Exception as e:
        print(f"Erreur lecture PDF : {e}", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("[INFO] Aucun texte extractible (PDF scanné sans OCR ?).")
        sys.exit(0)

    result = text.strip()
    if len(result) > max_chars:
        result = result[:max_chars] + f"\n\n[Tronqué à {max_chars} car. — total : {len(text)} car.]"

    # Sortie sur stdout — conforme au contrat agent
    print(result)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        target = sys.argv[1]
    else:
        # Chemin par défaut (rétro-compatibilité)
        base = os.path.dirname(os.path.abspath(__file__))
        target = os.path.normpath(os.path.join(base, "..", "..", "data", "test.pdf"))
        print(f"[INFO] Aucun argument. Fichier par défaut : {target}", file=sys.stderr)

    read_pdf(target)