/* global window, document */
const RULES = [
  {
    when: { nameEndsWith: "review_type", equals: "colheita" },
    then: [
      { nameEndsWith: "honey_harvest_amount" },
      { nameEndsWith: "propolis_harvest_amount" },
      { nameEndsWith: "wax_harvest_amount" },
      { nameEndsWith: "pollen_harvest_amount" },
      { nameEndsWith: "harvest_notes" },
    ],
  },
  {
    when: { nameEndsWith: "review_type", equals: "alimentacao" },
    then: [
      { nameEndsWith: "energetic_food_type" },
      { nameEndsWith: "energetic_food_amount" },
      { nameEndsWith: "protein_food_type" },
      { nameEndsWith: "protein_food_amount" },
      { nameEndsWith: "feeding_notes" },
    ],
  },
  {
    when: { nameEndsWith: "acquisition_method", equals: "compra" },
    then: [
      { nameEndsWith: "acquisition_date", required: true },
      { nameEndsWith: "origin", required: true }
    ],
  },
  // Não vazio ou seja, qualquer valor que não seja "---"
  {
    when: { nameEndsWith: "apiary", notEmpty: true },
    then: [{ nameEndsWith: "position", required: true }],
  },
  {
    when: { nameEndsWith: "acquisition_method", equals: "divisao" },
    then: [{ nameEndsWith: "origin_hive", required: true }],
  },
  {
    when: { nameEndsWith: "acquisition_method", equals: "captura" },
    then: [{ nameEndsWith: "transfer_box_date", required: true }],
  },
];

