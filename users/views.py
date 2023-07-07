
# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework import generics, status

from .serializers import UserSerializer


class UserCreateView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            user_id = response.data.get('id')
            send_welcome_email_delayed(user_id)
        return response
