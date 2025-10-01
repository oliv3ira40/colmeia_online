(function($) {
  if (!$ || !$.fn || !$.fn.select2) {
    return;
  }

  function initializeSpeciesFilter() {
    // Select do filtro de espécies na lista de colmeias
    $('.list-filter-dropdown').find('select').select2();

    // Select do formulário de colmeia
    $('#id_species').select2();

    // Select do formulário de revisões de colmeia
    $('#id_hive').select2();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSpeciesFilter);
  } else {
    initializeSpeciesFilter();
  }
})(typeof django !== 'undefined' ? django.jQuery : window.jQuery);
