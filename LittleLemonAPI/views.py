from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import MenuItem, Cart, Category, Order, OrderItem
from .serializers import *
from .permissions import IsManager, IsDeliveryCrew
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User, Group
import math
from datetime import date

# Create your views here.


class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
             permission_classes = [IsAuthenticated]
        return[permission() for permission in permission_classes]



class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        category = self.request.query_params.get('category')
        if category:
            queryset = self.queryset.filter(category__title = category)
        else:
            queryset = self.queryset
        return queryset

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            if self.request.method == 'PATCH':
                permission_classes = [IsAuthenticated, IsAdminUser | IsManager]
            else:
                permission_classes = [IsAuthenticated, IsAdminUser]
        return[permission() for permission in permission_classes]



class ManagerView(viewsets.ModelViewSet):
    queryset = User.objects.filter(groups__name='manager')
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    http_method_names = ['get', 'post', 'delete']

    def create(self, request, *args, **kwargs):
        username = self.request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='manager')
            managers.user_set.add(user)
            return Response(user.username + " added to the manager group")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user = get_object_or_404(User, pk=pk)
            managers = Group.objects.get(name='manager')
            managers.user_set.remove(user)
            return Response(user.username + " was removed from the manager group")
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        


class DeliveryCrewView(viewsets.ModelViewSet):
    queryset = User.objects.filter(groups__name='delivery-crew')
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsManager]
    http_method_names = ['get', 'post', 'delete']

    def create(self, request, *args, **kwargs):
        username = self.request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            deliveryCrew = Group.objects.get(name='delivery-crew')
            deliveryCrew.user_set.add(user)
            return Response(user.username + " added to the delivery crew")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user = get_object_or_404(User, pk=pk)
            deliveryCrew = Group.objects.get(name='delivery-crew')
            deliveryCrew.user_set.remove(user)
            return Response(user.username + " was removed from the delivery crew")
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        


class CartView(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Cart.objects.filter(user=self.request.user)
        return queryset
    
    def create(self, request, *arg, **kwargs):
        itemData = AddToCartSerializer(data=request.data)
        itemData.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=price, menuitem_id=id)
        except:
            return Response(status=status.HTTP_409_CONFLICT, data={'Item already present in cart'})
        return Response(status=status.HTTP_201_CREATED, data={item.title + ' added to cart'})

    def destroy(self, request, *arg, **kwargs):
        id = self.kwargs.get('pk') 
        if id:
            cart = get_object_or_404(Cart, user=request.user, menuitem=id)
            cart.delete()
            return Response(status=200, data={'Item removed from cart'})
        else:
            Cart.objects.filter(user=request.user).delete()
            return Response(status=201, data={'Cart is empty'})
        


class OrderView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
        
    def get_queryset(self):
        if self.request.user.groups.filter(name='manager').exists() or self.request.user.is_superuser == True :
            query = Order.objects.all()
        elif self.request.user.groups.filter(name='delivery-crew').exists():
            query = Order.objects.filter(delivery_crew=self.request.user)
        else:
            query = Order.objects.filter(user=self.request.user)
        return query

    def get_permissions(self):
        if self.request.method == 'GET' or 'POST' : 
            permission_classes = [IsAuthenticated]
        if self.request.method == 'PATCH':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser | IsDeliveryCrew]
        if self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

        return[permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)

        x = cart.values_list()
        if len(x) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'Your cart is empty'})

        total = math.fsum([float(x[-1]) for x in x])
        userOrder = Order.objects.create(user=request.user, delivery_crew=None, status=False, total=total, date=date.today())

        for item in cart.values():
            menuitem = get_object_or_404(MenuItem, id=item['menuitem_id'])
            orderitem = OrderItem.objects.create(order=userOrder, menuitem=menuitem, quantity=item['quantity'], unit_price=item['unit_price'], price=item['price'])
            orderitem.save()

        cart.delete()
        return Response(status=status.HTTP_201_CREATED, data={'Your order has been placed! Your order number is {}'.format(str(userOrder.id))})
    
    def update(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        if self.request.user.groups.filter(name='manager').exists() == True:
            delivery_crew = request.data['delivery-crew']
            if delivery_crew:
                deliverers = User.objects.filter(groups__name='delivery-crew')
                deliverer = get_object_or_404(deliverers, username=delivery_crew)
                order.delivery_crew = deliverer
                order.save()
            return Response("order assigned to delivery crew")
        if self.request.user.groups.filter(name='delivery-crew').exists() == True:
            order.status = not order.status
            order.save()
            if order.status == True:
                return Response("order marked as delivered")
            return Response("order marked as not delivered")

             

        
            

        