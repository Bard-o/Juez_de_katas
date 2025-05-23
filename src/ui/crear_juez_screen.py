import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class CrearJuezScreen:
    def __init__(self, root, torneo_screen_instance, competencia_path):
        self.root = root
        self.torneo_screen_instance = torneo_screen_instance
        self.competencia_path = competencia_path

        self.top_level = tk.Toplevel(root)
        self.top_level.title("Añadir Nuevo Juez")
        self.top_level.geometry("400x250") # Tamaño ajustado para el formulario
        self.top_level.grab_set()
        self.top_level.resizable(False, False)
        self.top_level.protocol("WM_DELETE_WINDOW", self.cancelar)

        self._crear_formulario()

    def _crear_formulario(self):
        main_frame = ttk.Frame(self.top_level, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text="ID del Juez:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.id_juez_entry = ttk.Entry(main_frame, width=30)
        self.id_juez_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(main_frame, text="Nombre del Juez:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.nombre_juez_entry = ttk.Entry(main_frame, width=30)
        self.nombre_juez_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(main_frame, text="Club del Juez:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.club_juez_entry = ttk.Entry(main_frame, width=30)
        self.club_juez_entry.grid(row=2, column=1, padx=5, pady=5)

        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=3, column=0, columnspan=2, pady=20)

        btn_guardar = ttk.Button(botones_frame, text="Guardar Juez", command=self.guardar_juez)
        btn_guardar.pack(side=tk.LEFT, padx=10)

        btn_cancelar = ttk.Button(botones_frame, text="Cancelar", command=self.cancelar)
        btn_cancelar.pack(side=tk.LEFT, padx=10)

    def guardar_juez(self):
        id_juez = self.id_juez_entry.get().strip()
        nombre = self.nombre_juez_entry.get().strip()
        club = self.club_juez_entry.get().strip()

        if not id_juez or not nombre or not club:
            messagebox.showerror("Error de Validación", "Todos los campos son obligatorios.", parent=self.top_level)
            return

        try:
            with open(self.competencia_path, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                if 'jueces' not in data:
                    data['jueces'] = []
                
                # Verificar si el ID del juez ya existe
                for juez_existente in data['jueces']:
                    if juez_existente.get('id_juez') == id_juez:
                        messagebox.showerror("Error", f"El ID de juez '{id_juez}' ya existe.", parent=self.top_level)
                        return

                nuevo_juez = {
                    "id_juez": id_juez,
                    "nombre": nombre,
                    "club": club
                }
                data['jueces'].append(nuevo_juez)
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()
            
            messagebox.showinfo("Éxito", "Juez añadido correctamente.", parent=self.top_level)
            self.torneo_screen_instance.recargar_datos_y_ui()
            self.top_level.destroy()

        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el juez: {e}", parent=self.top_level)

    def cancelar(self):
        self.top_level.destroy()
        # No es necesario llamar a deiconify en torneo_screen_instance ya que grab_set() se libera
        # y la ventana de torneo debería recuperar el foco automáticamente.

if __name__ == '__main__':
    # Código de prueba para CrearJuezScreen
    root_test = tk.Tk()
    root_test.title("Ventana Principal de Prueba")
    root_test.geometry("600x400")

    # Crear un archivo JSON de prueba si no existe
    test_data_dir_cj = os.path.join(os.path.dirname(__file__), "..", "..", "data_storage")
    if not os.path.exists(test_data_dir_cj):
        os.makedirs(test_data_dir_cj)
    
    test_competencia_file_cj = os.path.join(test_data_dir_cj, "competencia_para_crear_juez.json")
    if not os.path.exists(test_competencia_file_cj):
        initial_data = {
            "nombre": "Competencia de Prueba Jueces",
            "fecha": "2024-01-01",
            "lugar": "Lugar de Prueba",
            "categorias": [],
            "jueces": [
                {"id_juez": "J000", "nombre": "Juez Existente", "club": "Club Base"}
            ]
        }
        with open(test_competencia_file_cj, 'w', encoding='utf-8') as f_test:
            json.dump(initial_data, f_test, indent=4, ensure_ascii=False)

    # Simular TorneoScreen para la recarga
    class MockTorneoScreen:
        def __init__(self, r, path):
            self.root = r
            self.competencia_path = path
            self.competencia_data = None
            self.tree_jueces = None # Simular para evitar errores si se accede
            self.tree_categorias = None
            self._cargar_datos_competencia()
            print(f"MockTorneoScreen inicializado con {self.competencia_path}")

        def _cargar_datos_competencia(self):
            try:
                with open(self.competencia_path, 'r', encoding='utf-8') as f:
                    self.competencia_data = json.load(f)
            except Exception as e:
                print(f"Error cargando datos en mock: {e}")
                self.competencia_data = {}

        def recargar_datos_y_ui(self):
            self._cargar_datos_competencia()
            print("MockTorneoScreen: recargar_datos_y_ui() llamado.")
            print(f"Jueces actuales: {self.competencia_data['jueces'] if self.competencia_data else []}")
            # Aquí normalmente se actualizaría la UI del TorneoScreen
            # Para la prueba, solo imprimimos un mensaje.
            if hasattr(self, 'main_label'): # Ejemplo de actualización de UI
                jueces_count = len(self.competencia_data['jueces']) if self.competencia_data and 'jueces' in self.competencia_data else 0
                self.main_label.config(text=f"Jueces: {jueces_count}")

        def show_main_window(self):
            # Simula mostrar la ventana principal del torneo
            if not hasattr(self, 'main_label'):
                self.main_label = ttk.Label(self.root, text="Ventana de Torneo Simulada")
                self.main_label.pack(pady=20)
            
            ttk.Button(self.root, text="Abrir Añadir Juez", 
                       command=lambda: CrearJuezScreen(self.root, self, self.competencia_path)).pack(pady=10)
            self.root.deiconify()

    mock_torneo = MockTorneoScreen(root_test, test_competencia_file_cj)
    mock_torneo.show_main_window() # Mostrar la ventana principal simulada
    
    # Para abrir directamente la pantalla de crear juez al iniciar (opcional para prueba rápida)
    # CrearJuezScreen(root_test, mock_torneo, test_competencia_file_cj)

    root_test.mainloop()