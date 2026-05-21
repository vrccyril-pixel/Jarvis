# Jarvis V3 - Stabilization Status

## Objectif du Projet

Jarvis V3 vise à devenir une IA locale multi-agents stable, contrôlée et progressivement extensible.

La priorité actuelle est de stabiliser l'orchestration, le contrat agent, le registre et les agents simples avant toute réactivation d'un agent codeur autonome.

## État Actuel Validé

- `main` est à jour avec `origin/main`.
- Le worktree Git est propre.
- Les smoke tests passent.
- Les agents actifs sont déclarés dans `agents_registry.json`.
- Les agents non déclarés sont bloqués par le runner.
- `coder_agent.py` existe encore physiquement mais reste neutralisé.

## Agents Stabilisés

Agents actuellement stabilisés :

- `agents/system/ram_usage.py`
- `agents/office/outlook_agenda.py`
- `agents/tools/pdf_reader.py`
- `agents/web/web_search.py`

Note : `web_search.py` reste un placeholder. Il ne fait pas encore de vraie recherche web.

## Sécurité d'Orchestration

### Router

`jarvis_router.py` utilise le registre comme contexte de routage.

Il valide maintenant qu'un agent routé correspond à une clé déclarée dans `agents_registry.json`. Si le modèle propose un agent non déclaré, l'intention est convertie en `agent_missing`.

### Runner

`jarvis_runner.py` exécute les agents via subprocess.

Il applique une allowlist stricte basée sur `agents_registry.json`. Un fichier présent physiquement sous `agents/` ne peut pas être exécuté s'il n'est pas déclaré dans le registre.

### Registry

`agents_registry.json` est la source d'autorité pour les agents exécutables.

Chaque entrée déclarée doit correspondre à un fichier réel sous `agents/`.

### Coder Agent Bloqué

`agents/system/coder_agent.py` existe encore, mais n'est pas référencé dans `agents_registry.json`.

Il est donc bloqué par :

- le runner ;
- la validation du routeur ;
- un smoke test dédié.

## Contrat Agent Actuel

Un agent Jarvis doit :

- être exécutable en CLI ;
- accepter ses arguments via `sys.argv` ;
- écrire les résultats normaux sur `stdout` ;
- écrire les erreurs sur `stderr` ;
- retourner `0` en succès ;
- retourner un code non nul en erreur ;
- éviter les effets de bord à l'import ;
- exposer un `main() -> int` ;
- utiliser :

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

Un agent ne doit pas :

- modifier des fichiers hors du périmètre prévu ;
- appeler directement un autre agent ;
- appeler le LLM sans décision explicite d'architecture.

## Tests Disponibles

Les smoke tests vérifient actuellement :

- que `agents_registry.json` est lisible ;
- que les entrées du registre pointent vers des fichiers existants ;
- que `web_search.py` fonctionne comme placeholder déclaré ;
- que `coder_agent.py` est bloqué tant qu'il n'est pas déclaré ;
- que `jarvis_main.py` démarre et quitte proprement avec `quit`.

Commande :

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

## Ce Qu'il Ne Faut Pas Faire Maintenant

Ne pas réactiver `coder_agent.py`.

Ne pas l'ajouter à `agents_registry.json`.

Ne pas donner au routeur ou au runner un contournement du registre.

Ne pas lancer de gros refactor.

Ne pas transformer `web_search.py` en vrai agent web avant d'avoir défini son contrat réseau, ses dépendances et ses tests.

Ne pas élargir les permissions d'exécution sans test de sécurité associé.

## Prochaines Étapes Recommandées

1. Ajouter des tests ciblés pour les cas d'erreur du runner.
2. Nettoyer progressivement les sorties Unicode restantes dans l'interface CLI si nécessaire sous Windows.
3. Documenter le format attendu des agents dans un fichier dédié.
4. Ajouter un vrai test d'intégration pour un agent sans dépendance externe, comme `ram_usage.py`.
5. Préparer un plan de réactivation contrôlée de `coder_agent.py` :
   - capabilities limitées ;
   - sandbox claire ;
   - registre explicite ;
   - tests de blocage ;
   - validation humaine avant écriture ;
   - aucun accès implicite au runner ou au registre.
