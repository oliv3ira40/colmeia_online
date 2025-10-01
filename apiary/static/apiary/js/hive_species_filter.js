(function($) {
  if (!$ || !$.fn || !$.fn.select2) {
    return;
  }

  function initializeSpeciesFilter() {
    var filterSelect = document.querySelector(
      '#changelist-filter select[name="species__id__exact"]'
    );

    if (!filterSelect) {
      return;
    }

    var $filterSelect = $(filterSelect);

    if ($filterSelect.hasClass('select2-hidden-accessible')) {
      return;
    }

    var placeholderOption = filterSelect.querySelector('option[value=""]');
    var placeholderText = placeholderOption
      ? placeholderOption.textContent.trim()
      : filterSelect.getAttribute('data-placeholder') || '';

    $filterSelect.select2({
      width: '100%',
      allowClear: true,
      placeholder: placeholderText,
      dropdownAutoWidth: true
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSpeciesFilter);
  } else {
    initializeSpeciesFilter();
  }
})(typeof django !== 'undefined' ? django.jQuery : window.jQuery);
