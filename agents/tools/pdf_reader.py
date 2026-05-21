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
    except ImportError as exc:
        raise RuntimeError("Module 'fitz' manquant. Installez-le : pip install PyMuPDF") from exc

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    try:
        doc = fitz.open(file_path)
        text = ""
        for i, page in enumerate(doc, start=1):
            page_text = page.get_text().strip()
            if page_text:
                text += f"\n[Page {i}]\n{page_text}\n"
        doc.close()
    except Exception as e:
        raise RuntimeError(f"Erreur lecture PDF : {e}") from e

    if not text.strip():
        return "[INFO] Aucun texte extractible (PDF scanné sans OCR ?)."

    result = text.strip()
    if len(result) > max_chars:
        result = result[:max_chars] + f"\n\n[Tronqué à {max_chars} car. — total : {len(text)} car.]"

    return result


def main() -> int:
    if len(sys.argv) >= 2:
        target = sys.argv[1]
    else:
        # Chemin par défaut (rétro-compatibilité)
        base = os.path.dirname(os.path.abspath(__file__))
        target = os.path.normpath(os.path.join(base, "..", "..", "data", "test.pdf"))
        print(f"[INFO] Aucun argument. Fichier par défaut : {target}", file=sys.stderr)

    try:
        print(read_pdf(target))
    except Exception as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
