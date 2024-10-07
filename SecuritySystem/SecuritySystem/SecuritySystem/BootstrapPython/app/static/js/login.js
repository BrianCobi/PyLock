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