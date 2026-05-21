# Coder Agent Security Contract

## Pourquoi `coder_agent.py` Reste Désactivé

`agents/system/coder_agent.py` existe physiquement dans le dépôt, mais il n'est pas déclaré dans `agents_registry.json`.

Il reste donc bloqué par :

- l'allowlist du runner ;
- la validation du routeur ;
- les smoke tests.

Cette désactivation est volontaire. Un agent codeur autonome peut modifier du code, créer des fichiers, altérer l'orchestration ou contourner les garde-fous si son périmètre n'est pas strictement défini.

Avant toute réactivation, son comportement doit être limité, testable et validé humainement.

## Risques Interdits

Un futur `coder_agent.py` ne doit jamais pouvoir faire librement les actions suivantes.

### Écriture Libre Dans le Repo

L'agent ne doit pas pouvoir modifier n'importe quel fichier du dépôt.

Toute écriture doit être limitée à une liste explicite de fichiers autorisés pour la tâche en cours.

### Modification du Runner, Router, Main ou Registry

Par défaut, l'agent ne doit pas modifier :

- `jarvis_runner.py`
- `jarvis_router.py`
- `jarvis_main.py`
- `agents_registry.json`

Ces fichiers contrôlent l'orchestration et la sécurité d'exécution. Ils ne peuvent être modifiés que dans un mode maintenance explicite et validé humainement.

### Auto-Ajout au Registre

L'agent ne doit pas pouvoir s'ajouter lui-même à `agents_registry.json`.

Il ne doit pas non plus ajouter automatiquement de nouveaux agents au registre.

### Shell Arbitraire

L'agent ne doit pas lancer de commandes système arbitraires.

Aucune commande shell ne doit être exécutée sans validation explicite et sans périmètre clair.

### Commit ou Push Automatique

L'agent ne doit jamais faire automatiquement :

- `git add`
- `git commit`
- `git push`

Les commits doivent rester des étapes séparées, visibles et validées.

### Appel LLM Non Encadré

L'agent ne doit pas appeler un LLM librement sans contrat clair.

Tout appel LLM futur doit avoir :

- une entrée contrôlée ;
- une sortie structurée ;
- une limite de tâche ;
- aucune permission implicite d'écriture ;
- aucun accès implicite au shell ou au registre.

## Mode Autorisé Initial

Le premier mode autorisé pour `coder_agent.py` doit être strictement passif.

Il peut produire :

- un diagnostic ;
- une analyse de fichiers explicitement fournis ;
- une proposition de diff ;
- une liste de tests recommandés.

Il ne doit pas appliquer les modifications lui-même.

Ce mode est appelé `plan-only`.

## Périmètre d'Écriture Futur

Une future capacité d'écriture ne pourra être envisagée que si le périmètre est explicitement fourni.

Exemple de périmètre autorisé :

```text
allowed_files:
  - agents/tools/example_agent.py
  - tests/test_example_agent.py
```

Règles minimales :

- écrire uniquement dans les fichiers explicitement autorisés ;
- refuser toute modification hors périmètre ;
- refuser les chemins absolus non attendus ;
- refuser les path traversals comme `../` ;
- ne jamais modifier `jarvis_runner.py`, `jarvis_router.py`, `jarvis_main.py` ou `agents_registry.json` sans mode maintenance explicite.

## Contrat Agent CLI

Comme tout agent Jarvis, `coder_agent.py` devra respecter le contrat agent standard.

Il doit :

- être exécutable en CLI ;
- accepter ses arguments via `sys.argv` ;
- éviter tout effet de bord à l'import ;
- exposer un `main() -> int` ;
- utiliser :

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

Sorties attendues :

- `stdout` : résultat normal, diagnostic ou proposition de diff ;
- `stderr` : erreurs, refus de sécurité, arguments invalides ;
- code retour `0` : succès ;
- code retour non nul : erreur ou refus de sécurité.

## Workflow Obligatoire

Toute modification proposée par `coder_agent.py` doit suivre ce workflow.

1. Diagnostic de la demande.
2. Proposition d'un diff non appliqué.
3. Validation humaine explicite.
4. Application séparée du diff.
5. Exécution des tests ciblés.
6. Exécution des smoke tests.
7. Commit séparé et lisible.
8. Push séparé après validation.

L'agent ne doit pas fusionner ces étapes en une seule action autonome.

## Conditions Minimales Avant Ajout à `agents_registry.json`

Avant d'ajouter `system/coder_agent.py` au registre, les conditions suivantes doivent être remplies :

- le mode `plan-only` existe ;
- aucun fichier n'est modifié en mode `plan-only` ;
- les erreurs vont sur `stderr` ;
- les succès vont sur `stdout` ;
- le code retour est explicite ;
- les imports n'ont aucun effet de bord ;
- aucun shell arbitraire n'est disponible ;
- aucun commit ou push automatique n'est possible ;
- aucune modification du registre n'est possible ;
- des tests couvrent les refus de sécurité ;
- les smoke tests passent.

## Tests Nécessaires Avant Réactivation

Tests minimaux à ajouter avant réactivation :

- import sans effet de bord ;
- exécution sans argument retourne une erreur claire ;
- mode `plan-only` retourne `0` sans modifier de fichier ;
- tentative d'écriture hors périmètre refusée ;
- tentative de modifier `jarvis_runner.py` refusée ;
- tentative de modifier `jarvis_router.py` refusée ;
- tentative de modifier `jarvis_main.py` refusée ;
- tentative de modifier `agents_registry.json` refusée ;
- tentative de lancer une commande shell arbitraire refusée ;
- tentative de commit/push refusée ;
- smoke test confirmant que l'agent reste bloqué tant qu'il n'est pas déclaré.

## Prochaines Étapes Recommandées

1. Garder `coder_agent.py` non référencé dans `agents_registry.json`.
2. Documenter le mode `plan-only` attendu.
3. Transformer `coder_agent.py` en agent CLI conforme mais toujours non déclaré.
4. Ajouter des tests locaux du contrat CLI.
5. Ajouter des tests de refus de sécurité.
6. Ajouter seulement ensuite une entrée registre temporaire, si nécessaire, pour un mode plan-only.
7. Tester le routage, le runner et les refus.
8. Ne jamais activer l'écriture autonome sans validation humaine séparée.
