import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class ResultadosCategoriaScreen:
    def __init__(self, root, admin_menu_instance, competencia_path, category_data):
        self.root = root
        self.admin_menu_instance = admin_menu_instance
        self.competencia_path = competencia_path
        self.category_data = category_data

        self.top_level = tk.Toplevel(root)
        self.top_level.title(f"Resultados de Categoría: {self.category_data.get('nombre_categoria', 'N/A')}")
        self.top_level.state('zoomed')
        self.top_level.grab_set()
        self.top_level.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        self._crear_interfaz()

    def _crear_interfaz(self):
        style = ttk.Style(self.top_level)
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))
        style.configure("SubHeader.TLabel", font=('Helvetica', 12, 'bold'))
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        style.configure("Dark.TFrame", background="#dadada")
        style.configure("Content.TFrame", background="#ffffff")

        main_frame_expansible = ttk.Frame(self.top_level, style="Dark.TFrame")
        main_frame_expansible.pack(fill=tk.BOTH, expand=True)
        main_frame_expansible.columnconfigure(0, weight=1)
        main_frame_expansible.rowconfigure(0, weight=1)

        content_container = ttk.Frame(main_frame_expansible, padding="20", style="Content.TFrame")
        content_container.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)
        content_container.columnconfigure(0, weight=1)
        content_container.rowconfigure(1, weight=1) # Allow the scrollable frame to expand

        # Title
        titulo_label = ttk.Label(content_container, text=f"Resultados de Categoría: {self.category_data.get('nombre_categoria', 'N/A')}", style="Header.TLabel", background="#ffffff")
        titulo_label.pack(pady=(0, 20))

        # Sort pairs by total score
        self._calcular_puntajes_totales()
        sorted_parejas = sorted(self.category_data.get('parejas', []), key=lambda p: p.get('puntaje_total', 0), reverse=True)

        # Create a scrollable frame for pairs' results
        canvas = tk.Canvas(content_container, background="#ffffff")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

        scrollable_frame = ttk.Frame(canvas, style="Content.TFrame")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="scrollable_frame")

        # Bind mouse wheel for scrolling
        scrollable_frame.bind("<Enter>", lambda event: self._bind_mouse_wheel(canvas))
        scrollable_frame.bind("<Leave>", lambda event: self._unbind_mouse_wheel(canvas))

        for pareja in sorted_parejas:
            self._display_pareja_results(scrollable_frame, pareja)

        # Back button
        btn_volver = ttk.Button(content_container, text="Volver", command=self.cerrar_ventana)
        btn_volver.pack(pady=(20, 0))

    def _bind_mouse_wheel(self, canvas):
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    def _unbind_mouse_wheel(self, canvas):
        canvas.unbind_all("<MouseWheel>")

    def _calcular_puntajes_totales(self):
        for pareja in self.category_data.get('parejas', []):
            total_kata_score = 0
            evaluaciones_jueces = pareja.get('evaluaciones_jueces', [])

            # Group evaluations by technique name
            tecnicas_evaluadas = {}
            for eval_juez in evaluaciones_jueces:
                for tecnica in eval_juez.get('tecnicas', []):
                    nombre_tecnica = tecnica['nombre_tecnica']
                    if nombre_tecnica not in tecnicas_evaluadas:
                        tecnicas_evaluadas[nombre_tecnica] = []
                    tecnicas_evaluadas[nombre_tecnica].append(tecnica['puntaje_asignado_juez'])
            
            # Calculate score for each technique (dropping highest and lowest)
            for nombre_tecnica, scores in tecnicas_evaluadas.items():
                if len(scores) >= 3:
                    scores.sort()
                    # Drop highest and lowest, sum the rest
                    valid_scores = scores[1:-1] # This handles 3, 4, or 5 judges correctly
                    tecnica_score = sum(valid_scores)
                elif len(scores) > 0:
                    tecnica_score = sum(scores) # If less than 3 judges, sum all available scores
                else:
                    tecnica_score = 0
                total_kata_score += tecnica_score
            
            pareja['puntaje_total'] = total_kata_score

    def _display_pareja_results(self, parent_frame, pareja):
        pareja_frame = ttk.LabelFrame(parent_frame, text=f"Pareja: {pareja.get('nombre_participante1', 'N/A')} y {pareja.get('nombre_participante2', 'N/A')} (ID: {pareja.get('id_pareja', 'N/A')}) - Total: {pareja.get('puntaje_total', 0):.1f}", padding="10", style="Content.TFrame")
        pareja_frame.pack(fill=tk.X, padx=10, pady=10, expand=True)

        # Treeview for technique scores
        columns = ["Tecnica", "Juez 1", "Juez 2", "Juez 3", "Juez 4", "Juez 5", "Puntaje Válido"]
        self.tree_tecnicas = ttk.Treeview(pareja_frame, columns=columns, show="headings")

        for col in columns:
            self.tree_tecnicas.heading(col, text=col)
            self.tree_tecnicas.column(col, anchor=tk.CENTER, width=100)
        self.tree_tecnicas.column("Tecnica", anchor=tk.W, width=200)

        self.tree_tecnicas.pack(fill=tk.BOTH, expand=True)

        evaluaciones_jueces = pareja.get('evaluaciones_jueces', [])

        # Aggregate scores by technique and judge
        tecnicas_scores_by_judge = {}
        for eval_juez in evaluaciones_jueces:
            juez_id = eval_juez.get('id_juez')
            for tecnica_eval in eval_juez.get('tecnicas', []):
                nombre_tecnica = tecnica_eval['nombre_tecnica']
                if nombre_tecnica not in tecnicas_scores_by_judge:
                    tecnicas_scores_by_judge[nombre_tecnica] = {f"Juez {i+1}": "N/A" for i in range(5)} # Initialize for 5 judges
                
                if 1 <= juez_id <= 5:
                    tecnicas_scores_by_judge[nombre_tecnica][f"Juez {juez_id}"] = tecnica_eval['puntaje_asignado_juez']

        # Populate Treeview
        for nombre_tecnica, scores_data in tecnicas_scores_by_judge.items():
            row_values = [nombre_tecnica]
            judge_scores_list = []
            for i in range(1, 6):
                score = scores_data.get(f"Juez {i}", "N/A")
                row_values.append(score)
                if isinstance(score, (int, float)):
                    judge_scores_list.append(score)
            
            # Calculate valid score for the technique
            valid_tecnica_score = 0
            if len(judge_scores_list) >= 3:
                judge_scores_list.sort()
                valid_tecnica_score = sum(judge_scores_list[1:-1])
            elif len(judge_scores_list) > 0:
                valid_tecnica_score = sum(judge_scores_list)
            
            row_values.append(f"{valid_tecnica_score:.1f}")
            self.tree_tecnicas.insert("", tk.END, values=row_values)

    def cerrar_ventana(self):
        self.top_level.destroy()
        self.root.deiconify() # Show the previous window (TorneoScreen) again
        if self.admin_menu_instance and hasattr(self.admin_menu_instance, 'root') and self.admin_menu_instance.root.winfo_exists():
            self.admin_menu_instance.root.state('zoomed') # Set main window to maximized state
            self.admin_menu_instance.root.deiconify()
        elif self.root and self.root.winfo_exists(): # Fallback if admin_menu_instance is not as expected
             self.root.deiconify()

