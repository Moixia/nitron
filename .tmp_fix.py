p='/workspace/index.html'
s=open(p,encoding='utf-8').read()
orig_len=len(s)
def rep(old,new):
    global s
    assert s.count(old)==1, "NOT FOUND/AMBIGUOUS: "+repr(old[:90])+" count="+str(s.count(old))
    s=s.replace(old,new)

# A) fv(): no petar si falta el campo
rep('const fv=k=>document.querySelector(`[data-f="${k}"]`).value;',
    'const fv=k=>{const el=document.querySelector(`[data-f="${k}"]`);return el?el.value:"";};')

# B) saveCourse(): trim + guardas
rep('''function saveCourse(id){
  const name=fv("name")||"Curso sin nombre",fee=+fv("fee").replace(/\\D/g,"")||0,extra=getExtra();let c;''',
'''function saveCourse(id){
  const name=(fv("name")||"").trim()||"Curso sin nombre",fee=Math.max(0,+fv("fee").replace(/\\D/g,"")||0),extra=getExtra();let c;''')
rep('else{c=courses.find(x=>x.id==id);Object.assign(c,{name,fee,extra});}',
    'else{c=courses.find(x=>x.id==id);if(!c){toast("El curso ya no existe");location.hash="#/inicio";return;}Object.assign(c,{name,fee,extra});}')

# C) saveStudent(): guardar id ANTES del hashchange + guardas (curso inexistente / estudiante huérfano)
rep('''function saveStudent(id,cid){
  const name=fv("name")||"Sin nombre",c=courses.find(x=>x.name===fv("curso")),extra=getExtra();
  if(id==="new")students.push({id:++n,c:c.id,name,paid:0,extra});
  else Object.assign(students.find(x=>x.id==id),{name,c:c.id,extra});
  location.hash=id==="new"?"#/curso/"+c.id+"/estudiantes":"#/estudiante/"+id;
}''',
'''function saveStudent(id,cid){
  const name=(fv("name")||"").trim()||"Sin nombre",c=courses.find(x=>x.name===fv("curso")),extra=getExtra();let sid;
  if(!c){toast("Selecciona un curso válido");return;}
  if(id==="new"){sid=++n;students.push({id:sid,c:c.id,name,paid:0,extra});}
  else{const st0=students.find(x=>x.id==id);if(!st0){toast("El estudiante ya no existe");location.hash="#/inicio";return;}sid=st0.id;Object.assign(st0,{name,c:c.id,extra});}
  location.hash=id==="new"?"#/curso/"+c.id+"/estudiantes":"#/estudiante/"+sid;
}''')

# D) esc(): escapar también la comilla simple (XSS en atributos entre comillas simples)
rep('const esc = s => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;");',
    'const esc = s => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;").replace(/\'/g,"&#39;");')

# E) row(): sin onclick inline; href codificado (ids con @ o espacios) y escapado
rep('const row=(h,cells,num=[])=>`<tr class="go" onclick="location.hash=\'${h}\'">${cells.map((c,i)=>`<td class="${num.includes(i)?"num":""}">${i===0?`<a class="rowlink" href="${h}">${c}</a>`:c}</td>`).join("")}</tr>`;',
    'const row=(h,cells,num=[])=>{const hh=esc(h.replace(/(#\\/)(.*)$/, (m,r,id)=>r+encodeURIComponent(id)));return `<tr class="go" data-href="${hh}" tabindex="0">${cells.map((c,i)=>`<td class="${num.includes(i)?"num":""}">${i===0?`<a class="rowlink" href="${hh}">${c}</a>`:c}</td>`).join("")}</tr>`;};')

# F) Delegación de eventos para tramos de tabla (sustituye al onclick inline eliminado en E)
rep('document.addEventListener("click",e=>{\n  const mention=e.target.closest?.(".mention[data-doc]");',
'''document.addEventListener("click",e=>{
  const tr=e.target.closest?.("tr.go[data-href]");
  if(tr&&!e.target.closest("a,button,input,select")){location.hash=decodeURIComponent(tr.getAttribute("data-href").slice(1));return;}
  const mention=e.target.closest?.(".mention[data-doc]");''')

open(p,'w',encoding='utf-8').write(s)
print("OK", orig_len, "->", len(s))
