$(function() {
    var package_form = $('#package_form');

    if (package_form.length) {
        var value = package_form.find('.field-value');
        var input_value = value.find('input#id_value');
        input_value.attr('type', 'text');
        input_value.mask('00.000.000,00', {reverse: true});
        
        init_masks_date_field()

        var clear = setInterval(function() {
            var add_row = $('.add-row');
            if (add_row.length) {
                clearInterval(clear);
                var link = add_row.find('a');
                link.on('click', function() {
                    setTimeout(function() {
                        init_masks_date_field();
                    }, 100);
                });
            }
        }, 100);

        // Remova a formatação antes de enviar o formulário
        package_form.on('submit', function() {
            var formatted_value = input_value.val();
            var numeric_value = formatted_value.replace(/\./g, '').replace(',', '.');
            input_value.val(numeric_value);
        });

        function init_masks_date_field() {
            var date = package_form.find('.field-date');
            var input_date = date.find('input.vDateField');
            var input_time = date.find('input.vTimeField');
            input_date.mask('00/00/0000');
            input_time.mask('00:00:00');
        }
    }
})
