$(document).ready(function() {

    // 1. RESTRICCIÓN DE ENTRADA: Solo números en los inputs de cantidad
    $(document).on('keypress', '.update-qty', function(e) {
        if (e.which < 48 || e.which > 57) {
            e.preventDefault();
        }
    });

    // 2. ACTUALIZACIÓN MANUAL: Al perder el foco (blur) o presionar Enter
    $(document).on('blur', '.update-qty', function() {
        var id = $(this).attr('pid');
        var qty = $(this).val();
        var inputField = $(this);

        // Si el campo queda vacío o es 0, por defecto ponemos 1
        if (qty == "" || qty == "0") {
            qty = 1;
            inputField.val(1);
        }

        $.ajax({
            type: 'GET',
            url: '/update-qty-manual',
            data: {
                cart_id: id,
                qty: qty
            },
            success: function(data) {
                // Sincronizamos el input con lo que diga el servidor (por si excedió el stock)
                inputField.val(data.quantity);
                // Actualizamos totales globales
                $('#amount_tt').text(data.amount);
                $('#totalamount').text(data.total);
                // Actualizamos el total de esta fila específica
                $(`#line_total${id}`).text(data.line_total);
            }
        });
    });

    // Disparar la actualización manual al presionar Enter
    $(document).on('keyup', '.update-qty', function(e) {
        if (e.keyCode === 13) {
            $(this).blur();
        }
    });

    // 3. BOTÓN MÁS (+): Aumentar cantidad
    $('.plus-cart').off('click').on('click', function() {
        var id = $(this).attr('pid').toString();
        var inputField = $(this).siblings('input');

        $.ajax({
            type: 'GET',
            url: '/pluscart',
            data: { cart_id: id },
            success: function(data) {
                inputField.val(data.quantity);
                $('#amount_tt').text(data.amount);
                $('#totalamount').text(data.total);
                $(`#line_total${id}`).text(data.line_total); 
            }
        });
    });

    // 4. BOTÓN MENOS (-): Disminuir cantidad
    $('.minus-cart').off('click').on('click', function() {
        var id = $(this).attr('pid').toString();
        var inputField = $(this).siblings('input');

        $.ajax({
            type: 'GET',
            url: '/minuscart',
            data: { cart_id: id },
            success: function(data) {
                inputField.val(data.quantity);
                $('#amount_tt').text(data.amount);
                $('#totalamount').text(data.total);
                $(`#line_total${id}`).text(data.line_total); 
            }
        });
    });

    // 5. BOTÓN ELIMINAR: Quitar producto del carrito
    $('.remove-cart').off('click').on('click', function() {
        var id = $(this).attr('pid').toString();
        var row = $(this).closest('.card'); // Selecciona la tarjeta del producto

        $.ajax({
            type: 'GET',
            url: '/removecart',
            data: { cart_id: id },
            success: function(data) {
                $('#amount_tt').text(data.amount);
                $('#totalamount').text(data.total);
                
                // Efecto visual de desvanecimiento antes de eliminar del DOM
                row.fadeOut(300, function() { 
                    $(this).remove(); 
                });
                
                // Si el carrito llega a cero, recargamos para mostrar el mensaje de "Carrito Vacío"
                if (data.amount === "0") {
                    location.reload();
                }
            }
        });
    });
    // 6. AÑADIR AL CARRITO DESDE BUSQUEDA/HOME (AJAX)
$(document).on('click', '.add-to-cart-ajax', function(e) {
    e.preventDefault();
    var id = $(this).attr('pid');
    var btn = $(this);

    $.ajax({
        type: 'GET',
        url: '/add-to-cart/' + id,
        success: function(data) {
            // Cambio visual para que el usuario sepa que funcionó
            btn.html('<i class="fa-solid fa-check me-1"></i> ¡Agregado!');
            btn.addClass('btn-success').removeClass('btn-zora');
            
            // Si tienes un contador de productos en el navbar, actualízalo aquí
            // $('#cart-count').text(data.total_items);
            
            setTimeout(function() {
                btn.html('<i class="fa-solid fa-cart-plus me-1"></i> Añadir al carrito');
                btn.addClass('btn-zora').removeClass('btn-success');
            }, 2000);
        },
        error: function() {
            alert("Hubo un error al agregar el producto.");
        }
    });
});

});