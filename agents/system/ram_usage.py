import psutil


def main():
    # Obtenir les informations sur l'utilisation actuelle de la RAM
    ram = psutil.virtual_memory()

    print(f"Utilisation actuelle de la RAM : {ram.percent}%")


if __name__ == "__main__":
    main()
