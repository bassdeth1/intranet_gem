# intranet_core/views.py
import os
import mimetypes
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Para Class-Based Views
from django.views import View # Para Class-Based Views
from django.contrib import messages
from django.http import JsonResponse, FileResponse, HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.utils import timezone # Para manejo de fechas
from django.contrib.auth import update_session_auth_hash # Para cambio de contraseña
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User, Group # Para gestión de usuarios
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import modelformset_factory # Cambiamos a modelformset_factory para mejor manejo de instancias
from django.shortcuts import render, redirect, get_object_or_404
import json
# Modelos
from .models import (
    Archivo, Carpeta, ArticuloWiki, Notificacion,
    Formulario, CampoFormulario, RespuestaFormulario, DatoRespuesta,
    EventoCalendario,
    Tarea,
    PerfilUsuario,
    TipoRecurso, Recurso, Reserva
)

# Formularios
from .forms import (
    ArchivoForm, CarpetaForm, ArchivoEditForm, ArticuloWikiForm,
    FormularioModelForm, CampoFormularioModelForm,
    EventoCalendarioModelForm,
    TareaModelForm,
    PerfilUsuarioModelForm, UserUpdateForm, # Para perfil de usuario
    ReservaModelForm, UserEditStaffForm # UserEditStaffForm añadido
)
from django.forms import formset_factory, modelformset_factory # Para CampoFormulario

# --- Funciones Auxiliares ---
def es_staff(user):
    return user.is_staff

def crear_notificacion_global(usuario_destinatario, mensaje, url_destino_nombre=None, url_destino_args=None, url_destino_kwargs=None):
    url = None
    if url_destino_nombre:
        try:
            # Asegurar que args y kwargs sean iterables o diccionarios, incluso si son None
            args_to_pass = url_destino_args if url_destino_args is not None else []
            kwargs_to_pass = url_destino_kwargs if url_destino_kwargs is not None else {}
            url = reverse(url_destino_nombre, args=args_to_pass, kwargs=kwargs_to_pass)
        except Exception as e:
            print(f"Error al generar URL para notificación: {e}")
    Notificacion.objects.create(destinatario=usuario_destinatario, mensaje=mensaje, url_destino=url)

@login_required
def dashboard_view(request):
    numero_total_archivos = Archivo.objects.filter(subido_por=request.user).count()
    numero_total_carpetas = Carpeta.objects.filter(subido_por=request.user).count()
    notificaciones_no_leidas_count = Notificacion.objects.filter(destinatario=request.user, leida=False).count()
    
    # Nuevas estadísticas (ejemplos)
    tareas_pendientes_count = Tarea.objects.filter(asignado_a=request.user, estado__in=[Tarea.EstadoTarea.PENDIENTE, Tarea.EstadoTarea.EN_PROGRESO]).count()
    eventos_proximos_count = EventoCalendario.objects.filter(
        Q(creado_por=request.user) | Q(participantes=request.user) if hasattr(EventoCalendario, 'participantes') else Q(creado_por=request.user), # Ajustar si tienes M2M 'participantes'
        fecha_inicio__gte=timezone.now(),
        fecha_inicio__lte=timezone.now() + timezone.timedelta(days=7)
    ).count()


    context = {
        'page_title_for_header': 'Panel Principal',
        'active_nav': 'dashboard',
        'numero_archivos_totales': numero_total_archivos,
        'numero_carpetas_totales': numero_total_carpetas,
        'numero_formularios_creados': Formulario.objects.filter(creado_por=request.user).count(), # Actualizado
        'numero_notificaciones_nuevas': notificaciones_no_leidas_count,
        'numero_responsabilidades': tareas_pendientes_count, # Actualizado
        'eventos_proximos_count': eventos_proximos_count,
    }
    return render(request, 'intranet_core/dashboard.html', context)

