const cards=[...document.querySelectorAll('.fs-shot')];
const dialog=document.querySelector('#lightbox');
const lightboxImage=document.querySelector('#lightbox-image');
let selected=0;
function showShot(index){
  selected=(index+cards.length)%cards.length;
  const card=cards[selected];
  lightboxImage.src=card.dataset.src;
  lightboxImage.alt=card.dataset.caption;
  document.querySelector('#lightbox-title').textContent=card.dataset.title;
  document.querySelector('#lightbox-download').href=card.dataset.src;
}
cards.forEach((card,index)=>card.querySelector('button').addEventListener('click',()=>{showShot(index);dialog.showModal();}));
document.querySelector('#lightbox-close').addEventListener('click',()=>dialog.close());
document.querySelector('#previous').addEventListener('click',()=>showShot(selected-1));
document.querySelector('#next').addEventListener('click',()=>showShot(selected+1));
dialog.addEventListener('keydown',event=>{if(event.key==='ArrowRight'){event.preventDefault();showShot(selected+1)}if(event.key==='ArrowLeft'){event.preventDefault();showShot(selected-1)}});
// Every copy button carries the plain text an editor would paste.
document.querySelectorAll('[data-copy-text]').forEach(button=>button.addEventListener('click',async()=>{
  const label=button.textContent;
  try{await navigator.clipboard.writeText(button.dataset.copyText);button.textContent='copied';button.classList.add('copied')}
  catch{button.textContent='select the text';}
  setTimeout(()=>{button.textContent=label;button.classList.remove('copied')},1600);
}));
function revealLinkedPricing(){
  if(location.hash==='#pricing'){document.getElementById('pricing').scrollIntoView();}
}
window.addEventListener('hashchange',revealLinkedPricing);
revealLinkedPricing();
