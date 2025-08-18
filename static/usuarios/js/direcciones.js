document.addEventListener('DOMContentLoaded', function() {
    // Elementos del formulario
    const formDireccion = document.getElementById('form-direccion');
    const busquedaInput = document.getElementById('id_busqueda_direccion');
    const nombreInput = document.getElementById('id_nombre');
    const calleInput = document.getElementById('id_calle');
    const numeroExtInput = document.getElementById('id_numero_exterior');
    const numeroIntInput = document.getElementById('id_numero_interior');
    const coloniaInput = document.getElementById('id_colonia');
    const ciudadInput = document.getElementById('id_ciudad');
    const estadoInput = document.getElementById('id_estado');
    const cpInput = document.getElementById('id_codigo_postal');
    const telefonoInput = document.getElementById('id_telefono');
    const referenciasInput = document.getElementById('id_referencias');
    const principalCheckbox = document.getElementById('id_principal');
    
    // Elementos de respuesta
    const exitoDireccion = document.getElementById('direccion-exito');
    const errorDireccion = document.getElementById('direccion-error');
    
    let autocomplete = null;
    let lastPlace = null;

    // Inicializar autocompletado de Google Maps
    function initAutocomplete() {
        if (!busquedaInput || !window.google || !google.maps || !google.maps.places) {
            console.warn('Google Maps API no disponible');
            return;
        }

        autocomplete = new google.maps.places.Autocomplete(busquedaInput, {
            types: ['geocode'],
            componentRestrictions: { country: 'mx' }, // Restringir a México
            fields: ['address_components', 'formatted_address', 'place_id', 'geometry']
        });

        autocomplete.addListener('place_changed', function() {
            const place = autocomplete.getPlace();
            if (!place.geometry) {
                console.warn('No se encontró información de geometría para esta dirección');
                return;
            }

            lastPlace = place;
            fillAddressFields(place);
        });
    }

    // Llenar campos con datos de Google Places
    function fillAddressFields(place) {
        const addressComponents = place.address_components;
        
        // Mapear componentes de dirección
        const addressMap = {
            street_number: '',
            route: '',
            sublocality_level_1: '', // Colonia
            locality: '', // Ciudad
            administrative_area_level_1: '', // Estado
            postal_code: ''
        };

        // Extraer componentes
        addressComponents.forEach(component => {
            const types = component.types;
            
            if (types.includes('street_number')) {
                addressMap.street_number = component.long_name;
            } else if (types.includes('route')) {
                addressMap.route = component.long_name;
            } else if (types.includes('sublocality_level_1')) {
                addressMap.sublocality_level_1 = component.long_name;
            } else if (types.includes('locality')) {
                addressMap.locality = component.long_name;
            } else if (types.includes('administrative_area_level_1')) {
                addressMap.administrative_area_level_1 = component.long_name;
            } else if (types.includes('postal_code')) {
                addressMap.postal_code = component.long_name;
            }
        });

        // Llenar campos
        if (calleInput) calleInput.value = addressMap.route;
        if (numeroExtInput) numeroExtInput.value = addressMap.street_number;
        if (coloniaInput) coloniaInput.value = addressMap.sublocality_level_1;
        if (ciudadInput) ciudadInput.value = addressMap.locality;
        if (estadoInput) estadoInput.value = addressMap.administrative_area_level_1;
        if (cpInput) cpInput.value = addressMap.postal_code;

        // Generar nombre automático si está vacío
        if (nombreInput && !nombreInput.value.trim()) {
            const tipoDireccion = addressMap.sublocality_level_1 ? 'Casa' : 'Dirección';
            nombreInput.value = `${tipoDireccion} - ${addressMap.locality}`;
        }

        // Mostrar mensaje de éxito
        showMessage('Dirección autocompletada. Revisa y ajusta los campos si es necesario.', 'success');
    }

    // Manejar envío del formulario
    if (formDireccion) {
        formDireccion.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validar campos requeridos
            const camposRequeridos = ['calle', 'colonia', 'ciudad', 'estado', 'codigo_postal'];
            const camposFaltantes = [];
            
            camposRequeridos.forEach(campo => {
                const input = document.getElementById(`id_${campo}`);
                if (input && !input.value.trim()) {
                    camposFaltantes.push(campo);
                }
            });

            if (camposFaltantes.length > 0) {
                showMessage(`Por favor completa los siguientes campos: ${camposFaltantes.join(', ')}`, 'error');
                return;
            }

            // Preparar datos del formulario
            const formData = new FormData(formDireccion);
            
            // Agregar datos de Google Places si están disponibles
            if (lastPlace) {
                const placeData = {
                    place_id: lastPlace.place_id,
                    lat: lastPlace.geometry.location.lat(),
                    lng: lastPlace.geometry.location.lng()
                };
                formData.append('place_data', JSON.stringify(placeData));
            }

            // Enviar formulario
            fetch('/usuarios/direcciones/agregar/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    formDireccion.reset();
                    showMessage(data.message, 'success');
                    cargarDirecciones(); // Recargar lista
                    lastPlace = null; // Resetear lugar seleccionado
                } else {
                    let errorMsg = 'Error al guardar la dirección';
                    if (data.errors) {
                        const errors = Object.values(data.errors).flat();
                        errorMsg = errors.join(', ');
                    }
                    showMessage(errorMsg, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error de conexión', 'error');
            });
        });
    }

    // Función para mostrar mensajes
    function showMessage(message, type) {
        const successEl = document.getElementById('direccion-exito');
        const errorEl = document.getElementById('direccion-error');
        if (typeof mostrarMensajeGlobal === 'function') {
            mostrarMensajeGlobal({
                mensaje: message,
                tipo: type,
                exitoEl: successEl,
                errorEl: errorEl
            });
        } else {
            // Fallback local si la función global no existe
            if (type === 'success') {
                successEl.textContent = message;
                successEl.style.display = 'block';
                errorEl.style.display = 'none';
                setTimeout(() => { successEl.style.display = 'none'; }, 3000);
            } else {
                errorEl.textContent = message;
                errorEl.style.display = 'block';
                successEl.style.display = 'none';
                setTimeout(() => { errorEl.style.display = 'none'; }, 5000);
            }
        }
    }

    // Inicializar autocompletado cuando la API esté lista
    if (window.google && google.maps) {
        initAutocomplete();
    } else {
        // Esperar a que se cargue la API
        window.addEventListener('load', function() {
            if (window.google && google.maps) {
                initAutocomplete();
            }
        });
    }
}); 