@login_required
def carga_archivos_view(request, carpeta_id=None): # Modificado para aceptar carpeta_id
    form_carga_archivo_instance = ArchivoForm(user=request.user)
    form_crear_carpeta_instance = CarpetaForm()
    
    current_folder = None
    if carpeta_id:
        current_folder = get_object_or_404(Carpeta, id=carpeta_id, subido_por=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if action == 'create_folder':
            form_crear_carpeta_instance = CarpetaForm(request.POST)
            if form_crear_carpeta_instance.is_valid():
                nueva_carpeta = form_crear_carpeta_instance.save(commit=False)
                nueva_carpeta.subido_por = request.user
                # nueva_carpeta.carpeta_padre = current_folder # Si implementas subcarpetas
                try:
                    nueva_carpeta.save()
                    messages.success(request, f"Carpeta '{nueva_carpeta.nombre}' creada exitosamente.")
                    # Redirigir a la carpeta actual si existe, sino a la raíz
                    return redirect('intranet_core:carga_archivos', carpeta_id=current_folder.id) if current_folder else redirect('intranet_core:carga_archivos')
                except Exception as e: # Captura IntegrityError por unique_together
                    messages.error(request, f"Error al crear la carpeta: El nombre '{nueva_carpeta.nombre}' ya existe en esta ubicación o hubo otro problema.")
            else:
                messages.error(request, "No se pudo crear la carpeta. Revisa los errores en el formulario.")
        
        elif action == 'delete_file':
            file_id_to_delete = request.POST.get('file_id')
            try:
                archivo_a_eliminar = Archivo.objects.get(id=file_id_to_delete, subido_por=request.user)
                nombre_archivo_eliminado = archivo_a_eliminar.nombre_descriptivo or archivo_a_eliminar.nombre_original_archivo
                archivo_a_eliminar.delete()
                if is_ajax:
                    return JsonResponse({
                        'status': 'success',
                        'message': f"Archivo '{nombre_archivo_eliminado}' eliminado correctamente.",
                        'file_id': file_id_to_delete
                    })
                messages.success(request, f"Archivo '{nombre_archivo_eliminado}' eliminado correctamente.")
            except Archivo.DoesNotExist:
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': "Archivo no encontrado o sin permiso para eliminar."}, status=404)
                messages.error(request, "Archivo no encontrado o sin permiso para eliminar.")
            except Exception as e:
                error_message_user = "Ocurrió un error al intentar eliminar el archivo."
                print(f"Error en delete_file: {str(e)}")
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': error_message_user}, status=500)
                messages.error(request, error_message_user)
            
            if not is_ajax: # Redirigir a la carpeta actual si existe, sino a la raíz
                return redirect('intranet_core:carga_archivos', carpeta_id=current_folder.id) if current_folder else redirect('intranet_core:carga_archivos')

        else: # Asumimos subida de archivo
            form_carga_archivo_instance = ArchivoForm(request.POST, request.FILES, user=request.user)
            if form_carga_archivo_instance.is_valid():
                archivo_instancia = form_carga_archivo_instance.save(commit=False)
                archivo_instancia.subido_por = request.user
                if request.FILES.get('archivo_subido'):
                    archivo_instancia.nombre_original_archivo = request.FILES['archivo_subido'].name
                
                # Asignar a la carpeta actual si estamos dentro de una
                if current_folder:
                    archivo_instancia.carpeta = current_folder
                # Si no, se asigna a la carpeta seleccionada en el formulario, o a la raíz si no se selecciona ninguna.
                # Esto es manejado por el 'empty_label' del ArchivoForm y la lógica del SET_NULL

                archivo_instancia.save()
                messages.success(request, f"Archivo '{archivo_instancia.nombre_descriptivo or archivo_instancia.nombre_original_archivo}' subido exitosamente.")
                return redirect('intranet_core:carga_archivos', carpeta_id=current_folder.id) if current_folder else redirect('intranet_core:carga_archivos')
            else:
                messages.error(request, "Error al subir el archivo. Por favor, revise los campos.")
                
    # Filtrar carpetas y archivos según la carpeta actual
    if current_folder:
        carpetas_a_mostrar = Carpeta.objects.filter(subido_por=request.user, carpeta_padre=current_folder).order_by('nombre') # Si usas carpeta_padre
        archivos_a_mostrar = Archivo.objects.filter(subido_por=request.user, carpeta=current_folder).order_by('-fecha_subida')
    else: # Raíz
        carpetas_a_mostrar = Carpeta.objects.filter(subido_por=request.user, carpeta_padre__isnull=True).order_by('nombre') # Si usas carpeta_padre
        archivos_a_mostrar = Archivo.objects.filter(subido_por=request.user, carpeta__isnull=True).order_by('-fecha_subida')

    # Breadcrumbs (ejemplo básico)
    breadcrumbs = []
    temp_folder = current_folder
    while temp_folder:
        breadcrumbs.insert(0, {'nombre': temp_folder.nombre, 'id': temp_folder.id})
        temp_folder = temp_folder.carpeta_padre # Si usas carpeta_padre
    
    context = {
        'page_title_for_header': f'Gestor de Archivos{" / " + current_folder.nombre if current_folder else ""}',
        'active_nav': 'archivos',
        'form_carga_archivo': form_carga_archivo_instance,
        'form_crear_carpeta': form_crear_carpeta_instance,
        'carpetas': carpetas_a_mostrar, # Ajustar si se implementan subcarpetas
        'archivos_subidos': archivos_a_mostrar,
        'current_folder': current_folder,
        'breadcrumbs': breadcrumbs,
    }
    return render(request, 'intranet_core/carga_archivos.html', context)


@login_required
def editar_archivo_view(request, archivo_id):
    archivo = get_object_or_404(Archivo, id=archivo_id, subido_por=request.user)
    nombre_original_previo = archivo.nombre_original_archivo
    path_previo = archivo.archivo_subido.path if archivo.archivo_subido else None

    if request.method == 'POST':
        form = ArchivoEditForm(request.POST, request.FILES, instance=archivo, user=request.user)
        if form.is_valid():
            archivo_editado = form.save(commit=False)
            if request.FILES.get('archivo_subido'): # Si se subió un nuevo archivo
                # Eliminar el archivo físico antiguo si existe y es diferente del nuevo
                if path_previo and os.path.isfile(path_previo) and path_previo != archivo_editado.archivo_subido.path :
                    try:
                        os.remove(path_previo)
                    except OSError as e:
                        print(f"Error eliminando archivo antiguo {path_previo}: {e}")
                archivo_editado.nombre_original_archivo = request.FILES['archivo_subido'].name
            else: # Si no se subió un nuevo archivo, mantener el existente
                archivo_editado.archivo_subido = archivo.archivo_subido # Corregido el typo
                archivo_editado.nombre_original_archivo = nombre_original_previo
            
            archivo_editado.save()
            form.save_m2m() # Si hubiera campos M2M
            messages.success(request, f"Archivo '{archivo_editado.nombre_descriptivo or archivo_editado.nombre_original_archivo}' actualizado.")
            return redirect('intranet_core:carga_archivos', carpeta_id=archivo.carpeta.id if archivo.carpeta else None)
    else:
        form = ArchivoEditForm(instance=archivo, user=request.user)
    
    context = {
        'page_title_for_header': f'Editar Archivo: {archivo.nombre_descriptivo or archivo.nombre_original_archivo}',
        'active_nav': 'archivos',
        'form': form,
        'archivo': archivo,
    }
    return render(request, 'intranet_core/editar_archivo.html', context)

@login_required
def ver_archivo_view(request, archivo_id):
    archivo = get_object_or_404(Archivo, id=archivo_id)
    # Podrías añadir lógica de permisos más compleja aquí (ej. si el archivo es compartido)
    if archivo.subido_por != request.user and not request.user.is_staff: # Ejemplo: staff puede ver todos
        return HttpResponseForbidden("No tienes permiso para ver este archivo.")
    if not archivo.archivo_subido or not archivo.archivo_subido.path:
        raise Http404("El archivo no tiene un fichero físico asociado o la ruta no es válida.")
    try:
        file_path = archivo.archivo_subido.path
        if not os.path.exists(file_path):
            raise Http404("Archivo físico no encontrado en el servidor.")

        content_type, encoding = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'
        
        if archivo.is_viewable_in_browser():
            # Para archivos de texto, leer y mostrar como HttpResponse para evitar problemas de codificación con FileResponse
            if archivo.get_file_extension() in ['.txt', '.md', '.py', '.js', '.json', '.css', '.html', '.xml']:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                return HttpResponse(content, content_type=f"{content_type}; charset=utf-8")
            return FileResponse(open(file_path, 'rb'), content_type=content_type, as_attachment=False)
        else:
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=archivo.nombre_original_archivo)
    except FileNotFoundError:
        raise Http404("Archivo no encontrado en el servidor.")
    except Exception as e:
        print(f"Error al intentar ver el archivo {archivo_id}: {e}")
        messages.error(request, "No se pudo mostrar el archivo debido a un error.")
        return redirect('intranet_core:carga_archivos') # O a donde sea apropiado

