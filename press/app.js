const cards=[...document.querySelectorAll('.shot')];
const dialog=document.querySelector('#lightbox');
const lightboxImage=document.querySelector('#lightbox-image');
let selected=0;
function showShot(index){
  selected=(index+cards.length)%cards.length;
  const card=cards[selected];
  lightboxImage.src=card.dataset.src;
  lightboxImage.alt=card.dataset.caption;
  document.querySelector('#lightbox-title').textContent=card.dataset.title;
  document.querySelector('#lightbox-caption').textContent=card.dataset.caption;
  document.querySelector('#lightbox-download').href=card.dataset.src;
  document.querySelector('#lightbox-counter').textContent=`${selected+1} / ${cards.length}`;
}
cards.forEach((card,index)=>card.querySelector('button').addEventListener('click',()=>{showShot(index);dialog.showModal();}));
document.querySelector('#lightbox-close').addEventListener('click',()=>dialog.close());
document.querySelector('#previous').addEventListener('click',()=>showShot(selected-1));
document.querySelector('#next').addEventListener('click',()=>showShot(selected+1));
dialog.addEventListener('keydown',event=>{if(event.key==='ArrowRight'){event.preventDefault();showShot(selected+1)}if(event.key==='ArrowLeft'){event.preventDefault();showShot(selected-1)}});
document.querySelectorAll('.filter').forEach(button=>button.addEventListener('click',()=>{
  document.querySelectorAll('.filter').forEach(other=>other.setAttribute('aria-pressed',String(other===button)));
  cards.forEach(card=>{card.hidden=button.dataset.filter!=='all'&&card.dataset.category!==button.dataset.filter});
  document.querySelector('#gallery-status').textContent=`${cards.filter(card=>!card.hidden).length} screenshots shown.`;
}));
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{
  const source=document.getElementById(button.dataset.copy);
  const paragraphs=[...source.querySelectorAll('p')];
  const text=paragraphs.length?paragraphs.map(p=>p.textContent.trim()).join('\n\n'):source.textContent.trim();
  const status=document.querySelector('#copy-status');
  try{await navigator.clipboard.writeText(text);status.textContent='Copied.'}
  catch{
    let field=document.querySelector('#copy-fallback');
    if(!field){field=document.createElement('textarea');field.id='copy-fallback';field.className='copy-fallback';field.readOnly=true;field.setAttribute('aria-label','Press copy: select and copy');document.querySelector('.story').append(field)}
    field.value=text;field.focus();field.select();status.textContent='Text selected below. Press Ctrl+C or Command+C to copy.';
  }
}));
function revealLinkedPricing() {
  if (location.hash === '#pricing') {
    const pricing = document.getElementById('pricing');
    pricing.open = true;
    pricing.scrollIntoView();
  }
}
window.addEventListener('hashchange', revealLinkedPricing);
revealLinkedPricing();
