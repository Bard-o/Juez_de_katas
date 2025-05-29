import tkinter as tk
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

project_root = current_dir # Corrected
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.admin_menu import AdminMenu # Simplified import

def main():
    """Función principal para iniciar la aplicación de administrador."""
    root = tk.Tk()
    app = AdminMenu(root)
    root.state('zoomed') # Maximizar la ventana
    root.mainloop()

if __name__ == "__main__":
    data_storage_path = os.path.join(project_root, "data_storage")
    if not os.path.exists(data_storage_path):
        try:
            os.makedirs(data_storage_path)
            print(f"Directorio '{data_storage_path}' creado.")
        except OSError as e:
            print(f"Error al crear el directorio '{data_storage_path}': {e}")
    main()