# --- Vistas de Wiki (ya estaban bastante completas) ---
@login_required
def wiki_view(request):
    search_query = request.GET.get('q', '')
    articulos_qs = ArticuloWiki.objects.all()
    if search_query:
        articulos_qs = articulos_qs.filter(
            Q(titulo__icontains=search_query) | Q(contenido__icontains=search_query)
        )
        if not articulos_qs.exists():
            messages.info(request, f"No se encontraron artículos para: '{search_query}'.")
        else:
            messages.success(request, f"Mostrando resultados para: '{search_query}'.")
    
    articulos = articulos_qs.order_by('-actualizado_el', 'titulo')
    context = {
        'page_title_for_header': 'Base de Conocimiento (Wiki)',
        'active_nav': 'wiki',
        'articulos': articulos,
        'search_query': search_query,
    }
    return render(request, 'intranet_core/wiki_lista.html', context)

@login_required
def wiki_articulo_detalle_view(request, slug):
    articulo = get_object_or_404(ArticuloWiki, slug=slug)
    html_content = ""
    try:
        import markdown
        extensions = ['fenced_code', 'tables', 'attr_list', 'md_in_html', 'codehilite', 'toc']
        md = markdown.Markdown(extensions=extensions, extension_configs={'codehilite': {'css_class': 'codehilite'}})
        html_content = md.convert(articulo.contenido)
        toc = getattr(md, 'toc', '') if 'toc' in extensions else '' # Extraer TOC si la extensión está habilitada
    except ImportError:
        html_content = f"<p class='text-red-500'>La librería 'markdown' no está instalada. Por favor, instálala (<code>pip install markdown pygments</code>) para ver el contenido formateado.</p><pre>{articulo.contenido}</pre>"
        messages.warning(request, "La librería Markdown (y Pygments para resaltado) no está instalada.")
        toc = ''
    except Exception as e:
        html_content = f"<p class='text-red-500'>Error renderizando Markdown: {e}</p><pre>{articulo.contenido}</pre>"
        messages.error(request, f"Error al renderizar el contenido Markdown: {e}")
        toc = ''
    
    context = {
        'page_title_for_header': articulo.titulo,
        'active_nav': 'wiki',
        'articulo': articulo,
        'html_content': html_content,
        'toc_content': toc, # Pasar el TOC al template
    }
    return render(request, 'intranet_core/wiki_articulo_detalle.html', context)

@login_required
def wiki_crear_articulo_view(request):
    if request.method == 'POST':
        form = ArticuloWikiForm(request.POST)
        if form.is_valid():
            articulo = form.save(commit=False)
            articulo.autor = request.user
            articulo.save() 
            messages.success(request, f"Artículo '{articulo.titulo}' creado exitosamente.")
            crear_notificacion_global(
                usuario_destinatario=request.user, 
                mensaje=f"Nuevo artículo en la Wiki: '{articulo.titulo}' por {request.user.username}.",
                url_destino_nombre='intranet_core:wiki_articulo_detalle',
                url_destino_kwargs={'slug': articulo.slug} # Usar el nombre correcto del parámetro
            )
            return redirect(articulo.get_absolute_url())
    else:
        form = ArticuloWikiForm()
    
    context = {
        'page_title_for_header': 'Crear Nuevo Artículo Wiki',
        'active_nav': 'wiki',
        'form': form,
        'edit_mode': False,
    }
    return render(request, 'intranet_core/wiki_articulo_form.html', context)

