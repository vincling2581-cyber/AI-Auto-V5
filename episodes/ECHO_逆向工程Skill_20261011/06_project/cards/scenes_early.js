SCENES.C01=t=>{
 const k=H.k;let s=k.panel(100,302,700,602,'dark')+k.panel(910,302,900,602,'paper');
 s+=k.text('外面看见的',145,369,38,'muted')+k.text('内部发生的',960,369,38,'ink');
 s+=k.box(290,440,320,280,'#08110C','edge',22)+k.icon('question',387,495,128)+k.text('软件黑盒',450,787,46,'text','middle',true);
 const p=H.m(t,1.8,1.4),scan=H.p(t,1.8,1.4);
 const mod=k.box(295,445,310,270,'#264531','accent',20)+k.box(325,482,105,75,'accent','none',10)+k.box(469,482,105,75,'paper','none',10)+k.box(325,608,249,62,'dark','line',10)+k.path('M375 557V583H520V608',1,'accent',4);
 s+=H.reveal(mod,p,295,445,310,270);
 if(scan>0&&scan<1)s+=`<line x1="${295+310*p}" x2="${295+310*p}" y1="420" y2="740" stroke="#78EFA2" stroke-width="6"/>`;
 const d='M610 580C780 580 770 516 978 516';s+=H.transfer(d,t,3.5,1.1);
 const fields=[['模块结构','谁负责什么'],['调用逻辑','彼此怎样连接'],['风险线索','哪里值得检查']];
 fields.forEach((a,i)=>{const q=i===0?H.m(t,4.6,.45):H.m(t,4.6+i*.35,.45);s+=H.reveal(k.box(980,429+i*126,753,98,'#E2E9DF','none',16)+k.text(a[0],1010,491+i*126,42,'ink','start',true)+k.text(a[1],1315,491+i*126,34,'ink'),q,980,429+i*126,753,98)});
 return s;
};
SCENES.C02=t=>{
 const k=H.k;let s=k.panel(100,308,965,602,'dark')+k.panel(1180,308,630,602,'paper');
 const p=H.m(t,.1,1.1);s+=k.text('同一个软件',148,382,42,'text','start',true);
 const nodes=[[245,502,'入口'],[515,432,'模块 A'],[750,572,'模块 B'],[455,705,'数据']];
 const ds=['M355 546L555 486','M639 498L790 611','M553 521L520 724','M760 650L575 740'];
 ds.forEach(d=>s+=k.path(d,H.m(t,1.25,1),'line',4));
 nodes.forEach(([x,y,txt],i)=>{s+=k.group(k.box(x,y,185,88,i===2?'#23452D':'soft','edge',16)+k.text(txt,x+92,y+57,36,'text','middle'),1,(1-p)*(i%2?80:-80),0);});
 s+=k.icon('search',1240,371,82,'ink')+k.text('三个观察层',1350,432,42,'ink','start',true);
 ['结构切片','调用关系','待验证风险'].forEach((txt,i)=>s+=H.reveal(k.text('0'+(i+1),1240,560+i*117,30,'ink')+k.text(txt,1330,563+i*117,44,'ink','start',true),H.m(t,[.1,1.25,2.4][i],1),1220,509+i*117,530,88));
 const q=H.m(t,2.4,1.05);s+=k.group(`<rect x="728" y="550" width="229" height="130" rx="24" fill="none" stroke="#78EFA2" stroke-width="5"/>`,q)+k.path('M957 615C1100 615 1030 796 1235 796',q,'accent',3);
 return s;
};
SCENES.C03=t=>{
 const k=H.k;let s=k.panel(95,318,440,582,'dark')+k.panel(1128,318,680,582,'paper');
 s+=k.text('任务与样本',128,382,42,'text','start',true)+H.badge('APK',147,443,150,'accent')+H.badge('EXE',329,443,150,'soft')+k.text('示例：分析 APK',132,816,34,'muted');
 s+=k.icon('doc',241,558,118,'accent')+k.text('分析请求',315,733,46,'text','middle');
 s+=H.node('工具路由','识别样本类型',630,365,390,200,'dark','sliders');
 const route='M420 621C573 621 546 465 654 465';s+=H.transfer(route,t,.2,1.1);
 const selected=H.m(t,1.25,1.2);s+=k.group(k.panel(630,625,390,200,'accent')+k.text('Android 分析',825,695,42,'ink','middle',true)+k.text('JADX / Apktool',825,764,32,'ink','middle'),selected);
 s+=H.transfer('M825 565V625',t,1.25,1.2);
 s+=k.text('同一份分析记录',1169,384,44,'ink','start',true);
 s+=k.box(1169,430,596,152,'#E2E9DF','none',18)+k.text('证据',1201,485,34,'ink')+H.reveal(k.text('结构 · 调用 · 待验证项',1201,548,36,'ink','start',true),H.m(t,4,.4),1190,503,550,62);
 s+=H.transfer('M1020 725C1090 725 1070 515 1169 515',t,2.7,1.3);
 s+=k.box(1169,646,596,199,'#D7E7D6','none',18)+k.text('报告',1201,701,34,'ink');
 s+=H.transfer('M1467 582V646',t,4.8,1.3);
 s+=H.reveal(k.text('发现 + 依据 + 限制',1201,766,38,'ink','start',true)+k.text('保留可复核线索',1201,815,30,'ink'),H.m(t,6.1,.45),1190,720,550,120);
 return s;
};
SCENES.C04=t=>{
 const k=H.k;let s=H.node('分析结果','同一份证据来源',110,441,480,287,'dark','search');
 const d1='M590 550C820 550 790 423 1020 423',d2='M590 624C820 624 790 750 1020 750';
 s+=H.transfer(d1,t,.15,1.1)+H.transfer(d2,t,.15,1.1);
 s+=k.panel(1020,315,780,576,'paper');
 s+=k.text('交付输出',1060,385,44,'ink','start',true);
 if(t>=1.25){s+=k.icon('grid',1080,424,103,'ink')+k.text('结构图',1233,491,46,'ink','start',true)+k.text('关系看得见',1233,544,34,'ink')+k.path('M1060 604H1750',1,'paperLine',2)+k.icon('doc',1080,661,103,'ink')+k.text('分析报告',1233,727,46,'ink','start',true)+k.text('依据留得下',1233,780,34,'ink');}
 return s;
};
