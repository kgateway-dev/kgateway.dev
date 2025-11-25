// Mobile touch support for glossary terms
document.addEventListener('DOMContentLoaded', function() {
  const glossaryTerms = document.querySelectorAll('.glossary-term');
  
  // Close all open tooltips
  function closeAllTooltips() {
    glossaryTerms.forEach(term => {
      term.classList.remove('active');
    });
  }
  
  // Toggle tooltip on mobile
  glossaryTerms.forEach(term => {
    term.addEventListener('click', function(e) {
      if (window.innerWidth <= 768) {
        e.preventDefault();
        const wasActive = this.classList.contains('active');
        closeAllTooltips();
        if (!wasActive) {
          this.classList.add('active');
        }
      }
    });
  });
  
  // Close tooltips when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.glossary-term')) {
      closeAllTooltips();
    }
  });
  
  // Close on escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeAllTooltips();
    }
  });
});
