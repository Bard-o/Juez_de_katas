# Proyecto Final - Sistema de Gestión de Torneos de Kata

Este proyecto es una aplicación de escritorio desarrollada en Python con Tkinter para la gestión integral de torneos de Kata. Permite administrar competencias, categorías, jueces, parejas participantes y la evaluación detallada de las katas realizadas.

## Funcionalidades Principales

La aplicación se divide en dos módulos principales:

1.  **Aplicación de Administración (`main_admin_app.py`):**
    *   Permite crear y gestionar torneos (competiciones).
    *   Dentro de cada torneo, se pueden crear y administrar categorías (ej. Nage No Kata Adultos, Katame No Kata Juvenil).
    *   Permite registrar y gestionar jueces, asignándolos a los torneos.
    *   Permite registrar y gestionar parejas de competidores, asignándolas a las categorías correspondientes.
    *   Visualiza los resultados de las evaluaciones de las katas.

2.  **Aplicación de Juez (`main_juez_app.py`):**
    *   Permite a los jueces iniciar sesión seleccionando un torneo y su nombre.
    *   Muestra las parejas asignadas al juez para su evaluación dentro de una categoría específica.
    *   Proporciona una interfaz detallada para que el juez evalúe cada técnica de la kata realizada por una pareja, registrando errores (pequeños, medianos, grandes, olvidada) y compensaciones.
    *   Calcula y muestra el puntaje en tiempo real para cada técnica y el total de la kata evaluada por el juez.
    *   Guarda los resultados de la evaluación en el archivo JSON del torneo.

## Estructura del Proyecto

El proyecto se organiza en las siguientes carpetas principales:

*   `src/core`: Contiene las clases que modelan las entidades principales del sistema (ej. `Torneo`, `Categoria`, `Juez`, `Pareja`, `Tecnica`).
*   `src/data`: Maneja la persistencia de datos, principalmente a través de archivos JSON.
    *   `data_manager.py`: Contiene la lógica para cargar y guardar datos de los torneos.
    *   `katas/`: Almacena archivos JSON que definen la estructura de las diferentes katas (ej. `Nage no Kata.json`), incluyendo sus grupos de técnicas y las técnicas específicas.
*   `src/ui`: Contiene las clases responsables de la interfaz gráfica de usuario (GUI) construida con Tkinter.
    *   Cada pantalla principal de la aplicación (ej. login de juez, menú de administrador, pantalla de evaluación) tiene su propio archivo Python (ej. `juez_login_screen.py`, `admin_menu.py`, `evaluacion_kata_screen.py`).

## Flujo General y Interacción de Clases

1.  **Arranque de Aplicaciones:**
    *   `main_admin_app.py` inicia la interfaz de administración.
    *   `main_juez_app.py` inicia la interfaz de login para jueces.

2.  **Administración del Torneo (Admin App):**
    *   El administrador interactúa con pantallas como `CrearCompetenciaScreen`, `CrearCategoriaScreen`, `CrearJuezScreen`, `CrearParejaScreen`.
    *   Estas pantallas utilizan `DataManager` para leer y escribir en los archivos JSON de los torneos (almacenados, por ejemplo, en una carpeta `data_storage/`).
    *   La información de un torneo se estructura en un archivo JSON que contiene detalles del torneo, lista de categorías, jueces asociados, y dentro de cada categoría, las parejas inscritas.

3.  **Evaluación por Juez (Juez App):**
    *   Un juez inicia sesión a través de `JuezLoginScreen`, seleccionando un torneo y su perfil.
    *   `JuezMainScreen` muestra las parejas que el juez debe evaluar.
    *   Al seleccionar una pareja, se abre `EvaluacionKataScreen`.
    *   `EvaluacionKataScreen`:
        *   Carga la estructura de la kata (grupos de técnicas y técnicas) desde el archivo JSON correspondiente en `src/data/katas/` (ej. `Nage no Kata.json`).
        *   Permite al juez marcar errores y compensaciones para cada técnica.
        *   Calcula dinámicamente el puntaje por técnica y el puntaje total de la kata según las reglas de penalización (definidas en `PENALIZACIONES` dentro de la clase).
        *   Al "Enviar Resultados", la evaluación detallada del juez (incluyendo puntaje por técnica y total) se guarda en el archivo JSON del torneo, dentro de la estructura de la pareja evaluada, bajo una clave como `evaluaciones_jueces`.

4.  **Persistencia de Datos:**
    *   Los datos de los torneos, incluyendo categorías, jueces, parejas y las evaluaciones de los jueces, se almacenan en archivos JSON. Esto permite una fácil lectura y modificación.
    *   La estructura de las katas (técnicas y sus agrupaciones) también se define en archivos JSON separados, lo que facilita la adición o modificación de katas sin cambiar el código principal de la aplicación.

## Clases y Métodos Clave (Ejemplos)

*   **`src.ui.admin_menu.AdminMenuScreen`**:
    *   `_crear_nueva_competencia()`: Lanza `CrearCompetenciaScreen`.
    *   `_abrir_gestion_torneo()`: Lanza `TorneoScreen` para gestionar un torneo existente.
*   **`src.ui.torneo_screen.TorneoScreen`**:
    *   `_crear_nueva_categoria()`: Lanza `CrearCategoriaScreen`.
    *   `_anadir_nueva_pareja()`: Lanza `CrearParejaScreen`.
    *   `_anadir_nuevo_juez()`: Lanza `CrearJuezScreen`.
    *   `recargar_datos_y_ui()`: Actualiza la visualización de datos del torneo.
*   **`src.ui.juez_login_screen.JuezLoginScreen`**:
    *   `_cargar_competencias_y_jueces()`: Lee los archivos de torneo para poblar la lista de competencias y jueces disponibles.
    *   `_login()`: Valida la selección y abre `JuezMainScreen`.
*   **`src.ui.juez_main_screen.JuezMainScreen`**:
    *   `_cargar_parejas_para_evaluar()`: Filtra y muestra las parejas que el juez actual debe evaluar.
    *   `_abrir_pantalla_evaluacion()`: Instancia y muestra `EvaluacionKataScreen` para la pareja seleccionada.
*   **`src.ui.evaluacion_kata_screen.EvaluacionKataScreen`**:
    *   `_cargar_tecnicas_kata()`: Carga la definición de la kata desde su archivo JSON.
    *   `_inicializar_evaluaciones()`: Prepara las variables de Tkinter para cada técnica.
    *   `_actualizar_puntaje_tecnica()`: Recalcula el puntaje de una técnica cuando se modifica un error o compensación.
    *   `_enviar_resultados()`: Construye el objeto de evaluación y lo guarda en el archivo JSON del torneo, actualizando la sección `evaluaciones_jueces` de la pareja.
*   **`src.data.data_manager.DataManager`** (Implícito, aunque no una clase explícita en el código proporcionado, la lógica de manejo de archivos JSON está distribuida en las pantallas):
    *   Funciones para leer (`json.load()`) y escribir (`json.dump()`) datos de los torneos y katas. 
