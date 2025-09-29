$(function() {
    var client_form = $('#client_form');

    if (client_form.length) {
        var discountcoupon_amount = client_form.find('.field-cpf');
        var input_cpf = discountcoupon_amount.find('input#id_cpf');
        input_cpf.mask('000.000.000-00', {reverse: true});
        
        var discountcoupon_amount = client_form.find('.field-phone');
        var input_phone = discountcoupon_amount.find('input#id_phone');
        input_phone.mask('00 00000-0000', {reverse: true});

        var birth_date = client_form.find('.field-birth_date');
        var input_date = birth_date.find('input#id_birth_date');
        input_date.mask('00/00/0000');
    }
})