(function () {
  "use strict";

  const FIELD_CONTAINER_SELECTORS = [
    ".form-row",
    ".form-group",
    ".fieldBox",
    ".field-box",
    ".form-field",
    "div.field",
    "li.form-row",
    "td[class*='field-']",
  ];

  const targetState = new WeakMap();
  const ruleTrackedTargets = new Map();
  const controllerBindings = new WeakMap();

  // console.log("Conditional fields script loaded");

  function cssEscape(value) {
    if (typeof value !== "string") {
      return "";
    }
    if (window.CSS && typeof window.CSS.escape === "function") {
      return window.CSS.escape(value);
    }
    return value.replace(/([\0-\x1f\x7f-\x9f\-\[\]{}()*+?.,\\^$|#\s])/g, "\\$1");
  }

  function toArray(value) {
    if (Array.isArray(value)) {
      return value.slice();
    }
    if (value === undefined || value === null) {
      return [];
    }
    return [value];
  }

  function getRootNode(root) {
    if (!root) {
      return document;
    }
    if (root.jquery) {
      return root[0] || document;
    }
    if (root.nodeType === 1 || root.nodeType === 9 || root.nodeType === 11) {
      return root;
    }
    return document;
  }

  function collectElements(root, selector) {
    const node = getRootNode(root);
    const elements = [];
    if (!selector) {
      return elements;
    }
    if (node.nodeType === 1 && node.matches && node.matches(selector)) {
      elements.push(node);
    }
    const queryResult = (node.querySelectorAll || document.querySelectorAll).call(
      node,
      selector,
    );
    for (let i = 0; i < queryResult.length; i += 1) {
      elements.push(queryResult[i]);
    }
    return elements;
  }

  function findControllerElements(when, root) {
    if (!when) {
      return [];
    }
    let elements = [];
    if (when.nameEndsWith) {
      const selector = `[name$="${when.nameEndsWith}"]`;
      elements = collectElements(root, selector);
    } else if (when.idEquals) {
      const node = getRootNode(root);
      const element = node.getElementById
        ? node.getElementById(when.idEquals)
        : document.getElementById(when.idEquals);
      if (element) {
        elements = [element];
      }
    }
    if (when.idEquals) {
      const id = when.idEquals;
      elements = elements.filter((element) => element.id === id);
    }
    return elements;
  }

  function getNamePrefix(fullName, suffix) {
    if (!fullName || !suffix) {
      return null;
    }
    if (!fullName.endsWith(suffix)) {
      return null;
    }
    return fullName.slice(0, fullName.length - suffix.length);
  }

  function findTargets(configs, controller, when) {
    const targets = [];
    const prefix = controller ? getNamePrefix(controller.name || "", when && when.nameEndsWith) : null;
    configs.forEach((config) => {
      if (config.nameEndsWith) {
        const selector = `[name$="${config.nameEndsWith}"]`;
        const elements = collectElements(document, selector);
        elements.forEach((element) => {
          if (prefix !== null) {
            const targetName = element.name || "";
            if (!targetName.endsWith(config.nameEndsWith)) {
              return;
            }
            if (prefix && !targetName.startsWith(prefix)) {
              return;
            }
            if (!prefix && targetName.includes("-")) {
              return;
            }
          }
          targets.push({ element, config });
        });
      }
      if (config.idEquals) {
        const escaped = cssEscape(config.idEquals);
        const selector = `#${escaped}`;
        const elements = collectElements(document, selector);
        elements.forEach((element) => {
          if (prefix !== null) {
            const targetName = element.name || "";
            if (targetName && prefix && !targetName.startsWith(prefix)) {
              return;
            }
            if (targetName && !prefix && targetName.includes("-")) {
              return;
            }
          }
          targets.push({ element, config });
        });
      }
    });
    return targets;
  }

  function getRadioGroupElements(controller) {
    const name = controller && controller.name;
    if (!name) {
      return [controller];
    }
    const selector = `input[type="radio"][name="${cssEscape(name)}"]`;
    return collectElements(document, selector);
  }

  function getControllerValue(controller) {
    if (!controller) {
      return null;
    }
    const tagName = controller.tagName ? controller.tagName.toLowerCase() : "";
    if (tagName === "input") {
      const type = controller.type;
      if (type === "radio") {
        const radios = getRadioGroupElements(controller);
        for (let i = 0; i < radios.length; i += 1) {
          if (radios[i].checked) {
            return radios[i].value;
          }
        }
        return null;
      }
      if (type === "checkbox") {
        return controller.checked ? controller.value : "";
      }
    }
    return controller.value;
  }

  function isControllerChecked(controller) {
    if (!controller) {
      return false;
    }
    if (controller.type === "radio") {
      return controller.checked;
    }
    if (controller.type === "checkbox") {
      return controller.checked;
    }
    return Boolean(controller.value);
  }

  function evaluateCondition(controller, when) {
    if (!when) return true;

    // Começa assumindo que tudo passa; cada checagem vai fazendo AND
    let ok = true;
    const val = getControllerValue(controller);

    // 1) checkbox/radio marcado ou não
    if (Object.prototype.hasOwnProperty.call(when, "isChecked")) {
      ok = ok && (isControllerChecked(controller) === Boolean(when.isChecked));
    }

    // 2) igualdade exata
    if (Object.prototype.hasOwnProperty.call(when, "equals")) {
      ok = ok && (val === when.equals);
    }

    // 3) valor dentro de um conjunto
    if (Object.prototype.hasOwnProperty.call(when, "valueIn")) {
      const values = toArray(when.valueIn);
      ok = ok && values.includes(val);
    }

    // 4) açúcar sintático: "não vazio" (ignora null/undefined/"" após trim)
    //    Útil para selects do Django Admin cujo vazio tem value "".
    if (when.notEmpty === true) {
      const s = (val == null) ? "" : String(val).trim();
      ok = ok && (s !== "");
    }

    // 5) inversor genérico: se when.not === true, inverte o resultado.
    //    Ex.: { equals: "", not: true }  => "diferente de vazio"
    if (when.not === true) {
      ok = !ok;
    }

    return ok;
  }

  function findFieldContainer(element) {
    if (!element) {
      return null;
    }
    for (let i = 0; i < FIELD_CONTAINER_SELECTORS.length; i += 1) {
      const selector = FIELD_CONTAINER_SELECTORS[i];
      if (element.closest) {
        const container = element.closest(selector);
        if (container) {
          return container;
        }
      }
    }
    if (element.closest) {
      const cell = element.closest("td");
      if (cell) {
        return cell;
      }
    }
    return element.parentElement || null;
  }

  function updateTargetState(element, ruleIndex, isActive, isRequired) {
    if (!element) {
      return;
    }
    let state = targetState.get(element);
    if (!state) {
      state = {
        visibleRules: new Set(),
        requiredRules: new Set(),
        originalDisplay: null,
      };
      targetState.set(element, state);
    }

    if (isActive) {
      state.visibleRules.add(ruleIndex);
      if (isRequired) {
        state.requiredRules.add(ruleIndex);
      } else {
        state.requiredRules.delete(ruleIndex);
      }
    } else {
      state.visibleRules.delete(ruleIndex);
      state.requiredRules.delete(ruleIndex);
    }

    const container = findFieldContainer(element);
    if (container) {
      if (state.originalDisplay === null) {
        state.originalDisplay = container.style.display || "";
      }
      if (state.visibleRules.size > 0) {
        container.style.display = state.originalDisplay;
        container.removeAttribute("aria-hidden");
      } else {
        container.style.display = "none";
        container.setAttribute("aria-hidden", "true");
      }
    }

    if (state.requiredRules.size > 0) {
      element.required = true;
      element.setAttribute("required", "required");
    } else {
      element.required = false;
      element.removeAttribute("required");
    }
  }

  function evaluateRule(rule, ruleIndex) {
    const previousTargets = ruleTrackedTargets.get(ruleIndex) || new Set();
    const currentTargets = new Set();
    const controllers = findControllerElements(rule.when, document);

    if (controllers.length === 0) {
      const targets = findTargets(rule.then, null, rule.when);
      targets.forEach(({ element, config }) => {
        currentTargets.add(element);
        updateTargetState(element, ruleIndex, false, Boolean(config.required));
      });
    } else {
      controllers.forEach((controller) => {
        const isActive = evaluateCondition(controller, rule.when);
        const targets = findTargets(rule.then, controller, rule.when);
        targets.forEach(({ element, config }) => {
          currentTargets.add(element);
          updateTargetState(element, ruleIndex, isActive, Boolean(config.required));
        });
      });
    }

    previousTargets.forEach((element) => {
      if (!currentTargets.has(element)) {
        updateTargetState(element, ruleIndex, false, false);
      }
    });

    ruleTrackedTargets.set(ruleIndex, currentTargets);
  }

  function evaluateAllRules() {
    RULES.forEach((rule, index) => {
      evaluateRule(rule, index);
    });
  }

  function bindController(controller, rule, ruleIndex) {
    if (!controller) {
      return;
    }
    let bindings = controllerBindings.get(controller);
    if (!bindings) {
      bindings = new Map();
      controllerBindings.set(controller, bindings);
    }
    if (bindings.has(ruleIndex)) {
      return;
    }
    const handler = () => {
      evaluateRule(rule, ruleIndex);
    };
    controller.addEventListener("change", handler);
    controller.addEventListener("input", handler);
    bindings.set(ruleIndex, handler);
  }

  function bindControllers(rule, ruleIndex, root) {
    const controllers = findControllerElements(rule.when, root);
    controllers.forEach((controller) => {
      bindController(controller, rule, ruleIndex);
    });
  }

  function initialize(root) {
    RULES.forEach((rule, index) => {
      bindControllers(rule, index, root || document);
    });
    evaluateAllRules();
  }

  function onReady() {
    initialize(document);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onReady);
  } else {
    onReady();
  }

  if (window.django && window.django.jQuery) {
    const $ = window.django.jQuery;
    $(document).on("formset:added formset:removed", (event, row) => {
      initialize(row || document);
    });
  }
})();
