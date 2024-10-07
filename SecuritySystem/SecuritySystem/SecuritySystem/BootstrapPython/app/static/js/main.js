function updateDoorState() {
    const selectedState = $('input[type=radio][name=doorstate]:checked').val();
    const hostname = window.location.hostname;

    if(selectedState === 'unlocked'){
        $('#lockstate').html('Unlocked');
        fetch(`http://${hostname}:5000/door_state`, {  // Usar el hostname dinámico
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'state': 'unlocked'
            })
        });
    } else {
        $('#lockstate').html('Locked');
        fetch(`http://${hostname}:5000/door_state`, {  // Usar el hostname dinámico
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'state': 'locked'
            })
        });
    }
}

// Ejecutar la función al cambiar el estado del radio button
$('input[type=radio][name=doorstate]').on('change', function(){
    updateDoorState(); 
});

document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://192.168.2.1:5000');

    socket.on('connect', function() {
        console.log("Conectado al servidor Socket.IO");
    });

    socket.on('reload_page', function() {
        console.log("Evento de recarga recibido, recargando la página...");
        
        location.reload();  // Este debería recargar la página
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Tiempo en milisegundos para verificar la sesión (por ejemplo, cada 30 segundos)
    const checkInterval = 30000;

    function checkSession() {
        fetch('/check_session')
            .then(response => {
                if (response.status === 401) {
                    console.log("Sesión expirada, recargando la página...");
                    location.reload();  // Recargar la página
                }
            })
            .catch(error => {
                console.error("Error al verificar la sesión:", error);
            });
    }

    // Verificar la sesión periódicamente
    setInterval(checkSession, checkInterval);
});
