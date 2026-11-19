/**
 * Online Quiz System — Client-Side Application Logic
 * Confirmation dialogs, input sanitization, and double-submission prevention.
 */

document.addEventListener('DOMContentLoaded', () => {
  initConfirmationModal();
  initFlashDismiss();
  initDoubleSubmitPrevention();
  initQuestionTypeSwitcher();
});

/**
 * Confirmation Modal
 * Intercepts destructive actions (deletions, session termination) and requires explicit confirmation.
 */
function initConfirmationModal() {
  const modalOverlay = document.getElementById('confirmModal');
  if (!modalOverlay) return;

  const modalTitle = document.getElementById('confirmModalTitle');
  const modalMessage = document.getElementById('confirmModalMessage');
  const confirmBtn = document.getElementById('confirmModalSubmit');
  const cancelBtn = document.getElementById('confirmModalCancel');

  let activeForm = null;

  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      activeForm = form;

      const title = form.getAttribute('data-confirm-title') || 'Confirm Action';
      const message = form.getAttribute('data-confirm') || 'Are you sure you want to proceed with this operation?';

      if (modalTitle) modalTitle.textContent = title;
      if (modalMessage) modalMessage.textContent = message;

      modalOverlay.classList.add('open');
    });
  });

  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      modalOverlay.classList.remove('open');
      activeForm = null;
    });
  }

  if (confirmBtn) {
    confirmBtn.addEventListener('click', () => {
      if (activeForm) {
        modalOverlay.classList.remove('open');
        // Bypass data-confirm check on actual submit
        activeForm.removeAttribute('data-confirm');
        activeForm.submit();
      }
    });
  }

  // Close modal when clicking outside box
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
      modalOverlay.classList.remove('open');
      activeForm = null;
    }
  });
}

/**
 * Flash message dismiss button handler.
 */
function initFlashDismiss() {
  document.querySelectorAll('.alert-close').forEach((btn) => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) alert.remove();
    });
  });
}

/**
 * Prevents rapid double-click submissions.
 */
function initDoubleSubmitPrevention() {
  document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn && !form.hasAttribute('data-confirm')) {
        setTimeout(() => {
          submitBtn.disabled = true;
          submitBtn.dataset.originalText = submitBtn.textContent;
          submitBtn.textContent = 'Processing...';
        }, 50);
      }
    });
  });
}

/**
 * Dynamic form switching for question creation (MCQ vs True/False vs Short Answer).
 */
function initQuestionTypeSwitcher() {
  const typeSelect = document.getElementById('question_type');
  const mcqSection = document.getElementById('mcq_options_section');
  const tfSection = document.getElementById('tf_options_section');
  const textAnswerSection = document.getElementById('text_answer_section');
  const shortAnswerInput = document.getElementById('short_answer_input');

  if (!typeSelect) return;

  function updateVisibility() {
    const selected = typeSelect.value;
    const isMcq = (selected === 'mcq');
    const isTf = (selected === 'true_false');
    const isShort = (selected === 'short_answer');

    // 1. MCQ Section
    if (mcqSection) {
      mcqSection.style.display = isMcq ? 'block' : 'none';
      const opt1 = document.getElementById('mcq_option_1');
      const opt2 = document.getElementById('mcq_option_2');
      if (opt1) opt1.required = isMcq;
      if (opt2) opt2.required = isMcq;
      mcqSection.querySelectorAll('input').forEach((input) => {
        input.disabled = !isMcq;
      });
    }

    // 2. True / False Section
    if (tfSection) {
      tfSection.style.display = isTf ? 'block' : 'none';
      tfSection.querySelectorAll('input').forEach((input) => {
        input.disabled = !isTf;
      });
    }

    // 3. Short Answer Section
    if (textAnswerSection) {
      textAnswerSection.style.display = isShort ? 'block' : 'none';
      if (shortAnswerInput) {
        shortAnswerInput.disabled = !isShort;
        shortAnswerInput.required = isShort;
      }
    }
  }

  typeSelect.addEventListener('change', updateVisibility);
  updateVisibility();
}
