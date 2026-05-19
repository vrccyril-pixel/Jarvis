import sys
import os
import json
import re
import ollama

# --- CONFIGURATION ---
# Pour l'instant on utilise llama3. À l'avenir, tu pourras télécharger
# un modèle dédié au code (ex: "deepseek-coder" ou "qwen2.5-coder") et changer ce nom.
CODER_MODEL = "llama3" 
AGENTS_DIR = "agents"
REGISTRY_FILE = "agents_registry.json"
VALID_CATEGORIES = ["system", "office", "web", "tools"]

SYSTEM_PROMPT = """Tu es l'Agent Développeur (Ingénieur Python Senior) du système Jarvis.
Ton rôle est d'écrire des scripts Python complets, robustes et fonctionnels.
L'environnement de travail est Windows.

Tu dois ABSOLUMENT répondre en respectant CE FORMAT STRICT (n'ajoute aucun texte avant ou après) :

CATEGORIE: <system|office|web|tools>
NOM: <nom_du_fichier.py>
DESCRIPTION: <Une phrase courte décrivant ce que fait l'agent>
ARGS: <arg1, arg2> (laisse vide si l'agent n'a pas besoin d'arguments)
CODE:
```python
<le code source complet ici>
def generate_agent(request):
print(f"\n🧠 [Coder Agent] Réflexion en cours pour : '{request}'...")
try:
    response = ollama.chat(
        model=CODER_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Écris un outil Python pour répondre à cette demande : {request}"}
        ],
        options={"temperature": 0.2} # Basse température = code plus logique et moins fantaisiste
    )
except Exception as e:
    print(f"❌ Erreur de communication avec le modèle : {e}")
    return

content = response['message']['content']

# --- 1. Extraction des données ---
cat_match = re.search(r"CATEGORIE:\s*(\w+)", content)
name_match = re.search(r"NOM:\s*([\w\._-]+)", content)
desc_match = re.search(r"DESCRIPTION:\s*(.+)", content)
args_match = re.search(r"ARGS:\s*(.*)", content)
code_match = re.search(r"```python\n(.*?)\n```", content, re.DOTALL)

if not (name_match and code_match and desc_match):
    print("❌ Erreur : L'IA n'a pas respecté le format strict.")
    print("--- Réponse brute ---")
    print(content)
    return
    
category = cat_match.group(1).lower().strip() if cat_match else "tools"
if category not in VALID_CATEGORIES:
    category = "tools"
    
filename = name_match.group(1).strip()
description = desc_match.group(1).strip()

# Traitement des arguments demandés par l'outil
raw_args = args_match.group(1).strip() if args_match else ""
args_list = [a.strip() for a in raw_args.split(",")] if raw_args and raw_args.lower() not in ["aucun", "none", ""] else []

code = code_match.group(1).strip()

# --- 2. Affichage du compte-rendu pour l'humain ---
print("\n" + "="*50)
print("🛠️  PROPOSITION DE L'AGENT DÉVELOPPEUR  🛠️")
print("="*50)
print(f"📂 Catégorie   : {category}")
print(f"📄 Fichier     : {filename}")
print(f"📝 Description : {description}")
print(f"⚙️  Arguments   : {args_list}")
print("-" * 50)

# On n'affiche que les 15 premières lignes pour ne pas noyer le terminal
preview_code = "\n".join(code.split("\n")[:15])
print(preview_code + "\n\n... [Code tronqué pour l'aperçu] ...")
print("="*50)

# --- 3. Ligne de Défense : Autorisation Humaine ---
choix = input("\n⚠️ Autoriser l'écriture de ce fichier sur le disque ? (o/n) : ").strip().lower()

if choix == 'o':
    # Sauvegarde du fichier Python
    filepath = os.path.join(AGENTS_DIR, category, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"✅ Fichier sauvegardé : {filepath}")
    
    # Mise à jour du registre JSON
    registry = {}
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            try:
                registry = json.load(f)
            except json.JSONDecodeError:
                pass # Si le fichier est corrompu, on l'écrase proprement
                
    registry_key = f"{category}/{filename}"
    registry[registry_key] = {
        "description": description,
        "args": args_list
    }
    
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)
    print(f"✅ Registre mis à jour. L'Orchestrateur connaît maintenant '{filename}'.")
    
else:
    print("🛑 Opération annulée par l'utilisateur.")
if name == "main":
# L'Orchestrateur passera la suggestion via les arguments du terminal
if len(sys.argv) > 1:
user_request = " ".join(sys.argv[1:])
generate_agent(user_request)
else:
print("❌ Erreur : Aucune demande de création d'agent n'a été transmise.")