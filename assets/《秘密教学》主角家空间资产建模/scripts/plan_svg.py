from pathlib import Path
import math, html
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'平面确认'
INK='#263c45';WALL='#425861';BLUE='#4188a0';TEAL='#3b887a';ORANGE='#c27b35'
OPEN=[]
class Sheet:
    def __init__(self,title,sub,bounds,scale=60,offset=(100,1420),size=(1800,1700)):
        self.title=title;self.bounds=bounds;self.scale=scale;self.ox,self.oy=offset;self.w,self.h=size
        self.p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">', '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="#3b887a"/></marker></defs>', '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;fill:#263c45} .small{font-size:15px} .num{font-family:Arial,sans-serif}</style>',f'<rect width="{self.w}" height="{self.h}" fill="#faf9f5"/>']
        self.txt(65,65,title,32,weight=700);self.txt(65,102,sub,17)
        self.txt(65,self.h-44,'待确认平面方案 P2 · 横向展开 · 2026-10-17 · 影视设计参考尺寸，非实测 / 非施工图 · 尚未写入 V4 模型',16)
        self.p.append(f'<path d="M65 {self.h-72}H{self.w-65}" stroke="#bec9c5"/>')
    def xy(self,x,y):return (self.ox+x*self.scale,self.oy-y*self.scale)
    def txt(self,x,y,t,size=16,anchor='start',weight=400,color=None):
        self.p.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}"'+(f' style="fill:{color}"' if color else '')+'>'+html.escape(str(t))+'</text>')
    def wt(self,x,y,t,size=15,**kw):self.txt(*self.xy(x,y),t,size,**kw)
    def rect(self,b,fill='none',stroke=INK,sw=1,dash=None,rx=0):
        x,y=self.xy(b[0],b[3]);w=(b[2]-b[0])*self.scale;h=(b[3]-b[1])*self.scale
        self.p.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
    def line(self,a,b,col=INK,w=1,dash=None,arrow=False):
        x,y=self.xy(*a);xx,yy=self.xy(*b)
        self.p.append(f'<path d="M{x:.2f} {y:.2f}L{xx:.2f} {yy:.2f}" fill="none" stroke="{col}" stroke-width="{w}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arr)"' if arrow else '')+'/>')
    def circ(self,x,y,r,fill,stroke=INK):
        a,b=self.xy(x,y);self.p.append(f'<circle cx="{a:.2f}" cy="{b:.2f}" r="{r*self.scale:.2f}" fill="{fill}" stroke="{stroke}"/>')
    def poly(self,points,fill,stroke=INK,w=1):
        ps=' '.join(f'{x:.2f},{y:.2f}' for x,y in [self.xy(*p) for p in points]);self.p.append(f'<polygon points="{ps}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>')
    def dim(self,a,b,label,small=False):
        self.line(a,b,ORANGE,1.3)
        dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy);px,py=-dy/n*.08,dx/n*.08
        for p in [a,b]:self.line((p[0]-px,p[1]-py),(p[0]+px,p[1]+py),ORANGE,1.5)
        m=((a[0]+b[0])/2,(a[1]+b[1])/2)
        if abs(dx)<.01:
            x,y=self.xy(*m);self.p.append(f'<text x="{x-9:.2f}" y="{y:.2f}" font-size="{13 if small else 16}" text-anchor="middle" transform="rotate(-90 {x-9:.2f} {y:.2f})" style="fill:{ORANGE}">{html.escape(label)}</text>')
        else:self.wt(m[0],m[1]+.12,label,13 if small else 16,anchor='middle',color=ORANGE)
    def notes(self,x,y,sections,width=600):
        for title,lines in sections:
            self.p.append(f'<rect x="{x}" y="{y-24}" width="{width}" height="34" fill="#e3ebe6" rx="4"/>');self.txt(x+14,y,title,20,weight=700);y+=35
            for line in lines:self.txt(x+14,y,line,16);y+=29
            y+=25
    def finish(self,name):
        self.p.append('</svg>');(OUT/(name+'.svg')).write_text('\n'.join(self.p),encoding='utf8')

