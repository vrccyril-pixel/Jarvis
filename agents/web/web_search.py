import sys


def main():
    query = " ".join(sys.argv[1:]).strip()
    if query:
        print(
            "Agent web_search non implémenté : "
            f"la recherche web pour '{query}' n'est pas encore disponible."
        )
    else:
        print(
            "Agent web_search non implémenté : "
            "aucune requête de recherche n'a été fournie."
        )


if __name__ == "__main__":
    main()