@login_required
def wiki_editar_articulo_view(request, slug):
    articulo = get_object_or_404(ArticuloWiki, slug=slug)
    if articulo.autor != request.user and not request.user.is_staff:
        messages.error(request, "No tienes permiso para editar este artículo.")
        return redirect(articulo.get_absolute_url())
    
    if request.method == 'POST':
        form = ArticuloWikiForm(request.POST, instance=articulo)
        if form.is_valid():
            form.save()
            messages.success(request, f"Artículo '{articulo.titulo}' actualizado exitosamente.")
            return redirect(articulo.get_absolute_url())
    else:
        form = ArticuloWikiForm(instance=articulo)
    
    context = {
        'page_title_for_header': f'Editar: {articulo.titulo}',
        'active_nav': 'wiki',
        'form': form,
        'articulo': articulo,
        'edit_mode': True,
    }
    return render(request, 'intranet_core/wiki_articulo_form.html', context)

@login_required
def wiki_eliminar_articulo_view(request, slug):
    articulo = get_object_or_404(ArticuloWiki, slug=slug)
    if articulo.autor != request.user and not request.user.is_staff:
        messages.error(request, "No tienes permiso para eliminar este artículo.")
        return redirect(articulo.get_absolute_url())
    
    if request.method == 'POST':
        titulo_articulo = articulo.titulo
        articulo.delete()
        messages.success(request, f"Artículo '{titulo_articulo}' eliminado exitosamente.")
        return redirect('intranet_core:wiki')
    
    context = {
        'page_title_for_header': f'Confirmar Eliminación: {articulo.titulo}',
        'active_nav': 'wiki',
        'articulo': articulo
    }
    return render(request, 'intranet_core/wiki_articulo_confirm_delete.html', context)

# --- Vistas de Notificaciones (ya estaban bastante completas) ---
@login_required
def notificaciones_page_view(request):
    notificaciones_no_leidas = Notificacion.objects.filter(destinatario=request.user, leida=False).order_by('-fecha_creacion')
    notificaciones_leidas = Notificacion.objects.filter(destinatario=request.user, leida=True).order_by('-fecha_creacion')[:20] # Limitar historial
    context = {
        'page_title_for_header': 'Notificaciones y Anuncios',
        'active_nav': 'notificaciones_page',
        'notificaciones_no_leidas': notificaciones_no_leidas,
        'notificaciones_leidas': notificaciones_leidas,
    }
    return render(request, 'intranet_core/notificaciones_page.html', context)

@login_required
def marcar_notificacion_leida_view(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, destinatario=request.user)
    notificacion.leida = True
    notificacion.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Notificación marcada como leída.'})
    if notificacion.url_destino:
        return redirect(notificacion.url_destino)
    return redirect(request.GET.get('next', reverse('intranet_core:notificaciones_page')))


@login_required
def marcar_todas_notificaciones_leidas_view(request):
    if request.method == 'POST': # Asegurar que sea por POST
        Notificacion.objects.filter(destinatario=request.user, leida=False).update(leida=True)
        messages.success(request, "Todas las notificaciones han sido marcadas como leídas.")
    return redirect('intranet_core:notificaciones_page')

# --- Implementación de Vistas Placeholder ---

# 1. Módulo de Formularios
@login_required
def formularios_view(request): # Lista de formularios creados por el usuario
    formularios_usuario = Formulario.objects.filter(creado_por=request.user).order_by('-creado_el')
    context = {
        'page_title_for_header': 'Mis Formularios',
        'active_nav': 'formularios',
        'formularios': formularios_usuario,
    }
    return render(request, 'intranet_core/formularios_lista.html', context) # Nuevo template

@login_required
def formulario_crear_view(request):
    if request.method == 'POST':
        form = FormularioModelForm(request.POST) # Asume que tienes este form en forms.py
        if form.is_valid():
            formulario = form.save(commit=False)
            formulario.creado_por = request.user
            formulario.save()
            messages.success(request, f"Formulario '{formulario.titulo}' creado. Ahora puedes añadir campos.")
            return redirect('intranet_core:formulario_disenar', formulario_id=formulario.id) # Redirigir a diseñar
    else:
        form = FormularioModelForm()
    context = {
        'page_title_for_header': 'Crear Nuevo Formulario',
        'active_nav': 'formularios',
        'form': form,
    }
    return render(request, 'intranet_core/formulario_crear.html', context) # Nuevo template

