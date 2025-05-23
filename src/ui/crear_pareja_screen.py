import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class CrearParejaScreen:
    def __init__(self, master, torneo_screen_instance, competencia_path):
        self.master = master
        self.torneo_screen_instance = torneo_screen_instance
        self.competencia_path = competencia_path
        self.competencia_data = None
        self.categorias_disponibles = []

        self.top_level = tk.Toplevel(master)
        self.top_level.title("Añadir Nueva Pareja")
        self.top_level.geometry("500x450") # Tamaño ajustado
        self.top_level.grab_set()
        self.top_level.resizable(False, False)

        self._cargar_datos_competencia()
        self._crear_interfaz()

    def _cargar_datos_competencia(self):
        try:
            with open(self.competencia_path, 'r', encoding='utf-8') as f:
                self.competencia_data = json.load(f)
            self.categorias_disponibles = [cat.get("nombre_categoria", "Sin Nombre") for cat in self.competencia_data.get("categorias", [])]
        except Exception as e:
            messagebox.showerror("Error al Cargar", f"No se pudo cargar los datos de la competencia: {e}", parent=self.top_level)
            self.top_level.destroy()
            return
        
        if not self.categorias_disponibles:
            messagebox.showinfo("Información", "No hay categorías creadas en este torneo. Por favor, cree una categoría primero.", parent=self.top_level)
            self.top_level.destroy()

    def _crear_interfaz(self):
        if not self.competencia_data or not self.categorias_disponibles:
             # Ya se mostró mensaje en _cargar_datos_competencia si no hay categorías
            return

        main_frame = ttk.Frame(self.top_level, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text="ID Pareja:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.id_pareja_entry = ttk.Entry(main_frame, width=40)
        self.id_pareja_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(main_frame, text="Nombre Participante 1:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.nombre_p1_entry = ttk.Entry(main_frame, width=40)
        self.nombre_p1_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(main_frame, text="Nombre Participante 2:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.nombre_p2_entry = ttk.Entry(main_frame, width=40)
        self.nombre_p2_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(main_frame, text="Club:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.club_entry = ttk.Entry(main_frame, width=40)
        self.club_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(main_frame, text="Categoría:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.categoria_combobox = ttk.Combobox(main_frame, values=self.categorias_disponibles, state="readonly", width=37)
        self.categoria_combobox.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        if self.categorias_disponibles:
            self.categoria_combobox.current(0)

        # Frame para botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=5, column=0, columnspan=2, pady=20, sticky=tk.EW)
        botones_frame.columnconfigure(0, weight=1)
        botones_frame.columnconfigure(1, weight=1)

        btn_guardar = ttk.Button(botones_frame, text="Guardar Pareja", command=self._guardar_pareja)
        btn_guardar.grid(row=0, column=0, padx=10, sticky=tk.EW)

        btn_cancelar = ttk.Button(botones_frame, text="Cancelar", command=self.top_level.destroy)
        btn_cancelar.grid(row=0, column=1, padx=10, sticky=tk.EW)

        main_frame.columnconfigure(1, weight=1) # Para que los entry se expandan

    def _guardar_pareja(self):
        id_pareja = self.id_pareja_entry.get().strip()
        nombre_p1 = self.nombre_p1_entry.get().strip()
        nombre_p2 = self.nombre_p2_entry.get().strip()
        club = self.club_entry.get().strip()
        categoria_seleccionada_nombre = self.categoria_combobox.get()

        if not all([id_pareja, nombre_p1, nombre_p2, club, categoria_seleccionada_nombre]):
            messagebox.showerror("Error de Validación", "Todos los campos son obligatorios.", parent=self.top_level)
            return

        # Verificar si el ID de pareja ya existe en CUALQUIER categoría
        for cat_existente in self.competencia_data["categorias"] if self.competencia_data else []:
            for pareja_existente in cat_existente.get("parejas", []):
                if pareja_existente.get("id_pareja") == id_pareja:
                    messagebox.showerror("Error", f"El ID de pareja '{id_pareja}' ya existe en la categoría '{cat_existente.get('nombre_categoria', 'N/A')}'.", parent=self.top_level)
                    return

        nueva_pareja = {
            "id_pareja": id_pareja,
            "nombre_participante1": nombre_p1,
            "nombre_participante2": nombre_p2,
            "club": club,
            "puntaje_total": 0,
            "errores_tecnicas": {}
        }

        categoria_encontrada = False
        for categoria_data in self.competencia_data["categorias"] if self.competencia_data else []:
            if categoria_data.get("nombre_categoria") == categoria_seleccionada_nombre:
                if "parejas" not in categoria_data:
                    categoria_data["parejas"] = []
                categoria_data["parejas"].append(nueva_pareja)
                categoria_encontrada = True
                break
        
        if not categoria_encontrada:
            messagebox.showerror("Error", f"No se encontró la categoría '{categoria_seleccionada_nombre}'. Esto no debería ocurrir.", parent=self.top_level)
            return

        try:
            with open(self.competencia_path, 'w', encoding='utf-8') as f:
                json.dump(self.competencia_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Éxito", "Pareja añadida correctamente.", parent=self.top_level)
            self.torneo_screen_instance.recargar_datos_y_ui()
            self.top_level.destroy()
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar la pareja: {e}", parent=self.top_level)