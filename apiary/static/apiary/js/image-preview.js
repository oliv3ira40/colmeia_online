/* global window, document */
(function () {
  "use strict";

  const SELECTOR = 'input[type="file"][data-image-preview="true"]';

  function toArray(list) {
    if (!list) {
      return [];
    }
    return Array.prototype.slice.call(list);
  }

  function buildPreviewElements(input) {
    const wrapper = document.createElement("div");
    wrapper.className = "image-preview-wrapper";

    const header = document.createElement("div");
    header.className = "image-preview-header";

    const label = document.createElement("small");
    label.textContent = input.getAttribute("data-preview-label") || "Prévia";
    header.appendChild(label);

    const link = document.createElement("a");
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = input.getAttribute("data-preview-open-label") || "Abrir em nova aba";
    link.className = "image-preview-link";
    link.hidden = true;
    header.appendChild(link);

    const image = document.createElement("img");
    image.className = "thumb-150";
    image.alt = label.textContent || "Prévia";
    image.hidden = true;

    wrapper.appendChild(header);
    wrapper.appendChild(image);

    return { wrapper, label, image, link };
  }

  function findWidgetContainer(input) {
    return (
      input.closest(".clearable-file-input") ||
      input.closest(".form-row") ||
      input.parentElement ||
      input
    );
  }

  function updatePreviewVisibility(elements, { imageUrl, linkUrl }) {
    const { wrapper, image, link } = elements;

    if (imageUrl) {
      image.src = imageUrl;
      image.hidden = false;
      wrapper.hidden = false;
    } else {
      image.removeAttribute("src");
      image.hidden = true;
      wrapper.hidden = true;
    }

    if (linkUrl) {
      link.href = linkUrl;
      link.hidden = false;
    } else {
      link.removeAttribute("href");
      link.hidden = true;
    }
  }

  function handleChange(input, elements, state) {
    const clearCheckbox = state.clearCheckbox;
    const initialUrl = state.initialUrl;

    if (!input.files || input.files.length === 0) {
      if (clearCheckbox && clearCheckbox.checked) {
        updatePreviewVisibility(elements, { imageUrl: "", linkUrl: "" });
        return;
      }
      if (initialUrl) {
        updatePreviewVisibility(elements, { imageUrl: initialUrl, linkUrl: initialUrl });
      } else {
        updatePreviewVisibility(elements, { imageUrl: "", linkUrl: "" });
      }
      return;
    }

    const file = input.files[0];
    if (!window.FileReader) {
      updatePreviewVisibility(elements, { imageUrl: "", linkUrl: "" });
      return;
    }

    const reader = new window.FileReader();
    reader.addEventListener("load", function (event) {
      updatePreviewVisibility(elements, { imageUrl: event.target.result, linkUrl: "" });
      if (clearCheckbox) {
        clearCheckbox.checked = false;
      }
    });
    reader.addEventListener("error", function () {
      updatePreviewVisibility(elements, { imageUrl: "", linkUrl: "" });
    });
    reader.readAsDataURL(file);
  }

  function bindClearCheckbox(clearCheckbox, input, elements, state) {
    if (!clearCheckbox) {
      return;
    }

    clearCheckbox.addEventListener("change", function () {
      if (clearCheckbox.checked) {
        updatePreviewVisibility(elements, { imageUrl: "", linkUrl: "" });
        if (input.value) {
          input.value = "";
        }
      } else if (!input.files || input.files.length === 0) {
        if (state.initialUrl) {
          updatePreviewVisibility(elements, { imageUrl: state.initialUrl, linkUrl: state.initialUrl });
        } else {
          updatePreviewVisibility(elements, { imageUrl: "", linkUrl: "" });
        }
      }
    });
  }

  function initialiseInput(input) {
    if (!input || input.dataset.imagePreviewInitialised === "true") {
      return;
    }
    input.dataset.imagePreviewInitialised = "true";

    const initialUrl = input.getAttribute("data-initial-preview-url") || "";
    const elements = buildPreviewElements(input);
    const widgetContainer = findWidgetContainer(input);

    if (widgetContainer && widgetContainer !== input) {
      widgetContainer.insertAdjacentElement("afterend", elements.wrapper);
    } else if (input.parentElement) {
      input.parentElement.insertBefore(elements.wrapper, input.nextSibling);
    } else {
      input.insertAdjacentElement("afterend", elements.wrapper);
    }

    const state = {
      initialUrl,
      clearCheckbox: null,
    };

    const clearableContainer = input.closest(".clearable-file-input");
    if (clearableContainer) {
      state.clearCheckbox = clearableContainer.querySelector('input[type="checkbox"]');
    }

    bindClearCheckbox(state.clearCheckbox, input, elements, state);
    handleChange(input, elements, state);

    input.addEventListener("change", function () {
      handleChange(input, elements, state);
    });
  }

  function initialise(root) {
    const inputs = toArray((root || document).querySelectorAll(SELECTOR));
    inputs.forEach(initialiseInput);
  }

  window.addEventListener("DOMContentLoaded", function () {
    initialise(document);
  });

  document.addEventListener("formset:added", function (event) {
    if (!event || !event.target) {
      return;
    }
    initialise(event.target);
  });
})();
