import sys


def main():
    request = " ".join(sys.argv[1:]).strip()
    if request:
        print(
            "Agent codeur présent mais désactivé : "
            f"la demande '{request}' ne sera pas traitée tant que la création "
            "d'agents n'est pas sécurisée."
        )
    else:
        print(
            "Agent codeur présent mais désactivé : "
            "aucune demande de création d'agent n'a été fournie."
        )


if __name__ == "__main__":
    main()
