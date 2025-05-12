from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

from .models import User, Category, Product, Order
from .serializers import (
    UserSerializer, 
    CategorySerializer, 
    ProductSerializer, 
    OrderSerializer
)
from .permissions import IsAdmin, IsSeller, IsCustomer


# 1. Auth endpoints
class RegisterView(viewsets.GenericViewSet, viewsets.mixins.CreateModelMixin):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Register a new user",
        responses={201: UserSerializer},
        tags=["Authentication"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class JWTView(TokenObtainPairView):
    """
    API endpoint for obtaining JWT tokens.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        description="Obtain JWT token pair",
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# 2. Category CRUD (Admin only)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for category management (admin only).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated & IsAdmin]
    
    @extend_schema(
        description="List all categories",
        responses={200: CategorySerializer(many=True)},
        tags=["Categories"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        description="Retrieve a category",
        responses={200: CategorySerializer},
        tags=["Categories"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Create a new category (admin only)",
        request=CategorySerializer,
        responses={201: CategorySerializer},
        tags=["Categories"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        description="Update a category (admin only)",
        request=CategorySerializer,
        responses={200: CategorySerializer},
        tags=["Categories"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        description="Partially update a category (admin only)",
        request=CategorySerializer,
        responses={200: CategorySerializer},
        tags=["Categories"]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        description="Delete a category (admin only)",
        responses={204: None},
        tags=["Categories"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# 3. Product CRUD
class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for product management. 
    - Admins can see all products
    - Sellers can only see their own products
    - Customers can view all products but not create/edit
    """
    queryset = Product.objects.select_related('category', 'seller')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category__id']
    search_fields = ['name']
    
    def get_permissions(self):
        if not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
            return [IsAuthenticated()]
            
        if hasattr(self.request.user, 'role'):
            if self.request.user.role == 'admin':
                return [IsAuthenticated(), IsAdmin()]
            if self.request.user.role == 'seller':
                return [IsAuthenticated(), IsSeller()]
                
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Handle schema generation with AnonymousUser
        if not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
            return qs
            
        if hasattr(self.request.user, 'role'):
            if self.request.user.role == 'seller':
                return qs.filter(seller=self.request.user)
                
        return qs
    
    @extend_schema(
        description="List all products (filtered by seller for seller users)",
        parameters=[
            OpenApiParameter(name="category__id", type=int, description="Filter by category ID"),
            OpenApiParameter(name="search", type=str, description="Search products by name")
        ],
        responses={200: ProductSerializer(many=True)},
        tags=["Products"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        description="Retrieve a product",
        responses={200: ProductSerializer},
        tags=["Products"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Create a new product (seller and admin only)",
        request=ProductSerializer,
        responses={201: ProductSerializer},
        tags=["Products"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        description="Update a product (seller can only update their own)",
        request=ProductSerializer,
        responses={200: ProductSerializer},
        tags=["Products"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        description="Partially update a product (seller can only update their own)",
        request=ProductSerializer,
        responses={200: ProductSerializer},
        tags=["Products"]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        description="Delete a product (seller can only delete their own)",
        responses={204: None},
        tags=["Products"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# 4. Orders
class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for order management.
    - Customers can create orders
    - All authenticated users can view orders (filtered by role)
    - Admins can update, mark as paid, etc.
    """
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'items__product__category__id': ['exact'],
        'items__product__id': ['exact'],
        'created_at': ['gte', 'lte']
    }
    
    def get_permissions(self):
        """
        - create → only Customers
        - list/retrieve → any authenticated user
        - mark_paid (and other unsafe ops) → Admin only
        """
        if self.action == 'create':
            perms = [IsAuthenticated, IsCustomer]
        elif self.action in ('list', 'retrieve'):
            perms = [IsAuthenticated]
        else:
            perms = [IsAuthenticated, IsAdmin]
        
        # Create actual permission instances
        return [p() for p in perms]
        
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Handle schema generation with AnonymousUser
        if not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
            return qs
            
        # Filter based on user role if applicable
        if hasattr(self.request.user, 'role'):
            if self.request.user.role == 'customer':
                return qs.filter(customer=self.request.user)
            elif self.request.user.role == 'seller':
                return qs.filter(items__product__seller=self.request.user).distinct()
                
        # Admin sees all orders
        return qs
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
    
    @extend_schema(
        description="List orders (filtered by user role)",
        parameters=[
            OpenApiParameter(name="items__product__category__id", type=int, description="Filter by product category ID"),
            OpenApiParameter(name="items__product__id", type=int, description="Filter by product ID"),
            OpenApiParameter(name="created_at__gte", type=str, description="Filter by date greater than or equal (YYYY-MM-DD)"),
            OpenApiParameter(name="created_at__lte", type=str, description="Filter by date less than or equal (YYYY-MM-DD)")
        ],
        responses={200: OrderSerializer(many=True)},
        tags=["Orders"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        description="Retrieve an order",
        responses={200: OrderSerializer},
        tags=["Orders"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Create a new order (customers only)",
        request=OrderSerializer,
        responses={201: OrderSerializer},
        tags=["Orders"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        description="Update an order (admin only)",
        request=OrderSerializer,
        responses={200: OrderSerializer},
        tags=["Orders"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        description="Partially update an order (admin only)",
        request=OrderSerializer,
        responses={200: OrderSerializer},
        tags=["Orders"]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        description="Delete an order (admin only)",
        responses={204: None},
        tags=["Orders"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        description="Mark an order as paid (admin only)",
        responses={
            200: OpenApiResponse(
                description="Order marked as paid",
                examples=[
                    OpenApiExample(
                        name="Success",
                        value={"status": "marked as paid"}
                    )
                ]
            )
        },
        tags=["Orders"]
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdmin])
    def mark_paid(self, request, pk=None):
        order = self.get_object()
        order.payment_status = Order.PAID
        order.save()
        return Response({'status': 'marked as paid'})