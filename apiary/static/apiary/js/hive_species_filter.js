(function($) {
  if (!$ || !$.fn || !$.fn.select2) {
    return;
  }

  function toggleFieldsetVisibility(fieldset, shouldShow) {
    if (!fieldset) {
      return;
    }
    fieldset.style.display = shouldShow ? '' : 'none';
  }

  function bindRevisionTypeWatcher() {
    var select = document.getElementById('id_review_type');
    if (!select) {
      return;
    }

    var harvestFieldset = document.querySelector('fieldset.revision-harvest-group');
    var feedingFieldset = document.querySelector('fieldset.revision-feeding-group');

    function updateVisibility() {
      var value = select.value;
      toggleFieldsetVisibility(harvestFieldset, value === 'colheita');
      toggleFieldsetVisibility(feedingFieldset, value === 'alimentacao');
    }

    select.addEventListener('change', updateVisibility);
    updateVisibility();
  }

  function initializeSpeciesFilter() {
    // Select do filtro de espécies na lista de colmeias
    $('.list-filter-dropdown').find('select').select2();

    // Select do formulário de colmeia
    $('#id_species').select2();

    // Select do formulário de revisões de colmeia
    $('#id_hive').select2();

    bindRevisionTypeWatcher();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSpeciesFilter);
  } else {
    initializeSpeciesFilter();
  }
})(typeof django !== 'undefined' ? django.jQuery : window.jQuery);