def furniture(s,f,detail=False):
    b=f['box'];x,y,xx,yy=b;k=f['kind'];c=f['color'];cx=(x+xx)/2;cy=(y+yy)/2
    if k in ['rug','starrug']:s.rect(b,c,'#c2c1bd',.7,dash='4 3')
    elif k in ['circle','roundrug','trampoline']:s.circ(cx,cy,min(xx-x,yy-y)/2,c)
    else:s.rect(b,c,'#7b8987',1,rx=3)
    if k=='bed':
        # Master headboard south, all upstairs beds headboard north.
        hd=f.get('head','N')
        if hd in ['N','S']:
            hy=yy-.45 if hd=='N' else y+.05
            s.rect([x+.08,hy,xx-.08,hy+.35],'#f4f0e7','#82908d',.7,rx=4)
        else:
            hx=xx-.45 if hd=='E' else x+.05
            s.rect([hx,y+.08,hx+.35,yy-.08],'#f4f0e7','#82908d',.7,rx=4)
    elif k=='desk':
        if xx-x>yy-y:s.rect([cx-.26,yy-.18,cx+.26,yy-.07],'#597078',INK,.5)
        else:s.rect([x+.08,cy-.26,x+.19,cy+.26],'#597078',INK,.5)
    elif k=='hob':
        for a in [x+.2,xx-.2]:
            for z in [y+.16,yy-.16]:s.circ(a,z,.07,'none')
    elif k in ['sink','tub']:s.rect([x+.08,y+.08,xx-.08,yy-.08],'#eff6f5','#8da7ac',1,rx=6)
    elif k=='wc':s.circ(cx,cy,.2,'#fff')
    elif k=='bike':s.line((x+.15,y+.15),(xx-.15,yy-.15),INK,3);s.circ(cx,cy,.18,'none')
    elif k=='scope':
        for pt in [(x,y),(xx,y),(cx,yy)]:s.line((cx,cy),pt,INK,1.5)
        s.line((x,yy),(xx,y),INK,4)
    elif k=='starrug':
        pts=[]
        for i in range(10):
            t=i*math.pi/5+math.pi/2;r=.72 if i%2==0 else .3;pts.append((cx+r*math.cos(t),cy+r*math.sin(t)))
        s.poly(pts,'#71809d','none')
    if detail:
        label=f['name'];txtsize=14
        # Put long labels outside narrow symbols, ID inside identifies each item unambiguously.
        s.wt(cx,cy-.055,f['id'],14,anchor='middle',weight=700)
    elif k not in ['rug','roundrug','starrug']:s.wt(cx,cy-.05,f['id'],10,anchor='middle')

def wall_draw(s,w,ids=True):
    a,b=w['a'],w['b'];hor=a[1]==b[1];start=a[0] if hor else a[1];end=b[0] if hor else b[1];fixed=a[1] if hor else a[0]
    op=sorted([o for o in OPEN if o['wall']==w['id']],key=lambda z:z['start']);cursor=start
    def pt(t):return (t,fixed) if hor else (fixed,t)
    for o in op+[dict(start=end,end=end,type='end')]:
        if o['start']>cursor:s.line(pt(cursor),pt(o['start']),WALL,w['thickness']*s.scale)
        if o['type']=='end':break
        u,v=o['start'],o['end'];t=o['type'];r=v-u
        if t in ['window','glass']:
            for off in [-.035,.035]:s.line((u,fixed+off) if hor else (fixed+off,u),(v,fixed+off) if hor else (fixed+off,v),BLUE,1.8)
            s.line(pt((u+v)/2-.015),pt((u+v)/2+.015),BLUE,7)
            if t=='glass':s.line((u+.1,fixed+.13) if hor else (fixed+.13,u+.1),(v-.1,fixed+.13) if hor else (fixed+.13,v-.1),TEAL,1.2,arrow=True)
        elif t=='door':
            sign=o.get('side',1);hinge=pt(u);tip=(u,fixed+sign*r) if hor else (fixed+sign*r,u)
            s.line(hinge,tip,'#8e7859',1.8)
            pts=[]
            for i in range(21):
                th=i/20*math.pi/2;pts.append((u+r*math.cos(th),fixed+sign*r*math.sin(th)) if hor else (fixed+sign*r*math.sin(th),u+r*math.cos(th)))
            for p,q in zip(pts,pts[1:]):s.line(p,q,'#b0a28e',.8)
        elif t=='open':s.line(pt(u),pt(v),TEAL,1.5,'5 5')
        if ids:
            p=pt((u+v)/2);s.wt(p[0]+(.15 if not hor else 0),p[1]+(.17 if hor else 0),o['id'],10,color=BLUE if t in ['window','glass'] else INK)
        cursor=o['end']
