(function($) {
  if (!$ || !$.fn || !$.fn.select2) {
    return;
  }

  function getSelects(context) {
    return $(context)
      .find('select')
      .filter(function() {
        var $select = $(this);
        return (
          !$select.is('.select2-hidden-accessible') &&
          !$select.data('select2-initialized') &&
          !$select.prop('disabled')
        );
      });
  }

  function initializeSelect2(context) {
    getSelects(context).each(function() {
      var $select = $(this);
      $select.select2({
        width: 'style'
      });
      $select.data('select2-initialized', true);
    });
  }

  function onReady() {
    initializeSelect2(document);
    $(document).on('formset:added', function(_event, $row) {
      initializeSelect2($row);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
})(typeof django !== 'undefined' ? django.jQuery : window.jQuery);
