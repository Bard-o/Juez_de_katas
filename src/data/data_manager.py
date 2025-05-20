# src/data/data_manager.py
import json
import os
from typing import Dict, Any

# Importaciones relativas para asegurar que funcionen dentro del paquete
from ..core.torneo import Torneo
from ..core.categoria import Categoria
from ..core.pareja import Pareja
from ..core.juez import Juez
# Tecnica y PuntuacionKata no se guardan directamente como objetos de alto nivel en el JSON del torneo,
# sino como parte de las categorías o evaluaciones, por lo que no necesitan serializadores complejos aquí inicialmente.

class DataManager:
    def __init__(self, base_path: str = 'data_storage'):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def _get_torneo_filepath(self, nombre_torneo: str) -> str:
        return os.path.join(self.base_path, f"torneo_{nombre_torneo.replace(' ', '_').lower()}.json")

    def guardar_torneo(self, torneo: Torneo):
        filepath = self._get_torneo_filepath(torneo.nombre)
        data = self._convertir_torneo_a_dict(torneo)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Torneo '{torneo.nombre}' guardado en {filepath}")
        except IOError as e:
            print(f"Error al guardar el torneo '{torneo.nombre}': {e}")

    def cargar_torneo(self, nombre_torneo: str) -> Torneo | None:
        filepath = self._get_torneo_filepath(nombre_torneo)
        if not os.path.exists(filepath):
            print(f"No se encontró el archivo de datos para el torneo '{nombre_torneo}'.")
            return None
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            torneo = self._convertir_dict_a_torneo(data)
            print(f"Torneo '{torneo.nombre}' cargado desde {filepath}")
            return torneo
        except IOError as e:
            print(f"Error al cargar el torneo '{nombre_torneo}': {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error al decodificar el JSON del torneo '{nombre_torneo}': {e}")
            return None

    def _convertir_torneo_a_dict(self, torneo: Torneo) -> Dict[str, Any]:
        return {
            'nombre': torneo.nombre,
            'fecha': torneo.fecha,
            'lugar': torneo.lugar,
            'categorias': [self._convertir_categoria_a_dict(cat) for cat in torneo.categorias],
            'jueces': [self._convertir_juez_a_dict(juez) for juez in torneo.jueces]
        }

    def _convertir_dict_a_torneo(self, data: Dict[str, Any]) -> Torneo:
        torneo = Torneo(data['nombre'], data['fecha'], data['lugar'])
        for cat_data in data.get('categorias', []):
            categoria = self._convertir_dict_a_categoria(cat_data)
            torneo.agregar_categoria(categoria)
        for juez_data in data.get('jueces', []):
            juez = self._convertir_dict_a_juez(juez_data)
            torneo.agregar_juez(juez)
        return torneo

    def _convertir_categoria_a_dict(self, categoria: Categoria) -> Dict[str, Any]:
        return {
            'nombre_categoria': categoria.nombre_categoria,
            'tipo_kata': categoria.tipo_kata,
            'parejas': [self._convertir_pareja_a_dict(p) for p in categoria.parejas]
        }

    def _convertir_dict_a_categoria(self, data: Dict[str, Any]) -> Categoria:
        categoria = Categoria(data['nombre_categoria'], data['tipo_kata'])
        for pareja_data in data.get('parejas', []):
            pareja = self._convertir_dict_a_pareja(pareja_data)
            categoria.agregar_pareja(pareja)
        return categoria

    def _convertir_pareja_a_dict(self, pareja: Pareja) -> Dict[str, Any]:
        return {
            'id_pareja': pareja.id_pareja,
            'nombre_participante1': pareja.nombre_participante1,
            'nombre_participante2': pareja.nombre_participante2,
            'club': pareja.club,
            'puntaje_total': pareja.puntaje_total,
            'errores_tecnicas': pareja.errores_tecnicas # Asumiendo que esto es un dict simple
        }

    def _convertir_dict_a_pareja(self, data: Dict[str, Any]) -> Pareja:
        pareja = Pareja(data['id_pareja'], data['nombre_participante1'], data['nombre_participante2'], data['club'])
        # El ID ya se pasa al constructor, así que la siguiente línea no es necesaria si el constructor lo maneja.
        # pareja.id_pareja = data['id_pareja'] # Restaurar ID existente
        pareja.puntaje_total = data.get('puntaje_total', 0)
        pareja.errores_tecnicas = data.get('errores_tecnicas', {})
        return pareja

    def _convertir_juez_a_dict(self, juez: Juez) -> Dict[str, Any]:
        return {
            'id_juez': juez.id_juez,
            'nombre': juez.nombre,
            'club': juez.club
        }

    def _convertir_dict_a_juez(self, data: Dict[str, Any]) -> Juez:
        return Juez(data['id_juez'], data['nombre'], data['club'])

# Ejemplo de cómo se podría extender para guardar/cargar configuraciones de katas (lista de técnicas)
# def guardar_config_kata(self, nombre_kata: str, tecnicas: List[Tecnica]): ...
# def cargar_config_kata(self, nombre_kata: str) -> List[Tecnica]: ...