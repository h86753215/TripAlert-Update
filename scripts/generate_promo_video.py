from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import subprocess, os

W,H=1280,720
OUT=Path("/tmp/hta-promo")
OUT.mkdir(parents=True,exist_ok=True)

FONT_B="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
ICON="hta-tangxun-icon.webp"

def F(s,b=True):
    return ImageFont.truetype(FONT_B if b else FONT_R,s)

def txt(d,xy,s,size,color=(248,249,251),bold=True,anchor=None):
    d.text(xy,s,font=F(size,bold),fill=color,anchor=anchor)

def bg():
    im=Image.new("RGBA",(W,H),(7,9,13,255))
    glow=Image.new("RGBA",(W,H),(0,0,0,0))
    g=ImageDraw.Draw(glow)
    g.ellipse((790,-170,1450,490),fill=(239,54,86,78))
    g.ellipse((-220,420,520,1120),fill=(216,171,93,48))
    glow=glow.filter(ImageFilter.GaussianBlur(115))
    im.alpha_composite(glow)
    d=ImageDraw.Draw(im)
    for x in range(0,W,80): d.line((x,0,x,H),fill=(255,255,255,6))
    for y in range(0,H,80): d.line((0,y,W,y),fill=(255,255,255,6))
    return im

def header(d,label):
    txt(d,(52,44),"HTA 趟訊",20,(241,214,152),True)
    d.rounded_rectangle((1060,35,1228,72),radius=18,fill=(97,228,162,20),outline=(97,228,162,100))
    txt(d,(1144,54),"● 上線中",15,(97,228,162),True,"mm")

def pill(d,x,y,s,color):
    w=max(112,len(s)*18+30)
    d.rounded_rectangle((x,y,x+w,y+38),radius=11,fill=(*color,23),outline=(*color,165),width=2)
    txt(d,(x+w/2,y+19),s,15,color,True,"mm")
    return w

def panel(d,box,title=None):
    x1,y1,x2,y2=box
    d.rounded_rectangle(box,radius=22,fill=(15,19,26,240),outline=(62,69,82,255),width=2)
    if title:
        txt(d,(x1+20,y1+16),title,15,(121,218,255),True)

slides=[]

# 1 — App list screen
im=bg(); d=ImageDraw.Draw(im); header(d,"")
txt(d,(52,102),"車單一進來，先變成能判斷的樣子。",42)
txt(d,(52,157),"不用先點回 LINE 才知道這張值不值得看。",21,(164,173,187),False)
panel(d,(52,220,1228,655),"車單列表")

cards=[
    ("肥單・即時","桃園區 → 板橋區","接駕 2.8 km  ·  行程 31 km","NT$670",(255,91,113)),
    ("預約 23:40","中壢區 → 松山區","接駕約 12 分  ·  行程 45 km","NT$950",(113,170,255)),
    ("順路","龜山區 → 新莊區","行程 18 km  ·  方向符合","NT$410",(97,228,162)),
]
yy=270
for tag,route,sub,money,col in cards:
    d.rounded_rectangle((80,yy,1200,yy+102),radius=18,fill=(20,24,32),outline=(*col,95),width=2)
    pill(d,98,yy+15,tag,col)
    txt(d,(310,yy+18),route,22)
    txt(d,(310,yy+55),sub,16,(139,148,162),False)
    txt(d,(1168,yy+51),money,29,(255,255,255),True,"rm")
    yy+=118
slides.append(im)

# 2 — Filters first screen
im=bg(); d=ImageDraw.Draw(im); header(d,"")
txt(d,(52,102),"常用篩選直接放第一屏。",44)
txt(d,(52,160),"想看什麼，就留下什麼。",23,(241,214,152),True)
panel(d,(52,225,1228,645),"快速篩選")

rows=[
    ("顯示條件",[("全部",(255,140,70)),("肥單",(255,91,113)),("主群／免回金",(241,201,109)),("順路",(97,228,162))]),
    ("時間類型",[("全部",(180,186,197)),("即時",(190,130,255)),("預約",(113,170,255))]),
    ("排序方式",[("距離近→遠",(99,219,228)),("金額高→低",(241,201,109))])
]
yy=285
for label,items in rows:
    txt(d,(85,yy),label,18,(126,220,255),True)
    xx=250
    for s,col in items:
        w=max(155,len(s)*22+42)
        d.rounded_rectangle((xx,yy-8,xx+w,yy+46),radius=15,fill=(*col,22),outline=(*col,165),width=2)
        txt(d,(xx+w/2,yy+19),s,18,col,True,"mm")
        xx+=w+12
    yy+=105
