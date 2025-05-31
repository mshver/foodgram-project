from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from api.filters import DishFilter, ComponentFilter
from api.models import ShoppingCart, Bookmark, Component, ComponentQuantity, Dish, Category
from api.pagination import CustomPagination
from api.permissions import AdminOrRead, CreatorOnly
from api.serializers import DishPreviewSerializer, ComponentSerializer, DishSerializer, CategorySerializer

class CategoriesView(ReadOnlyModelViewSet):
    permission_classes = (AdminOrRead,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ComponentsView(ReadOnlyModelViewSet):
    permission_classes = (AdminOrRead,)
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    filter_backends = (ComponentFilter,)
    search_fields = ('^title',)

class DishView(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    pagination_class = CustomPagination
    filter_class = DishFilter
    permission_classes = [CreatorOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        if request.method == 'POST':
            return self.manage_model(Bookmark, request.user, pk)
        elif request.method == 'DELETE':
            return self.remove_model(Bookmark, request.user, pk)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def cart(self, request, pk=None):
        if request.method == 'POST':
            return self.manage_model(ShoppingCart, request.user, pk)
        elif request.method == 'DELETE':
            return self.remove_model(ShoppingCart, request.user, pk)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def export_cart(self, request):
        cart_items = {}
        ingredients = ComponentQuantity.objects.filter(
            dish__cart_items__user=request.user
        ).values_list('component__title', 'component__unit', 'quantity')
        
        for name, unit, amount in ingredients:
            if name not in cart_items:
                cart_items[name] = {'unit': unit, 'total': amount}
            else:
                cart_items[name]['total'] += amount
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'
        
        pdf = canvas.Canvas(response)
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        pdf.setFont('Arial', 24)
        pdf.drawString(100, 800, 'Список покупок')
        pdf.setFont('Arial', 16)
        
        y_position = 750
        for idx, (name, data) in enumerate(cart_items.items(), start=1):
            pdf.drawString(80, y_position, f"{idx}. {name} - {data['total']} {data['unit']}")
            y_position -= 25
        
        pdf.showPage()
        pdf.save()
        return response

    def manage_model(self, model, user, dish_id):
        if model.objects.filter(user=user, dish_id=dish_id).exists():
            return Response(
                {'error': 'Рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        dish = get_object_or_404(Dish, id=dish_id)
        model.objects.create(user=user, dish=dish)
        return Response(
            DishPreviewSerializer(dish).data,
            status=status.HTTP_201_CREATED
        )

    def remove_model(self, model, user, dish_id):
        obj = model.objects.filter(user=user, dish_id=dish_id)
        if not obj.exists():
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)