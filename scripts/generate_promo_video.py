from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import subprocess, os

W,H=1280,720
OUT=Path("/tmp/hta-promo")
OUT.mkdir(parents=True,exist_ok=True)

FONT_B="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
ICON="hta-tangxun-icon.webp"

def f(sz,b=True):
    return ImageFont.truetype(FONT_B if b else FONT_R,sz)

def bg():
    im=Image.new("RGBA",(W,H),(7,8,12,255))
    glow=Image.new("RGBA",(W,H),(0,0,0,0))
    g=ImageDraw.Draw(glow)
    g.ellipse((760,-180,1440,500),fill=(255,52,83,88))
    g.ellipse((-260,400,500,1080),fill=(216,171,93,52))
    glow=glow.filter(ImageFilter.GaussianBlur(115))
    im.alpha_composite(glow)
    d=ImageDraw.Draw(im)
    for x in range(0,W,80): d.line((x,0,x,H),fill=(255,255,255,6))
    for y in range(0,H,80): d.line((0,y,W,y),fill=(255,255,255,6))
    return im

def txt(d,xy,s,sz,color=(248,249,251),bold=True,anchor=None):
    d.text(xy,s,font=f(sz,bold),fill=color,anchor=anchor)

def tag(d,x,y,s,color=(241,214,152)):
    w=max(160,len(s)*20+38)
    d.rounded_rectangle((x,y,x+w,y+42),radius=21,fill=(*color,24),outline=(*color,100),width=1)
    txt(d,(x+w/2,y+21),s,17,color,True,"mm")

def icon(im,x,y,size):
    src=Image.open(ICON).convert("RGB").resize((size,size),Image.LANCZOS)
    mask=Image.new("L",(size,size),0)
    md=ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,size,size),radius=int(size*.18),fill=255)
    sh=Image.new("RGBA",(size+50,size+50),(0,0,0,0))
    sd=ImageDraw.Draw(sh)
    sd.rounded_rectangle((22,22,22+size,22+size),radius=int(size*.18),fill=(0,0,0,150))
    sh=sh.filter(ImageFilter.GaussianBlur(16))
    im.alpha_composite(sh,(x-22,y-18))
    im.paste(src,(x,y),mask)

def pill(d,x,y,s,color):
    w=max(110,len(s)*19+32)
    d.rounded_rectangle((x,y,x+w,y+40),radius=12,fill=(*color,22),outline=(*color,170),width=2)
    txt(d,(x+w/2,y+20),s,16,color,True,"mm")
    return w

slides=[]

# 1 — Pain point first: show LINE chaos immediately
im=bg(); d=ImageDraw.Draw(im)
tag(d,54,48,"每天都在刷群組？",(255,91,113))
txt(d,(54,118),"車單一直跳，",58)
txt(d,(54,188),"真正值得看的只有幾張。",58,(241,214,152))
txt(d,(54,284),"別再一則一則慢慢找。",28,(178,186,198),False)
# LINE-like raw notification stack
x1,y1,x2=735,90,1210
msgs=[
    ("LINE 車隊 A","桃園區 XX路 → 板橋區 XX路 31K"),
    ("LINE 車隊 B","23:40 中壢區 → 松山區 預約"),
    ("LINE 車隊 C","八德區 XX路 上車／新莊區 下車"),
    ("LINE 車隊 D","桃園區 即時單 2.8K 接駕")
]
yy=y1
for title,msg in msgs:
    d.rounded_rectangle((x1,yy,x2,yy+118),radius=22,fill=(20,24,31),outline=(255,255,255,26),width=1)
    d.ellipse((x1+18,yy+19,x1+54,yy+55),fill=(6,199,85))
    txt(d,(x1+70,yy+18),title,17)
    txt(d,(x1+22,yy+67),msg,16,(174,182,194),False)
    yy+=132
d.rounded_rectangle((54,520,446,592),radius=18,fill=(226,42,75))
txt(d,(250,556),"HTA 幫你先整理",24,(255,255,255),True,"mm")
slides.append(im)

# 2 — The most important slide: raw order -> decision card
im=bg(); d=ImageDraw.Draw(im)
tag(d,54,48,"HTA 自動整理",(97,228,162))
txt(d,(54,118),"先把這張單",58)
txt(d,(54,188),"變成能直接判斷的資訊。",54,(241,214,152))
# route card
d.rounded_rectangle((54,300,1225,625),radius=30,fill=(15,19,26),outline=(85,91,105),width=2)
pill(d,82,326,"肥單・即時",(255,91,113))
txt(d,(82,392),"桃園區  →  板橋區",34)
# big metrics
metrics=[
    ("接駕","2.8 km",(99,219,228)),
    ("行程","31 km",(113,170,255)),
    ("估價","NT$670",(241,201,109)),
]
xx=82
for label,val,col in metrics:
    d.rounded_rectangle((xx,462,xx+300,565),radius=20,fill=(*col,14),outline=(*col,70),width=1)
    txt(d,(xx+18,480),label,16,(145,154,168),False)
    txt(d,(xx+18,516),val,32,col,True)
    xx+=325
