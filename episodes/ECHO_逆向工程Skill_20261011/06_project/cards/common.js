window.SCENES={};window.H={};
H.e=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
H.img=(path,x,y,w,h,fit='xMidYMid meet')=>`<image href="../../${H.e(path)}" x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="${fit}"/>`;
H.p=(t,s,d)=>Math.max(0,Math.min(1,(t-s)/d));
H.m=(t,s,d)=>1-Math.pow(1-H.p(t,s,d),3);
H.badge=(s,x,y,w=220,tone='soft')=>H.k.panel(x,y,w,58,tone,16)+H.k.text(s,x+w/2,y+40,30,tone==='paper'||tone==='accent'?'ink':'muted','middle');
H.reveal=(body,p,x,y,w,h)=>H.k.clip(body,p,x,y,w,h);
H.node=(title,sub,x,y,w,h,tone='dark',icon='doc')=>H.k.panel(x,y,w,h,tone)+H.k.icon(icon,x+28,y+26,64,tone==='paper'||tone==='accent'?'ink':'accent')+H.k.text(title,x+115,y+72,46,tone==='paper'||tone==='accent'?'ink':'text','start',true)+(sub?H.k.text(sub,x+30,y+h-30,34,tone==='paper'||tone==='accent'?'ink':'muted'):'');
H.transfer=(d,t,s,duration)=>{const p=H.m(t,s,duration);return H.k.path(d,p,'line',3)+H.k.packet(d,p,'accent',13,'doc');};
H.frame=(c,t)=>{
 let b='';const k=H.k;
 if(c.type==='animation'){
  b=H.img('04_assets/'+c.art,0,0,1920,1080,'xMidYMid slice');
  const labels={A01b:['逆向团队 → AI Skill',1040,160,670],A01c:['工具，可以被调度',1030,160,690],A02a:['工具链的门槛',1060,140,620],A03a:['会诊类比',94,120,330],A03b:['会诊类比',94,120,330]};
  if(labels[c.id]){const [s,x,y,w]=labels[c.id];b+=`<rect x="${x}" y="${y}" width="${w}" height="92" rx="22" fill="#07110C" opacity=".9"/>`+k.text(s,x+w/2,y+62,44,'text','middle',true);}
  if(c.id.startsWith('A05')){
   const words={A05a:[['末日？'],['新外挂？']],A05b:[['人的','判断力'],['AI','工具箱']],A05c:[['评论区','聊聊'],['更多 AI','新玩法']]}[c.id];
   words.forEach((lines,i)=>lines.forEach((s,j)=>b+=k.text(s,i?1605:312,lines.length===1?750:716+j*63,44,'ink','middle',true)));
  }
 }else{
  b=k.box(0,0,1920,1080,'background','none',0)+`<path d="M90 242H1830" stroke="#33533B" stroke-width="2"/>`;
  b+=k.text(c.kicker,94,99,32,'muted')+k.text(c.title,90,196,72,'text','start',true);
  b+=(SCENES[c.id]||(()=>{throw new Error('Missing scene '+c.id)}))(t,c);
  b+=k.text(c.footer,94,1018,30,'muted');
 }
 b+=k.panel(1515,40,320,55,c.type==='animation'?'paper':'dark',14)+k.text('ECHO · AI SKILLS',1675,78,30,c.type==='animation'?'ink':'muted','middle');
 return `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080" font-family="Microsoft YaHei"><defs><clipPath id="frameClip"><rect width="1920" height="1080"/></clipPath></defs><g clip-path="url(#frameClip)">${b}</g></svg>`;
};
