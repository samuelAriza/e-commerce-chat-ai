from sqlalchemy.orm import Session
from .models import ProductModel
from ..db.database import SessionLocal

def load_initial_data() -> None:
    """
    Carga datos iniciales en la base de datos.
    
    Verifica si ya existen productos en la BD. Si no existen,
    crea 10 productos de ejemplo con marcas, categorías y precios variados.
    
    Productos de ejemplo:
    - Variedad de marcas: Nike, Adidas, Puma, New Balance, Converse
    - Categorías: Running, Casual, Formal, Training
    - Precios: Entre $50 y $200
    - Stock: Variado (0 a 50)
    
    Ejemplo de uso:
        from src.infrastructure.db.init_data import load_initial_data
        from src.infrastructure.db.database import init_db
        
        if __name__ == "__main__":
            init_db()
            load_initial_data()
    """
    # Crear sesión
    db = SessionLocal()
    
    try:
        # Verificar si ya existen productos
        product_count = db.query(ProductModel).count()
        
        if product_count > 0:
            print(f"Base de datos ya contiene {product_count} productos. Saltando carga inicial.")
            return
        
        print("Cargando datos iniciales...")
        
        # Crear lista de productos de ejemplo
        initial_products = [
            ProductModel(
                name="Nike Air Max 90",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=129.99,
                stock=15,
                description="Zapatillas de running con amortiguación Air Max. Comodidad y estilo clásico."
            ),
            ProductModel(
                name="Adidas Ultra Boost 21",
                brand="Adidas",
                category="Running",
                size="41",
                color="Blanco",
                price=159.99,
                stock=8,
                description="Zapatillas de running con tecnología Boost. Máxima amortiguación y responsive."
            ),
            ProductModel(
                name="Puma RS-X",
                brand="Puma",
                category="Casual",
                size="40",
                color="Rojo",
                price=89.99,
                stock=22,
                description="Zapatillas casuales retro con diseño moderno. Perfectas para el día a día."
            ),
            ProductModel(
                name="New Balance 574",
                brand="New Balance",
                category="Casual",
                size="43",
                color="Gris",
                price=99.99,
                stock=18,
                description="Zapatillas clásicas de New Balance. Comodidad y versatilidad garantizadas."
            ),
            ProductModel(
                name="Converse Chuck Taylor All Star",
                brand="Converse",
                category="Casual",
                size="39",
                color="Azul",
                price=59.99,
                stock=35,
                description="Las icónicas zapatillas de lona. Un clásico que nunca pasa de moda."
            ),
            ProductModel(
                name="Nike Court Legacy",
                brand="Nike",
                category="Formal",
                size="42",
                color="Blanco",
                price=74.99,
                stock=12,
                description="Zapatillas de corte clásico para uso formal. Diseño elegante y moderno."
            ),
            ProductModel(
                name="Adidas NMD R1",
                brand="Adidas",
                category="Training",
                size="44",
                color="Negro",
                price=139.99,
                stock=10,
                description="Zapatillas de training con diseño futurista. Tecnología Boost integrada."
            ),
            ProductModel(
                name="Puma Future Rider",
                brand="Puma",
                category="Running",
                size="41",
                color="Verde",
                price=85.99,
                stock=0,
                description="Zapatillas para running con confort optimizado. Actualmente sin stock."
            ),
            ProductModel(
                name="Nike ZoomX Vaporfly Next",
                brand="Nike",
                category="Running",
                size="42",
                color="Naranja",
                price=199.99,
                stock=5,
                description="Zapatillas profesionales para competencia. Tecnología de carrera avanzada."
            ),
            ProductModel(
                name="Adidas Superstar",
                brand="Adidas",
                category="Casual",
                size="40",
                color="Blanco con Negro",
                price=79.99,
                stock=28,
                description="Las legendarias Superstar de Adidas. Estilo urbano y comodidad asegurada."
            ),
        ]
        
        # Insertar todos los productos de una vez
        db.add_all(initial_products)
        
        # Hacer commit para guardar los cambios
        db.commit()
        
        print(f"Se cargaron {len(initial_products)} productos iniciales exitosamente.")
        
        # Mostrar resumen de productos cargados
        loaded_count = db.query(ProductModel).count()
        brands = db.query(ProductModel.brand).distinct().all()
        categories = db.query(ProductModel.category).distinct().all()
        
        print(f"Resumen:")
        print(f"   - Total de productos: {loaded_count}")
        print(f"   - Marcas: {', '.join([b[0] for b in brands])}")
        print(f"   - Categorías: {', '.join([c[0] for c in categories])}")
    
    except Exception as e:
        print(f"Error al cargar datos iniciales: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()


def clear_all_products() -> None:
    """
    Elimina todos los productos de la base de datos.
    
    Esta función elimina TODOS los productos.
    Usar solo en desarrollo o testing.
    
    Ejemplo de uso:
        from src.infrastructure.db.init_data import clear_all_products
        clear_all_products()
    """
    db = SessionLocal()
    
    try:
        # Contar productos antes de eliminar
        count = db.query(ProductModel).count()
        
        if count == 0:
            print("No hay productos para eliminar.")
            return
        
        # Eliminar todos los productos
        db.query(ProductModel).delete()
        db.commit()
        
        print(f"Se eliminaron {count} productos de la base de datos.")
    
    except Exception as e:
        print(f"Error al eliminar productos: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()


def reset_database() -> None:
    """
    Reinicia la base de datos: elimina todos los productos y carga datos iniciales.
    
    Útil para resetear el estado durante desarrollo o testing.
    
    Ejemplo de uso:
        from src.infrastructure.db.init_data import reset_database
        reset_database()
    """
    print("Reiniciando base de datos...")
    clear_all_products()
    load_initial_data()
    print("Base de datos reiniciada exitosamente.")