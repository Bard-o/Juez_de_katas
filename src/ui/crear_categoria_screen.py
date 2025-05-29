import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

KATAS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "katas")

class CrearCategoriaScreen:
    def __init__(self, root, torneo_screen_instance, competencia_path):
        self.torneo_screen_instance = torneo_screen_instance
        self.competencia_path = competencia_path
        self.top_level = tk.Toplevel(root)
        self.top_level.title("Añadir Nueva Categoría")
        self.top_level.geometry("500x350") # Tamaño ajustado para el contenido
        self.top_level.grab_set() # Modal
        self.top_level.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        # Configurar estilo
        style = ttk.Style(self.top_level)
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))
        style.configure("Dark.TFrame", background="#dadada")

        main_frame = ttk.Frame(self.top_level, style="Dark.TFrame", padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        titulo_label = ttk.Label(main_frame, text="Formulario de Nueva Categoría", style="Header.TLabel")
        titulo_label.pack(pady=(0, 20))

        ttk.Label(main_frame, text="Nombre de la Categoría:").pack(anchor=tk.W, pady=(5,0))
        self.nombre_categoria_entry = ttk.Entry(main_frame, width=40)
        self.nombre_categoria_entry.pack(fill=tk.X, pady=(0,10))

        ttk.Label(main_frame, text="Tipo de Kata:").pack(anchor=tk.W, pady=(5,0))
        self.tipo_kata_combobox = ttk.Combobox(main_frame, width=38, state="readonly")
        self.tipo_kata_combobox.pack(fill=tk.X, pady=(0,20))
        self._cargar_tipos_kata()

        botones_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        botones_frame.pack(fill=tk.X, pady=(20,0))

        btn_guardar = ttk.Button(botones_frame, text="Guardar Categoría", command=self.guardar_categoria)
        btn_guardar.pack(side=tk.RIGHT, padx=(10,0))

        btn_cancelar = ttk.Button(botones_frame, text="Cancelar", command=self.cerrar_ventana)
        btn_cancelar.pack(side=tk.RIGHT)

    def _cargar_tipos_kata(self):
        try:
            if os.path.exists(KATAS_PATH) and os.path.isdir(KATAS_PATH):
                tipos_kata = [os.path.splitext(f)[0] for f in os.listdir(KATAS_PATH) if f.endswith('.json')]
                if tipos_kata:
                    self.tipo_kata_combobox['values'] = sorted(tipos_kata)
                    self.tipo_kata_combobox.current(0) # Seleccionar el primero por defecto
                else:
                    self.tipo_kata_combobox['values'] = ['No hay katas disponibles']
                    self.tipo_kata_combobox.current(0)
                    self.tipo_kata_combobox.config(state="disabled")
            else:
                messagebox.showwarning("Advertencia", f"El directorio de katas no existe: {KATAS_PATH}", parent=self.top_level)
                self.tipo_kata_combobox['values'] = ['Error al cargar katas']
                self.tipo_kata_combobox.current(0)
                self.tipo_kata_combobox.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los tipos de kata: {e}", parent=self.top_level)
            self.tipo_kata_combobox['values'] = ['Error']
            self.tipo_kata_combobox.current(0)
            self.tipo_kata_combobox.config(state="disabled")

    def guardar_categoria(self):
        nombre_categoria = self.nombre_categoria_entry.get().strip()
        tipo_kata = self.tipo_kata_combobox.get()

        if not nombre_categoria:
            messagebox.showwarning("Campo Vacío", "Por favor, ingrese el nombre de la categoría.", parent=self.top_level)
            return

        if not tipo_kata or tipo_kata in ['No hay katas disponibles', 'Error al cargar katas', 'Error']:
            messagebox.showwarning("Selección Inválida", "Por favor, seleccione un tipo de kata válido.", parent=self.top_level)
            return

        try:
            with open(self.competencia_path, 'r+', encoding='utf-8') as f:
                competencia_data = json.load(f)
                
                nueva_categoria = {
                    "nombre_categoria": nombre_categoria,
                    "tipo_kata": tipo_kata,
                    "parejas": [] # Inicialmente sin parejas
                }
                
                # Verificar si la categoría ya existe (por nombre)
                for cat in competencia_data.get("categorias", []):
                    if cat.get("nombre_categoria") == nombre_categoria:
                        messagebox.showwarning("Categoría Existente", f"La categoría '{nombre_categoria}' ya existe en este torneo.", parent=self.top_level)
                        return

                competencia_data.setdefault("categorias", []).append(nueva_categoria)
                
                f.seek(0) # Volver al inicio del archivo
                json.dump(competencia_data, f, indent=4, ensure_ascii=False)
                f.truncate() # Eliminar contenido restante si el nuevo es más corto

            messagebox.showinfo("Éxito", f"Categoría '{nombre_categoria}' guardada correctamente.", parent=self.top_level)
            if self.torneo_screen_instance and hasattr(self.torneo_screen_instance, 'recargar_datos_y_ui'):
                self.torneo_screen_instance.recargar_datos_y_ui()
            self.cerrar_ventana()

        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró el archivo de la competencia: {self.competencia_path}", parent=self.top_level)
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Error al decodificar el archivo JSON de la competencia.", parent=self.top_level)
        except IOError as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar la categoría en el archivo: {e}", parent=self.top_level)
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error inesperado: {e}", parent=self.top_level)

    def cerrar_ventana(self):
        self.top_level.destroy()

  