@login_required
def formulario_disenar_view(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id, creado_por=request.user)
    
    CampoFormSet = modelformset_factory(
        CampoFormulario,
        form=CampoFormularioModelForm,
        fields=['etiqueta', 'tipo_campo', 'ayuda_texto', 'es_obligatorio', 'opciones_choices', 'orden'],
        extra=0,
        can_delete=True,
        can_order=False
    )

    if request.method == 'POST':
        formset = CampoFormSet(request.POST, request.FILES, queryset=formulario.campos.all().order_by('orden'), prefix='campos')
        
        if formset.is_valid():
            instances_to_save = []
            
            for form_idx, form in enumerate(formset.forms):
                if formset.can_delete and form.cleaned_data.get('DELETE', False):
                    if form.instance.pk:
                        form.instance.delete()
                    continue 
                if form.has_changed() or not form.instance.pk: # Guardar si cambió o es nuevo (y no está marcado para eliminar)
                    # Asegurar que la instancia tiene el formulario padre asignado antes de añadirla
                    form.instance.formulario = formulario 
                    instances_to_save.append(form.instance)
            
            current_order = 0
            for instance in instances_to_save:
                instance.orden = current_order
                instance.save() 
                current_order += 1
            
            messages.success(request, f"Campos del formulario '{formulario.titulo}' actualizados exitosamente.")
            return redirect('intranet_core:formulario_disenar', formulario_id=formulario.id)
        else:
            messages.error(request, "Por favor corrige los errores en los campos del formulario.")
            # Para depuración en consola del servidor:
            # for i, form_errors in enumerate(formset.errors):
            #     if form_errors:
            #         print(f"Errores en el subformulario de campo {i}: {form_errors}")
            # if formset.non_form_errors():
            #     print(f"Errores generales del formset: {formset.non_form_errors()}")

    else: # GET request
        formset = CampoFormSet(queryset=formulario.campos.all().order_by('orden'), prefix='campos')

    context = {
        'page_title_for_header': f'Diseñar Formulario: {formulario.titulo}',
        'active_nav': 'formularios',
        'formulario': formulario,
        'formset': formset,
        'campo_tipos': CampoFormulario.TipoCampo.choices,
        # Cambio aquí: Convertir a string JSON en la vista
        'campo_tipos_json_string': json.dumps(dict(CampoFormulario.TipoCampo.choices)) 
    }
    return render(request, 'intranet_core/formulario_disenar.html', context)

@login_required
def formulario_llenar_view(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id, activo=True)
    # Aquí construirías un formulario dinámicamente basado en `formulario.campos.all()`
    # Esto es complejo y generalmente se hace iterando los campos en el template y creando los inputs.
    # El procesamiento del POST requerirá guardar una `RespuestaFormulario` y múltiples `DatoRespuesta`.
    # Por simplicidad, este es un placeholder más detallado:
    if request.method == 'POST':
        # Lógica para procesar los datos de cada campo
        respuesta = RespuestaFormulario.objects.create(formulario=formulario, respondido_por=request.user)
        for campo in formulario.campos.all():
            valor_campo = request.POST.get(f'campo_{campo.id}')
            if valor_campo is not None: # O manejar casillas de verificación múltiples
                DatoRespuesta.objects.create(respuesta_formulario=respuesta, campo_formulario=campo, valor=valor_campo)
        messages.success(request, f"Gracias por completar el formulario '{formulario.titulo}'.")
        return redirect('intranet_core:dashboard') # O a una página de agradecimiento
        
    context = {
        'page_title_for_header': f'Llenar: {formulario.titulo}',
        'active_nav': 'formularios', # O ninguna si es una página pública
        'formulario': formulario,
        'campos': formulario.campos.all().order_by('orden')
    }
    return render(request, 'intranet_core/formulario_llenar.html', context) # Nuevo template

@login_required
def formulario_respuestas_view(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)
    # Permitir solo al creador o staff ver respuestas
    if not (request.user == formulario.creado_por or request.user.is_staff):
        return HttpResponseForbidden("No tienes permiso para ver estas respuestas.")
    respuestas_qs = RespuestaFormulario.objects.filter(formulario=formulario).prefetch_related('datos', 'datos__campo_formulario')
    # Paginación para muchas respuestas
    paginator = Paginator(respuestas_qs, 20)  # 20 por página
    page = request.GET.get('page')
    try:
        respuestas = paginator.page(page)
    except PageNotAnInteger:
        respuestas = paginator.page(1)
    except EmptyPage:
        respuestas = paginator.page(paginator.num_pages)
    context = {
        'page_title_for_header': f'Respuestas para: {formulario.titulo}',
        'active_nav': 'formularios',
        'formulario': formulario,
        'respuestas': respuestas,
    }
    return render(request, 'intranet_core/formulario_respuestas.html', context) # Nuevo template

# 2. Módulo de Calendario
@login_required
def calendario_view(request):
    # Esta vista puede renderizar la página principal del calendario.
    # Los eventos se cargarían vía AJAX o se pasarían directamente si no son demasiados.
    eventos = EventoCalendario.objects.filter(Q(creado_por=request.user) | Q(participantes=request.user) if hasattr(EventoCalendario, 'participantes') else Q(creado_por=request.user)).distinct() # Ejemplo
    context = {
        'page_title_for_header': 'Calendario de Actividades',
        'active_nav': 'calendario',
        'eventos_json_url': reverse('intranet_core:calendario_eventos_json'), # URL para FullCalendar
    }
    # El template `calendario.html` necesitaría JS para FullCalendar.
    return render(request, 'intranet_core/calendario.html', context)

@login_required
def calendario_eventos_json_view(request):
    # Filtra eventos por usuario y por rango de fechas si se proveen
    eventos_qs = EventoCalendario.objects.filter(
        Q(creado_por=request.user) | Q(participantes=request.user) if hasattr(EventoCalendario, 'participantes') else Q(creado_por=request.user)
    ).distinct()
    # Validar parámetros de fecha
    start_param = request.GET.get('start')
    end_param = request.GET.get('end')
    try:
        if start_param:
            start_dt = timezone.datetime.fromisoformat(start_param)
            eventos_qs = eventos_qs.filter(fecha_inicio__gte=start_dt)
        if end_param:
            end_dt = timezone.datetime.fromisoformat(end_param)
            eventos_qs = eventos_qs.filter(fecha_fin__lte=end_dt)
    except Exception:
        pass  # Si hay error en el formato, ignorar el filtro
    eventos_list = []
    for evento in eventos_qs:
        eventos_list.append({
            'id': evento.id,
            'title': evento.titulo,
            'start': evento.fecha_inicio.isoformat(),
            'end': evento.fecha_fin.isoformat() if evento.fecha_fin else None,
            'description': evento.descripcion,
            'color': getattr(evento, 'color_evento', None),
            'url': reverse('intranet_core:evento_calendario_detalle', args=[evento.id])
        })
    return JsonResponse(eventos_list, safe=False)

