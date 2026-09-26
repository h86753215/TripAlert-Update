from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import subprocess, os, shutil

W,H=1280,720
OUT=Path("/tmp/hta-promo")
OUT.mkdir(parents=True,exist_ok=True)

FONT_B="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
ICON="hta-tangxun-icon.webp"

def f(sz,b=True):
    return ImageFont.truetype(FONT_B if b else FONT_R,sz)

def bg():
    im=Image.new("RGBA",(W,H),(8,9,13,255))
    glow=Image.new("RGBA",(W,H),(0,0,0,0))
    g=ImageDraw.Draw(glow)
    g.ellipse((760,-180,1420,500),fill=(255,52,83,90))
    g.ellipse((-240,380,480,1080),fill=(216,171,93,55))
    glow=glow.filter(ImageFilter.GaussianBlur(110))
    im.alpha_composite(glow)
    d=ImageDraw.Draw(im)
    for x in range(0,W,80): d.line((x,0,x,H),fill=(255,255,255,7))
    for y in range(0,H,80): d.line((0,y,W,y),fill=(255,255,255,7))
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
    md=ImageDraw.Draw(mask); md.rounded_rectangle((0,0,size,size),radius=int(size*.18),fill=255)
    sh=Image.new("RGBA",(size+50,size+50),(0,0,0,0))
    sd=ImageDraw.Draw(sh); sd.rounded_rectangle((22,22,22+size,22+size),radius=int(size*.18),fill=(0,0,0,150))
    sh=sh.filter(ImageFilter.GaussianBlur(16))
    im.alpha_composite(sh,(x-22,y-18))
    im.paste(src,(x,y),mask)

def pill(d,x,y,s,color):
    w=len(s)*19+32
    d.rounded_rectangle((x,y,x+w,y+40),radius=12,fill=(*color,22),outline=(*color,170),width=2)
    txt(d,(x+w/2,y+20),s,16,color,True,"mm")
    return w

slides=[]

# 1 Hero
im=bg(); d=ImageDraw.Draw(im); icon(im,855,150,280)
tag(d,62,60,"HTA 趟訊")
txt(d,(62,145),"不用一直刷 LINE。",62)
txt(d,(62,222),"先看值得看的單。",62,(241,214,152))
txt(d,(62,324),"肥單・距離・預約・順路",28,(183,190,202),False)
txt(d,(62,367),"先整理，再決定要不要接。",28,(183,190,202),False)
d.rounded_rectangle((62,500,440,570),radius=18,fill=(226,42,75))
txt(d,(251,535),"48 小時免費試用",25,(255,255,255),True,"mm")
txt(d,(62,620),"htaxun.com",22,(147,156,170),False)
slides.append(im)

# 2 Decision UI
im=bg(); d=ImageDraw.Draw(im)
tag(d,62,60,"快速判斷")
txt(d,(62,140),"一張單，先看重點。",56)
txt(d,(62,210),"不用在訊息裡慢慢找。",34,(255,94,119))
# mock phone/card
d.rounded_rectangle((700,65,1205,655),radius=34,fill=(11,14,20),outline=(55,62,75),width=2)
txt(d,(742,104),"HTA 趟訊",23)
txt(d,(1125,108),"● 上線中",16,(97,228,162),False,"ra")
cards=[("肥單・即時","桃園區 → 板橋區","接駕 2.8 km・行程 31 km","$1,260",(255,91,113)),
       ("預約","中壢區 → 松山區","23:40・接駕約 12 分","$780",(113,170,255)),
       ("順路","龜山區 → 台北方向","方向符合・可直接導航","$540",(97,228,162))]
yy=165
for t,r,s,m,c in cards:
    d.rounded_rectangle((735,yy,1170,yy+132),radius=20,fill=(18,22,30),outline=(*c,110),width=2)
    pill(d,755,yy+16,t,c)
    txt(d,(755,yy+66),r,19)
    txt(d,(755,yy+96),s,15,(138,147,162),False)
    txt(d,(1146,yy+65),m,26,(255,255,255),True,"ra")
    yy+=148
rows=[("接駕距離","分開看"),("行程公里","分開看"),("估價 / 肥單","直接標示")]
yy=345
for a,b in rows:
    d.line((62,yy-12,565,yy-12),fill=(255,255,255,25))
    txt(d,(62,yy),a,21,(184,191,203),False)
    txt(d,(565,yy),b,21,(241,214,152),True,"ra")
    yy+=65
