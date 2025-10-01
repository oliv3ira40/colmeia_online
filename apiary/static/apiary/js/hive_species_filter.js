(function($) {
  if (!$ || !$.fn || !$.fn.select2) {
    return;
  }

  function initializeSpeciesFilter() {
    setTimeout(function() {
      // Select do filtro de espécies na lista de colmeias
      $('.list-filter-dropdown').find('select').select2();

      // Select do formulário de colmeia
      var speciesSelect = $('#id_species[name="species"]');
      if (speciesSelect.length) {
        speciesSelect.select2();
      }

      // Select do formulário de revisões de colmeia
      $('#id_hive').select2();
      
      // Select de cidades
      $('#id_city').select2();
      
      // Select do formulário de origem de colmeia
      $('#id_origin_hive').select2();

      // Select do formulário de caixa de colmeia
      $('#id_box_model').select2();
    }, 200);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSpeciesFilter);
  } else {
    initializeSpeciesFilter();
  }
})(typeof django !== 'undefined' ? django.jQuery : window.jQuery);
