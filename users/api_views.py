from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from maintenance.utils import create_audit_log

from .models import User
from .permissions import UserManagementPermission
from .serializers import (
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    MeSerializer,
    PublicUserSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [UserManagementPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()

        if not user.is_authenticated:
            return queryset.none()

        if user.role == User.Role.ADMIN:
            return queryset

        if user.role == User.Role.RESPONSABLE:
            return queryset.filter(
                Q(pk=user.pk) | Q(is_active=True, role__in=[User.Role.RESPONSABLE, User.Role.OPERATEUR, User.Role.TECHNICIEN])
            ).distinct()

        if user.role == User.Role.OPERATEUR:
            return queryset.filter(Q(pk=user.pk) | Q(is_active=True, role=User.Role.TECHNICIEN)).distinct()

        if user.role == User.Role.TECHNICIEN:
            return queryset.filter(pk=user.pk)

        return queryset.none()

    def get_serializer_class(self):
        if self.request.user.is_authenticated and self.request.user.role != User.Role.ADMIN and self.action in ["list", "retrieve"]:
            return PublicUserSerializer
        return UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        create_audit_log(
            user=self.request.user,
            action="create",
            model_name="User",
            object_id=user.pk,
            details={"email": user.email, "full_name": user.full_name},
        )

    def perform_update(self, serializer):
        user = serializer.save()
        create_audit_log(
            user=self.request.user,
            action="update",
            model_name="User",
            object_id=user.pk,
            details={"email": user.email, "full_name": user.full_name},
        )

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {"detail": "Vous ne pouvez pas supprimer votre propre compte."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        create_audit_log(
            user=request.user,
            action="delete",
            model_name="User",
            object_id=user.pk,
            details={"email": user.email, "full_name": user.full_name},
        )
        return super().destroy(request, *args, **kwargs)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if response.status_code == 200 and user:
            create_audit_log(
                user=user,
                action="login",
                model_name="User",
                object_id=user.pk,
                details={"message": "Connexion API JWT"},
            )
        return response


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        create_audit_log(
            user=request.user,
            action="logout",
            model_name="User",
            object_id=request.user.pk,
            details={"message": "Déconnexion API JWT"},
        )
        return Response({"detail": "Déconnexion réussie."}, status=status.HTTP_200_OK)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data)
