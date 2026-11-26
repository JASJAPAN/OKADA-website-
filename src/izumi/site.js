/* いずみ精肉店 天文館店 */
(function () {
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-copy]');
    if (b) {
      var text = b.getAttribute('data-copy'), label = b.textContent;
      var done = function () { b.textContent = b.getAttribute('data-done'); setTimeout(function () { b.textContent = label; }, 1800); };
      try { navigator.clipboard.writeText(text).then(done, function () {}); } catch (e) {}
      return;
    }
    var open = document.querySelector('.langsel[open]');
    if (open && !ev.target.closest('.langsel')) open.open = false;
  });
})();
