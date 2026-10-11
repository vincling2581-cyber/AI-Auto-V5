window.SCENES={};
window.H={};H.mark=(_kind,value)=>value;
H.e=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
H.phase=(t,s,d)=>Math.max(0,Math.min(1,(t-s)/d));
H.ease=(t,s,d)=>1-Math.pow(1-H.phase(t,s,d),3);
H.text=(s,x,y,size=46,color='#F0F3EC',bold=false,anchor='start')=>`<text x="${x}" y="${y}" font-size="${size}" fill="${color}" font-weight="${bold?700:400}" text-anchor="${anchor}">${H.e(s)}</text>`;
H.box=(x,y,w,h,fill='#14271B',stroke='#31533B',r=28)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
H.img=(file,x,y,w,h,fit='xMidYMid meet')=>`<image href="../../04_assets/${H.e(file)}" x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="${fit}"/>`;
H.line=(d,color='#78EFA2',width=5,p=1)=>H.k.path(d,p,color,width);
H.dot=(d,p,r=12,color='#78EFA2')=>H.k.packet(d,p,color,r);
H.group=(s,dx=0,dy=0,opacity=1,scale=1)=>`<g opacity="${opacity}" transform="translate(${dx},${dy}) scale(${scale})">${s}</g>`;
H.tag=(s,x,y,w=220,light=false)=>H.box(x,y,w,54,light?'#DBEBDD':'#233E2B','none',14)+H.text(s,x+w/2,y+37,30,light?'#294A34':'#A8D6B6',false,'middle');
H.frame=(c,t)=>{const art=c.id.startsWith('A');let body='';
if(art){body=H.img('illustrations/'+c.id+'.png',0,0,1920,1080,'xMidYMid slice');
 if(c.label){body+=`<rect x="84" y="773" width="${c.label.length>20?1040:720}" height="115" rx="24" fill="#07110C" opacity=".91"/>`+H.text(c.label,120,847,46,'#F0F3EC',true);}
}else{body=H.box(0,0,1920,1080,'#07110C','none',0)+`<path d="M90 235H1830" stroke="#33533D" stroke-width="2"/>`;
 body+=H.text(c.kicker,92,94,32,'#A1C4AB')+H.text(c.title,90,193,c.title.length>25?62:72,'#F0F3EC',true);
 body+=(SCENES[c.id]||(()=>H.text('场景尚未加载',100,500))) (t);
 body+=H.text(c.footer,94,1018,30,'#A4B5A9');
 body+=`<rect x="90" y="1051" width="1740" height="3" fill="#24422E"/><rect x="90" y="1051" width="${1740*Math.min(1,t/(c.frame_count/30))}" height="3" fill="#78EFA2"/>`;
}
body+=H.box(1510,42,322,55,art?'#F0F3EC':'#14271B','none',15)+H.text('ECHO · AI新玩法',1671,80,30,art?'#24362B':'#A1C4AB',false,'middle');
return `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080" font-family="Microsoft YaHei" shape-rendering="geometricPrecision"><defs><clipPath id="screen"><rect width="1920" height="1080"/></clipPath></defs><g clip-path="url(#screen)">${body}</g></svg>`;};
