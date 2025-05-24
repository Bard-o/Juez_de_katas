import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


PENALIZACIONES = {
    "pequeno1": 0.5,
    "pequeno2": 0.5, # Si se marcan ambos, sería -1.0 en total por pequeños
    "mediano": 1.0,
    "grande": 3.0,
    "olvidada": 10.0
}
PUNTAJE_BASE_TECNICA = 10.0

class EvaluacionKataScreen:
    def __init__(self, root, pareja_info, juez_main_screen_instance):
        self.root = root
        self.pareja_info = pareja_info # Contiene info de la pareja, categoría, juez, ruta_competencia
        self.juez_main_screen_instance = juez_main_screen_instance
        self.kata_tecnicas = []
        self.evaluaciones_tecnicas_actuales = {} # {nombre_tecnica: {errores: {}, compensacion: 0, puntaje: 10.0}}

        self.top_level = tk.Toplevel(root)
        self.top_level.title(f"Evaluación Kata - Juez: {self.pareja_info['juez_info']['nombre_juez']}")
        self.top_level.state('zoomed')
        self.top_level.grab_set()
        self.top_level.protocol("WM_DELETE_WINDOW", self.cerrar_y_volver)

        self._cargar_tecnicas_kata()
        self._inicializar_evaluaciones()
        self._crear_interfaz()

    def _cargar_tecnicas_kata(self):
        # Ejemplo: self.pareja_info['tipo_kata_categoria'] podría ser 'Nage no Kata'
        # Debería haber un archivo como 'Nage no Kata.json' en src/data/katas/
        nombre_kata_archivo = f"{self.pareja_info['tipo_kata_categoria']}.json"
        ruta_archivo_kata = os.path.join(os.path.dirname(__file__), '..', 'data', 'katas', nombre_kata_archivo)
        try:
            with open(ruta_archivo_kata, 'r', encoding='utf-8') as f:
                data_kata = json.load(f)
                # Asumiendo que el JSON tiene una lista de técnicas bajo una clave como "tecnicas"
                # Y cada técnica es un objeto con "nombre" y opcionalmente "sub_tecnicas"
                for grupo_tecnica in data_kata.get('tecnicas', []):
                    for sub_tecnica in grupo_tecnica.get('sub_tecnicas', []):
                        self.kata_tecnicas.append(sub_tecnica['nombre'])
            if not self.kata_tecnicas:
                 messagebox.showwarning("Sin Técnicas", f"No se encontraron técnicas para {self.pareja_info['tipo_kata_categoria']}. Verifique el archivo.", parent=self.top_level)
                 # self.cerrar_y_volver() # Podría ser una opción
        except FileNotFoundError:
            messagebox.showerror("Error", f"Archivo de kata no encontrado: {nombre_kata_archivo}", parent=self.top_level)
            self.cerrar_y_volver()
        except Exception as e:
            messagebox.showerror("Error al Cargar Kata", f"No se pudo cargar el archivo de kata: {e}", parent=self.top_level)
            self.cerrar_y_volver()

    def _inicializar_evaluaciones(self):
        for tecnica_nombre in self.kata_tecnicas:
            self.evaluaciones_tecnicas_actuales[tecnica_nombre] = {
                'errores': {
                    'pequeno1': tk.BooleanVar(value=False),
                    'pequeno2': tk.BooleanVar(value=False),
                    'mediano': tk.BooleanVar(value=False),
                    'grande': tk.BooleanVar(value=False),
                    'olvidada': tk.BooleanVar(value=False)
                },
                'compensacion': tk.DoubleVar(value=0.0),
                'puntaje_var': tk.DoubleVar(value=PUNTAJE_BASE_TECNICA)
            }
            # Conectar la actualización del puntaje a los cambios en errores y compensación
            for error_var in self.evaluaciones_tecnicas_actuales[tecnica_nombre]['errores'].values():
                error_var.trace_add("write", lambda *args, tn=tecnica_nombre: self._actualizar_puntaje_tecnica(tn))
            self.evaluaciones_tecnicas_actuales[tecnica_nombre]['compensacion'].trace_add("write", lambda *args, tn=tecnica_nombre: self._actualizar_puntaje_tecnica(tn))

    def _crear_interfaz(self):
        style = ttk.Style(self.top_level)
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))
        style.configure("SubHeader.TLabel", font=('Helvetica', 11))
        style.configure("Bold.TLabel", font=('Helvetica', 10, 'bold'))
        style.configure("Dark.TFrame", background="#333333")
        style.configure("Content.TFrame", background="#dadada")

        main_frame_expansible = ttk.Frame(self.top_level, style="Dark.TFrame")
        main_frame_expansible.pack(fill=tk.BOTH, expand=True)
        main_frame_expansible.columnconfigure(0, weight=1)
        main_frame_expansible.rowconfigure(1, weight=1) # Para el canvas

        # Header Info
        header_frame = ttk.Frame(main_frame_expansible, style="Content.TFrame", padding="10")
        header_frame.grid(row=0, column=0, sticky="ew")
        info_text = (
            f"Juez: {self.pareja_info['juez_info']['nombre_juez']} ({self.pareja_info['juez_info']['id_juez']}) - "
            f"Club Juez: {self.pareja_info['juez_info']['club_juez']}\n"
            f"Evaluando Pareja ID: {self.pareja_info['id_pareja']} ({self.pareja_info['nombre_participante1']} y {self.pareja_info['nombre_participante2']}) - "
            f"Club Pareja: {self.pareja_info['club']}\n"
            f"Categoría: {self.pareja_info['nombre_categoria']} - Kata: {self.pareja_info['tipo_kata_categoria']}"
        )
        ttk.Label(header_frame, text=info_text, style="SubHeader.TLabel", background="#dadada", justify=tk.LEFT).pack(fill=tk.X)

        # Canvas y Scrollbar para la lista de técnicas
        canvas_frame = ttk.Frame(main_frame_expansible, style="Content.TFrame")
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        canvas = tk.Canvas(canvas_frame, bg="#dadada", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Content.TFrame") # Frame interior

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Encabezados de la tabla de técnicas
        headers = ["Técnica", "Err. Peq. 1", "Err. Peq. 2", "Err. Med.", "Err. Gra.", "Olvidada", "Compensación", "Puntaje"]
        for col, header_text in enumerate(headers):
            ttk.Label(scrollable_frame, text=header_text, style="Bold.TLabel", padding=(5,2), background="#dadada").grid(row=0, column=col, sticky="ew", padx=2)

        # Filas de técnicas
        if not self.kata_tecnicas:
            ttk.Label(scrollable_frame, text="No hay técnicas cargadas para esta kata.", background="#dadada").grid(row=1, column=0, columnspan=len(headers), pady=10)
        
        for i, tecnica_nombre in enumerate(self.kata_tecnicas, start=1):
            eval_data = self.evaluaciones_tecnicas_actuales[tecnica_nombre]
            ttk.Label(scrollable_frame, text=tecnica_nombre, background="#dadada", wraplength=150).grid(row=i, column=0, sticky="w", padx=5)

            # Checkboxes para errores
            ttk.Checkbutton(scrollable_frame, variable=eval_data['errores']['pequeno1']).grid(row=i, column=1)
            ttk.Checkbutton(scrollable_frame, variable=eval_data['errores']['pequeno2']).grid(row=i, column=2)
            ttk.Checkbutton(scrollable_frame, variable=eval_data['errores']['mediano']).grid(row=i, column=3)
            ttk.Checkbutton(scrollable_frame, variable=eval_data['errores']['grande']).grid(row=i, column=4)
            ttk.Checkbutton(scrollable_frame, variable=eval_data['errores']['olvidada']).grid(row=i, column=5)

            # Radiobuttons para compensación
            comp_frame = ttk.Frame(scrollable_frame, style="Content.TFrame")
            comp_frame.grid(row=i, column=6)
            ttk.Radiobutton(comp_frame, text="-0.5", variable=eval_data['compensacion'], value=-0.5).pack(side=tk.LEFT)
            ttk.Radiobutton(comp_frame, text="0", variable=eval_data['compensacion'], value=0.0).pack(side=tk.LEFT)
            ttk.Radiobutton(comp_frame, text="+0.5", variable=eval_data['compensacion'], value=0.5).pack(side=tk.LEFT)

            # Label para puntaje de técnica
            ttk.Label(scrollable_frame, textvariable=eval_data['puntaje_var'], style="Bold.TLabel", background="#dadada").grid(row=i, column=7, padx=5)

        # Botón de Enviar
        footer_frame = ttk.Frame(main_frame_expansible, style="Content.TFrame", padding="10")
        footer_frame.grid(row=2, column=0, sticky="ew")
        self.btn_enviar = ttk.Button(footer_frame, text="Enviar Resultados", command=self._enviar_resultados)
        self.btn_enviar.pack(pady=5)
        if not self.kata_tecnicas:
            self.btn_enviar.config(state=tk.DISABLED)

    def _actualizar_puntaje_tecnica(self, tecnica_nombre):
        eval_data = self.evaluaciones_tecnicas_actuales[tecnica_nombre]
        puntaje = PUNTAJE_BASE_TECNICA

        if eval_data['errores']['olvidada'].get():
            puntaje = 0 # Si está olvidada, el puntaje es 0, independientemente de otros errores o compensación
        else:
            if eval_data['errores']['pequeno1'].get():
                puntaje -= PENALIZACIONES['pequeno1']
            if eval_data['errores']['pequeno2'].get():
                puntaje -= PENALIZACIONES['pequeno2']
            if eval_data['errores']['mediano'].get():
                puntaje -= PENALIZACIONES['mediano']
            if eval_data['errores']['grande'].get():
                puntaje -= PENALIZACIONES['grande']
            
            puntaje += eval_data['compensacion'].get()
        
        # Asegurar que el puntaje no sea negativo o mayor al base (a menos que compensación lo permita)
        puntaje = max(0, puntaje) # No puede ser menor que 0
        # Podríamos limitar el máximo si la compensación no puede superar el puntaje base
        # puntaje = min(PUNTAJE_BASE_TECNICA + 0.5, puntaje) # Ejemplo de límite superior

        eval_data['puntaje_var'].set(round(puntaje, 2))

    def _enviar_resultados(self):
        # Construir el objeto de evaluación para este juez y esta kata/pareja
        evaluacion_final_juez = {
            "id_juez": self.pareja_info['juez_info']['id_juez'],
            "nombre_juez": self.pareja_info['juez_info']['nombre_juez'],
            "nombre_kata_evaluado": self.pareja_info['tipo_kata_categoria'],
            "tecnicas": [],
            "puntaje_total_juez_para_kata": 0.0
        }
        sum_puntajes_tecnicas = 0.0

        for tecnica_nombre, data in self.evaluaciones_tecnicas_actuales.items():
            tecnica_eval = {
                "nombre_tecnica": tecnica_nombre,
                "errores": {
                    "pequeno1": data['errores']['pequeno1'].get(),
                    "pequeno2": data['errores']['pequeno2'].get(),
                    "mediano": data['errores']['mediano'].get(),
                    "grande": data['errores']['grande'].get(),
                    "olvidada": data['errores']['olvidada'].get()
                },
                "compensacion": data['compensacion'].get(),
                "puntaje_asignado_juez": data['puntaje_var'].get()
            }
            evaluacion_final_juez["tecnicas"].append(tecnica_eval)
            sum_puntajes_tecnicas += data['puntaje_var'].get()
        
        evaluacion_final_juez["puntaje_total_juez_para_kata"] = round(sum_puntajes_tecnicas, 2)

        # Lógica para guardar en el JSON de la competencia
        try:
            with open(self.pareja_info['ruta_competencia'], 'r+', encoding='utf-8') as f:
                competencia_data = json.load(f)
                
                # Encontrar la categoría y la pareja
                found_pareja = False
                for cat in competencia_data.get('categorias', []):
                    if cat.get('nombre_categoria') == self.pareja_info['nombre_categoria']:
                        for p in cat.get('parejas', []):
                            if p.get('id_pareja') == self.pareja_info['id_pareja']:
                                # Añadir o actualizar la evaluación del juez
                                if 'evaluaciones_jueces' not in p:
                                    p['evaluaciones_jueces'] = []
                                
                                # Remover evaluación previa del mismo juez para la misma kata si existe
                                p['evaluaciones_jueces'] = [
                                    ev for ev in p['evaluaciones_jueces'] 
                                    if not (ev.get('id_juez') == evaluacion_final_juez['id_juez'] and 
                                            ev.get('nombre_kata_evaluado') == evaluacion_final_juez['nombre_kata_evaluado'])
                                ]
                                p['evaluaciones_jueces'].append(evaluacion_final_juez)
                                found_pareja = True
                                break
                    if found_pareja: break
                
                if not found_pareja:
                    messagebox.showerror("Error", "No se encontró la pareja en el archivo de competencia.", parent=self.top_level)
                    return

                f.seek(0)
                json.dump(competencia_data, f, ensure_ascii=False, indent=4)
                f.truncate()
            
            messagebox.showinfo("Resultados Enviados", "La evaluación ha sido guardada exitosamente.", parent=self.top_level)
            self.cerrar_y_volver()

        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar la evaluación: {e}", parent=self.top_level)

    def cerrar_y_volver(self):
        self.top_level.destroy()
        if self.juez_main_screen_instance:
            self.juez_main_screen_instance.reactivate() # Asume que JuezMainScreen tiene este método

# Para pruebas directas (opcional)
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw() # Ocultar la ventana raíz principal para la prueba

    # Crear datos de prueba simulados
    mock_juez_info = {"id_juez": "J001", "nombre_juez": "Juez Prueba", "club_juez": "Club Jueces"}
    mock_pareja_info = {
        "id_pareja": "P001",
        "nombre_participante1": "Atleta Uno",
        "nombre_participante2": "Atleta Dos",
        "club": "Club Parejas",
        "nombre_categoria": "Nage No Kata Adultos",
        "tipo_kata_categoria": "Nage no Kata", # Nombre del archivo JSON de kata (sin .json)
        "juez_info": mock_juez_info,
        "ruta_competencia": "../../data_storage/torneo_prueba_eval.json" # Ruta a un JSON de prueba
    }

    # Crear un archivo de kata de prueba (ej. Nage no Kata.json)
    kata_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'katas')
    os.makedirs(kata_dir, exist_ok=True)
    nage_no_kata_content = {
        "nombre": "Nage no Kata",
        "tecnicas": [
            {"nombre_grupo": "Te-waza", "sub_tecnicas": [{"nombre": "Uki-otoshi"}, {"nombre": "Seoi-nage"}, {"nombre": "Kata-guruma"}]},
            {"nombre_grupo": "Koshi-waza", "sub_tecnicas": [{"nombre": "Uki-goshi"}, {"nombre": "Harai-goshi"}, {"nombre": "Tsurikomi-goshi"}]}
            # ... más técnicas
        ]
    }
    with open(os.path.join(kata_dir, "Nage no Kata.json"), 'w', encoding='utf-8') as f:
        json.dump(nage_no_kata_content, f, ensure_ascii=False, indent=4)

    # Crear un archivo de competencia de prueba
    data_storage_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data_storage')
    os.makedirs(data_storage_dir, exist_ok=True)
    torneo_prueba_content = {
        "nombre": "Torneo Prueba Eval",
        "categorias": [
            {
                "nombre_categoria": "Nage No Kata Adultos",
                "tipo_kata": "Nage no Kata",
                "parejas": [
                    {
                        "id_pareja": "P001", 
                        "nombre_participante1": "Atleta Uno", 
                        "nombre_participante2": "Atleta Dos", 
                        "club": "Club Parejas",
                        # "evaluaciones_jueces": [] # Se llenará al guardar
                    }
                ]
            }
        ],
        "jueces": [mock_juez_info]
    }
    with open(mock_pareja_info['ruta_competencia'], 'w', encoding='utf-8') as f:
        json.dump(torneo_prueba_content, f, ensure_ascii=False, indent=4)

    # Mock de la pantalla principal del juez (solo para que reactivate no falle)
    class MockJuezMainScreen:
        def reactivate(self):
            print("MockJuezMainScreen reactivado. Cerrando aplicación de prueba.")
            root.quit()

    app = EvaluacionKataScreen(root, mock_pareja_info, MockJuezMainScreen())
    root.mainloop()