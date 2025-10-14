from typing import List, Optional
from sqlalchemy.orm import Session
from ...domain.entities import Product
from ...domain.repositories import IProductRepository
from ..db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """
    Implementación del repositorio de productos usando SQLAlchemy y SQLite.
    
    Implementa la interface IProductRepository con operaciones CRUD
    sobre la tabla de productos en la base de datos.
    Realiza conversiones automáticas entre modelos ORM y entidades del dominio.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión de BD.
        
        Args:
            db: Sesión de SQLAlchemy inyectada desde FastAPI.
        """
        self.db = db
    
    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos de la base de datos.
        
        Retorna:
            List[Product]: Lista de todas las entidades Product.
                          Retorna lista vacía si no hay productos.
        """
        try:
            # Query a todos los productos
            product_models = self.db.query(ProductModel).all()
            
            # Convierte modelos ORM a entidades del dominio
            products = [self._model_to_entity(model) for model in product_models]
            
            return products
        
        except Exception as e:
            print(f"Error obteniendo todos los productos: {str(e)}")
            return []
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto específico por su ID.
        
        Args:
            product_id: El identificador del producto.
            
        Retorna:
            Optional[Product]: La entidad Product si existe, None si no se encuentra.
        """
        try:
            # Query con filter por ID
            product_model = self.db.query(ProductModel).filter(
                ProductModel.id == product_id
            ).first()
            
            # Si no existe, retorna None
            if product_model is None:
                return None
            
            # Convierte a entidad del dominio
            return self._model_to_entity(product_model)
        
        except Exception as e:
            print(f"Error obteniendo producto por ID {product_id}: {str(e)}")
            return None
    
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Obtiene todos los productos de una marca específica.
        
        Args:
            brand: El nombre de la marca a filtrar.
            
        Retorna:
            List[Product]: Lista de productos de esa marca.
                          Retorna lista vacía si no hay coincidencias.
        """
        try:
            # Query con filter por brand
            product_models = self.db.query(ProductModel).filter(
                ProductModel.brand == brand
            ).all()
            
            # Convierte modelos a entidades
            products = [self._model_to_entity(model) for model in product_models]
            
            return products
        
        except Exception as e:
            print(f"Error obteniendo productos de la marca '{brand}': {str(e)}")
            return []
    
    def get_by_category(self, category: str) -> List[Product]:
        """
        Obtiene todos los productos de una categoría específica.
        
        Args:
            category: El nombre de la categoría a filtrar.
            
        Retorna:
            List[Product]: Lista de productos de esa categoría.
                          Retorna lista vacía si no hay coincidencias.
        """
        try:
            # Query con filter por category
            product_models = self.db.query(ProductModel).filter(
                ProductModel.category == category
            ).all()
            
            # Convierte modelos a entidades
            products = [self._model_to_entity(model) for model in product_models]
            
            return products
        
        except Exception as e:
            print(f"Error obteniendo productos de la categoría '{category}': {str(e)}")
            return []
    
    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto en la base de datos.
        
        - Si el producto tiene ID, lo actualiza
        - Si el producto NO tiene ID (None), crea uno nuevo
        - Después de guardar, retorna el producto con ID asignado
        
        Args:
            product: Entidad Product a guardar o actualizar.
            
        Retorna:
            Product: El producto guardado con su ID asignado.
            
        Raises:
            Exception: Si hay error al guardar en la BD.
        """
        try:
            # Convierte la entidad del dominio a modelo ORM
            product_model = self._entity_to_model(product)
            
            if product.id is not None:
                # Actualizar producto existente
                # Merge se usa para actualizar objetos que ya existen
                product_model = self.db.merge(product_model)
            else:
                # Crear nuevo producto
                # Add se usa para nuevos objetos
                self.db.add(product_model)
            
            # Hacer commit para guardar cambios
            self.db.commit()
            
            # Refresh para obtener el ID si fue creado
            self.db.refresh(product_model)
            
            # Convierte el modelo guardado a entidad del dominio
            saved_product = self._model_to_entity(product_model)
            
            return saved_product
        
        except Exception as e:
            print(f"Error guardando producto: {str(e)}")
            self.db.rollback()
            raise
    
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto de la base de datos por su ID.
        
        Args:
            product_id: El ID del producto a eliminar.
            
        Retorna:
            bool: True si el producto se eliminó correctamente,
                  False si el producto no existía.
        """
        try:
            # Buscar el producto
            product_model = self.db.query(ProductModel).filter(
                ProductModel.id == product_id
            ).first()
            
            # Si no existe, retorna False
            if product_model is None:
                return False
            
            # Eliminar el producto
            self.db.delete(product_model)
            
            # Hacer commit
            self.db.commit()
            
            return True
        
        except Exception as e:
            print(f"Error eliminando producto con ID {product_id}: {str(e)}")
            self.db.rollback()
            return False
    
    # Métodos privados
    
    def _model_to_entity(self, model: ProductModel) -> Product:
        """
        Convierte un modelo ORM (ProductModel) a una entidad del dominio (Product).
        
        Args:
            model: Modelo ORM de la base de datos.
            
        Retorna:
            Product: Entidad del dominio con los mismos datos.
        """
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description
        )
    
    def _entity_to_model(self, entity: Product) -> ProductModel:
        """
        Convierte una entidad del dominio (Product) a modelo ORM (ProductModel).
        
        Args:
            entity: Entidad del dominio.
            
        Retorna:
            ProductModel: Modelo ORM listo para guardar en BD.
        """
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description
        )