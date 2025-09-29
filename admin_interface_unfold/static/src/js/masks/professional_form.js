$(function() {
    var professional_form = $('#professional_form');

    if (professional_form.length) {
        var discountcoupon_amount = professional_form.find('.field-cpf');
        var input_cpf = discountcoupon_amount.find('input#id_cpf');
        input_cpf.mask('000.000.000-00', {reverse: true});
        
        var discountcoupon_amount = professional_form.find('.field-phone');
        var input_phone = discountcoupon_amount.find('input#id_phone');
        input_phone.mask('00 00000-0000', {reverse: true});
    }
})
