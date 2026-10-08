const $=id=>document.getElementById(id);
const audio=$('audio');let book,page=1,zoom=100,editing=false,activeKey='',drag=null,requestId=0;
const store={get(k){try{return JSON.parse(localStorage.getItem(k));}catch{return null;}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v));}catch{$('status').textContent='浏览器无法保存更改，请导出坐标备份。';}}};
let edits=store.get('opw3-hotspots')||{};
function spots(){return edits[page]||book.pages[page-1].hotspots;}
function key(h){return `${h.disc}-${String(h.track).padStart(2,'0')}`;}
function time(n){return Number.isFinite(n)?`${Math.floor(n/60)}:${String(Math.floor(n%60)).padStart(2,'0')}`:'0:00';}
function render(){
 const p=book.pages[page-1];$('pageNumber').value=page;$('prev').disabled=page===1;$('next').disabled=page===book.pages.length;
 $('pageImage').src=p.image;$('pageImage').alt=`Oxford Phonics World 3，PDF 第 ${page} 页`;
 $('sheet').style.aspectRatio=`${p.width}/${p.height}`;
 $('hotspots').replaceChildren();$('pageTracks').replaceChildren();
 spots().forEach((h,i)=>{
  const b=document.createElement('button');b.className='hotspot'+(activeKey===key(h)?' active':'');b.style.cssText=`left:${h.x*100}%;top:${h.y*100}%;width:${h.w*100}%;height:${h.h*100}%`;
  b.title=b.ariaLabel=`${editing?'删除区域：':'播放：'}Disc ${h.disc} · Track ${String(h.track).padStart(2,'0')}`;
  b.onclick=()=>{if(editing){edits[page]=spots().filter((_,j)=>j!==i);save();render();}else playTrack(h);};$('hotspots').append(b);
  const t=document.createElement('button');t.textContent=`♫ ${h.disc} / ${String(h.track).padStart(2,'0')}`;t.onclick=()=>playTrack(h);$('pageTracks').append(t);
 });
 $('status').textContent=editing?'拖动框选音频图标，点击已有区域可删除。':spots().length?`本页有 ${spots().length} 处音频 · 点击绿色区域即可播放`:'本页没有音频标记 · 使用上方箭头继续翻页';
 store.set('opw3-page',page);updateContents();
}
function save(){store.set('opw3-hotspots',edits);}
function go(n){if(!Number.isFinite(n))return;page=Math.max(1,Math.min(book.pages.length,Math.round(n)));render();$('viewport').scrollTop=0;}
async function playTrack(h){
 const k=key(h),src=book.tracks[k];if(!src){$('status').textContent=`找不到 Disc ${h.disc} Track ${h.track} 的音频。`;return;}
 const token=++requestId;
 if(activeKey!==k){audio.pause();audio.src=src;activeKey=k;}
 $('player').hidden=false;$('trackTitle').textContent=`Disc ${h.disc} · Track ${String(h.track).padStart(2,'0')}`;$('playingState').textContent='正在载入…';render();
 try{await audio.play();}catch(e){if(token===requestId&&e.name!=='AbortError')$('playingState').textContent='播放失败，请点击播放重试';}
}
$('prev').onclick=()=>go(page-1);$('next').onclick=()=>go(page+1);$('pageNumber').onchange=e=>go(Number(e.target.value));
function setZoom(n){zoom=Math.max(60,Math.min(180,n));$('sheet').style.width=zoom+'%';$('sheet').style.maxWidth=900*zoom/100+'px';$('zoomLabel').textContent=zoom+'%';}
$('zoomIn').onclick=()=>setZoom(zoom+20);$('zoomOut').onclick=()=>setZoom(zoom-20);
$('hints').onclick=()=>{const hidden=$('sheet').classList.toggle('no-hints');$('hints').setAttribute('aria-pressed',String(!hidden));$('hints').textContent=hidden?'显示点击区域':'隐藏点击区域';};
$('play').onclick=async()=>{if(audio.paused){try{await audio.play();}catch{$('playingState').textContent='播放失败，请重试';}}else audio.pause();};
function skip(delta){if(Number.isFinite(audio.duration))audio.currentTime=Math.max(0,Math.min(audio.duration,audio.currentTime+delta));}
$('back').onclick=()=>skip(-5);$('forward').onclick=()=>skip(5);
$('close').onclick=()=>{++requestId;audio.pause();$('player').hidden=true;activeKey='';render();};
audio.onplay=()=>{$('play').textContent='Ⅱ';$('play').ariaLabel='暂停';$('playingState').textContent='正在播放 · 跟着读一读';};
audio.onpause=()=>{$('play').textContent='▶';$('play').ariaLabel='播放';$('playingState').textContent='已暂停';};
audio.onended=()=>{$('playingState').textContent='播放完成 · 再听一次？';};
audio.onerror=()=>{$('playingState').textContent='音频载入失败，请检查本地文件';};
function updateTime(){$('elapsed').textContent=time(audio.currentTime);$('duration').textContent=time(audio.duration);$('seek').value=audio.duration?audio.currentTime/audio.duration*100:0;}
audio.ontimeupdate=updateTime;audio.onloadedmetadata=updateTime;
$('seek').oninput=e=>{if(Number.isFinite(audio.duration))audio.currentTime=Number(e.target.value)/100*audio.duration;};
$('edit').onclick=()=>{editing=!editing;document.body.classList.toggle('editing',editing);$('editor').hidden=!editing;$('edit').textContent=editing?'结束调整':'调整音频区域';render();};
const point=e=>{const r=$('sheet').getBoundingClientRect();return {x:Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),y:Math.max(0,Math.min(1,(e.clientY-r.top)/r.height))};};
$('hotspots').onpointerdown=e=>{if(!editing||e.target.closest('button'))return;drag=point(e);$('hotspots').setPointerCapture(e.pointerId);};
$('hotspots').onpointermove=e=>{if(!drag)return;const p=point(e),s=$('selection');s.hidden=false;s.style.cssText=`left:${Math.min(p.x,drag.x)*100}%;top:${Math.min(p.y,drag.y)*100}%;width:${Math.abs(p.x-drag.x)*100}%;height:${Math.abs(p.y-drag.y)*100}%`;};
$('hotspots').onpointerup=e=>{if(!drag)return;const p=point(e),h={disc:Number($('disc').value),track:Number($('track').value),x:Math.min(p.x,drag.x),y:Math.min(p.y,drag.y),w:Math.abs(p.x-drag.x),h:Math.abs(p.y-drag.y)};drag=null;$('selection').hidden=true;if(h.w<.005||h.h<.005)return;if(!book.tracks[key(h)]){$('status').textContent='该曲目不存在，请先选择有效的 Disc 和 Track。';return;}edits[page]=[...spots(),h];save();render();};
$('hotspots').onpointercancel=()=>{drag=null;$('selection').hidden=true;};
$('export').onclick=()=>{const data={...book,pages:book.pages.map(p=>({...p,hotspots:edits[p.page]||p.hotspots}))};const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='book.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
$('reset').onclick=()=>{delete edits[page];save();render();};
document.onkeydown=e=>{if(!book||editing||['INPUT','SELECT','BUTTON','TEXTAREA'].includes(e.target.tagName))return;if(e.key==='ArrowLeft')go(page-1);if(e.key==='ArrowRight')go(page+1);if(e.code==='Space'&&!$('player').hidden){e.preventDefault();$('play').click();}};
fetch('book.json').then(r=>{if(!r.ok)throw Error();return r.json();}).then(b=>{book=b;initContents();Object.keys(b.tracks).sort().forEach(k=>{const o=document.createElement('option');o.value=k;o.textContent='Disc '+k.split('-')[0]+' · Track '+k.split('-')[1];$('audioList').append(o);});$('total').textContent=b.pages.length;$('pageNumber').max=b.pages.length;go(Number(store.get('opw3-page'))||1);}).catch(()=>{$('status').textContent='教材载入失败。请通过启动脚本打开，并确认 public/book.json 存在。';});

$('libraryPlay').onclick=()=>{const [disc,track]=$('audioList').value.split('-').map(Number);playTrack({disc,track});};