slides.append(im)

# 3 Actions
im=bg(); d=ImageDraw.Draw(im)
tag(d,62,60,"少切畫面")
txt(d,(62,140),"看到適合的單，",56)
txt(d,(62,210),"直接往下一步。",56,(241,214,152))
items=[("10 分報時","常用分鐘快速處理"),("Google Maps","一鍵開導航"),("順路篩選","依方向輔助判斷"),("歷史 / 記帳","收入公里留下來")]
yy=330
for i,(a,b) in enumerate(items):
    x=62+(i%2)*420; y=yy+(i//2)*135
    d.rounded_rectangle((x,y,x+390,y+105),radius=20,fill=(17,21,29),outline=(255,255,255,30),width=1)
    txt(d,(x+22,y+22),a,23)
    txt(d,(x+22,y+60),b,16,(147,156,170),False)
slides.append(im)

# 4 Filters
im=bg(); d=ImageDraw.Draw(im)
tag(d,62,60,"照你的跑法篩")
txt(d,(62,140),"不是每張單，",56)
txt(d,(62,210),"都值得你花時間看。",56,(97,228,162))
badges=[("肥單",(255,91,113)),("主群／免回金",(241,201,109)),("順路",(90,224,184)),
        ("即時",(190,130,255)),("預約",(113,170,255)),("距離近→遠",(99,219,228)),("金額高→低",(241,201,109))]
x,y=62,350
for s,c in badges:
    w=max(145,len(s)*22+42)
    if x+w>1180: x=62; y+=78
    d.rounded_rectangle((x,y,x+w,y+54),radius=16,fill=(*c,25),outline=(*c,175),width=2)
    txt(d,(x+w/2,y+27),s,20,c,True,"mm")
    x+=w+16
slides.append(im)

# 5 Official LINE
im=bg(); d=ImageDraw.Draw(im); icon(im,880,170,250)
tag(d,62,60,"官方 LINE")
txt(d,(62,140),"試用、購買、更新、客服",48)
txt(d,(62,205),"全部集中一個地方。",48,(241,214,152))
features=["48 小時免費試用","授權購買／續費","版本更新","使用教學","問題回報"]
yy=330
for s in features:
    d.rounded_rectangle((62,yy,550,yy+48),radius=14,fill=(255,255,255,10),outline=(255,255,255,24))
    txt(d,(86,yy+24),"✓  "+s,18,(206,212,222),True,"lm")
    yy+=61
txt(d,(1005,470),"HTA 趟訊",30,(255,255,255),True,"mm")
txt(d,(1005,515),"官方 LINE",20,(151,160,174),False,"mm")
slides.append(im)

# 6 Offer
im=bg(); d=ImageDraw.Draw(im); icon(im,855,145,285)
tag(d,62,60,"NEW USER OFFER")
txt(d,(62,140),"先免費試 48 小時。",52)
txt(d,(62,220),"首月體驗價",34,(241,214,152))
txt(d,(62,270),"NT$499",86)
txt(d,(62,385),"之後月繳 NT$599",24,(179,187,199),False)
txt(d,(62,428),"不綁卡・不自動續費",24,(179,187,199),False)
d.rounded_rectangle((62,520,480,590),radius=18,fill=(226,42,75))
txt(d,(271,555),"加入官方 LINE 申請試用",22,(255,255,255),True,"mm")
txt(d,(62,635),"htaxun.com",20,(145,154,168),False)
slides.append(im)

slide_paths=[]
for i,im in enumerate(slides,1):
    p=OUT/f"slide{i}.png"; im.convert("RGB").save(p,quality=95); slide_paths.append(p)

# poster
slides[0].convert("RGB").save("hta-main-demo-poster.jpg",quality=88,optimize=True)

clips=[]
for i,p in enumerate(slide_paths,1):
    clip=OUT/f"clip{i}.mp4"
    subprocess.run([
        "ffmpeg","-y","-loop","1","-t","3","-i",str(p),
        "-vf","fade=t=in:st=0:d=0.18,fade=t=out:st=2.82:d=0.18,format=yuv420p",
        "-r","24","-c:v","libx264","-preset","veryfast","-crf","27","-an",str(clip)
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
