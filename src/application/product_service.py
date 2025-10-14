from typing import List, Optional, Dict, Any
from ..domain.entities import Product
from ..domain.repositories import IProductRepository
from ..domain.exceptions import ProductNotFoundError, InvalidProductDataError
from .dtos import ProductDTO

class ProductService:
    """
    Servicio de aplicación para gestionar productos.
    
    Orquesta la lógica de negocio entre la capa de presentación
    y la capa de datos. Realiza validaciones y conversiones entre
    DTOs y entidades del dominio.
    """
    
    def __init__(self, repository: IProductRepository):
        """
        Inicializa el servicio con inyección de dependencia.
        
        Args:
            repository: Implementación del repositorio de productos.
                       No se crea aquí, viene inyectado de la infraestructura.
        """
        self.repository = repository
    
    def get_all_products(self) -> List[ProductDTO]:
        """
        Obtiene todos los productos disponibles.
        
        Retorna:
            List[ProductDTO]: Lista de todos los productos convertidos a DTO.
        """
        products = self.repository.get_all()
        return [self._entity_to_dto(product) for product in products]
    
    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """
        Busca un producto específico por su ID.
        
        Args:
            product_id: El identificador del producto.
            
        Retorna:
            ProductDTO: El producto encontrado.
            
        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        product = self.repository.get_by_id(product_id)
        
        if product is None:
            raise ProductNotFoundError(product_id=product_id)
        
        return self._entity_to_dto(product)
    
    def search_products(self, filters: Dict[str, Any]) -> List[ProductDTO]:
        """
        Busca productos según criterios de filtrado.
        
        Filtros soportados:
        - 'brand': Marca del producto
        - 'category': Categoría del producto
        
        Args:
            filters: Diccionario con los criterios de filtrado.
                    Ejemplo: {'brand': 'Nike', 'category': 'Zapatos'}
            
        Retorna:
            List[ProductDTO]: Lista de productos que cumplen los criterios.
        """
        results = []
        
        # Si hay filtro de marca, busca por marca
        if 'brand' in filters:
            brand = filters['brand']
            brand_products = self.repository.get_by_brand(brand)
            results = brand_products
        
        # Si hay filtro de categoría, filtra adicional
        if 'category' in filters:
            category = filters['category']
            if results:
                # Filtra los resultados anteriores por categoría
                results = [p for p in results if p.category == category]
            else:
                # Primera búsqueda por categoría
                results = self.repository.get_by_category(category)
        
        # Si no hay filtros, retorna todos
        if not results and not filters:
            results = self.repository.get_all()
        
        return [self._entity_to_dto(product) for product in results]
    
    def create_product(self, product_dto: ProductDTO) -> ProductDTO:
        """
        Crea un nuevo producto en el repositorio.
        
        Args:
            product_dto: DTO con los datos del nuevo producto.
                        El ID debe ser None (será asignado por el repositorio).
            
        Retorna:
            ProductDTO: El producto creado con su ID asignado.
            
        Raises:
            InvalidProductDataError: Si los datos del producto son inválidos.
        """
        try:
            # Convierte el DTO a entidad del dominio
            product_entity = self._dto_to_entity(product_dto)
            
            # Guarda en el repositorio
            saved_product = self.repository.save(product_entity)
            
            # Convierte la entidad guardada a DTO
            return self._entity_to_dto(saved_product)
        
        except ValueError as e:
            raise InvalidProductDataError(message=str(e))
    
    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """
        Actualiza un producto existente.
        
        Args:
            product_id: ID del producto a actualizar.
            product_dto: DTO con los nuevos datos del producto.
            
        Retorna:
            ProductDTO: El producto actualizado.
            
        Raises:
            ProductNotFoundError: Si el producto no existe.
            InvalidProductDataError: Si los datos son inválidos.
        """
        # Verifica que el producto existe
        existing_product = self.repository.get_by_id(product_id)
        if existing_product is None:
            raise ProductNotFoundError(product_id=product_id)
        
        try:
            # Asigna el ID al DTO para mantener la identidad
            product_dto.id = product_id
            
            # Convierte a entidad
            product_entity = self._dto_to_entity(product_dto)
            
            # Guarda la actualización
            updated_product = self.repository.save(product_entity)
            
            return self._entity_to_dto(updated_product)
        
        except ValueError as e:
            raise InvalidProductDataError(message=str(e))
    
    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto del repositorio.
        
        Args:
            product_id: ID del producto a eliminar.
            
        Retorna:
            bool: True si el producto se eliminó, False si no existía.
            
        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        # Verifica que el producto existe antes de eliminar
        existing_product = self.repository.get_by_id(product_id)
        if existing_product is None:
            raise ProductNotFoundError(product_id=product_id)
        
        # Elimina del repositorio
        return self.repository.delete(product_id)
    
    def get_available_products(self) -> List[ProductDTO]:
        """
        Obtiene solo los productos que tienen stock disponible.
        
        Retorna:
            List[ProductDTO]: Lista de productos con stock > 0.
        """
        all_products = self.repository.get_all()
        
        # Filtra solo productos disponibles
        available_products = [p for p in all_products if p.is_available()]
        
        return [self._entity_to_dto(product) for product in available_products]
    
    def reduce_product_stock(self, product_id: int, quantity: int) -> ProductDTO:
        """
        Reduce el stock de un producto.
        
        Args:
            product_id: ID del producto.
            quantity: Cantidad a reducir del stock.
            
        Retorna:
            ProductDTO: El producto con stock actualizado.
            
        Raises:
            ProductNotFoundError: Si el producto no existe.
            InvalidProductDataError: Si hay error al reducir stock.
        """
        product = self.repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id=product_id)
        
        try:
            # Reduce el stock usando el método del dominio
            product.reduce_stock(quantity)
            
            # Guarda los cambios
            updated_product = self.repository.save(product)
            
            return self._entity_to_dto(updated_product)
        
        except ValueError as e:
            raise InvalidProductDataError(message=str(e))
    
    def increase_product_stock(self, product_id: int, quantity: int) -> ProductDTO:
        """
        Aumenta el stock de un producto.
        
        Args:
            product_id: ID del producto.
            quantity: Cantidad a aumentar al stock.
            
        Retorna:
            ProductDTO: El producto con stock actualizado.
            
        Raises:
            ProductNotFoundError: Si el producto no existe.
            InvalidProductDataError: Si hay error al aumentar stock.
        """
        product = self.repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id=product_id)
        
        try:
            # Aumenta el stock usando el método del dominio
            product.increase_stock(quantity)
            
            # Guarda los cambios
            updated_product = self.repository.save(product)
            
            return self._entity_to_dto(updated_product)
        
        except ValueError as e:
            raise InvalidProductDataError(message=str(e))
    
    # Métodos privados para conversión entre entidades y DTOs
    
    def _entity_to_dto(self, product: Product) -> ProductDTO:
        """
        Convierte una entidad de dominio a DTO.
        
        Args:
            product: Entidad Product del dominio.
            
        Retorna:
            ProductDTO: DTO listo para enviar a la presentación.
        """
        return ProductDTO(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description
        )
    
    def _dto_to_entity(self, dto: ProductDTO) -> Product:
        """
        Convierte un DTO a entidad de dominio.
        
        Args:
            dto: DTO con los datos del producto.
            
        Retorna:
            Product: Entidad del dominio lista para persistir.
        """
        return Product(
            id=dto.id,
            name=dto.name,
            brand=dto.brand,
            category=dto.category,
            size=dto.size,
            color=dto.color,
            price=dto.price,
            stock=dto.stock,
            description=dto.description
        )