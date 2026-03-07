document.addEventListener('DOMContentLoaded', function () {
  // Render markdown in field values, then typeset MathJax
  if (window.marked && window.DOMPurify) {
    document.querySelectorAll('.field-value').forEach(function (el) {
      var text = el.textContent;
      el.innerHTML = DOMPurify.sanitize(marked.parse(text));
    });
  }

  // Re-render MathJax after markdown conversion
  if (window.MathJax && window.MathJax.typesetPromise) {
    window.MathJax.typesetPromise();
  }

  // Likert scale interactions
  document.querySelectorAll('.likert-option input[type="radio"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
      var fieldCard = this.closest('.field-card');
      if (!fieldCard) return;

      // Remove all answered classes
      for (var i = 1; i <= 5; i++) {
        fieldCard.classList.remove('answered-' + i);
      }
      fieldCard.classList.add('answered-' + this.value);

      // Auto-show comment box when rating is 1 or 2
      var commentBox = fieldCard.querySelector('.comment-box');
      if (commentBox && (this.value === '1' || this.value === '2')) {
        commentBox.classList.add('visible');
        var textarea = commentBox.querySelector('textarea');
        if (textarea) textarea.focus();
      }
    });
  });

  // Comment toggle buttons
  document.querySelectorAll('.comment-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var commentBox = this.closest('.comment-section').querySelector('.comment-box');
      if (commentBox) {
        commentBox.classList.toggle('visible');
        if (commentBox.classList.contains('visible')) {
          var textarea = commentBox.querySelector('textarea');
          if (textarea) textarea.focus();
        }
      }
    });
  });

  // Form validation
  var form = document.getElementById('review-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      var fieldCards = form.querySelectorAll('.field-card');
      var allAnswered = true;

      fieldCards.forEach(function (card) {
        var radios = card.querySelectorAll('.likert-option input[type="radio"]');
        var answered = Array.from(radios).some(function (r) { return r.checked; });
        if (!answered) {
          allAnswered = false;
          card.style.borderColor = '#dc3545';
          card.style.boxShadow = '0 0 0 2px rgba(220, 53, 69, 0.2)';
        }
      });

      if (!allAnswered) {
        e.preventDefault();
        var firstUnanswered = form.querySelector('.field-card:not([class*="answered-"])');
        if (firstUnanswered) {
          firstUnanswered.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        alert('Please rate all questions before submitting.');
      }
    });
  }

  // Copy URL button
  document.querySelectorAll('.btn-copy').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var input = this.closest('.copy-url-container').querySelector('input');
      if (input) {
        navigator.clipboard.writeText(input.value).then(function () {
          btn.textContent = 'Copied!';
          setTimeout(function () { btn.textContent = 'Copy'; }, 2000);
        });
      }
    });
  });

  // Initialize state for pre-filled forms (editing)
  document.querySelectorAll('.likert-option input[type="radio"]:checked').forEach(function (radio) {
    radio.dispatchEvent(new Event('change'));
  });

  // Show comment boxes that have content
  document.querySelectorAll('.comment-box textarea').forEach(function (textarea) {
    if (textarea.value.trim()) {
      textarea.closest('.comment-box').classList.add('visible');
    }
  });
});
