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

  if (!typeSelect) return;

  function updateVisibility() {
    const selected = typeSelect.value;
    if (mcqSection) mcqSection.style.display = selected === 'mcq' ? 'block' : 'none';
    if (tfSection) tfSection.style.display = selected === 'true_false' ? 'block' : 'none';
    if (textAnswerSection) textAnswerSection.style.display = selected === 'short_answer' ? 'block' : 'none';
  }

  typeSelect.addEventListener('change', updateVisibility);
  updateVisibility();
}
