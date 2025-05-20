class Categoria:
    def __init__(self, nombre_categoria: str, tipo_kata: str):
        self.nombre_categoria = nombre_categoria
        self.tipo_kata = tipo_kata
        self.parejas = []

    def agregar_pareja(self, pareja):
        self.parejas.append(pareja)
        print(f"Pareja '{pareja.id_pareja}' agregada a la categoría '{self.nombre_categoria}'.")

    def __str__(self):
        return f"Categoría: {self.nombre_categoria}, Tipo de Kata: {self.tipo_kata}"

# Implementación del patrón Factory
class CategoriaFactory:
    @staticmethod
    def crear_categoria(tipo: str):
        if tipo.lower() == "infantil":
            return Categoria("Infantil", "Kata Básico")
        elif tipo.lower() == "juvenil":
            return Categoria("Juvenil", "Kata Intermedio")
        elif tipo.lower() == "adulto":
            return Categoria("Adulto", "Kata Avanzado")
        else:
            raise ValueError("Tipo de categoría desconocido")