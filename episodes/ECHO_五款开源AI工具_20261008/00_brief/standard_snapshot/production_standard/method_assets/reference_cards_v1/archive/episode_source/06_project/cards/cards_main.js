/* C02/C04/C11/C13: new episode content, reference-derived explanatory motion. */
(()=>{
 const {clamp,lerp,phase,m,box,panel,text,group,clip,settle,path,icon,packet,morph,folder}=window.CardKit;
 const ink='#12251A',mutedPaper='#53705B';
 window.cardScenes.C02=t=>{
   let left=panel(126,286,780,570,'dark')+text('Prompt',186,365,58,'text','start',true)+text('临时交代',186,419,34,'muted');
   left+=group(icon('chat',226,480,136,'accent',m(t,.15,.45)),1-.48*m(t,.45,.9));
   left+=path('M382 548H637',m(t,.4,.65),'line',3)+packet('M382 548H637',phase(t,.65,.65),'accent',8);
   left+=icon('clipboard',656,474,142,'accent',m(t,1.28,.16))+group(text('本次任务',727,678,40,'text','middle',true),m(t,1.1,.3));
   left+=morph('bubble','clipboard',t,.35,1.05,[226,480,136,136],[656,474,142,142],'dark','paper','accent',58);
   left+=clip(text('一次任务，一次交代',186,802,34,'muted'),m(t,1.35,.4),176,756,600,70);
   let right=panel(1014,286,780,570,'paper')+text('Skill',1074,365,58,ink,'start',true)+text('长期工作手册',1074,419,34,mutedPaper);
   const open=Math.sin(phase(t,1.4,.85)*Math.PI);
   right+=folder(1090,520,266,open,ink,'paper');
   right+=group(icon('doc',1160,463,123,ink,m(t,1.25,.4)),1-m(t,1.4,.65));
   right+=morph('paper','doc',t,1.4,.85,[1115,446,240,182],[1135,559,157,118],'paper','paper',ink,56);
   right+=text('方法存档',1223,691,40,ink,'middle',true);
   [0,1].forEach(i=>{const y=520+i*174,s=2.35+i*1.25,d=`M1328 650C1418 650 1392 ${y+38} 1470 ${y+38}`;
     const entry=panel(1470,y,260,88,'dark',20)+text(`任务 ${i?'B':'A'}`,1600,y+57,40,'text','middle');
     right+=clip(entry,m(t,s,.4),1468,y-2,266,96,'x');
     right+=path(d,m(t,s-.15,.65),mutedPaper,3)+packet(d,phase(t,s+.05,.75),ink,8);
     right+=icon('check',1740,y+20,44,ink,m(t,s+.75,.25));
   });
   right+=clip(text('保存一次，按需调用',1074,802,34,ink),m(t,4.6,.35),1060,755,700,70);
   return settle(left,t,0,.65,516,570,{dy:18,scale:.97,rotate:0})+settle(right,t,.05,.7,1404,570,{dy:25,scale:.94,rotate:-1.5});
 };
 window.cardScenes.C04=t=>{
   const labels=['痛点','冲突','开头','案例','互动'],xs=[256,608,960,1312,1664],starts=[.12,.84,1.56,2.28,3];
   let s='';
   // Persistent workpaper receives a real retained row from each step.
   let paper=panel(416,610,1088,266,'paper')+text('同一份文案',472,680,46,ink,'start',true);
   labels.forEach((label,i)=>{const x=724+i*140;
     paper+=clip(box(x,715,106,13,'#CAD3C7','none',6)+box(x,742,84,10,'#D6DED2','none',5)+text(label,x+53,819,34,ink,'middle'),m(t,starts[i]+.72,.38),x-2,711,112,130,'y');
   });
   s+=settle(paper,t,.2,.7,960,743,{dy:25,scale:.94,rotate:-1});
   labels.forEach((label,i)=>{const q=m(t,starts[i],.48),active=t>=starts[i]&&t<starts[i]+.8;
     const node=panel(xs[i]-137,307,274,204,active?'accent':'dark')+icon(i===0?'target':i===1?'sliders':i===2?'doc':i===3?'grid':'chat',xs[i]-42,325,84,active?ink:'accent',q)+text(label,xs[i],470,46,active?ink:'text','middle',true);
     s+=clip(group(node,1,-28*(1-q),0),q,xs[i]-168,299,314,221);
     if(i<4){const d=`M${xs[i]+137} 409H${xs[i+1]-137}`;s+=path(d,m(t,starts[i]+.3,.48),'line',3)+packet(d,phase(t,starts[i]+.36,.48),'accent',7)}
     const d=`M${xs[i]} 512V557Q${xs[i]} 575 ${xs[i]<960?xs[i]+24:xs[i]-24} 575H${777+i*140}V715`;
     s+=path(d,m(t,starts[i]+.4,.52),'line',2)+packet(d,phase(t,starts[i]+.52,.65),'accent',7);
   });
   s+=clip(text('成稿',552,795,58,ink,'middle',true)+icon('check',621,744,66,ink,m(t,4.15,.35)),m(t,4,.55),448,730,258,92);
   return s;
 };
 window.cardScenes.C11=t=>{
   let s='';const ys=[330,521,712],labels=['文案手册','分析手册','剪辑手册'];
   s+=panel(120,400,372,344,'dark')+icon('chat',256,437,100,'accent',m(t,.1,.5))+text('写短视频文案',306,615,46,'text','middle',true)+text('任务示例',306,681,34,'muted','middle');
   const candidates=[];
   ys.forEach((y,i)=>{const q=m(t,.75+i*.24,.5),chosen=i===0&&t>=3.65,dim=i>0?1-.62*m(t,3.65,.45):1;
     const d=`M492 572H596V${y+60}H744`;
     s+=path(d,m(t,1+i*.28,.6),chosen?'accent':'line',3);
     let node=panel(744,y,462,120,chosen?'paper':'dark')+icon('clipboard',766,y+24,70,chosen?ink:'accent',m(t,.95+i*.24,.45))+text(labels[i],990,y+74,46,chosen?ink:'text','middle',true);
     candidates.push(group(clip(node,q,731,y-3,479,132),dim,-55*(1-q),0));
   });s+=candidates.join('');
   s+=clip(text('先查看介绍',964,276,34,'muted','middle'),m(t,1.25,.35),772,228,390,62);
   if(t>=1.75&&t<=3.5){const y=lerp(ys[0],ys[2],phase(t,1.75,1.75));s+=box(728,y-12,494,145,'none','#B0CABB',30)+icon('search',1240,y+20,60,'accent')}
   const end=panel(1422,400,374,344,'soft')+icon('clipboard',1558,452,102,'accent',m(t,4.58,.16))+text('执行任务',1609,615,46,'text','middle',true)+text('按选中的方法',1609,681,34,'muted','middle');
   s+=group(end,.38+.62*m(t,4.75,.4),-65*(1-m(t,3.5,.65)),0);
   const chosen='M1206 390H1300Q1336 390 1336 426V536Q1336 572 1372 572H1422';
   s+=path(chosen,m(t,3.95,.75),'accent',4)+packet(chosen,phase(t,4.3,.8),'accent',9);
   s+=morph('doc','clipboard',t,3.8,.9,[1150,330,98,98],[1558,452,102,102],'paper','paper','accent',72);
   s+=clip(text('只接通匹配的手册',964,889,34,'accent','middle'),m(t,5.25,.4),653,839,637,65);
   return s;
 };
 window.cardScenes.C13=t=>{
   let s=panel(126,286,780,575,'dark')+text('没有 Skill',186,365,58,'text','start',true);
   const ys=[461,603,745];
   ys.forEach((y,i)=>{const start=.15+i*.45,q=m(t,start,.4),d=`M470 ${y+14}H637`;
     const row=icon('chat',196,y-38,90,'accent',q)+text('重新交代',310,y+25,40,'text')+panel(637,y-35,216,91,'soft',20)+text(`任务 ${i+1}`,745,y+25,40,'text','middle');
     s+=clip(row,q,184,y-48,682,116);s+=path(d,m(t,start+.2,.55),'line',3)+packet(d,phase(t,start+.3,.7),'accent',8);
   });
   let right=panel(1014,286,780,575,'paper')+text('有 Skill',1074,365,58,ink,'start',true);
   const open=Math.sin(phase(t,2.5,.85)*Math.PI);
   let stored=folder(1094,513,248,open,ink,'paper')+text('方法存档',1218,765,40,ink,'middle',true);
   right+=group(stored,m(t,2.25,.35));
   right+=morph('paper','doc',t,2.5,.85,[1084,422,286,205],[1146,548,146,133],'paper','paper',ink,65);
   ys.forEach((y,i)=>{const start=3.25+i*.67,d=`M1320 651C1410 651 1390 ${y+14} 1470 ${y+14}`;
     const target=panel(1470,y-35,255,91,'dark',20)+text(`任务 ${i+1}`,1597,y+25,40,'text','middle');
     right+=clip(target,m(t,start,.4),1467,y-38,263,98);
     right+=path(d,m(t,start-.1,.65),mutedPaper,3)+packet(d,phase(t,start+.2,.9),ink,8);
     right+=icon('check',1730,y-7,42,ink,m(t,start+1.02,.25));
   });
   right+=clip(text('保存方法，反复调用',1074,824,34,ink),m(t,6,.35),1068,778,690,70);
   return s+settle(right,t,.05,.65,1404,574,{dy:20,scale:.96,rotate:-1});
 };
})();
