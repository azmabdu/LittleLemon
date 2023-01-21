from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import *
from .serializers import *
from .permissions import *
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404


class CategoryView(APIView):
    permission_classes = [IsAdminUser|IsManager|ReadOnly|IsCustomerSafeMethod]

    def get(self, request):
        categories = Category.objects.all()
        serializers = CategorySerializer(categories, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializers = CategorySerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)


class MenuItemView(APIView):
    permission_classes = [IsAdminUser|IsManager|ReadOnly|IsCustomerSafeMethod]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [OrderingFilter, SearchFilter]
    filterset_fields = ['category', 'price', 'featured', 'title']
    ordering_fields = ['id', 'price', 'title']
    search_fields = ['category__title', 'title']

    def get(self, request):
        menuitems = MenuItem.objects.select_related('category').all()
        serializers = MenuItemSerializer(menuitems, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializers = MenuItemSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)


class SingleMenuItem(APIView):
    permission_classes = [IsAdminUser|IsManager|ReadOnly|IsCustomerSafeMethod]

    def get(self, request, id):
        menuitem = MenuItem.objects.select_related('category').get(id=id)
        serializers = MenuItemSerializer(menuitem, many=False)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        menuitem = MenuItem.objects.select_related('category').get(id=id)
        serializers = MenuItemSerializer(instance=menuitem, data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        menuitem = MenuItem.objects.select_related('category').get(id=id)
        serializers = MenuItemSerializer(instance=menuitem, data=request.data, partial=True)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        menuitem = MenuItem.objects.select_related('category').get(id=id)
        menuitem.delete()
        return Response("Deleted", status=status.HTTP_200_OK)


class CartView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        carts = Cart.objects.filter(user=request.user)
        if not carts.exists():
            return Response('No Cart', status=status.HTTP_404_NOT_FOUND)

        cart = carts.select_related('menuitem').filter(user=request.user)
        serializers = CartSerializer(cart, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializers = CartSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        id = serializers.validated_data['menuitem_id']
        menuitem = MenuItem.objects.get(id=id)
        quantity = serializers.validated_data['quantity']
        serializers.validated_data['menuitem'] = menuitem
        serializers.validated_data['unit_price'] = menuitem.price
        serializers.validated_data['price'] = quantity * menuitem.price
        serializers.validated_data['user'] = request.user
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        carts = Cart.objects.filter(user=request.user)
        carts.delete()
        return Response("Deleted", status=status.HTTP_200_OK)


class ManagerView(APIView):
    permission_classes = [IsManager|IsAdminUser]

    def get(self, request):
        managers = User.objects.filter(groups__name='Manager')
        serializers = UserSerializer(managers, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        username = request.POST.get('username')

        if username and User.objects.filter(username=username).exists():
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            serializers = UserSerializer(user)
            return Response(serializers.data, status=status.HTTP_201_CREATED)

        return Response("Username Required", status=status.HTTP_400_BAD_REQUEST)


class SingleManagerView(APIView):
    permission_classes = [IsManager|IsAdminUser]

    def delete(self, request, id):
        user = User.objects.get(id=id)
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)

        return Response(f"{user} Removed", status=status.HTTP_200_OK)


class DeliveryCrewView(APIView):
    permission_classes = [IsManager|IsAdminUser]

    def get(self, request):
        delivery_crew = User.objects.filter(groups__name='Delivery Crew')
        serializers = UserSerializer(delivery_crew, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        username = request.POST.get('username')

        if username and User.objects.filter(username=username).exists():
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name='Delivery Crew')
            delivery_crew.user_set.add(user)
            serializers = UserSerializer(user)
            return Response(serializers.data, status=status.HTTP_201_CREATED)

        return Response("Username Required", status=status.HTTP_400_BAD_REQUEST)


class SingleDeliveryCrewView(APIView):
    permission_classes = [IsManager|IsAdminUser]

    def delete(self, request, id):
        user = User.objects.get(id=id)
        delivery_crew = Group.objects.get(name='Delivery Crew')
        delivery_crew.user_set.remove(user)
        return Response(f"{user} Removed", status=status.HTTP_200_OK)


class OrderView(APIView):
    def get(self, request):
        if request.user.groups.filter(name="Manager").exists():
            orders = Order.objects.all()
            serializers = OrderSerializer(orders, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)

        if request.user.groups.filter(name="Delivery Crew").exists():
            orders = Order.objects.filter(delivery_crew=request.user)
            serializers = OrderSerializer(orders, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)

        if not request.user.groups.exists():
            orders = Order.objects.filter(user=request.user)
            serializers = OrderSerializer(orders, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        if not user.groups.exists() and Cart.objects.filter(user=user):
            serializers = OrderSerializer(data=request.data)
            serializers.is_valid(raise_exception=True)
            serializers.validated_data['user'] = request.user
            serializers.validated_data['status'] = 0
            serializers.validated_data['total'] = 0
            serializers.save()

            order = Order.objects.get(user=user)
            carts = Cart.objects.filter(user=user)
            for cart in carts:
                order.total += cart.price
                OrderItem.objects.create(
                    order=order,
                    menuitem=cart.menuitem,
                    quantity=cart.quantity,
                    unit_price=cart.unit_price,
                    price=cart.price,
                )
                cart.delete()
            order.save()
            return Response("Created", status=status.HTTP_201_CREATED)
        return Response("No Carts", status=status.HTTP_404_NOT_FOUND)


class SingleOrderView(APIView):
    def get(self, request, id):
        if not request.user.groups.exists() or request.user.groups.filter(name="Manager").exists() :
            order = Order.objects.get(id=id)
            serializers = OrderSerializer(order)
            return Response(serializers.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if request.user.groups.filter(name="Manager").exists():
            order = Order.objects.get(id=id)
            order.delete()
            return Response("Deleted")

    def put(self, request, id):
        if not request.user.groups.exists():
            order = Order.objects.get(id=id)
            serializers = OrderSerializer(instance=order, data=request.data)
            serializers.is_valid(raise_exception=True)
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        if not request.user.groups.exists():
            order = Order.objects.get(id=id)
            serializers = OrderSerializer(instance=order, data=request.data, partial=True)
            serializers.is_valid(raise_exception=True)
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)

        if request.user.groups.filter(name="Delivery Crew").exists() or request.user.groups.filter(name="Manager").exists():
            order = Order.objects.get(id=id)
            serializers = OrderSerializer(instance=order, data=request.data, partial=True)
            serializers.is_valid(raise_exception=True)
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)








