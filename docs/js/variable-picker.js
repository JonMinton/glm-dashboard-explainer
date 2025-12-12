/**
 * Variable Picker - Mobile-friendly interaction for GLM tutorials
 *
 * On desktop: Drag and drop variables to zones
 * On mobile/touch: Tap to select, then tap zone to place
 *
 * Usage: Include this script and call initVariablePicker(config) with:
 *   - variablePool: DOM element containing variable cards
 *   - predictorZone: DOM element for predictor drop zone
 *   - responseZone: DOM element for response drop zone
 *   - onDrop: callback(variable, zone) when a valid drop occurs
 *   - validateDrop: callback(variable, zone) returns true if drop is valid
 */

(function() {
  'use strict';

  // Detect touch device
  const isTouchDevice = ('ontouchstart' in window) ||
                        (navigator.maxTouchPoints > 0) ||
                        (navigator.msMaxTouchPoints > 0);

  // State for tap-to-select mode
  let selectedVariable = null;
  let selectedCard = null;

  /**
   * Initialize the variable picker with mobile support
   */
  function initVariablePicker(config) {
    const { variablePool, predictorZone, responseZone, onDrop, validateDrop } = config;

    // Add mobile indicator class to body
    if (isTouchDevice) {
      document.body.classList.add('touch-device');
    }

    // Setup drop zones for both modes
    setupDropZone(predictorZone, 'predictor', onDrop, validateDrop);
    setupDropZone(responseZone, 'response', onDrop, validateDrop);

    // Observe variable pool for new cards
    const observer = new MutationObserver(() => {
      setupVariableCards(variablePool, predictorZone, responseZone, onDrop, validateDrop);
    });
    observer.observe(variablePool, { childList: true, subtree: true });

    // Initial setup
    setupVariableCards(variablePool, predictorZone, responseZone, onDrop, validateDrop);

    // Clear selection when tapping elsewhere (mobile)
    if (isTouchDevice) {
      document.addEventListener('click', (e) => {
        if (!e.target.closest('.variable-card') &&
            !e.target.closest('.drop-zone')) {
          clearSelection();
        }
      });
    }
  }

  /**
   * Setup variable cards with both drag and tap handlers
   */
  function setupVariableCards(pool, predictorZone, responseZone, onDrop, validateDrop) {
    const cards = pool.querySelectorAll('.variable-card');

    cards.forEach(card => {
      // Skip if already setup
      if (card.dataset.pickerSetup) return;
      card.dataset.pickerSetup = 'true';

      const varName = card.dataset.var;
      const isDimmed = card.classList.contains('dimmed');

      if (isDimmed) return;

      // Desktop: Drag handlers
      if (!isTouchDevice) {
        card.addEventListener('dragstart', (e) => {
          e.dataTransfer.effectAllowed = 'move';
          e.dataTransfer.setData('text/plain', varName);
          card.classList.add('dragging');
          // Store for drop handler
          card._draggedVar = varName;
        });

        card.addEventListener('dragend', () => {
          card.classList.remove('dragging');
        });
      }

      // Mobile: Tap to select
      if (isTouchDevice) {
        card.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();

          // If already selected, deselect
          if (selectedCard === card) {
            clearSelection();
            return;
          }

          // Clear previous selection
          clearSelection();

          // Select this card
          selectedVariable = varName;
          selectedCard = card;
          card.classList.add('selected');

          // Update instruction hint
          showMobileHint('Now tap the target zone to place it');
        });
      }
    });
  }

  /**
   * Setup a drop zone with both drag and tap handlers
   */
  function setupDropZone(zone, zoneType, onDrop, validateDrop) {
    // Desktop: Drag handlers
    if (!isTouchDevice) {
      zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('drag-over');
      });

      zone.addEventListener('dragleave', () => {
        zone.classList.remove('drag-over');
      });

      zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('drag-over');

        const varName = e.dataTransfer.getData('text/plain');

        if (validateDrop && !validateDrop(varName, zoneType)) {
          zone.classList.add('wrong');
          setTimeout(() => zone.classList.remove('wrong'), 300);
          return;
        }

        onDrop(varName, zoneType);
      });
    }

    // Mobile: Tap to place
    if (isTouchDevice) {
      zone.addEventListener('click', (e) => {
        if (!selectedVariable) return;

        e.preventDefault();
        e.stopPropagation();

        if (validateDrop && !validateDrop(selectedVariable, zoneType)) {
          zone.classList.add('wrong');
          setTimeout(() => zone.classList.remove('wrong'), 300);
          clearSelection();
          return;
        }

        const varName = selectedVariable;
        clearSelection();
        onDrop(varName, zoneType);
      });
    }
  }

  /**
   * Clear the current selection (mobile mode)
   */
  function clearSelection() {
    if (selectedCard) {
      selectedCard.classList.remove('selected');
    }
    selectedVariable = null;
    selectedCard = null;
    hideMobileHint();
  }

  /**
   * Show a mobile hint message
   */
  function showMobileHint(message) {
    let hint = document.getElementById('mobile-picker-hint');
    if (!hint) {
      hint = document.createElement('div');
      hint.id = 'mobile-picker-hint';
      hint.className = 'mobile-picker-hint';
      document.body.appendChild(hint);
    }
    hint.textContent = message;
    hint.classList.add('show');
  }

  /**
   * Hide the mobile hint message
   */
  function hideMobileHint() {
    const hint = document.getElementById('mobile-picker-hint');
    if (hint) {
      hint.classList.remove('show');
    }
  }

  // Export to global scope
  window.initVariablePicker = initVariablePicker;
  window.isTouchDevice = isTouchDevice;
})();
