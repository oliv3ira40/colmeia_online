(function($) {
  if (!$ || !$.fn || !$.fn.select2) {
    return;
  }

  function initializeSpeciesFilter() {
    // Select do filtro de espécies na lista de colmeias -> Funcionou
    $('.list-filter-dropdown').find('select').select2();

    // Select do formulário de colmeia -> Funcionou
    $('#id_species').select2();

    // Select do formulário de revisões de colmeia-> Não funcionou
    $('#id_hive').select2();

    // TODO: Seria bom que o Select2 estive funcionando em todos o admin do Django.
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSpeciesFilter);
  } else {
    initializeSpeciesFilter();
  }
})(typeof django !== 'undefined' ? django.jQuery : window.jQuery);
