import tkinter as tk
import sys
import os

# Añadir el directorio raíz del proyecto al sys.path
# Esto asume que main_juez_app.py está en la raíz del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir # Si main_juez_app.py está en la raíz
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.juez_login_screen import JuezLoginScreen

DATA_STORAGE_PATH = os.path.join(project_root, "data_storage")

def main():
    """Función principal para iniciar la aplicación de login de juez."""
    # Crear el directorio data_storage si no existe
    if not os.path.exists(DATA_STORAGE_PATH):
        try:
            os.makedirs(DATA_STORAGE_PATH)
            print(f"Directorio '{DATA_STORAGE_PATH}' creado.")
        except OSError as e:
            print(f"Error al crear el directorio '{DATA_STORAGE_PATH}': {e}")
            # Podríamos decidir salir si no se puede crear el directorio, 
            # o dejar que la JuezLoginScreen maneje el error de directorio no encontrado.

    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana raíz principal, JuezLoginScreen usará un Toplevel
    app = JuezLoginScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()