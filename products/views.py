import os
import threading
from io import BytesIO

from django.conf import settings
from PIL import Image
# Create your views here.
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem, Product
from .serializers import CartSerializer, ProductSerializer


class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get("category")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")

        if category:
            queryset = queryset.filter(category=category)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset


class ProductImageUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        image = request.FILES.get("image")
        product_id = request.data.get("product_id")

        if not product_id:
            return Response({"error": "Product ID is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response({"error": "Product not found"},
                            status=status.HTTP_404_NOT_FOUND)

        # Validate the image and perform any necessary checks
        # Save the image to the product instance
        product.image = image
        product.save()

        # Perform image processing in a separate thread
        thread = threading.Thread(target=self.process_image, args=(product,))
        thread.start()

        return Response({"message": "Image uploaded successfully"})

    def process_image(self, product):
        # Open the uploaded image using Pillow
        uploaded_file = product.image
        file = BytesIO(uploaded_file.read())

        # Open the image using the file-like object
        img = Image.open(file)

        # Generate and save thumbnail
        thumbnail_size = (100, 100)
        thumbnail = img.copy()
        thumbnail.thumbnail(thumbnail_size)

        # Get the base directory for media uploads
        media_root = settings.MEDIA_ROOT

        # Generate paths for thumbnail and full-size image
        thumbnail_path = os.path.join(media_root, product.image.name)

        # Save thumbnail
        thumbnail.save(thumbnail_path)

        # Update the product with the processed image paths
        product.thumbnail_image = os.path.relpath(thumbnail_path, media_root)
        product.save()


class CartView(APIView):
    def get(self, request, format=None):
        cart = Cart.objects.filter(user=request.user).first()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.get(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()
        return Response({"message": "Product added to cart"})

    def put(self, request, format=None):
        data = request.data
        cart_item_id = data.get("cart_item_id")
        quantity = int(data.get("quantity", 1))

        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Cart item quantity updated"})

    def delete(self, request, format=None):
        data = request.data
        cart_item_id = data.get("cart_item_id")

        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.delete()

        return Response({"message": "Cart item removed"})
