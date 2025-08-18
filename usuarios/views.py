from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
import re
import json
from .models import Perfil, DireccionUsuario
from .forms import DireccionForm, EditarPerfilForm
from productos.models import Pedido
from django.template.loader import render_to_string

# vistas de usuarios

@login_required
def perfil(request):
    form_direccion = DireccionForm()
    mensaje = None
    errores = None
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, user=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            user = request.user
            user.first_name = cd['first_name']
            user.last_name = cd['last_name']
            user.email = cd['email']
            user.username = cd['username']
            if cd['password']:
                user.set_password(cd['password'])
            user.save()
            perfil, _ = Perfil.objects.get_or_create(user=user)
            perfil.fecha_nacimiento = cd['fecha_nacimiento']
            perfil.genero = cd['genero']
            perfil.telefono = cd['telefono']
            perfil.save()
            mensaje = 'Los cambios se realizaron correctamente.'
            form = EditarPerfilForm(user=user)  # Recargar con datos actualizados
        else:
            errores = form.errors
    else:
        form = EditarPerfilForm(user=request.user)
    return render(request, 'usuarios/perfil.html', {'form_direccion': form_direccion, 'usuario': request.user, 'form_perfil': form, 'mensaje': mensaje, 'errores': errores})

# Eliminar la vista editar_usuario

@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        actual = request.POST.get('actual')
        nueva = request.POST.get('nueva')
        confirmar = request.POST.get('confirmar')
        user = request.user
        errores = []
        # Validar contraseña actual
        if not user.check_password(actual):
            errores.append('La contraseña actual es incorrecta.')
        # Validar que la nueva no sea igual a la anterior
        if actual == nueva:
            errores.append('La nueva contraseña no puede ser igual a la anterior.')
        # Validar reglas de seguridad
        if len(nueva) < 8:
            errores.append('La contraseña debe tener al menos 8 caracteres.')
        if not re.search(r'[A-Z]', nueva):
            errores.append('Debe contener al menos una letra mayúscula.')
        if not re.search(r'[^A-Za-z0-9]', nueva):
            errores.append('Debe contener al menos un carácter especial.')
        if nueva != confirmar:
            errores.append('Las contraseñas no coinciden.')
        if errores:
            return render(request, 'usuarios/cambiar_contrasena.html', {'errores': errores})
        # Cambiar contraseña
        user.set_password(nueva)
        user.save()
        update_session_auth_hash(request, user)
        return render(request, 'usuarios/cambiar_contrasena.html', {'exito': True})
    return render(request, 'usuarios/cambiar_contrasena.html')

@login_required
def direcciones_lista(request):
    """Listar direcciones del usuario"""
    direcciones = DireccionUsuario.objects.filter(user=request.user)
    return JsonResponse({
        'direcciones': [
            {
                'id': dir.id,
                'nombre': dir.nombre,
                'calle': dir.calle,
                'numero_exterior': dir.numero_exterior,
                'numero_interior': dir.numero_interior,
                'colonia': dir.colonia,
                'ciudad': dir.ciudad,
                'estado': dir.estado,
                'codigo_postal': dir.codigo_postal,
                'telefono': dir.telefono,
                'referencias': dir.referencias,
                'principal': dir.principal,
                'direccion_completa': dir.get_direccion_completa(),
                'direccion_corta': dir.get_direccion_corta()
            } for dir in direcciones
        ]
    })

@login_required
def direccion_agregar(request):
    """Agregar nueva dirección"""
    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            try:
                # Verificar duplicados antes de guardar
                data = form.cleaned_data
                existe = DireccionUsuario.objects.filter(
                    user=request.user,
                    nombre=data['nombre'],
                    calle=data['calle'],
                    numero_exterior=data['numero_exterior'],
                    colonia=data['colonia'],
                    ciudad=data['ciudad'],
                    estado=data['estado'],
                    codigo_postal=data['codigo_postal'],
                ).exists()
                if existe:
                    return JsonResponse({
                        'success': False,
                        'errors': {'general': ['Ya existe una dirección igual registrada para este usuario.']}
                    })
                direccion = form.save(user=request.user)
                # Guardar datos adicionales de Google Places si están disponibles
                place_data = request.POST.get('place_data')
                if place_data:
                    try:
                        place_info = json.loads(place_data)
                        direccion.place_id = place_info.get('place_id', '')
                        direccion.latitud = place_info.get('lat', None)
                        direccion.longitud = place_info.get('lng', None)
                        direccion.save()
                    except json.JSONDecodeError:
                        pass  # Si no hay datos válidos, continuar sin ellos
                messages.success(request, 'Dirección agregada correctamente.')
                return JsonResponse({
                    'success': True, 
                    'message': 'Dirección agregada correctamente.',
                    'direccion_id': direccion.id
                })
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'errors': {'general': ['Error al guardar la dirección: ' + str(e)]}
                })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def direccion_eliminar(request, direccion_id):
    """Eliminar dirección"""
    direccion = get_object_or_404(DireccionUsuario, id=direccion_id, user=request.user)
    direccion.delete()
    messages.success(request, 'Dirección eliminada correctamente.')
    return JsonResponse({'success': True, 'message': 'Dirección eliminada correctamente.'})

@login_required
def direccion_principal(request, direccion_id):
    """Marcar dirección como principal"""
    # Desmarcar todas las direcciones como principales
    DireccionUsuario.objects.filter(user=request.user).update(principal=False)
    # Marcar la seleccionada como principal
    direccion = get_object_or_404(DireccionUsuario, id=direccion_id, user=request.user)
    direccion.principal = True
    direccion.save()
    messages.success(request, 'Dirección marcada como principal.')
    return JsonResponse({'success': True, 'message': 'Dirección marcada como principal.'})

@login_required
def pedidos_fragment(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    html = render_to_string('usuarios/pedidos_fragment.html', {'pedidos': pedidos})
    return JsonResponse({'html': html})