@login_required
def evento_calendario_crear_view(request):
    if request.method == 'POST':
        form = EventoCalendarioModelForm(request.POST) # Asume este form
        if form.is_valid():
            evento = form.save(commit=False)
            evento.creado_por = request.user
            evento.save()
            messages.success(request, "Evento creado exitosamente.")
            return redirect('intranet_core:calendario')
    else:
        # Pre-llenar fecha_inicio si viene por GET (ej. desde FullCalendar al hacer clic en un día)
        initial_data = {}
        date_str = request.GET.get('date')
        if date_str:
            try:
                initial_data['fecha_inicio'] = timezone.datetime.fromisoformat(date_str)
            except ValueError:
                pass # Ignorar si la fecha no es válida
        form = EventoCalendarioModelForm(initial=initial_data)
        
    context = {'form': form, 'page_title_for_header': 'Crear Evento', 'active_nav': 'calendario'}
    return render(request, 'intranet_core/evento_calendario_form.html', context) # Nuevo template

@login_required
def evento_calendario_detalle_view(request, evento_id):
    evento = get_object_or_404(EventoCalendario, id=evento_id)
    # Añadir verificación de permisos si es necesario
    context = {'evento': evento, 'page_title_for_header': evento.titulo, 'active_nav': 'calendario'}
    return render(request, 'intranet_core/evento_calendario_detalle.html', context) # Nuevo template

@login_required
def evento_calendario_editar_view(request, evento_id):
    evento = get_object_or_404(EventoCalendario, id=evento_id, creado_por=request.user) # Solo el creador edita
    if request.method == 'POST':
        form = EventoCalendarioModelForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento actualizado.")
            return redirect('intranet_core:calendario')
    else:
        form = EventoCalendarioModelForm(instance=evento)
    context = {'form': form, 'evento': evento, 'page_title_for_header': f'Editar: {evento.titulo}', 'active_nav': 'calendario'}
    return render(request, 'intranet_core/evento_calendario_form.html', context)

@login_required
def evento_calendario_eliminar_view(request, evento_id):
    evento = get_object_or_404(EventoCalendario, id=evento_id, creado_por=request.user) # Solo el creador elimina
    if request.method == 'POST':
        evento.delete()
        messages.success(request, "Evento eliminado.")
        return redirect('intranet_core:calendario')
    context = {'evento': evento, 'page_title_for_header': f'Eliminar: {evento.titulo}', 'active_nav': 'calendario'}
    return render(request, 'intranet_core/evento_calendario_confirm_delete.html', context) # Nuevo template

# 3. Módulo de Responsabilidades (Tareas)
@login_required
def responsabilidades_view(request): # Lista de tareas
    # Filtros (ej. mis tareas, tareas que creé, todas si es staff)
    filter_type = request.GET.get('filter', 'mis_tareas')
    tareas_qs = Tarea.objects.all()

    if filter_type == 'mis_tareas':
        tareas_qs = tareas_qs.filter(asignado_a=request.user)
        page_subtitle = "Mis Tareas Asignadas"
    elif filter_type == 'creadas_por_mi':
        tareas_qs = tareas_qs.filter(creado_por=request.user)
        page_subtitle = "Tareas Creadas por Mí"
    elif filter_type == 'todas' and request.user.is_staff:
        page_subtitle = "Todas las Tareas"
    else: # Por defecto o si no es staff y pide 'todas'
        tareas_qs = tareas_qs.filter(Q(asignado_a=request.user) | Q(creado_por=request.user)).distinct()
        page_subtitle = "Mis Tareas y Creadas por Mí"
        
    tareas_pendientes = tareas_qs.filter(estado__in=[Tarea.EstadoTarea.PENDIENTE, Tarea.EstadoTarea.EN_PROGRESO]).order_by('fecha_limite', 'prioridad')
    tareas_completadas = tareas_qs.filter(estado=Tarea.EstadoTarea.COMPLETADA).order_by('-fecha_limite')[:20] # Limitar

    context = {
        'page_title_for_header': f'Gestión de Responsabilidades: {page_subtitle}',
        'active_nav': 'responsabilidades',
        'tareas_pendientes': tareas_pendientes,
        'tareas_completadas': tareas_completadas,
        'current_filter': filter_type,
    }
    return render(request, 'intranet_core/responsabilidades_lista.html', context) # Nuevo template

@login_required
def tarea_crear_view(request):
    if request.method == 'POST':
        form = TareaModelForm(request.POST) # Asume este form
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.creado_por = request.user
            tarea.save()
            # Notificar al asignado_a si es diferente del creador
            if tarea.asignado_a and tarea.asignado_a != request.user:
                 crear_notificacion_global(
                    tarea.asignado_a,
                    f"Nueva tarea asignada: '{tarea.titulo}' por {request.user.username}.",
                    'intranet_core:tarea_detalle', kwargs={'tarea_id': tarea.id} # Ajusta el nombre de la URL de detalle
                )
            messages.success(request, "Tarea creada exitosamente.")
            return redirect('intranet_core:responsabilidades')
    else:
        form = TareaModelForm(initial={'asignado_a': request.user}) # Pre-asignar al usuario actual
    context = {'form': form, 'page_title_for_header': 'Crear Nueva Tarea', 'active_nav': 'responsabilidades'}
    return render(request, 'intranet_core/tarea_form.html', context) # Nuevo template

