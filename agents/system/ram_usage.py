import psutil

# Obtenir les informations sur l'utilisation actuelle de la RAM
ram = psutil.virtual_memory()

print(f"Utilisation actuelle de la RAM : {ram.percent}%")
