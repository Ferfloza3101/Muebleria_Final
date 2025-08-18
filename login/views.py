from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import re
from usuarios.models import Perfil

# Create your views here.

def user_login(request):
    mensaje = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            mensaje = 'Usuario o contraseña incorrectos'
    return render(request, 'login/login.html', {'mensaje': mensaje or 'Ingrese sus credenciales'})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login:login')

# Vista principal (home)
def home(request):
    return render(request, 'base.html')

# Vista de registro de usuario
def registro(request):
    mensaje = ''
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        correo = request.POST.get('correo', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        fecha_nacimiento = request.POST.get('fecha_nacimiento', '')
        genero = request.POST.get('genero', '')
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()

        # Validaciones
        if not all([nombre, apellidos, correo, username, password, fecha_nacimiento, genero, direccion, telefono]):
            mensaje = 'Todos los campos son obligatorios.'
        elif User.objects.filter(username=username).exists():
            mensaje = 'El nombre de usuario ya está en uso.'
        elif User.objects.filter(email=correo).exists():
            mensaje = 'El correo ya está registrado.'
        elif len(password) < 8:
            mensaje = 'La contraseña debe tener al menos 8 caracteres.'
        elif not re.search(r'[A-Z]', password):
            mensaje = 'La contraseña debe tener al menos una letra mayúscula.'
        elif not re.search(r'[^A-Za-z0-9]', password):
            mensaje = 'La contraseña debe tener al menos un carácter especial.'
        elif genero not in ['masculino', 'femenino']:
            mensaje = 'Selecciona un género válido.'
        else:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                password=password,
                email=correo,
                first_name=nombre,
                last_name=apellidos
            )
            # Crear perfil con datos extra
            Perfil.objects.create(
                user=user,
                fecha_nacimiento=fecha_nacimiento,
                genero=genero,
                telefono=telefono
            )
            return redirect('login:login')
    return render(request, 'login/registro.html', {'mensaje': mensaje})
