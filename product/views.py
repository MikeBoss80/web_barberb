from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.generic.edit import FormView
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from admin_module.utils.mixins import BreadcrumbMixin
from .models import Product, ProductCategory, StockMovement, ProductEstablishment
from .forms import (
    ProductForm, ProductCategoryForm, StockMovementForm, 
    QuickStockAdjustmentForm, LowStockReportForm
)
from .utils.inventory import InventoryManager, ProductCompositionManager


class ProductListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    """Lista de productos con filtros y búsqueda"""
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 25
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [{'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'}]
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Filtros
        search = self.request.GET.get('search', '')
        category_id = self.request.GET.get('category', '')
        product_type = self.request.GET.get('product_type', '')
        low_stock = self.request.GET.get('low_stock', '')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(internal_reference__icontains=search) |
                Q(barcode__icontains=search)
            )
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        
        if low_stock == 'true':
            # Filtrar productos con stock bajo
            low_stock_ids = []
            for product in queryset:
                if product.track_inventory and product.is_low_stock:
                    low_stock_ids.append(product.id)
            queryset = queryset.filter(id__in=low_stock_ids)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': ProductCategory.objects.filter(is_active=True),
            'search': self.request.GET.get('search', ''),
            'selected_category': self.request.GET.get('category', ''),
            'selected_type': self.request.GET.get('product_type', ''),
            'show_low_stock': self.request.GET.get('low_stock', ''),
        })
        return context


class ProductDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    """Detalle de un producto específico"""
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        product = self.get_object()
        return [
            {'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'},
            {'label': f'Producto: {product.name}', 'url': '', 'icon': 'eye'}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Obtener movimientos recientes
        recent_movements = StockMovement.objects.filter(
            product=product
        ).select_related('establishment', 'created_by').order_by('-created_at')[:10]
        
        # Obtener stock por establecimiento
        establishment_stocks = ProductEstablishment.objects.filter(
            product=product
        ).select_related('establishment')
        
        # Si es producto compuesto, obtener componentes
        components = []
        if product.product_type == 'composite':
            components = product.components.all().select_related('component_product')
        
        context.update({
            'recent_movements': recent_movements,
            'establishment_stocks': establishment_stocks,
            'components': components,
            'total_composition_cost': ProductCompositionManager.calculate_total_cost(product),
        })
        return context


class ProductCreateView(LoginRequiredMixin, BreadcrumbMixin, SuccessMessageMixin, CreateView):
    """Crear un nuevo producto"""
    model = Product
    form_class = ProductForm
    template_name = 'product/form_product.html'
    success_url = reverse_lazy('product:product_list')
    success_message = "Producto '%(name)s' creado exitosamente."
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [
            {'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'},
            {'label': 'Crear Producto', 'url': '', 'icon': 'plus-circle'}
        ]
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Si es petición AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Producto "{self.object.name}" creado exitosamente.',
                'redirect_url': str(self.success_url)
            })
        return response
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        
        # Si es petición AJAX, retornar errores
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formProductTitle'] = 'Agregar Producto'
        return context
    
    def get_template_names(self):
        # Si es una petición AJAX, retornar solo el formulario
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['product/form_product.html']
        return super().get_template_names()


class ProductUpdateView(LoginRequiredMixin, BreadcrumbMixin, SuccessMessageMixin, UpdateView):
    """Editar un producto existente"""
    model = Product
    form_class = ProductForm
    template_name = 'product/form_product.html'
    success_url = reverse_lazy('product:product_list')
    success_message = "Producto '%(name)s' actualizado exitosamente."
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        product = self.get_object()
        return [
            {'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'},
            {'label': f'Editar: {product.name}', 'url': '', 'icon': 'pencil-square'}
        ]
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        
        # Si es petición AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Producto "{self.object.name}" actualizado exitosamente.',
                'redirect_url': str(self.success_url)
            })
        return response
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        
        # Si es petición AJAX, retornar errores
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formProductTitle'] = f'Editar Producto: {self.object.name}'
        return context
    
    def get_template_names(self):
        # Si es una petición AJAX, retornar solo el formulario
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['product/form_product.html']
        return super().get_template_names()


class ProductDeleteView(LoginRequiredMixin, BreadcrumbMixin, DeleteView):
    """Eliminar producto (soft delete)"""
    model = Product
    success_url = reverse_lazy('product:product_list')
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        product = self.get_object()
        return [
            {'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'},
            {'label': f'Eliminar: {product.name}', 'url': '', 'icon': 'trash'}
        ]
    
    def delete(self, request, *args, **kwargs):
        """Realizar soft delete en lugar de eliminar físicamente"""
        self.object = self.get_object()
        product_name = self.object.name
        self.object.is_active = False
        self.object.updated_by = request.user
        self.object.save()
        
        # Si es petición AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Producto "{product_name}" eliminado exitosamente.',
                'redirect_url': str(self.success_url)
            })
        
        messages.success(request, f'Producto "{product_name}" eliminado exitosamente.')
        return redirect(self.success_url)


class StockMovementListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    """Lista de movimientos de inventario"""
    model = StockMovement
    template_name = 'product/movimientos_list.html'
    context_object_name = 'movements'
    paginate_by = 50
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [
            {'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'},
            {'label': 'Movimientos', 'url': reverse('product:stock_movement_list'), 'icon': 'arrow-left-right'}
        ]
    
    def get_queryset(self):
        queryset = StockMovement.objects.all().select_related(
            'product', 'establishment', 'created_by'
        ).order_by('-created_at')
        
        # Filtros
        product_id = self.request.GET.get('product', '')
        establishment_id = self.request.GET.get('establishment', '')
        movement_type = self.request.GET.get('movement_type', '')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        if establishment_id:
            queryset = queryset.filter(establishment_id=establishment_id)
        
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'selected_product': self.request.GET.get('product', ''),
            'selected_establishment': self.request.GET.get('establishment', ''),
            'selected_movement_type': self.request.GET.get('movement_type', ''),
        })
        return context


class StockMovementCreateView(LoginRequiredMixin, BreadcrumbMixin, SuccessMessageMixin, CreateView):
    """Crear un nuevo movimiento de inventario"""
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'product/movement_form.html'
    success_url = reverse_lazy('product:stock_movement_list')
    success_message = "Movimiento de inventario registrado exitosamente."
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [
            {'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'},
            {'label': 'Movimientos', 'url': reverse('product:stock_movement_list'), 'icon': 'arrow-left-right'},
            {'label': 'Nuevo Movimiento', 'url': '', 'icon': 'plus-circle'}
        ]
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Actualizar stock por establecimiento
        InventoryManager.update_establishment_stock(
            self.object.product, 
            self.object.establishment
        )
        
        return response


class QuickStockAdjustmentView(LoginRequiredMixin, BreadcrumbMixin, FormView):
    """Ajuste rápido de inventario"""
    form_class = QuickStockAdjustmentForm
    template_name = 'product/quick_adjustment.html'
    success_url = reverse_lazy('product:product_list')
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [
            {'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'},
            {'label': 'Ajuste Rápido', 'url': '', 'icon': 'sliders'}
        ]
    
    def form_valid(self, form):
        product = form.cleaned_data['product']
        establishment = form.cleaned_data['establishment']
        new_stock = form.cleaned_data['new_stock']
        reason = form.cleaned_data['reason'] or 'Ajuste rápido'
        
        try:
            movement = InventoryManager.adjust_stock(
                product=product,
                establishment=establishment,
                new_quantity=new_stock,
                reason='inventory_adjustment',
                notes=reason,
                user=self.request.user
            )
            
            if movement:
                messages.success(self.request, f'Stock ajustado para {product.name}.')
            else:
                messages.info(self.request, 'No se detectaron cambios en el stock.')
                
        except ValueError as e:
            messages.error(self.request, str(e))
        
        return super().form_valid(form)


class LowStockReportView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    """Reporte de productos con stock bajo"""
    template_name = 'product/low_stock_report.html'
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [
            {'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'},
            {'label': 'Reporte Stock Bajo', 'url': '', 'icon': 'exclamation-triangle'}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        form = LowStockReportForm(self.request.GET or None)
        low_stock_products = []
        
        if form and form.is_valid():
            establishment = form.cleaned_data.get('establishment')
            category = form.cleaned_data.get('category')
            
            low_stock_products = InventoryManager.get_low_stock_products(
                establishment=establishment,
                category=category
            )
        
        context.update({
            'form': form,
            'low_stock_products': low_stock_products,
        })
        return context


class CategoryListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    """Lista de categorías de productos"""
    model = ProductCategory
    template_name = 'product/category_list.html'
    context_object_name = 'categories'
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [
            {'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'},
            {'label': 'Categorías', 'url': reverse('product:category_list'), 'icon': 'tags'}
        ]
    
    def get_queryset(self):
        return ProductCategory.objects.filter(is_active=True).order_by('name')


class CategoryCreateView(LoginRequiredMixin, BreadcrumbMixin, SuccessMessageMixin, CreateView):
    """Crear nueva categoría"""
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = 'product/category_form.html'
    success_url = reverse_lazy('product:category_list')
    success_message = "Categoría '%(name)s' creada exitosamente."
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [
            {'label': 'Inventario', 'url': reverse('product:product_list'), 'icon': 'box-seam'},
            {'label': 'Categorías', 'url': reverse('product:category_list'), 'icon': 'tags'},
            {'label': 'Nueva Categoría', 'url': '', 'icon': 'plus-circle'}
        ]


# Vista AJAX para obtener stock de productos
class GetProductStockAjaxView(LoginRequiredMixin, View):
    """API AJAX para obtener el stock actual de un producto"""
    
    def get(self, request, product_id, establishment_id):
        try:
            product = Product.objects.get(pk=product_id)
            from establishment.models import Establishment
            establishment = Establishment.objects.get(pk=establishment_id)
            
            current_stock = InventoryManager.get_current_stock(product, establishment)
            
            return JsonResponse({
                'success': True,
                'current_stock': float(current_stock),
                'unit_of_measure': product.unit_of_measure,
                'minimum_stock': product.minimum_stock,
            })
        except (Product.DoesNotExist, Exception) as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
