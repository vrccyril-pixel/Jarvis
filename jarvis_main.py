"""
╔══════════════════════════════════════════════════════════════════╗
║       JARVIS  –  Orchestrateur Senior (V2)                      ║
║       Gestion proactive des dépendances & Routage JSON          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import json
import os
import subprocess
import sys
import time
from jarvis_router import build_intent
from jarvis_memory import recall_memory, save_memory
from jarvis_runner import run_agent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# --- CONFIGURATION ---
ORCHESTRATOR_MODEL = "llama3"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
REGISTRY_FILE = os.path.join(BASE_DIR, "agents_registry.json")
AGENT_TIMEOUT = 60

# --- EXÉCUTION ---
def load_registry():

    if not os.path.exists(REGISTRY_FILE):
        return {}

    with open(REGISTRY_FILE,"r",encoding="utf-8") as f:

        try:
            return json.load(f)

        except Exception:
            return {}
def main():

    print("🤖 Jarvis V3 prêt.")

    last_output = ""

    while True:

        query = input("\n> ").strip()

        if query.lower() in ["quit", "exit"]:
            break

        try:

            memory_context = recall_memory(query)

            intent = build_intent(
                user_query=query,
                last_output=last_output,
                memory_context=memory_context,
                registry=load_registry()
            )

            action = intent["action"]

            if action == "run_agent":

                success, output = run_agent(
                    intent["category"],
                    intent["agent"],
                    intent.get("args", [])
                )

                if success:
                    last_output = output

                    print("\n[RESULT]")
                    print(output)
                else:
                    print("\n[AGENT ERROR]")
                    print(output)

            elif action == "answer":

                print("\n💬")
                print(intent["text"])

                last_output = intent["text"]

            elif action == "save_memory":

                save_memory(
                    intent["fact"],
                    intent.get("id", "memo")
                )

                print("\n🧠 Mémoire enregistrée.")

            elif action == "agent_missing":

                print("\n⚠ Agent manquant :")
                print(intent["suggestion"])

        except Exception as e:

            print("\n⚠ Erreur :")
            print(e)


if __name__ == "__main__":
    main()
