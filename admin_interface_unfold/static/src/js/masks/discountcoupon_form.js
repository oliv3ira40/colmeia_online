$(function() {
    var discountcoupon_form = $('#discountcoupon_form');

    if (discountcoupon_form.length) {
        var discountcoupon_amount = discountcoupon_form.find('.field-discount_amount');
        var input_discountcoupon_amount = discountcoupon_amount.find('input#id_discount_amount');
        input_discountcoupon_amount.attr('type', 'text');
        input_discountcoupon_amount.mask('00.000.000,00', {reverse: true});
        
        var discount_percentage = discountcoupon_form.find('.field-discount_percentage');
        var input_discount_percentage = discount_percentage.find('input#id_discount_percentage');
        input_discount_percentage.attr('type', 'text');
        input_discount_percentage.mask('00%', {reverse: true});

        var max_value_discount = discountcoupon_form.find('.field-max_value_discount');
        var input_max_value_discount = max_value_discount.find('input#id_max_value_discount');
        input_max_value_discount.attr('type', 'text');
        input_max_value_discount.mask('00.000.000,00', {reverse: true});

        // Remova a formatação antes de enviar o formulário
        discountcoupon_form.on('submit', function() {
            var formatted_value = input_discountcoupon_amount.val();
            var numeric_value = formatted_value.replace(/\./g, '').replace(',', '.');
            input_discountcoupon_amount.val(numeric_value);

            var formatted_percentage = input_discount_percentage.val();
            var numeric_percentage = formatted_percentage.replace('%', '');
            input_discount_percentage.val(numeric_percentage);

            var formatted_max_value_discount = input_max_value_discount.val();
            var numeric_max_value_discount = formatted_max_value_discount.replace(/\./g, '').replace(',', '.');
            input_max_value_discount.val(numeric_max_value_discount);
        });
    }
})
