$(function() {
    var service_form = $('#service_form');

    if (service_form.length) {
        var value = service_form.find('.field-average_price');
        var input_value = value.find('input#id_average_price');
        input_value.attr('type', 'text');
        input_value.mask('00.000.000,00', {reverse: true});
        
        var date = service_form.find('.field-average_duration');
        var input_time = date.find('input.vTimeField');
        input_time.mask('00:00:00');

        // Remova a formatação antes de enviar o formulário
        service_form.on('submit', function() {
            var formatted_value = input_value.val();
            var numeric_value = formatted_value.replace(/\./g, '').replace(',', '.');
            input_value.val(numeric_value);
        });
    }
})
