# src/core/__init__.py
# Esto permite que la carpeta 'core' sea tratada como un paquete.

# Importaciones selectivas para facilitar el acceso desde niveles superiores si es necesario
# Ejemplo: from .torneo import Torneo
# Esto permitiría hacer `from src.core import Torneo` en lugar de `from src.core.torneo import Torneo`

from .torneo import Torneo
from .categoria import Categoria
from .pareja import Pareja
from .juez import Juez
from .tecnica import Tecnica
from .puntuacion_kata import PuntuacionKata