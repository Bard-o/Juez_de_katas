# src/ui/console_ui.py
import os
import platform
from ..core.torneo import Torneo
from ..core.categoria import Categoria
from ..core.pareja import Pareja
from ..core.juez import Juez
from ..core.tecnica import Tecnica
from ..core.puntuacion_kata import PuntuacionKata
import json 
from ..data.data_manager import DataManager
from typing import List, Dict

class ConsoleUI:
    def __init__(self):
        self.data_manager = DataManager()
        self.torneo_actual = None
        self.config_katas = {}
        self._cargar_config_katas_desde_json()

    def _cargar_config_katas_desde_json(self, katas_dir_path: str = None):
        """Carga la configuración de las katas y sus técnicas desde archivos JSON."""
        if katas_dir_path is None:
            # Asume que la estructura del proyecto es src/ui/console_ui.py y src/data/katas/
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            katas_dir_path = os.path.join(base_dir, 'data', 'katas')

        if not os.path.isdir(katas_dir_path):
            print(f"Advertencia: El directorio de configuración de katas '{katas_dir_path}' no existe.")
            return

        for filename in os.listdir(katas_dir_path):
            if filename.endswith('.json'):
                filepath = os.path.join(katas_dir_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for kata_name, tecnicas in data.items():
                                if isinstance(tecnicas, list) and all(isinstance(t, str) for t in tecnicas):
                                    if kata_name in self.config_katas:
                                        print(f"Advertencia: Kata '{kata_name}' del archivo '{filename}' ya está definido. Se sobrescribirá.")
                                    self.config_katas[kata_name] = tecnicas
                                else:
                                    print(f"Advertencia: Formato incorrecto para técnicas de '{kata_name}' en '{filename}'. Se omitirá.")
                        else:
                            print(f"Advertencia: El archivo JSON '{filename}' no tiene el formato esperado (diccionario de katas). Se omitirá.")
                except json.JSONDecodeError:
                    print(f"Error al decodificar JSON en el archivo: {filepath}")
                except IOError as e:
                    print(f"Error al leer el archivo de configuración de kata '{filepath}': {e}")
        
        if not self.config_katas:
            print("Advertencia: No se cargó ninguna configuración de Kata desde los archivos JSON.")
        else:
            print(f"Configuración de Katas cargada: {list(self.config_katas.keys())}")

    def limpiar_consola(self):
        """Limpia la consola."""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    def esperar_tecla(self, mensaje="Presione Enter para continuar..."):
        """Espera a que el usuario presione una tecla."""
        input(mensaje)

    def mostrar_menu_principal(self):
        print("\n--- Sistema de Juzgamiento de Katas de Judo ---")
        print("1. Crear Nuevo Torneo")
        print("2. Cargar Torneo Existente")
        if self.torneo_actual:
            print("3. Gestionar Torneo Actual")
            print("4. Guardar Torneo Actual")
        print("0. Salir")
        return input("Seleccione una opción: ")

    def mostrar_menu_torneo(self):
        print(f"\n--- Torneo: {self.torneo_actual.nombre} ---")
        print("1. Agregar Categoría")
        print("2. Agregar Juez al Torneo")
        print("3. Seleccionar Categoría para Gestionar")
        print("4. Ver Información del Torneo")
        print("0. Volver al Menú Principal")
        return input("Seleccione una opción: ")

    def mostrar_menu_categoria(self, categoria: Categoria):
        print(f"\n--- Categoría: {categoria.nombre_categoria} ({categoria.tipo_kata}) ---")
        print("1. Agregar Pareja")
        print("2. Registrar Puntuación de Kata para Pareja")
        print("3. Ver Resultados de la Categoría")
        print("4. Ver Información de la Categoría")
        print("0. Volver al Menú del Torneo")
        return input("Seleccione una opción: ")

    def crear_nuevo_torneo(self):
        nombre = input("Nombre del torneo: ")
        fecha = input("Fecha del torneo (YYYY-MM-DD): ")
        lugar = input("Lugar del torneo: ")
        self.torneo_actual = Torneo(nombre, fecha, lugar)
        print(f"Torneo '{nombre}' creado.")

    def cargar_torneo_existente(self):
        nombre_torneo = input("Nombre del torneo a cargar: ")
        torneo = self.data_manager.cargar_torneo(nombre_torneo)
        if torneo:
            self.torneo_actual = torneo
        else:
            print(f"No se pudo cargar el torneo '{nombre_torneo}'.")

    def guardar_torneo_actual(self):
        if self.torneo_actual:
            self.data_manager.guardar_torneo(self.torneo_actual)
        else:
            print("No hay torneo actual para guardar.")

    def agregar_categoria_a_torneo(self):
        if not self.torneo_actual:
            print("Primero debe crear o cargar un torneo.")
            return
        nombre_cat = input("Nombre de la categoría: ")
        print("Tipos de Kata disponibles:")
        for i, tipo_k in enumerate(self.config_katas.keys()):
            print(f"  {i+1}. {tipo_k}")
        try:
            seleccion_tipo_kata = int(input("Seleccione el tipo de Kata: ")) -1
            tipo_kata_seleccionado = list(self.config_katas.keys())[seleccion_tipo_kata]
        except (ValueError, IndexError):
            print("Selección de tipo de Kata inválida.")
            return
        
        categoria = Categoria(nombre_cat, tipo_kata_seleccionado)
        self.torneo_actual.agregar_categoria(categoria)

    def agregar_juez_a_torneo(self):
        if not self.torneo_actual:
            print("Primero debe crear o cargar un torneo.")
            return
        id_juez = input("ID del Juez (para login): ")
        # Verificar si el ID ya existe
        for j in self.torneo_actual.jueces:
            if j.id_juez == id_juez:
                print(f"Error: Ya existe un juez con el ID '{id_juez}'.")
                return
        nombre_juez = input("Nombre del Juez: ")
        club_juez = input("Club del Juez: ")
        juez = Juez(id_juez, nombre_juez, club_juez)
        self.torneo_actual.agregar_juez(juez)

    def seleccionar_categoria_para_gestionar(self) -> Categoria | None:
        if not self.torneo_actual or not self.torneo_actual.categorias:
            print("No hay categorías en el torneo actual.")
            return None
        print("Categorías disponibles:")
        for i, cat in enumerate(self.torneo_actual.categorias):
            print(f"  {i+1}. {cat.nombre_categoria} ({cat.tipo_kata})")
        try:
            seleccion = int(input("Seleccione una categoría: ")) - 1
            return self.torneo_actual.categorias[seleccion]
        except (ValueError, IndexError):
            print("Selección inválida.")
            return None

    def agregar_pareja_a_categoria(self, categoria: Categoria):
        p1_nombre = input("Nombre del participante 1: ")
        p2_nombre = input("Nombre del participante 2: ")
        club = input("Club de la pareja: ")
        pareja = Pareja(p1_nombre, p2_nombre, club)
        categoria.agregar_pareja(pareja)

    def registrar_puntuacion_kata(self, categoria: Categoria):
        if not categoria.parejas:
            print("No hay parejas en esta categoría.")
            return
        if not self.torneo_actual.jueces or len(self.torneo_actual.jueces) < 5:
            print("Se necesitan al menos 5 jueces registrados en el torneo para evaluar.")
            # Podríamos permitir menos, pero el requerimiento dice 5 para descartar.
            return

        print("Seleccione la pareja a evaluar:")
        for i, p in enumerate(categoria.parejas):
            print(f"  {i+1}. {p.nombre_participante1} y {p.nombre_participante2} (ID: {p.id_pareja})")
        try:
            seleccion_pareja = int(input("Seleccione una pareja: ")) - 1
            pareja_a_evaluar = categoria.parejas[seleccion_pareja]
        except (ValueError, IndexError):
            print("Selección de pareja inválida.")
            return

        tipo_kata = categoria.tipo_kata
        if tipo_kata not in self.config_katas:
            print(f"Error: Tipo de Kata '{tipo_kata}' no configurado con técnicas.")
            return
        
        tecnicas_definidas = [Tecnica(nombre) for nombre in self.config_katas[tipo_kata]]
        print(f"\nEvaluando Kata: {tipo_kata} para {pareja_a_evaluar.nombre_participante1} y {pareja_a_evaluar.nombre_participante2}")
        print(f"Número de técnicas: {len(tecnicas_definidas)}")

        evaluaciones_jueces_kata_actual: Dict[str, List[Dict]] = {}

        # Simulación de login de jueces y entrada de puntuaciones
        jueces_participantes = self.torneo_actual.jueces[:5] # Tomamos los primeros 5 para simplificar
        print(f"\nParticiparán los siguientes {len(jueces_participantes)} jueces en la evaluación:")
        for j in jueces_participantes:
            print(f" - {j.nombre} (ID: {j.id_juez})")
        
        input("Presione Enter para comenzar la evaluación de los jueces...")

        for juez_actual in jueces_participantes:
            print(f"\n--- Juez: {juez_actual.nombre} (ID: {juez_actual.id_juez}) --- ")
            # Aquí se podría pedir el ID del juez para 'loguearlo'
            # id_juez_login = input(f"Juez {juez_actual.nombre}, ingrese su ID para confirmar: ")
            # if id_juez_login != juez_actual.id_juez:
            #     print("ID incorrecto. No se puede continuar con este juez.")
            #     continue # O manejar de otra forma

            evaluaciones_este_juez = []
            for i, tecnica in enumerate(tecnicas_definidas):
                print(f"  Técnica {i+1}: {tecnica.nombre_tecnica}")
                errores_tecnica = {'pequeno': 0, 'mediano': 0, 'grande': 0, 'olvidada': False}
                compensacion = 0.0
                try:
                    errores_tecnica['pequeno'] = int(input("    Errores pequeños (0, 1 o 2): "))
                    if errores_tecnica['pequeno'] < 0 or errores_tecnica['pequeno'] > 2:
                        print("Valor inválido, se usará 0.")
                        errores_tecnica['pequeno'] = 0
                    
                    errores_tecnica['mediano'] = int(input("    Errores medianos (0 o 1): "))
                    if errores_tecnica['mediano'] < 0 or errores_tecnica['mediano'] > 1:
                        print("Valor inválido, se usará 0.")
                        errores_tecnica['mediano'] = 0

                    errores_tecnica['grande'] = int(input("    Errores grandes (0 o 1): "))
                    if errores_tecnica['grande'] < 0 or errores_tecnica['grande'] > 1:
                        print("Valor inválido, se usará 0.")
                        errores_tecnica['grande'] = 0

                    olvidada_input = input("    Técnica olvidada (s/n): ").lower()
                    errores_tecnica['olvidada'] = olvidada_input == 's'

                    compensacion = float(input("    Compensación (ej: 0.5, -0.5): "))
                except ValueError:
                    print("Entrada inválida. Se usarán valores por defecto (0 errores, 0 compensación).")
                    errores_tecnica = {'pequeno': 0, 'mediano': 0, 'grande': 0, 'olvidada': False}
                    compensacion = 0.0
                
                evaluaciones_este_juez.append({'errores': errores_tecnica, 'compensacion': compensacion})
            evaluaciones_jueces_kata_actual[juez_actual.id_juez] = evaluaciones_este_juez

        # Procesar puntuación
        puntuacion = PuntuacionKata(pareja_a_evaluar, tecnicas_definidas, evaluaciones_jueces_kata_actual)
        puntuacion.calcular_puntajes_tecnicas()
        
        print("\n--- Resultados de la Kata --- ")
        print(puntuacion)
        # Guardar el puntaje en la pareja (ya se hace en PuntuacionKata.calcular_puntajes_tecnicas)
        # Podríamos guardar el objeto PuntuacionKata completo si fuera necesario para auditoría, 
        # pero por ahora solo el puntaje total en la pareja y los errores.
        pareja_a_evaluar.errores_tecnicas = puntuacion.obtener_errores_totales_por_tecnica()
        print(f"Puntaje total para {pareja_a_evaluar.nombre_participante1} y {pareja_a_evaluar.nombre_participante2}: {pareja_a_evaluar.puntaje_total}")

    def ver_resultados_categoria(self, categoria: Categoria):
        if not categoria.parejas:
            print("No hay parejas en esta categoría para mostrar resultados.")
            return

        # Ordenar parejas por puntaje (mayor a menor)
        parejas_ordenadas = sorted(categoria.parejas, key=lambda p: p.puntaje_total, reverse=True)

        print(f"\n--- Resultados de la Categoría: {categoria.nombre_categoria} ({categoria.tipo_kata}) ---")
        print("Posición | Pareja (ID)                               | Club                | Puntaje Total")
        print("---------|-------------------------------------------|---------------------|---------------")
        for i, pareja in enumerate(parejas_ordenadas):
            nombres = f"{pareja.nombre_participante1} y {pareja.nombre_participante2}"
            print(f"{i+1:<8} | {nombres[:30]} ({pareja.id_pareja[:8]}...) | {pareja.club[:19]:<19} | {pareja.puntaje_total:.2f}")

    def ver_info_torneo(self):
        if not self.torneo_actual:
            print("No hay torneo cargado.")
            return
        print(self.torneo_actual)
        print("Categorías:")
        if self.torneo_actual.categorias:
            for cat in self.torneo_actual.categorias:
                print(f"  - {cat.nombre_categoria} ({cat.tipo_kata}), Parejas: {len(cat.parejas)}")
        else:
            print("  (No hay categorías)")
        print("Jueces:")
        if self.torneo_actual.jueces:
            for juez in self.torneo_actual.jueces:
                print(f"  - {juez.nombre} (ID: {juez.id_juez}, Club: {juez.club})")
        else:
            print("  (No hay jueces)")

    def ver_info_categoria(self, categoria: Categoria):
        print(categoria)
        print("Parejas inscritas:")
        if categoria.parejas:
            for p in categoria.parejas:
                print(f"  - {p.nombre_participante1} y {p.nombre_participante2} (Club: {p.club}, ID: {p.id_pareja}, Puntaje: {p.puntaje_total})")
        else:
            print("  (No hay parejas inscritas)")

    def ejecutar(self):
        while True:
            self.limpiar_consola()
            opcion_principal = self.mostrar_menu_principal()
            
            if opcion_principal == '1':
                self.limpiar_consola()
                self.crear_nuevo_torneo()
                self.esperar_tecla()
            elif opcion_principal == '2':
                self.limpiar_consola()
                self.cargar_torneo_existente()
                self.esperar_tecla()
            elif opcion_principal == '3' and self.torneo_actual:
                self.gestionar_torneo_actual() # Ya limpia consola al inicio
            elif opcion_principal == '4' and self.torneo_actual:
                self.limpiar_consola()
                self.guardar_torneo_actual()
                self.esperar_tecla()
            elif opcion_principal == '0':
                self.limpiar_consola()
                if self.torneo_actual:
                    guardar = input("¿Desea guardar el torneo actual antes de salir? (s/n): ").lower()
                    if guardar == 's':
                        self.guardar_torneo_actual()
                        self.esperar_tecla("Torneo guardado. Presione Enter para salir.")
                print("Saliendo del sistema.")
                break
            else:
                self.limpiar_consola()
                print("Opción no válida.")
                self.esperar_tecla()

    def gestionar_torneo_actual(self):
        while True:
            self.limpiar_consola()
            opcion_torneo = self.mostrar_menu_torneo()

            if opcion_torneo == '1':
                self.limpiar_consola()
                self.agregar_categoria_a_torneo()
                self.esperar_tecla()
            elif opcion_torneo == '2':
                self.limpiar_consola()
                self.agregar_juez_a_torneo()
                self.esperar_tecla()
            elif opcion_torneo == '3':
                self.limpiar_consola()
                categoria_seleccionada = self.seleccionar_categoria_para_gestionar()
                if categoria_seleccionada:
                    self.gestionar_categoria_actual(categoria_seleccionada) # Ya limpia consola al inicio
                else:
                    self.esperar_tecla() # Si no se seleccionó o no hay categorías
            elif opcion_torneo == '4':
                self.limpiar_consola()
                self.ver_info_torneo()
                self.esperar_tecla()
            elif opcion_torneo == '0':
                self.limpiar_consola() # Limpia antes de volver al menú principal
                break
            else:
                self.limpiar_consola()
                print("Opción no válida.")
                self.esperar_tecla()

    def gestionar_categoria_actual(self, categoria: Categoria):
        while True:
            self.limpiar_consola()
            opcion_categoria = self.mostrar_menu_categoria(categoria)

            if opcion_categoria == '1':
                self.limpiar_consola()
                self.agregar_pareja_a_categoria(categoria)
                self.esperar_tecla()
            elif opcion_categoria == '2':
                self.limpiar_consola()
                self.registrar_puntuacion_kata(categoria)
                self.esperar_tecla()
            elif opcion_categoria == '3':
                self.limpiar_consola()
                self.ver_resultados_categoria(categoria)
                self.esperar_tecla()
            elif opcion_categoria == '4':
                self.limpiar_consola()
                self.ver_info_categoria(categoria)
                self.esperar_tecla()
            elif opcion_categoria == '0':
                self.limpiar_consola() # Limpia antes de volver al menú de torneo
                break
            else:
                self.limpiar_consola()
                print("Opción no válida.")
                self.esperar_tecla()

if __name__ == '__main__':
    # Esto es solo para pruebas rápidas de la UI, el main.py real importará y usará ConsoleUI
    ui = ConsoleUI()
    # Simulación para prueba
    # ui.torneo_actual = Torneo("Demo Cup", "2024-01-01", "Gimnasio Central")
    # nage_no_kata = Categoria("Nage no Kata Senior", "Nage no Kata")
    # ui.torneo_actual.agregar_categoria(nage_no_kata)
    # ui.torneo_actual.agregar_juez(Juez("juez001", "Pedro Juez", "Club Judo Master"))
    # ui.torneo_actual.agregar_juez(Juez("juez002", "Ana Jueza", "Club Judo Master"))
    # ui.torneo_actual.agregar_juez(Juez("juez003", "Luis Juez", "Club Judo Master"))
    # ui.torneo_actual.agregar_juez(Juez("juez004", "Maria Jueza", "Club Judo Master"))
    # ui.torneo_actual.agregar_juez(Juez("juez005", "Carlos Juez", "Club Judo Master"))
    # pareja1 = Pareja("Tori Uno", "Uke Uno", "Club A")
    # nage_no_kata.agregar_pareja(pareja1)
    ui.ejecutar()