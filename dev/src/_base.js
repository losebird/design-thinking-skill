const DT=(function(){
 const raw=document.getElementById('dt-data').textContent.trim();
 let init={};try{init=raw&&raw.indexOf('DT_DATA')<0?JSON.parse(raw):{}}catch(e){console.error('数据解析失败',e)}
 const tpl=document.body.dataset.tpl||'page';
 const clone=o=>JSON.parse(JSON.stringify(o));
 const PRJ=(init.meta&&init.meta.project)||'default',SK='dt:shared:'+PRJ,OWN='dt:'+tpl+':'+PRJ+':'+(init._target||'');
 const strip=o=>{const c=clone(o);delete c._target;delete c._rev;return c};
 const HS=(function(t){let x=5381;for(let i=0;i<t.length;i++)x=((x<<5)+x+t.charCodeAt(i))|0;return String(x>>>0)})(JSON.stringify(strip(init)));
 const REV=init._rev||'';
 // 同一项目的所有页面共享一份数据（dt:shared:<项目>）；若本页比共享数据旧，则只在本页独立保存，避免覆盖。
 let st,fresh=false,KEY=SK,older=false;
 function readK(k){try{const s=localStorage.getItem(k);return s?JSON.parse(s):null}catch(e){return null}}
 (function(){const o=readK(SK);
  if(o&&o.__base===HS){st=o.st}
  else if(o&&o.__rev&&REV&&REV<o.__rev){older=true;KEY=OWN;const m=readK(OWN);st=m&&m.__base===HS?m.st:strip(init)}
  else{if(o){try{localStorage.setItem(SK+':prev',JSON.stringify(o))}catch(e){}fresh=true}st=strip(init);try{localStorage.setItem(SK,JSON.stringify({__base:HS,__rev:REV,st}))}catch(e){}}})();
 st.meta=st.meta||{};
 let opts={};
 const $=id=>document.getElementById(id);
 const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 let seq=Date.now()%100000;const nid=p=>(p||'x')+(++seq).toString(36);
 function get(path,def){if(!path)return st;let o=st;const ks=path.split('.');for(let i=0;i<ks.length;i++){if(o[ks[i]]==null){if(def===undefined)return undefined;o[ks[i]]=i===ks.length-1?def:{}}o=o[ks[i]]}return o}
 function save(){st.meta.updatedAt=new Date().toISOString();try{localStorage.setItem(KEY,JSON.stringify({__base:HS,__rev:REV,st:strip(st)}))}catch(e){}}
 function toast(t){let e=$('dt-toast');e.textContent=t;e.classList.add('show');clearTimeout(e._t);e._t=setTimeout(()=>e.classList.remove('show'),1800)}
 function ed(el,obj,key,ph,onChange){el.contentEditable='true';el.spellcheck=false;el.classList.add('ed');if(ph)el.dataset.ph=ph;el.textContent=obj[key]==null?'':obj[key];
  el.addEventListener('input',()=>{obj[key]=el.textContent;save();onChange&&onChange()});
  el.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&el.dataset.multi!=='1'){e.preventDefault();el.blur()}});return el}
 function h(tag,attrs,html){const e=document.createElement(tag);if(attrs)for(const k in attrs){if(k==='class')e.className=attrs[k];else if(k.startsWith('on'))e[k]=attrs[k];else e.setAttribute(k,attrs[k])}if(html!=null)e.innerHTML=html;return e}
 function dl(name,text,type){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
 async function copy(t,msg){try{await navigator.clipboard.writeText(t);toast(msg||'已复制')}catch(e){const ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');toast(msg||'已复制')}catch(_){toast('复制失败，请改用导出 JSON')}ta.remove()}}
 const out=()=>strip(st);
 function aiBadge(){const g=st.meta.generatedBy||'ai';const m={ai:['','AI 假设 · 待验证'],mixed:['info','调研 + AI 推断'],human:['ok','基于真实调研']}[g]||['','AI 假设 · 待验证'];return '<button class="badge '+m[0]+'" id="dt-src" title="数据来源（点击切换）：AI 假设 / 调研 + AI 推断 / 基于真实调研">'+m[1]+'</button>'}
 const PATHS={persona:'personas, personaSteps','empathy-map':'empathyMap',journey:'journey',hook:'hook',pov:'define',scamper:'ideate.scamper, ideate.matrix',matrix:'ideate.matrix',box:'prototype','ab-test':'test.ab',storyboard:'storyboard','value-canvas':'valueCanvas',overview:'meta','research-plan':'researchPlan','research-query':'deskResearch.query','source-board':'deskResearch.sources',synthesis:'deskResearch.synthesis','gap-analysis':'deskResearch.gaps','research-report':'deskResearch.report',dashboard:'全部'};
 const PATH=()=>init._target||PATHS[tpl]||'全部';
 function header(){const hd=$('dt-head');
  hd.innerHTML='<div><h1>'+esc(opts.title)+'<small>'+esc(opts.en||'')+'</small></h1><div class="sub">'+esc(st.meta.project||'')+(opts.subtitle?' · '+esc(opts.subtitle()):'')+' '+aiBadge()+'</div></div><div class="tools" id="dt-tools"></div>';
  $('dt-src').onclick=()=>{const o=['ai','mixed','human'];st.meta.generatedBy=o[(o.indexOf(st.meta.generatedBy||'ai')+1)%3];save();header()};const t=$('dt-tools');(opts.extra||[]).forEach(b=>t.appendChild(b));
  const b=(txt,cls,fn,title)=>{const x=h('button',{class:cls||''},txt);if(title)x.title=title;x.onclick=fn;t.appendChild(x)};
  b('复制给 AI','primary',()=>copy('以下是我在可视化页面中修改后的设计思维项目数据（当前页面「'+opts.title+'」，负责路径：'+PATH()+'）。'+(older?'注意：本页是旧版本，只合并本页负责的路径。':'各页面数据已同步，与 project.json 不同的部分都是我的修改。')+'请合并回 project.json，然后继续：\n```json\n'+JSON.stringify(out(),null,2)+'\n```','已复制，粘贴回对话即可继续'),'把修改后的完整数据复制到剪贴板');
  if(opts.md)b('导出 Markdown','',()=>dl(tpl+'.md',opts.md(),'text/markdown'));
  b('导出 JSON','',()=>dl((st.meta.project||'project')+'.json',JSON.stringify(out(),null,2),'application/json'));
  b('导入','',openImport,'粘贴 JSON 数据替换当前页面');
  b('重置','',()=>{if(!confirm('清除本项目所有页面的本地修改，恢复 agent 生成的初始数据？'))return;try{localStorage.removeItem(KEY)}catch(e){}st=strip(init);st.meta=st.meta||{};rerender();toast('已恢复初始数据')},'清除本地修改')}
 const TOPS=['meta','personas','personaSteps','empathyMap','journey','hook','define','ideate','prototype','test','boards','tables','radials','storyboard','valueCanvas','researchPlan','deskResearch'];
 const isObj=o=>o!==null&&typeof o==='object'&&!Array.isArray(o);
 function deep(a,b){if(!isObj(a)||!isObj(b))return clone(b);const r=Object.assign({},a);for(const k in b)r[k]=deep(a[k],b[k]);return r}
 function setPath(path,val){const ks=path.split('.');let o=st;for(let i=0;i<ks.length-1;i++){if(!isObj(o[ks[i]]))o[ks[i]]={};o=o[ks[i]]}const k=ks[ks.length-1];o[k]=isObj(o[k])&&isObj(val)?deep(o[k],val):clone(val)}
 const myPaths=()=>PATH()==='全部'?[]:PATH().split(/\s*,\s*/).filter(Boolean);
 function openImport(){const m=$('dt-modal');m.classList.add('open');const ps=myPaths();$('dt-imp-h').textContent='可粘贴：① 完整项目 JSON（含 meta，会替换全部数据）；② 数据片段'+(ps.length?'——只合并到本页负责的路径 '+ps.join('、')+'，其他数据不受影响':'，如 {"deskResearch":{…}}，按顶层字段合并')+'。可带 ```json 代码块。';const ta=$('dt-imp');ta.value='';ta.focus()}
 // 合并规则：含 meta → 整体替换（需确认）；顶层字段片段 → 深度合并；否则写入本页路径（对象深度合并、数组整体替换）
 function importData(o){const ps=myPaths();
  if(isObj(o)&&o.meta){if(!confirm('这是一份完整项目数据（含 meta），将替换当前项目的全部内容。继续？'))return null;st=strip(o);st.meta=st.meta||{};return '已导入完整项目'}
  const keys=isObj(o)?Object.keys(o):[];
  if(keys.length&&keys.every(k=>TOPS.indexOf(k)>=0)){st=deep(st,o);return '已合并：'+keys.join('、')}
  if(!ps.length)throw new Error('片段需以顶层字段包裹，如 {"deskResearch":{…}}');
  const last=ps.map(p=>p.split('.').pop());
  if(keys.length&&keys.every(k=>last.indexOf(k)>=0)){keys.forEach(k=>setPath(ps[last.indexOf(k)],o[k]));return '已合并到 '+keys.map(k=>ps[last.indexOf(k)]).join('、')}
  setPath(ps[0],o);return '已合并到 '+ps[0]}
 function doImport(){let t=$('dt-imp').value.trim().replace(/^```(json)?/,'').replace(/```$/,'').trim();let o;try{o=JSON.parse(t)}catch(e){toast('JSON 格式不正确');return}
  try{const msg=importData(o);if(!msg)return;save();$('dt-modal').classList.remove('open');rerender();toast(msg)}catch(e){toast(e.message)}}
 function rerender(){header();opts.render&&opts.render()}
 function evBtn(obj){const EV=['quote','observed','inferred','assumed'],L={quote:'原话',observed:'观察',inferred:'推断',assumed:'假设'};obj.evidence=obj.evidence||'assumed';
  const b=h('button',{class:'ev '+obj.evidence,title:'切换证据类型'},L[obj.evidence]);b.onclick=e=>{e.stopPropagation();obj.evidence=EV[(EV.indexOf(obj.evidence)+1)%4];b.className='ev '+obj.evidence;b.textContent=L[obj.evidence];save()};return b}
 function list(container,arr,prefix,ph,onChange){container.innerHTML='';arr.forEach((it,i)=>{const c=h('div',{class:'card'});const t=h('div');ed(t,it,'text',ph,onChange);c.appendChild(t);
   const d=h('button',{class:'icon del','aria-label':'删除',title:'删除'},'×');d.onclick=()=>{arr.splice(i,1);save();list(container,arr,prefix,ph,onChange);onChange&&onChange()};c.appendChild(d);container.appendChild(c)});
  const a=h('button',{class:'ghost'},'+ 添加');a.onclick=()=>{arr.push({id:nid(prefix),text:''});save();list(container,arr,prefix,ph,onChange);const e=container.querySelectorAll('.card .ed');e.length&&e[e.length-1].focus()};container.appendChild(a)}
 // AI 辅助面板：btns=[{label,kind:'fill'|'review',build:()=>prompt}]，点击复制并预览 prompt
 function aiPanel(btns,note){const w=h('section',{class:'aip','aria-label':'AI 辅助'});
  w.appendChild(h('div',{class:'aip-hd'},'<b>🤖 AI 辅助</b><span class="hint">'+esc(note||'点击按钮复制 prompt 粘贴给 agent；agent 返回 JSON 后点右上角「导入」或直接让它更新 project.json')+'</span>'));
  const row=h('div',{class:'aip-btns'}),box=h('pre',{class:'aip-box'});
  btns.forEach(b=>{const x=h('button',{class:b.kind==='review'?'aip-rv':'primary'},(b.kind==='review'?'🔍 ':'✨ ')+esc(b.label));x.onclick=()=>{const t=b.build();box.textContent=t;box.classList.add('open');copy(t,'「'+b.label+'」prompt 已复制')};row.appendChild(x)});
  w.append(row,box);return w}
 function ctx(){const m=st.meta||{};return '项目：'+(m.project||'')+'\n设计挑战：'+(m.challenge||'（未填写）')}
 // 来源标签：在条目上显示/编辑关联的 deskResearch.sources id（obj[key] 为 id 数组）
 function srcPick(obj,key,onChange){key=key||'sources';obj[key]=obj[key]||[];const srcs=(st.deskResearch&&st.deskResearch.sources)||[];const w=h('div',{class:'srcs'});
  const draw=()=>{w.innerHTML='';obj[key].forEach((id,i)=>{const s=srcs.find(x=>x.id===id);const c=h('button',{class:'src-chip'+(s?'':' miss'),title:s?(s.title||'')+(s.url?'\n'+s.url:''):'来源不存在：'+id+'（点击移除）'},esc(id)+' ×');c.onclick=()=>{obj[key].splice(i,1);save();draw();onChange&&onChange()};w.appendChild(c)});
   const left=srcs.filter(s=>obj[key].indexOf(s.id)<0);if(left.length){const sel=h('select',{class:'src-add','aria-label':'关联来源'});sel.appendChild(h('option',{value:''},'+ 来源'));left.forEach(s=>sel.appendChild(h('option',{value:s.id},esc(s.id+' · '+(s.title||'').slice(0,24)))));sel.onchange=()=>{if(sel.value){obj[key].push(sel.value);save();draw();onChange&&onChange()}};w.appendChild(sel)}};draw();return w}
 function boot(o){opts=o;
  // 非仪表盘页面注入固定顶部导航栏
  if(tpl!=='dashboard'){
    const nb=document.createElement('nav');nb.id='dt-nav';nb.setAttribute('aria-label','项目导航');
    nb.innerHTML='<a href="dashboard.html" class="dt-nav-home" title="返回项目仪表盘">⬡ 仪表盘</a><a href="overview.html" class="dt-nav-ov" title="查看全部工具">工具总览</a><span class="dt-nav-sep"></span><span class="dt-nav-proj" id="dt-nav-proj"></span>';
    document.body.insertBefore(nb,document.body.firstChild);
    // 更新项目名
    setTimeout(()=>{const el=document.getElementById('dt-nav-proj');if(el)el.textContent=st.meta&&st.meta.name||st.meta&&st.meta.project||'';},50);
  }
  document.body.insertAdjacentHTML('beforeend','<div class="toast" id="dt-toast" role="status" aria-live="polite"></div><div class="modal" id="dt-modal" role="dialog" aria-label="导入 JSON"><div class="panel"><b>导入 JSON</b><p class="hint" id="dt-imp-h"></p><textarea id="dt-imp"></textarea><div class="tools" style="justify-content:flex-end;margin-top:12px"><button id="dt-imp-c">取消</button><button class="primary" id="dt-imp-ok">导入</button></div></div></div>');
  $('dt-imp-c').onclick=()=>$('dt-modal').classList.remove('open');$('dt-imp-ok').onclick=doImport;
  document.addEventListener('keydown',e=>{if(e.key==='Escape')$('dt-modal').classList.remove('open')});
  window.addEventListener('storage',e=>{if(e.key!==KEY||!e.newValue)return;try{const o=JSON.parse(e.newValue);if(o.__base===HS){st=o.st;st.meta=st.meta||{};rerender()}}catch(_){}});
  rerender();if(fresh)setTimeout(()=>toast('已载入 agent 生成的新版本数据（旧的本地修改已备份）'),300);if(older)setTimeout(()=>toast('本页数据比其他已打开的页面旧，修改只保存在本页'),300)}
 return {get st(){return st},get,save,toast,esc,ed,h,nid,dl,copy,boot,rerender,evBtn,list,openImport,importData,aiPanel,ctx,srcPick,target:init._target||''};
})();
