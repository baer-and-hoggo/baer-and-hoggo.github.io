// The public Farmion gallery uses the original screenshots also offered in the press kit.
(() => {
  const dialog = document.getElementById('farmion-lightbox');
  const image = document.getElementById('farmion-lightbox-image');
  const title = document.getElementById('farmion-lightbox-title');
  const cards = [...document.querySelectorAll('.fp-shot')];
  let selected = 0;
  function show(index) {
    selected = (index + cards.length) % cards.length;
    const card = cards[selected];
    image.src = card.querySelector('img').getAttribute('src');
    image.alt = card.querySelector('img').alt;
    title.textContent = card.querySelector('figcaption').textContent;
  }
  cards.forEach((card, index) => card.querySelector('button').addEventListener('click', () => {
    show(index);
    dialog.showModal();
  }));
  document.getElementById('farmion-lightbox-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight') { event.preventDefault(); show(selected + 1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); show(selected - 1); }
  });
  document.getElementById('link-return-studio').addEventListener('click', event => {
    event.preventDefault();
    window.triggerVoxelTransition('studio');
  });
})();
