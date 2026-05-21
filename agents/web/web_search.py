import sys


def main() -> int:
    query = " ".join(sys.argv[1:]).strip()
    if query:
        print(
            "Agent web_search non implémenté : "
            f"la recherche web pour '{query}' n'est pas encore disponible."
        )
        return 0

    print(
        "Erreur : aucune requête de recherche n'a été fournie.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
