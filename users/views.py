from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from maintenance.utils import create_audit_log

from .forms import LoginForm, UserForm
from .mixins import RoleRequiredMixin
from .models import User


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Connexion réussie.")
        return super().form_valid(form)


class CustomLogoutView(View):
    def get(self, request):
        auth_logout(request)
        messages.success(request, "Déconnexion réussie.")
        return redirect("users:login")

    def post(self, request):
        return self.get(request)


class UserListView(RoleRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    allowed_roles = ["admin"]

    def get_queryset(self):
        queryset = User.objects.all()
        q = self.request.GET.get("q", "").strip()
        role = self.request.GET.get("role", "").strip()
        if q:
            queryset = queryset.filter(Q(full_name__icontains=q) | Q(email__icontains=q))
        if role:
            queryset = queryset.filter(role=role)
        return queryset


class UserCreateView(RoleRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:list")
    allowed_roles = ["admin"]

    def form_valid(self, form):
        response = super().form_valid(form)
        create_audit_log(
            user=self.request.user,
            action="create",
            model_name="User",
            object_id=self.object.pk,
            details={"email": self.object.email, "full_name": self.object.full_name},
        )
        messages.success(self.request, "Utilisateur ajouté avec succès.")
        return response


class UserUpdateView(RoleRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:list")
    allowed_roles = ["admin"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["password"].help_text = "Renseigner uniquement pour changer le mot de passe."
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        create_audit_log(
            user=self.request.user,
            action="update",
            model_name="User",
            object_id=self.object.pk,
            details={"email": self.object.email, "full_name": self.object.full_name},
        )
        messages.success(self.request, "Utilisateur mis à jour.")
        return response


class UserDeleteView(RoleRequiredMixin, DeleteView):
    model = User
    template_name = "common/confirm_delete.html"
    success_url = reverse_lazy("users:list")
    allowed_roles = ["admin"]

    def dispatch(self, request, *args, **kwargs):
        if self.get_object() == request.user:
            messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
            return redirect("users:list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        request = self.request
        self.object = self.get_object()
        if self.object == request.user:
            return redirect("users:list")
        create_audit_log(
            user=request.user,
            action="delete",
            model_name="User",
            object_id=self.object.pk,
            details={"email": self.object.email, "full_name": self.object.full_name},
        )
        messages.success(request, "Utilisateur supprimé.")
        return super().form_valid(form)
