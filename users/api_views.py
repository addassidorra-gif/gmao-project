from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    RegistrationSerializer,
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

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response(
                {"detail": "Votre propre compte ne peut pas être validé depuis cette action."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.approval_status = User.ApprovalStatus.ACCEPTED
        user.is_active = True
        user.save(update_fields=["approval_status", "is_active"])
        create_audit_log(
            user=request.user,
            action="approve",
            model_name="User",
            object_id=user.pk,
            details={"email": user.email, "full_name": user.full_name},
        )
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response(
                {"detail": "Vous ne pouvez pas refuser votre propre compte."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.approval_status = User.ApprovalStatus.REJECTED
        user.is_active = False
        user.save(update_fields=["approval_status", "is_active"])
        create_audit_log(
            user=request.user,
            action="reject",
            model_name="User",
            object_id=user.pk,
            details={"email": user.email, "full_name": user.full_name},
        )
        return Response(UserSerializer(user).data)

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


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        create_audit_log(
            user=None,
            action="register",
            model_name="User",
            object_id=user.pk,
            details={"email": user.email, "full_name": user.full_name, "role": user.role},
        )
        return Response(
            {
                "detail": "Votre demande de compte a été envoyée. Un administrateur doit la valider.",
                "user": RegistrationSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


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
