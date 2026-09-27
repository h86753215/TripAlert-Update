from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import subprocess, os

W,H=1280,720
SRC=Path("assets/app-real-1.webp")
OUT=Path("/tmp/hta-real-demo")
OUT.mkdir(parents=True,exist_ok=True)

FONT_B="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

def F(s,b=True):
    return ImageFont.truetype(FONT_B if b else FONT_R,s)

def txt(d,xy,s,size,color=(248,249,251),bold=True,anchor=None):
    d.text(xy,s,font=F(size,bold),fill=color,anchor=anchor)

def bg():
    im=Image.new("RGBA",(W,H),(7,8,12,255))
    gl=Image.new("RGBA",(W,H),(0,0,0,0))
    gd=ImageDraw.Draw(gl)
    gd.ellipse((760,-150,1450,500),fill=(239,54,86,76))
    gd.ellipse((-220,420,520,1100),fill=(216,171,93,42))
    gl=gl.filter(ImageFilter.GaussianBlur(110))
    im.alpha_composite(gl)
    return im

def fit_h(im,h):
    return im.resize((round(im.width*h/im.height),h),Image.Resampling.LANCZOS)

def paste_phone(base,src,x,y):
    sh=Image.new("RGBA",(src.width+60,src.height+60),(0,0,0,0))
    sd=ImageDraw.Draw(sh)
    sd.rounded_rectangle((22,22,22+src.width,22+src.height),radius=32,fill=(0,0,0,185))
    sh=sh.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(sh,(x-22,y-18))
    mask=Image.new("L",src.size,0)
    md=ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,*src.size),radius=28,fill=255)
    base.paste(src,(x,y),mask)

app=Image.open(SRC).convert("RGB")
phone=fit_h(app,620)

scenes=[]

# 1 Full app screen
im=bg(); d=ImageDraw.Draw(im)
txt(d,(54,46),"HTA 趟訊｜APP 實機畫面",20,(241,214,152))
txt(d,(54,120),"不是概念圖。",52)
txt(d,(54,185),"直接看真正程式畫面。",48,(241,214,152))
txt(d,(54,300),"車單列表・快速篩選・距離・估價",24,(180,188,201),False)
txt(d,(54,342),"都在 APP 裡直接操作。",24,(180,188,201),False)
paste_phone(im,phone,840-phone.width//2,48)
scenes.append(im.convert("RGB"))

# 2 Filter focus
im=bg(); d=ImageDraw.Draw(im)
txt(d,(54,46),"01｜快速篩選",20,(241,214,152))
txt(d,(54,120),"肥單、順路、即時、預約",44)
txt(d,(54,177),"常用條件直接在第一屏。",36,(97,228,162))
txt(d,(54,300),"距離近 → 遠",28,(99,219,228))
txt(d,(54,350),"金額高 → 低",28,(241,201,109))
txt(d,(54,400),"主群／免回金",28,(255,103,126))
crop=app.crop((0,0,app.width,int(app.height*.58))).resize((560,650),Image.Resampling.LANCZOS)
paste_phone(im,crop,680,35)
scenes.append(im.convert("RGB"))

# 3 Trip card focus
im=bg(); d=ImageDraw.Draw(im)
txt(d,(54,46),"02｜車單資訊",20,(241,214,152))
txt(d,(54,120),"看到單，先看值不值得。",44)
txt(d,(54,180),"上下車、距離、公里、估價",34,(241,214,152))
txt(d,(54,300),"桃園區 → 板橋區",30)
txt(d,(54,350),"接駕 2.8 km｜行程 31 km",24,(180,188,201),False)
txt(d,(54,392),"估價 NT$670",30,(241,201,109))
crop=app.crop((0,int(app.height*.35),app.width,app.height)).resize((560,650),Image.Resampling.LANCZOS)
paste_phone(im,crop,680,35)
scenes.append(im.convert("RGB"))

# 4 CTA + actual app still visible
im=bg(); d=ImageDraw.Draw(im)
txt(d,(54,46),"03｜直接往下一步",20,(241,214,152))
txt(d,(54,120),"看單 → 篩選 → 操作",44)
txt(d,(54,180),"少切畫面，接單節奏更快。",34,(97,228,162))
txt(d,(54,300),"48 小時免費試用",30)
txt(d,(54,352),"首月 NT$499",44,(241,214,152))
txt(d,(54,420),"不綁卡・不自動續費",21,(180,188,201),False)
d.rounded_rectangle((54,510,450,578),radius=18,fill=(226,42,75))
txt(d,(252,544),"加入官方 LINE 申請",21,(255,255,255),True,"mm")
paste_phone(im,phone,840-phone.width//2,48)
scenes.append(im.convert("RGB"))

clips=[]
for i,s in enumerate(scenes,1):
    png=OUT/f"scene{i}.png"
    s.save(png,quality=95)
    clip=OUT/f"clip{i}.mp4"
    subprocess.run([
        "ffmpeg","-y","-loop","1","-t","2.25","-i",str(png),
        "-vf","fade=t=in:st=0:d=0.12,fade=t=out:st=2.13:d=0.12,format=yuv420p",
        "-r","24","-c:v","libx264","-preset","veryfast","-crf","27","-an",str(clip)
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    clips.append(clip)

lst=OUT/"concat.txt"
lst.write_text("\n".join("file '"+str(c)+"'" for c in clips),encoding="utf-8")
subprocess.run([
    "ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
    "-c","copy","-movflags","+faststart","hta-main-demo.mp4"
],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

scenes[0].save("hta-main-demo-poster.jpg",quality=86,optimize=True)
print("video bytes",os.path.getsize("hta-main-demo.mp4"))
