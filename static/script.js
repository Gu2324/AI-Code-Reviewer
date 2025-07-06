window.addEventListener('DOMContentLoaded', function() {
  const pre = document.querySelector('.reviewed_code_zone pre');
  if (!pre) return;
  const text = pre.textContent;
  pre.textContent = '';
  let i = 0;
  function type() {
    if (i <= text.length) {
      pre.textContent = text.slice(0, i);
      i++;
      setTimeout(type, 12); // velocità scrittura
    }
  }
  type();
});