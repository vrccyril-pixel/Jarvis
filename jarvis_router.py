"""
jarvis_router.py  –  Couche LLM de routage
═══════════════════════════════════════════

Responsabilité unique : prendre une requête utilisateur et retourner
un intent JSON structuré. Ce module est le SEUL endroit où Ollama est
appelé dans tout le système d'orchestration.

Il n'écrit rien, ne lit rien, ne lance aucun subprocess.
"""

import json
import re

import ollama

# ─────────────────────────────────────────────────────────────────
ORCHESTRATOR_MODEL = "llama3"   # Modèle léger pour le routage pur

# Les 4 actions possibles — toute autre valeur doit être rejetée
VALID_ACTIONS = {"run_agent", "answer", "save_memory", "agent_missing"}

# ─────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
Tu es le module de ROUTAGE de Jarvis, un système multi-agents 100% local.
LANGUE OBLIGATOIRE : Français.

TON RÔLE : Analyser l'intention de l'utilisateur et choisir la bonne action.
INTERDICTIONS : Inventer des résultats. Générer du code. Modifier des fichiers.

━━━━ AGENTS DISPONIBLES ━━━━
{agents_block}

━━━━ MÉMOIRE CONTEXTUELLE ━━━━
{memory_context}

━━━━ RÉSULTAT DU DERNIER AGENT ━━━━
{last_output}

━━━━ FORMAT DE RÉPONSE OBLIGATOIRE ━━━━
Tu dois répondre UNIQUEMENT avec un objet JSON valide.
Aucun texte avant ou après. Aucun bloc ```json```.
Choisis UNE des quatre actions :

Action 1 – Lancer un agent existant de la liste ci-dessus :
{{"action": "run_agent", "category": "<categorie>", "agent": "<fichier.py>", "args": ["<arg1>", "..."]}}

Action 2 – Répondre directement (question simple, info en mémoire, calcul) :
{{"action": "answer", "text": "<ta réponse>"}}

Action 3 – Mémoriser une information donnée par l'utilisateur :
{{"action": "save_memory", "fact": "<information>", "id": "<identifiant_court>"}}

Action 4 – L'intention nécessite un agent qui N'EST PAS dans la liste :
{{"action": "agent_missing", "suggestion": "<description de la capacité manquante>"}}

RÈGLE SUR LES RÉSULTATS : Si l'utilisateur demande "que dit le résultat ?",
"résume le PDF", etc., base-toi UNIQUEMENT sur le champ "RÉSULTAT DU DERNIER AGENT".
N'invente rien. Si le champ est vide, dis-le.

RÈGLE SUR LES ARGS : Les args doivent être des strings. Si l'utilisateur
mentionne un chemin de fichier, inclus-le dans args. Exemple :
"lis le PDF data/test.pdf" → {{"action": "run_agent", "category": "tools",
"agent": "pdf_reader.py", "args": ["data/test.pdf"]}}
"""


def _build_agents_block(registry: dict) -> str:
    """Formate le registre pour le prompt LLM."""
    entries = [
        (k, v) for k, v in registry.items()
        if not k.startswith("_") and isinstance(v, dict)
    ]
    if not entries:
        return "  (aucun agent disponible)"

    lines = []
    for key, meta in entries:
        desc = meta.get("description", "—")
        args = meta.get("args", [])
        astr = ", ".join(f"<{a}>" for a in args) if args else "aucun"
        # Exemples pour aider le routage
        examples = meta.get("examples", [])
        ex_str = ""
        if examples:
            ex_str = f" | ex: \"{examples[0]}\""
        lines.append(f"  • {key:<40} {desc}  [args: {astr}]{ex_str}")
    return "\n".join(lines)


def _extract_json(raw: str) -> dict:
    """
    Extrait et valide le JSON de la réponse LLM.
    Gère les cas où le LLM entoure le JSON de backticks ou de texte parasite.
    """
    # Tentative 1 : la réponse entière est un JSON pur
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Tentative 2 : extraire le premier bloc {...}
    match = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            raise ValueError(
                f"JSON extrait mais invalide : {e}\n"
                f"JSON brut :\n{match.group(0)}"
            )

    raise ValueError(
        f"Aucun JSON trouvé dans la réponse LLM.\n"
        f"Réponse brute (100 premiers car.) : {raw[:100]!r}"
    )


def _validate_intent(intent: dict) -> dict:
    """
    Valide la structure de l'intent JSON.
    Lève ValueError si le format est incorrect.
    """
    action = intent.get("action")

    if action not in VALID_ACTIONS:
        raise ValueError(
            f"Action '{action}' invalide. Valeurs autorisées : {VALID_ACTIONS}"
        )

    if action == "run_agent":
        if not intent.get("agent"):
            raise ValueError("Action 'run_agent' sans champ 'agent'.")
        if not intent.get("category"):
            intent["category"] = "tools"    # Défaut raisonnable
        if "args" not in intent:
            intent["args"] = []

    elif action == "answer":
        if not intent.get("text"):
            intent["text"] = "(réponse vide)"

    elif action == "save_memory":
        if not intent.get("fact"):
            raise ValueError("Action 'save_memory' sans champ 'fact'.")

    return intent


# ─────────────────────────────────────────────────────────────────
#  POINT D'ENTRÉE PUBLIC
# ─────────────────────────────────────────────────────────────────

def build_intent(
    user_query: str,
    last_output: str,
    memory_context: str,
    registry: dict,
) -> dict:
    """
    Envoie la requête au LLM routeur et retourne un intent JSON validé.

    Paramètres :
      user_query    – la saisie brute de l'utilisateur
      last_output   – stdout du dernier agent lancé (peut être vide)
      memory_context – souvenirs pertinents remontés par ChromaDB
      registry      – dict chargé depuis agents_registry.json

    Retourne : dict avec au minimum {"action": <str>}
    Lève    : ValueError si le LLM retourne un format invalide
    """
    system_prompt = _SYSTEM_PROMPT.format(
        agents_block   = _build_agents_block(registry),
        memory_context = memory_context or "Aucune mémoire pertinente.",
        last_output    = (last_output[:800] + "…") if len(last_output) > 800
                         else (last_output or "Aucun agent lancé précédemment."),
    )

    response = ollama.chat(
        model=ORCHESTRATOR_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_query},
        ],
        options={"temperature": 0.05},  # Maximum déterministe pour le routage
    )

    raw     = response["message"]["content"].strip()
    intent  = _extract_json(raw)
    intent  = _validate_intent(intent)
    return intent
