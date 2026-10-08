// Printed page numbers from the two original contents pages (PDF pages 3–4).
// This scan has one extra page before printed page 1.
const tableOfContents = [
 {title:'Unit 1',sound:'long a',phonics:'a_e · ame · ake · ate · ave',page:4,color:'#e5576b',lessons:[['a_e','tape · cape · cane · mane'],['ame · ake','game · cake · name · lake'],['ate · ave','gate · wave · skate · cave']],story:11},
 {title:'Unit 2',sound:'long i',phonics:'i_e · ime · ike · ive · ine',page:12,color:'#c7a520',lessons:[['i_e','kite · pipe · ripe · fine'],['ime · ike','lime · bike · time · hike'],['ive · ine','five · nine · dive · line']],story:19},
 {title:'Review 1',page:20,color:'#7aaa72',children:[['Song',20],['Game',23]]},
 {title:'Unit 3',sound:'long o · long u',phonics:'o_e · u_e · u_e',page:24,color:'#9869af',lessons:[['o_e','home · bone · cone · rope'],['u_e','cube · mute · cute · mule'],['u_e','tube · June · tune · rule']],story:31},
 {title:'Unit 4',sound:'long a',phonics:'ai · ay',page:32,color:'#e79836',lessons:[['ai','rain · nail · tail · wait'],['ay','bay · day · say · pay'],['ai · ay','sail · mail · hay · May']],story:39},
 {title:'Review 2',page:40,color:'#7aaa72',children:[['Song',40],['Game',43]]},
 {title:'Unit 5',sound:'long e',phonics:'ee · ea · y · ey',page:44,color:'#bd519d',lessons:[['ee','bee · feet · seed · jeep'],['ea','leaf · eat · sea · meat'],['y · ey','candy · key · happy · money']],story:51},
 {title:'Unit 6',sound:'long i',phonics:'igh · ie · y',page:52,color:'#488bbb',lessons:[['igh','light · night · high · right'],['ie','pie · tie · lie · die'],['y','spy · sky · cry · my']],story:59},
 {title:'Review 3',page:60,color:'#7aaa72',children:[['Song',60],['Game',63]]},
 {title:'Unit 7',sound:'long o',phonics:'oa · ow',page:64,color:'#23a1b3',lessons:[['oa','boat · coat · soap · road'],['ow','bow · row · yellow · pillow'],['oa · ow','goat · toad · elbow · window']],story:71},
 {title:'Unit 8',sound:'long u',phonics:'ue · ui · ew · oo',page:72,color:'#9aaf39',lessons:[['ue','blue · glue · clue · Tuesday'],['ui · ew','fruit · suit · new · dew'],['oo','moon · zoo · food · boot']],story:79},
 {title:'Review 4',page:80,color:'#7aaa72',children:[['Song',80],['Game',83]]},
 {title:'Picture Dictionary',page:84,color:'#bd519d'},
 {title:'Student Cards',page:89,color:'#bd519d'},
 {title:'Certificate',page:101,color:'#bd519d'}
];
function setContentsOpen(open){
 document.body.classList.toggle('contents-open',open);
 document.getElementById('tocMenu').setAttribute('aria-expanded',String(open));
 document.getElementById('tocBackdrop').hidden=!open;
 if(open)document.getElementById('tocClose').focus();
}
function initContents(){
 const root=document.getElementById('contents');
 const jump=printed=>{go(printed+1);setContentsOpen(false);document.getElementById('pageNumber').focus({preventScroll:true});window.scrollTo({top:0,behavior:'smooth'});};
 tableOfContents.forEach((entry,i)=>{
  const group=document.createElement('section');group.className='toc-group';group.style.setProperty('--unit-color',entry.color);group.dataset.index=i;
  const heading=document.createElement('div');heading.className='toc-heading';
  const link=document.createElement('button');link.className='toc-link';link.dataset.page=entry.page;link.title=`${entry.title} · 书本第 ${entry.page} 页`;link.onclick=()=>jump(entry.page);
  const name=document.createElement('span');name.className='toc-name';name.textContent=entry.title;
  if(entry.sound){const sound=document.createElement('small');sound.textContent=entry.sound;name.append(sound);}
  const number=document.createElement('span');number.className='toc-page';number.textContent=entry.page;link.append(name,number);heading.append(link);group.append(heading);
  if(entry.lessons||entry.children){
   const toggle=document.createElement('button');toggle.className='toc-toggle';toggle.textContent='⌄';toggle.setAttribute('aria-label',`展开 ${entry.title}`);toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-controls',`toc-items-${i}`);
   const children=document.createElement('div');children.className='toc-items';children.id=`toc-items-${i}`;children.hidden=true;
   toggle.onclick=()=>{children.hidden=!children.hidden;toggle.setAttribute('aria-expanded',String(!children.hidden));toggle.setAttribute('aria-label',`${children.hidden?'展开':'收起'} ${entry.title}`);};heading.append(toggle);
   if(entry.lessons){const phonics=document.createElement('div');phonics.className='toc-phonics';phonics.textContent=entry.phonics;children.append(phonics);
    entry.lessons.forEach(([pattern,words])=>{const row=document.createElement('div');row.className='toc-words';const p=document.createElement('strong');p.textContent=pattern;const w=document.createElement('span');w.textContent=words;row.append(p,w);children.append(row);});
   }
   const rows=entry.children||[['Story',entry.story]];
   rows.forEach(([label,p])=>{const child=document.createElement('button');child.className='toc-child';child.dataset.page=p;const text=document.createElement('span');text.textContent=label;const num=document.createElement('span');num.className='toc-page';num.textContent=p;child.append(text,num);child.onclick=()=>jump(p);children.append(child);});
   group.append(children);
  }
  root.append(group);
 });
 document.getElementById('tocMenu').onclick=()=>setContentsOpen(!document.body.classList.contains('contents-open'));
 document.getElementById('tocClose').onclick=()=>{setContentsOpen(false);document.getElementById('tocMenu').focus();};
 document.getElementById('tocBackdrop').onclick=()=>setContentsOpen(false);
 document.getElementById('originalContents').onclick=()=>{go(3);setContentsOpen(false);window.scrollTo({top:0,behavior:'smooth'});};
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.body.classList.contains('contents-open')){setContentsOpen(false);document.getElementById('tocMenu').focus();}});
}
let previousContentsGroup=-1;
function updateContents(){
 const printed=page-1;
 const index=tableOfContents.findIndex((e,i)=>printed>=e.page&&printed<(tableOfContents[i+1]?.page||102));
 document.querySelectorAll('.toc-group').forEach((group,i)=>{
  group.classList.toggle('current',i===index);
  const heading=group.querySelector('.toc-link');heading.removeAttribute('aria-current');
  group.querySelectorAll('.toc-child').forEach(b=>b.removeAttribute('aria-current'));
  if(i!==index)return;
  const candidates=[heading,...group.querySelectorAll('.toc-child')].filter(b=>Number(b.dataset.page)<=printed);
  candidates.at(-1)?.setAttribute('aria-current','page');
  if(index!==previousContentsGroup){const items=group.querySelector('.toc-items');const toggle=group.querySelector('.toc-toggle');if(items){items.hidden=false;toggle.setAttribute('aria-expanded','true');toggle.setAttribute('aria-label',`收起 ${tableOfContents[i].title}`);}}
 });
 previousContentsGroup=index;
}