slides.append(im)

# 3 — Action workflow
im=bg(); d=ImageDraw.Draw(im); header(d,"")
txt(d,(52,102),"看到可以接，直接做下一步。",44)
txt(d,(52,160),"少打一點字，少切幾個 App。",23,(241,214,152),True)

actions=[
    ("10 分","快速報時","桃園10",(255,91,113)),
    ("導航","Google Maps","桃園區上車點",(99,219,228)),
    ("預約","準 / 晚5 / 晚10","一鍵回覆",(113,170,255)),
    ("記帳","收入與公里","完成後留下紀錄",(97,228,162)),
]
yy=245
for i,(button,title,sub,col) in enumerate(actions):
    d.rounded_rectangle((52,yy,1228,yy+88),radius=20,fill=(17,21,29),outline=(255,255,255,27),width=1)
    d.rounded_rectangle((76,yy+18,226,yy+70),radius=15,fill=(*col,32),outline=(*col,170),width=2)
    txt(d,(151,yy+44),button,20,col,True,"mm")
    txt(d,(264,yy+18),title,22)
    txt(d,(264,yy+52),sub,16,(145,154,168),False)
    txt(d,(1188,yy+44),"›",34,(241,214,152),True,"rm")
    yy+=102
slides.append(im)

# 4 — Efficiency + CTA
im=bg(); d=ImageDraw.Draw(im); header(d,"")
txt(d,(52,102),"接完也不是就消失。",44)
txt(d,(52,160),"公里、收入、效益，之後還看得到。",23,(97,228,162),True)

panel(d,(52,235,780,610),"今日摘要")
metrics=[
    ("已完成","6 趟",(255,255,255)),
    ("今日收入","NT$4,230",(241,214,152)),
    ("今日公里","186 km",(113,170,255)),
    ("每公里營收","NT$22.7",(97,228,162)),
]
positions=[(82,300),(420,300),(82,420),(420,420)]
for (label,val,col),(x,y) in zip(metrics,positions):
    txt(d,(x,y),label,15,(139,148,162),False)
    txt(d,(x,y+34),val,30,col,True)

# CTA card
d.rounded_rectangle((820,235,1228,610),radius=24,fill=(20,16,20),outline=(216,171,93,90),width=2)
txt(d,(854,275),"先免費試",20,(241,214,152),True)
txt(d,(854,318),"48 小時",52,(255,255,255),True)
txt(d,(854,392),"首月 NT$499",30,(241,214,152),True)
txt(d,(854,443),"之後月繳 NT$599",17,(166,175,188),False)
txt(d,(854,479),"不綁卡・不自動續費",17,(166,175,188),False)
d.rounded_rectangle((854,525,1193,580),radius=16,fill=(226,42,75))
txt(d,(1024,553),"加入官方 LINE 申請",19,(255,255,255),True,"mm")
txt(d,(52,650),"實機操作版｜介面為操作流程示意，功能依最新版調整",14,(119,128,142),False)
slides.append(im)

# Generate 4 x 2.2s = 8.8s
clip_paths=[]
for i,slide in enumerate(slides,1):
    png=OUT/f"b_slide{i}.png"
    slide.convert("RGB").save(png,quality=95)
    clip=OUT/f"b_clip{i}.mp4"
    subprocess.run([
        "ffmpeg","-y","-loop","1","-t","2.2","-i",str(png),
        "-vf","fade=t=in:st=0:d=0.12,fade=t=out:st=2.08:d=0.12,format=yuv420p",
        "-r","24","-c:v","libx264","-preset","veryfast","-crf","25","-an",str(clip)
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    clip_paths.append(clip)

lst=OUT/"concat.txt"
lst.write_text("\n".join("file '"+str(c)+"'" for c in clip_paths),encoding="utf-8")
subprocess.run([
    "ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
    "-c","copy","-movflags","+faststart","hta-main-demo.mp4"
],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

slides[0].convert("RGB").save("hta-main-demo-poster.jpg",quality=88,optimize=True)
print("video bytes",os.path.getsize("hta-main-demo.mp4"))
