from django.urls import path

from .views import (
    CustomLoginView,
    CustomLogoutView,
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserUpdateView,
)


app_name = "users"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("utilisateurs/", UserListView.as_view(), name="list"),
    path("utilisateurs/ajouter/", UserCreateView.as_view(), name="create"),
    path("utilisateurs/<int:pk>/modifier/", UserUpdateView.as_view(), name="update"),
    path("utilisateurs/<int:pk>/supprimer/", UserDeleteView.as_view(), name="delete"),
]
