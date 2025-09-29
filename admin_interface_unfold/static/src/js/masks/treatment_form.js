$(function() {
    var treatment_form = $('#treatment_form');

    if (treatment_form.length) {
        var value = treatment_form.find('.field-value');
        var input_value = value.find('input#id_value');
        input_value.attr('type', 'text');
        input_value.mask('00.000.000,00', {reverse: true});
        
        var date = treatment_form.find('.field-date');
        var input_date = date.find('input.vDateField');
        var input_time = date.find('input.vTimeField');
        input_date.mask('00/00/0000');
        input_time.mask('00:00:00');

        // Remova a formatação antes de enviar o formulário
        treatment_form.on('submit', function() {
            var formatted_value = input_value.val();
            var numeric_value = formatted_value.replace(/\./g, '').replace(',', '.');
            input_value.val(numeric_value);
        });
    }
})
