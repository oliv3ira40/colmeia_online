/* global window, document */
(function () {
  "use strict";

  // Configure which file inputs receive a preview using the same style as
  // `conditional-fields.js`. The `when` key accepts `nameEndsWith`,
  // `nameEquals`, `idEquals`, `selector`, or `containerClass` (CSS class without
  // the dot) and the remaining keys customise the preview labels.
  const FIELDS = [
    {
      when: { nameEndsWith: "photo" },
      previewLabel: "Prévia da imagem"
    },
    {
      when: { nameEndsWith: "file" },
      previewLabel: "Prévia da imagem"
    },
  ];

  const ATTRIBUTE_SELECTOR = 'input[type="file"][data-image-preview="true"]';
  const FILE_SELECTOR = 'input[type="file"]';
  const optionsByInput = new WeakMap();

  function getQueryRoot(root) {
    if (!root) {
      return document;
    }
    if (root.nodeType === 1 || root.nodeType === 9 || root.nodeType === 11) {
      return root;
    }
    if (root.ownerDocument) {
      return root;
    }
    return document;
  }

  function collectElements(root, selector) {
    if (!selector) {
      return [];
    }
    const context = getQueryRoot(root);
    const elements = [];
    if (context.nodeType === 1 && context.matches && context.matches(selector)) {
      elements.push(context);
    }
    if (context.querySelectorAll) {
      const found = context.querySelectorAll(selector);
      for (let index = 0; index < found.length; index += 1) {
        elements.push(found[index]);
      }
    }
    return elements;
  }

  function uniqueElements(elements) {
    const unique = [];
    const marker = new Set();
    elements.forEach((element) => {
      if (!element || marker.has(element)) {
        return;
      }
      marker.add(element);
      unique.push(element);
    });
    return unique;
  }

  function ensureFileInputs(elements) {
    const inputs = [];
    elements.forEach((element) => {
      if (!element) {
        return;
      }
      if (element.matches && element.matches(FILE_SELECTOR)) {
        inputs.push(element);
        return;
      }
      if (element.querySelector) {
        const candidate = element.querySelector(FILE_SELECTOR);
        if (candidate) {
          inputs.push(candidate);
        }
      }
    });
    return uniqueElements(inputs);
  }

  function findById(root, id) {
    if (!id) {
      return null;
    }
    const context = getQueryRoot(root);
    if (context.getElementById) {
      return context.getElementById(id);
    }
    if (context.ownerDocument && context.ownerDocument.getElementById) {
      return context.ownerDocument.getElementById(id);
    }
    return document.getElementById(id);
  }

  function findInputsByWhen(when, root) {
    if (!when) {
      return [];
    }

    const matches = [];

    if (when.selector) {
      matches.push.apply(matches, collectElements(root, when.selector));
    }
    if (when.containerClass) {
      matches.push.apply(matches, collectElements(root, `.${when.containerClass}`));
    }
    if (when.nameEquals) {
      matches.push.apply(
        matches,
        collectElements(root, `${FILE_SELECTOR}[name="${when.nameEquals}"]`),
      );
    }
    if (when.nameEndsWith) {
      matches.push.apply(
        matches,
        collectElements(root, `${FILE_SELECTOR}[name$="${when.nameEndsWith}"]`),
      );
    }
    if (when.idEquals) {
      const element = findById(root, when.idEquals);
      if (element) {
        matches.push(element);
      }
    }

    return ensureFileInputs(matches);
  }

  function registerInput(input, options) {
    if (!input) {
      return null;
    }
    const current = optionsByInput.get(input) || {};
    const merged = Object.assign({}, current, options || {});
    optionsByInput.set(input, merged);
    return input;
  }

  function extractOptionsFromDataset(input) {
    if (!input || !input.dataset) {
      return {};
    }
    const dataset = input.dataset;
    const options = {};
    if (dataset.previewLabel) {
      options.previewLabel = dataset.previewLabel;
    }
    if (dataset.initialPreviewUrl) {
      options.initialUrl = dataset.initialPreviewUrl;
    }
    if (dataset.imagePreviewThumbnailClass) {
      options.thumbnailClass = dataset.imagePreviewThumbnailClass;
    }
    return options;
  }

  function collectConfiguredInputs(root) {
    const inputs = [];
    const seen = new Set();

    const marked = collectElements(root, ATTRIBUTE_SELECTOR);
    marked.forEach((input) => {
      registerInput(input, extractOptionsFromDataset(input));
      if (!seen.has(input)) {
        seen.add(input);
        inputs.push(input);
      }
    });

    FIELDS.forEach((config) => {
      if (!config || typeof config !== "object") {
        return;
      }
      const when = config.when || {};
      const options = Object.assign({}, config);
      delete options.when;

      const matchedInputs = findInputsByWhen(when, root);
      matchedInputs.forEach((input) => {
        registerInput(input, options);
        if (!seen.has(input)) {
          seen.add(input);
          inputs.push(input);
        }
      });
    });

    return inputs;
  }

  function buildPreviewElements(options) {
    const wrapper = document.createElement("div");
    wrapper.className = "image-preview-wrapper";

    const image = document.createElement("img");
    image.className = options.thumbnailClass || "thumb-150";
    image.alt = options.previewLabel || "Prévia"
    image.hidden = true;

    const label = document.createElement("small");
    // label.textContent = options.previewLabel || "";

    wrapper.appendChild(label);
    wrapper.appendChild(image);

    return { wrapper, image };
  }

  function findInitialPreviewUrl(input, options) {
    if (options && options.initialUrl) {
      return options.initialUrl;
    }
    if (input && input.getAttribute) {
      const attributeValue = input.getAttribute("data-initial-preview-url");
      if (attributeValue) {
        return attributeValue;
      }
    }
    const clearable = input ? input.closest(".clearable-file-input") : null;
    const fileUpload = input ? input.closest(".file-upload") : null;
    const container = clearable || fileUpload;
    if (container) {
      const anchor = container.querySelector("a[href]");
      if (anchor && anchor.href) {
        return anchor.href;
      }
    }
    return "";
  }

  function ensureFieldContainer(input, previewWrapper) {
    if (!input || !previewWrapper) {
      return null;
    }

    if (!input.closest) {
      return null;
    }

    const fileUpload = input.closest("p.file-upload");
    if (!fileUpload || !fileUpload.parentElement) {
      return null;
    }

    const parent = fileUpload.parentElement;
    let container = parent;

    if (!parent.classList.contains("image-preview-field-container")) {
      container = document.createElement("div");
      container.className = "image-preview-field-container";
      parent.insertBefore(container, fileUpload);
      container.appendChild(fileUpload);
    }

    container.appendChild(previewWrapper);
    return container;
  }

  function updatePreviewVisibility(elements, context) {
    const imageUrl = context && context.imageUrl;

    if (imageUrl) {
      elements.image.src = imageUrl;
      elements.image.hidden = false;
      elements.wrapper.hidden = false;
    } else {
      elements.image.removeAttribute("src");
      elements.image.hidden = true;
      elements.wrapper.hidden = true;
    }
  }

  function handleChange(input, elements, state) {
    const clearCheckbox = state.clearCheckbox;
    const initialUrl = state.initialUrl;

    if (!input.files || input.files.length === 0) {
      if (clearCheckbox && clearCheckbox.checked) {
        updatePreviewVisibility(elements, { imageUrl: "" });
        return;
      }
      if (initialUrl) {
        updatePreviewVisibility(elements, {
          imageUrl: initialUrl,
        });
      } else {
        updatePreviewVisibility(elements, { imageUrl: "" });
      }
      return;
    }

    const file = input.files[0];
    if (!window.FileReader) {
      updatePreviewVisibility(elements, { imageUrl: "" });
      return;
    }

    const reader = new window.FileReader();
    reader.addEventListener("load", function (event) {
      updatePreviewVisibility(elements, {
        imageUrl: event.target && event.target.result,
      });
      if (clearCheckbox) {
        clearCheckbox.checked = false;
      }
    });
    reader.addEventListener("error", function () {
      updatePreviewVisibility(elements, { imageUrl: "" });
    });
    reader.readAsDataURL(file);
  }

  function bindClearCheckbox(clearCheckbox, input, elements, state) {
    if (!clearCheckbox) {
      return;
    }

    clearCheckbox.addEventListener("change", function () {
      if (clearCheckbox.checked) {
        updatePreviewVisibility(elements, { imageUrl: "" });
        if (input.value) {
          input.value = "";
        }
      } else if (!input.files || input.files.length === 0) {
        if (state.initialUrl) {
          updatePreviewVisibility(elements, {
            imageUrl: state.initialUrl,
          });
        } else {
          updatePreviewVisibility(elements, { imageUrl: "" });
        }
      }
    });
  }

  function initialiseInput(input) {
    if (!input || input.dataset.imagePreviewInitialised === "true") {
      return;
    }
    input.dataset.imagePreviewInitialised = "true";

    const configOptions = optionsByInput.get(input) || {};
    const datasetOptions = extractOptionsFromDataset(input);
    const options = Object.assign({}, configOptions, datasetOptions);

    const elements = buildPreviewElements(options);
    const container = ensureFieldContainer(input, elements.wrapper);

    if (!container) {
      if (input.parentElement && input.parentElement.appendChild) {
        input.parentElement.appendChild(elements.wrapper);
      } else {
        input.insertAdjacentElement("afterend", elements.wrapper);
      }
    }

    const state = {
      initialUrl: findInitialPreviewUrl(input, options),
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
    const inputs = collectConfiguredInputs(root || document);
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
