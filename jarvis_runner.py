"""
jarvis_runner.py  –  Couche d'exécution subprocess
═══════════════════════════════════════════════════

Responsabilité unique : lancer un agent Python via subprocess,
capturer sa sortie, et retourner un résultat propre.

CONTRAT AGENT (à respecter par tous les scripts dans agents/) :
  ✅ Écrire les résultats sur  stdout  (print())
  ✅ Écrire les erreurs sur    stderr  (print(..., file=sys.stderr))
  ✅ Retourner le code 0 si succès, ≠0 si échec
  ✅ Accepter les arguments via sys.argv (ex: sys.argv[1] = chemin_fichier)
  ❌ Ne PAS modifier de fichiers hors de workspace/
  ❌ Ne PAS appeler d'autres agents directement
  ❌ Ne PAS appeler le LLM (sauf agents spécialisés Phase C)
"""

import os
import re
import subprocess
import sys

# ─────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR    = os.path.join(BASE_DIR, "agents")
AGENT_TIMEOUT = 60  # secondes

VALID_CATEGORIES = {"system", "office", "web", "tools"}

# Dictionnaire d'alias pip : nom_import → nom_paquet_pip
_PIP_ALIASES = {
    "fitz":     "PyMuPDF",
    "pymupdf":  "PyMuPDF",
    "cv2":      "opencv-python",
    "sklearn":  "scikit-learn",
    "bs4":      "beautifulsoup4",
    "PIL":      "Pillow",
    "docx":     "python-docx",
    "pptx":     "python-pptx",
}
# ─────────────────────────────────────────────────────────────────


def _detect_missing_module(stderr_text: str) -> str | None:
    """Retourne le nom pip du module manquant, ou None."""
    match = re.search(r"No module named '([^']+)'", stderr_text)
    if not match:
        return None
    module = match.group(1).split(".")[0]
    return _PIP_ALIASES.get(module.lower(), module)


def _install_module(pip_package: str) -> bool:
    """Tente d'installer un paquet pip. Retourne True si succès."""
    print(f"  📦 Installation de '{pip_package}'...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", pip_package, "--quiet"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"  ✅ '{pip_package}' installé avec succès.")
        return True
    print(f"  ❌ Échec d'installation de '{pip_package}' :\n{result.stderr.strip()}")
    return False


def run_agent(
    category: str,
    filename: str,
    args: list[str] | None = None,
    _retry: bool = True,
) -> tuple[bool, str]:
    """
    Lance un agent Python via subprocess de manière sécurisée.

    Retourne : (succès: bool, sortie: str)
      - succès = True  + stdout si l'agent s'est terminé avec code 0
      - succès = False + message d'erreur sinon

    Garanties :
      • Le chemin est construit de façon déterministe (pas d'injection)
      • Le répertoire de travail est toujours BASE_DIR
      • Une seule tentative d'auto-installation de dépendance (_retry)
      • Timeout configurable
    """
    # ── Validation de la catégorie ────────────────────────────────
    if category not in VALID_CATEGORIES:
        return False, f"Catégorie '{category}' invalide. Valeurs : {sorted(VALID_CATEGORIES)}"

    # ── Construction du chemin (sécurisé, pas de path traversal) ─
    agent_path = os.path.normpath(os.path.join(AGENTS_DIR, category, filename))

    # Vérification que le chemin résolu reste dans AGENTS_DIR
    if not agent_path.startswith(os.path.normpath(AGENTS_DIR)):
        return False, f"Tentative de path traversal détectée : {filename}"

    if not os.path.isfile(agent_path):
        return False, (
            f"Agent introuvable : agents/{category}/{filename}\n"
            f"Vérifiez que le fichier existe et que l'entrée est dans agents_registry.json."
        )

    cmd = [sys.executable, agent_path] + (args or [])
    print(f"  ⚙️  {category}/{filename}  {args or ''}")

    # ── Exécution ──────────────────────────────────────────────────
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=AGENT_TIMEOUT,
            cwd=BASE_DIR,
        )
    except subprocess.TimeoutExpired:
        return False, f"Timeout : l'agent n'a pas répondu en {AGENT_TIMEOUT}s."
    except Exception as e:
        return False, f"Impossible de lancer l'agent : {e}"

    # ── Auto-installation (une seule tentative) ───────────────────
    if result.returncode != 0 and "ModuleNotFoundError" in result.stderr and _retry:
        pip_pkg = _detect_missing_module(result.stderr)
        if pip_pkg and _install_module(pip_pkg):
            # Deuxième tentative sans possibilité de re-retry
            return run_agent(category, filename, args, _retry=False)

    # ── Résultat final ─────────────────────────────────────────────
    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip() or "(pas de message d'erreur)"
        return False, f"Code retour {result.returncode}\n{error_msg}"

    output = result.stdout.strip()
    if not output:
        return True, "(L'agent s'est terminé sans produire de sortie.)"
    return True, output