@login_required
def tarea_detalle_view(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    # Verificar permisos: asignado, creador o staff
    if not (request.user == tarea.asignado_a or request.user == tarea.creado_por or request.user.is_staff):
        return HttpResponseForbidden("No tienes permiso para ver esta tarea.")
    context = {'tarea': tarea, 'page_title_for_header': f'Tarea: {tarea.titulo}', 'active_nav': 'responsabilidades'}
    return render(request, 'intranet_core/tarea_detalle.html', context) # Nuevo template

@login_required
def tarea_editar_view(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    # Verificar permisos: solo creador o staff (o asignado si se permite)
    if not (request.user == tarea.creado_por or request.user.is_staff):
        return HttpResponseForbidden("No tienes permiso para editar esta tarea.")
        
    if request.method == 'POST':
        form = TareaModelForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            messages.success(request, "Tarea actualizada.")
            return redirect('intranet_core:tarea_detalle', tarea_id=tarea.id)
    else:
        form = TareaModelForm(instance=tarea)
    context = {'form': form, 'tarea': tarea, 'page_title_for_header': f'Editar Tarea: {tarea.titulo}', 'active_nav': 'responsabilidades'}
    return render(request, 'intranet_core/tarea_form.html', context)

@login_required
def tarea_eliminar_view(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if not (request.user == tarea.creado_por or request.user.is_staff):
        return HttpResponseForbidden("No tienes permiso para eliminar esta tarea.")
    
    if request.method == 'POST':
        tarea.delete()
        messages.success(request, "Tarea eliminada.")
        return redirect('intranet_core:responsabilidades')
    context = {'tarea': tarea, 'page_title_for_header': f'Eliminar Tarea: {tarea.titulo}', 'active_nav': 'responsabilidades'}
    return render(request, 'intranet_core/tarea_confirm_delete.html', context)

# 4. Módulo de Directorio de Usuarios
@login_required
def directorio_view(request):
    search_query = request.GET.get('q', '').strip()
    usuarios_qs = User.objects.filter(is_active=True).select_related('perfil').order_by('last_name', 'first_name')
    if search_query:
        usuarios_qs = usuarios_qs.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(perfil__departamento__icontains=search_query) |
            Q(perfil__cargo__icontains=search_query)
        ).distinct()
        
    paginator = Paginator(usuarios_qs, 25)
    page_number = request.GET.get('page')
    try:
        usuarios_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        usuarios_paginados = paginator.page(1)
    except EmptyPage:
        usuarios_paginados = paginator.page(paginator.num_pages)
        
    context = {
        'page_title_for_header': 'Directorio de Usuarios',
        'active_nav': 'directorio',
        'usuarios': usuarios_paginados, # Pasa el objeto Page
        'search_query': search_query,
    }
    return render(request, 'intranet_core/directorio_lista.html', context)

@login_required
def directorio_usuario_detalle_view(request, username):
    usuario_perfil = get_object_or_404(User.objects.select_related('perfil'), username=username, is_active=True)
    context = {
        'page_title_for_header': f'Perfil de {usuario_perfil.get_full_name() or usuario_perfil.username}',
        'active_nav': 'directorio',
        'perfil_usuario_obj': usuario_perfil, # El template debe acceder a usuario_perfil.perfil
    }
    return render(request, 'intranet_core/directorio_usuario_detalle.html', context)

# 5. Módulo de Reserva de Recursos
@login_required
def reservas_view(request):
    recursos = Recurso.objects.filter(esta_activo=True).select_related('tipo_recurso')
    tipos_recurso = TipoRecurso.objects.all()
    context = {
        'page_title_for_header': 'Reserva de Recursos',
        'active_nav': 'reservas',
        'recursos': recursos,
        'tipos_recurso': tipos_recurso,
        'reservas_json_url': reverse('intranet_core:reservas_eventos_json'),
        'form_reserva': ReservaModelForm() # Para un modal
    }
    return render(request, 'intranet_core/reservas_lista_recursos.html', context)

@login_required
def reservas_eventos_json_view(request):
    reservas_qs = Reserva.objects.filter(estado=Reserva.EstadoReserva.APROBADA).select_related('recurso', 'reservado_por')
    
    recurso_id = request.GET.get('recurso_id')
    if recurso_id:
        reservas_qs = reservas_qs.filter(recurso_id=recurso_id)
    
    start_param = request.GET.get('start')
    end_param = request.GET.get('end')
    if start_param:
        reservas_qs = reservas_qs.filter(fecha_fin__gte=start_param)
    if end_param:
        reservas_qs = reservas_qs.filter(fecha_inicio__lte=end_param)

    eventos_list = []
    for reserva in reservas_qs:
        eventos_list.append({
            'id': reserva.id,
            'title': f"{reserva.recurso.nombre} ({reserva.reservado_por.username})",
            'start': reserva.fecha_inicio.isoformat(),
            'end': reserva.fecha_fin.isoformat(),
            'resourceId': reserva.recurso.id,
            'description': reserva.motivo or '',
            'color': reserva.recurso.tipo_recurso.icono_fa.split(' ')[1] if reserva.recurso.tipo_recurso.icono_fa else None # Usar color de tipo si existe
        })
    return JsonResponse(eventos_list, safe=False)

@login_required
def reserva_crear_view(request, recurso_id=None):
    recurso = None
    initial_data = {}
    if recurso_id:
        recurso = get_object_or_404(Recurso, id=recurso_id, esta_activo=True)
        initial_data['recurso'] = recurso

    # Pre-llenar fechas si vienen por GET (ej. desde FullCalendar)
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    if start_str: 
        try: initial_data['fecha_inicio'] = timezone.datetime.fromisoformat(start_str)
        except: pass
    if end_str: 
        try: initial_data['fecha_fin'] = timezone.datetime.fromisoformat(end_str)
        except: pass

    if request.method == 'POST':
        form = ReservaModelForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.reservado_por = request.user
            # Lógica de aprobación si 'requiere_aprobacion' está en el modelo Recurso
            # if reserva.recurso.requiere_aprobacion:
            #     reserva.estado = Reserva.EstadoReserva.PENDIENTE
            #     messages.info(request, f"Solicitud de reserva para '{reserva.recurso.nombre}' enviada para aprobación.")
            # else:
            reserva.estado = Reserva.EstadoReserva.APROBADA # Por ahora, aprobación automática
            messages.success(request, f"Reserva para '{reserva.recurso.nombre}' creada exitosamente.")
            reserva.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                 return JsonResponse({'status': 'success', 'message': 'Reserva creada.', 'evento_id': reserva.id}) # Adaptar para FullCalendar
            return redirect('intranet_core:reservas')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        form = ReservaModelForm(initial=initial_data)
        if recurso:
            form.fields['recurso'].disabled = True
    
    context = {
        'form': form, 
        'recurso': recurso,
        'page_title_for_header': f'Crear Reserva {"para " + recurso.nombre if recurso else ""}',
        'active_nav': 'reservas',
        'edit_mode': False
    }
    return render(request, 'intranet_core/reserva_form.html', context)

# 6. Módulo de Gestión de Usuarios (Staff)
@login_required
@user_passes_test(es_staff, login_url=reverse_lazy('intranet_core:dashboard'))
def usuarios_gestion_view(request):
    search_query = request.GET.get('q', '')
    usuarios_qs = User.objects.all().select_related('perfil').prefetch_related('groups').order_by('username')
    
    if search_query:
        usuarios_qs = usuarios_qs.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    paginator = Paginator(usuarios_qs, 25)
    page_number = request.GET.get('page')
    try:
        usuarios_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        usuarios_paginados = paginator.page(1)
    except EmptyPage:
        usuarios_paginados = paginator.page(paginator.num_pages)

    context = {
        'page_title_for_header': 'Gestión de Usuarios',
        'active_nav': 'usuarios_gestion',
        'usuarios': usuarios_paginados,
        'search_query': search_query,
    }
    return render(request, 'intranet_core/usuarios_gestion_lista.html', context)

@login_required
@user_passes_test(es_staff)
def usuario_gestion_editar_view(request, user_id):
    usuario_a_editar = get_object_or_404(User, id=user_id)
    perfil_usuario, created = PerfilUsuario.objects.get_or_create(usuario=usuario_a_editar)

    if request.method == 'POST':
        user_form = UserEditStaffForm(request.POST, instance=usuario_a_editar)
        perfil_form = PerfilUsuarioModelForm(request.POST, request.FILES, instance=perfil_usuario)
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save() # El save() de UserEditStaffForm maneja los grupos
            perfil_form.save()
            messages.success(request, f"Usuario '{usuario_a_editar.username}' actualizado exitosamente.")
            return redirect('intranet_core:usuarios_gestion')
        else:
            messages.error(request, "Error al actualizar el usuario. Revisa los campos.")
    else:
        user_form = UserEditStaffForm(instance=usuario_a_editar)
        perfil_form = PerfilUsuarioModelForm(instance=perfil_usuario)
    
    context = {
        'page_title_for_header': f'Editar Usuario: {usuario_a_editar.username}',
        'active_nav': 'usuarios_gestion',
        'usuario_a_editar': usuario_a_editar,
        'user_form': user_form,
        'perfil_form': perfil_form,
    }
    return render(request, 'intranet_core/usuario_gestion_form.html', context)

# 7. Módulo de Perfil de Usuario
@login_required
def perfil_view(request):
    user_profile, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    user_form = UserUpdateForm(instance=request.user)
    profile_form = PerfilUsuarioModelForm(instance=user_profile)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = PerfilUsuarioModelForm(request.POST, request.FILES, instance=user_profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
                return redirect('intranet_core:perfil')
            else:
                messages.error(request, 'Por favor corrige los errores en el formulario de perfil.')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) 
                messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
                return redirect('intranet_core:perfil')
            else:
                messages.error(request, 'Error al cambiar la contraseña. Por favor corrige los errores.')
    
    context = {
        'page_title_for_header': 'Mi Perfil',
        'active_nav': 'perfil',
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'perfil_usuario_obj': user_profile, # Usado para mostrar la foto actual, etc.
    }
    return render(request, 'intranet_core/perfil_editar.html', context)

# 8. Módulo de Configuración
@login_required
def configuracion_view(request):
    context = {
        'page_title_for_header': 'Configuración',
        'active_nav': 'configuracion'
    }
    messages.info(request, "La sección de Configuración está en desarrollo.")
    return render(request, 'intranet_core/configuracion.html', context)