txt(d,(82,594),"範例估價：基本 50 + 20 / km｜31 km = 670 元",15,(126,135,149),False)
slides.append(im)

# 3 — Direct action after deciding
im=bg(); d=ImageDraw.Draw(im)
tag(d,54,48,"看懂後直接做")
txt(d,(54,118),"覺得可以接？",58)
txt(d,(54,188),"不用再切一堆畫面。",56,(241,214,152))
actions=[
    ("10 分","快速回覆分鐘","→"),
    ("導航","直接開 Google Maps","→"),
    ("記帳","收入／公里留下來","✓"),
]
yy=318
for i,(a,b,c) in enumerate(actions):
    d.rounded_rectangle((54,yy,1195,yy+92),radius=22,fill=(17,21,29),outline=(255,255,255,28),width=1)
    d.rounded_rectangle((78,yy+20,212,yy+72),radius=15,fill=(226,42,75) if i==0 else (34,39,50))
    txt(d,(145,yy+46),a,22,(255,255,255),True,"mm")
    txt(d,(250,yy+29),b,22)
    txt(d,(1145,yy+46),c,30,(97,228,162) if c=="✓" else (241,214,152),True,"mm")
    yy+=108
txt(d,(54,652),"從「看到單」到「回覆／導航」留在同一個流程。",17,(142,151,164),False)
slides.append(im)

# 4 — Filters, but practical
im=bg(); d=ImageDraw.Draw(im)
tag(d,54,48,"照你的跑法看")
txt(d,(54,118),"不是每張單都要看。",56)
txt(d,(54,188),"只留你現在想接的。",56,(97,228,162))
groups=[
    ("我只想看","肥單","主群／免回金","順路"),
    ("我現在要","即時","預約","距離近→遠"),
    ("我想先搶","金額高→低","接駕近","方向對"),
]
yy=320
colors=[(255,91,113),(241,201,109),(97,228,162)]
for gi,row in enumerate(groups):
    txt(d,(54,yy+10),row[0],18,(144,153,167),False)
    xx=210
    for s in row[1:]:
        w=max(150,len(s)*22+42)
        col=colors[gi]
        d.rounded_rectangle((xx,yy,xx+w,yy+54),radius=16,fill=(*col,22),outline=(*col,145),width=2)
        txt(d,(xx+w/2,yy+27),s,19,col,True,"mm")
        xx+=w+14
    yy+=100
slides.append(im)

# 5 — Strong CTA
im=bg(); d=ImageDraw.Draw(im); icon(im,870,150,275)
tag(d,54,48,"現在就能試",(241,214,152))
txt(d,(54,118),"先免費試 48 小時。",54)
txt(d,(54,195),"首月體驗價",30,(241,214,152))
txt(d,(54,242),"NT$499",86)
txt(d,(54,360),"之後月繳 NT$599",23,(178,186,198),False)
txt(d,(54,402),"不綁卡・不自動續費",23,(178,186,198),False)
d.rounded_rectangle((54,500,510,572),radius=18,fill=(226,42,75))
txt(d,(282,536),"加入官方 LINE 申請試用",22,(255,255,255),True,"mm")
txt(d,(54,628),"htaxun.com",21,(147,156,170),False)
txt(d,(1008,480),"HTA 趟訊",31,(255,255,255),True,"mm")
txt(d,(1008,526),"少刷群組，先看值得看的單",17,(150,159,173),False,"mm")
slides.append(im)

slide_paths=[]
for i,im in enumerate(slides,1):
    p=OUT/f"slide{i}.png"
    im.convert("RGB").save(p,quality=95)
    slide_paths.append(p)

slides[0].convert("RGB").save("hta-main-demo-poster.jpg",quality=88,optimize=True)

clips=[]
for i,p in enumerate(slide_paths,1):
    clip=OUT/f"clip{i}.mp4"
    subprocess.run([
        "ffmpeg","-y","-loop","1","-t","2.8","-i",str(p),
        "-vf","zoompan=z='min(zoom+0.00045,1.025)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=68:s=1280x720:fps=24,fade=t=in:st=0:d=0.12,fade=t=out:st=2.68:d=0.12,format=yuv420p",
        "-r","24","-c:v","libx264","-preset","veryfast","-crf","26","-an",str(clip)
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    clips.append(clip)

lst=OUT/"concat.txt"
lst.write_text("\n".join("file '"+str(c)+"'" for c in clips),encoding="utf-8")
subprocess.run([
    "ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
    "-c","copy","-movflags","+faststart","hta-main-demo.mp4"
],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

print("video bytes",os.path.getsize("hta-main-demo.mp4"))
print("poster bytes",os.path.getsize("hta-main-demo-poster.jpg"))
