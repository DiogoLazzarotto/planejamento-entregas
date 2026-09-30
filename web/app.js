'use strict';
const $=id=>document.getElementById(id);
const fmt=n=>new Intl.NumberFormat('pt-BR').format(n);
let state={orders:[],trips:[],vehicles:[]};
function el(tag,text,className){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;}
function notify(text,error=false){$('message').textContent=text;$('message').className=error?'error':'';}
async function request(path,data){const response=await fetch(path,data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const body=await response.json();if(!response.ok)throw new Error(body.error||'Falha na requisição');return body;}
async function refresh(){state=await request('/api/state');render();}
async function mutate(path,data){await request(path,data);await refresh();notify('Alteração salva.');}
function button(text,action,className){const b=el('button',text,className);b.type='button';b.addEventListener('click',async()=>{b.disabled=true;try{await action();}catch(e){notify(e.message,true);}finally{b.disabled=false;}});return b;}
function render(){
 const pending=state.orders.filter(o=>o.status==='pendente');$('pending').textContent=pending.length;$('volume').textContent=fmt(pending.reduce((n,o)=>n+o.kg,0))+' kg';$('tripcount').textContent=state.trips.length;
 const prev=$('vehicles').value;$('vehicles').replaceChildren(...state.vehicles.map(v=>{const o=el('option',`${v.name} · ${fmt(v.capacity)} kg`);o.value=v.id;return o;}));if(prev)$('vehicles').value=prev;
 $('trips').replaceChildren(...state.trips.map(t=>{const card=el('article',undefined,'trip');const pr=document.createElement('progress');pr.max=t.capacity;pr.value=t.load;pr.setAttribute('aria-label',`Ocupação da viagem ${t.id}`);card.append(el('h3',`#${t.id} · ${t.name}`),el('p',t.day),el('strong',`${fmt(t.load)} / ${fmt(t.capacity)} kg`),pr,el('small',`Disponível: ${fmt(t.capacity-t.load)} kg`));return card;}));if(!state.trips.length)$('trips').append(el('p','Crie uma viagem para começar.','muted'));
 const rows=state.orders.filter(o=>$('filter').value==='todos'||o.status===$('filter').value).map(o=>{
  const tr=el('tr');const first=el('td',`#${o.id} · ${o.producer}`);first.append(el('small',o.product));const status=el('td');status.append(el('span',o.status,'badge'));const action=el('td');
  if(o.status==='pendente'){
   const trips=state.trips.filter(t=>t.day===o.day&&t.capacity-t.load>=o.kg);const select=document.createElement('select');select.setAttribute('aria-label',`Viagem para pedido ${o.id}`);
   if(trips.length){for(const t of trips){const opt=el('option',`#${t.id} · ${t.name}`);opt.value=t.id;select.append(opt);}action.append(select,button('Planejar',()=>mutate('/api/assign',{order_id:o.id,trip_id:Number(select.value)})));}else action.append(el('small','Crie uma viagem compatível com data e peso.'));
  }
  const buttons=el('div',undefined,'actions');
  if(o.status==='planejado'){action.append(el('small',`Viagem #${o.trip_id}`));buttons.append(button('Entregue',()=>mutate('/api/status',{order_id:o.id,status:'entregue'})),button('Desplanejar',()=>mutate('/api/status',{order_id:o.id,status:'pendente'}),'secondary'));}
  if(['pendente','planejado'].includes(o.status))buttons.append(button('Cancelar',()=>mutate('/api/status',{order_id:o.id,status:'cancelado'}),'danger'));
  action.append(buttons);tr.append(first,el('td',o.day),el('td',fmt(o.kg)+' kg'),status,action);return tr;
 });$('orders').replaceChildren(...rows);if(!rows.length){const tr=el('tr'),td=el('td','Nenhum pedido neste filtro.');td.colSpan=5;tr.append(td);$('orders').append(tr);}
}
for(const [id,path] of [['order-form','/api/orders'],['trip-form','/api/trips']])$(id).addEventListener('submit',async e=>{e.preventDefault();const form=e.currentTarget;const data=Object.fromEntries(new FormData(form));const submit=form.querySelector('button');submit.disabled=true;try{await mutate(path,data);if(id==='order-form'){form.elements.producer.value='';form.elements.product.value='';form.elements.kg.value='';}}catch(err){notify(err.message,true);}finally{submit.disabled=false;}});
$('filter').addEventListener('change',render);refresh().catch(e=>notify('Não foi possível carregar o planejador: '+e.message,true));
