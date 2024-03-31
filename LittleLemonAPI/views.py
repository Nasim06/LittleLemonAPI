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

# Create your views here.

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated ,IsAdminUser]


class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

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
    serializer_class = ManagerGroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    http_method_names = ['get', 'post', 'delete']


    def create(self, request, *args, **kwargs):
        username = self.request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='manager')
            managers.user_set.add(user)
            return Response("User added to the manager group")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user = get_object_or_404(User, pk=pk)
            managers = Group.objects.get(name='manager')
            managers.user_set.remove(user)
            return Response("User was removed from the manager group")
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

class DeliveryCrewView(viewsets.ModelViewSet):
    queryset = User.objects.filter(groups__name='delivery-crew')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsManager]
    http_method_names = ['get', 'post', 'delete']


    def create(self, request, *args, **kwargs):
        username = self.request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            deliveryCrew = Group.objects.get(name='delivery-crew')
            deliveryCrew.user_set.add(user)
            return Response("User added to the delivery crew")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user = get_object_or_404(User, pk=pk)
            deliveryCrew = Group.objects.get(name='delivery-crew')
            deliveryCrew.user_set.remove(user)
            return Response("User was removed from the delivery crew")
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
