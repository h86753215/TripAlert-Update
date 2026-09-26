from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import subprocess, os

W,H=1280,720
OUT=Path("/tmp/hta-promo")
OUT.mkdir(parents=True,exist_ok=True)

FONT_B="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
APP="assets/app-real.webp"

def F(s,b=True):
    return ImageFont.truetype(FONT_B if b else FONT_R,s)

def txt(d,xy,s,size,color=(248,249,251),bold=True,anchor=None):
    d.text(xy,s,font=F(size,bold),fill=color,anchor=anchor)

def bg():
    im=Image.new("RGBA",(W,H),(7,9,13,255))
    glow=Image.new("RGBA",(W,H),(0,0,0,0))
    g=ImageDraw.Draw(glow)
    g.ellipse((780,-180,1450,500),fill=(239,54,86,72))
    g.ellipse((-240,420,520,1120),fill=(216,171,93,45))
    glow=glow.filter(ImageFilter.GaussianBlur(115))
    im.alpha_composite(glow)
    return im

def rounded_paste(base,src,xy,radius=28,shadow=True):
    x,y=xy
    src=src.convert("RGB")
    if shadow:
        sh=Image.new("RGBA",(src.width+60,src.height+60),(0,0,0,0))
        sd=ImageDraw.Draw(sh)
        sd.rounded_rectangle((25,25,25+src.width,25+src.height),radius=radius,fill=(0,0,0,185))
        sh=sh.filter(ImageFilter.GaussianBlur(17))
        base.alpha_composite(sh,(x-25,y-20))
    mask=Image.new("L",src.size,0)
    md=ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,src.width,src.height),radius=radius,fill=255)
    base.paste(src,(x,y),mask)

def fit_h(im,h):
    w=round(im.width*h/im.height)
    return im.resize((w,h),Image.LANCZOS)

app=Image.open(APP).convert("RGB")
slides=[]

# 1: full real app
im=bg(); d=ImageDraw.Draw(im)
txt(d,(52,45),"HTA 趟訊｜實際 APP 畫面",20,(241,214,152))
txt(d,(52,112),"這才是實際使用時",47)
txt(d,(52,174),"你會看到的畫面。",47,(241,214,152))
txt(d,(52,270),"車單、快速篩選、距離、金額",23,(182,190,202),False)
txt(d,(52,307),"全部集中在同一頁。",23,(182,190,202),False)
screen=fit_h(app,640)
rounded_paste(im,screen,(840-screen.width//2,40),30)
slides.append(im)

# 2: zoom quick filter section from the actual screenshot
im=bg(); d=ImageDraw.Draw(im)
txt(d,(52,45),"01｜快速篩選",20,(241,214,152))
txt(d,(52,110),"先選你現在要看的單。",45)
txt(d,(52,175),"肥單・主群／免回金・順路・即時／預約",22,(182,190,202),False)
# crop upper-middle filter area
crop=app.crop((8,115,420,430))
crop=crop.resize((760,580),Image.LANCZOS)
rounded_paste(im,crop,(475,95),28)
d=ImageDraw.Draw(im)
d.rounded_rectangle((52,300,420,363),radius=17,fill=(239,54,86,32),outline=(255,94,119,170),width=2)
txt(d,(236,332),"真正 APP 篩選區",21,(255,104,126),True,"mm")
txt(d,(52,415),"不必先進 LINE 一張一張找。",22,(241,214,152),True)
slides.append(im)

# 3: zoom actual trip card list
im=bg(); d=ImageDraw.Draw(im)
txt(d,(52,45),"02｜實際車單",20,(241,214,152))
txt(d,(52,110),"直接看上下車、",45)
txt(d,(52,170),"接駕、行程、估價。",45,(97,228,162))
txt(d,(52,258),"畫面上的資料就是 APP 實際呈現方式。",21,(181,189,201),False)
crop=app.crop((8,390,420,752))
crop=crop.resize((760,668),Image.LANCZOS)
rounded_paste(im,crop,(475,34),28)
d=ImageDraw.Draw(im)
d.rounded_rectangle((52,392,400,455),radius=17,fill=(97,228,162,25),outline=(97,228,162,150),width=2)
txt(d,(226,424),"看到單就能直接判斷",20,(97,228,162),True,"mm")
slides.append(im)

# 4: full real app + CTA
im=bg(); d=ImageDraw.Draw(im)
txt(d,(52,45),"03｜少切畫面，直接操作",20,(241,214,152))
txt(d,(52,112),"看單 → 篩選 → 導航",44)
txt(d,(52,170),"都從 HTA 接著做。",44,(241,214,152))
txt(d,(52,260),"48 小時免費試用",30,(255,255,255),True)
txt(d,(52,310),"首月體驗價 NT$499",37,(241,214,152),True)
txt(d,(52,365),"之後月繳 NT$599",20,(176,184,197),False)
txt(d,(52,403),"不綁卡・不自動續費",20,(176,184,197),False)
d.rounded_rectangle((52,505,420,568),radius=18,fill=(226,42,75))
txt(d,(236,537),"加入官方 LINE 申請",21,(255,255,255),True,"mm")
screen=fit_h(app,610)
rounded_paste(im,screen,(920-screen.width//2,64),30)
slides.append(im)

clips=[]
for i,slide in enumerate(slides,1):
    png=OUT/f"real_slide{i}.png"
    slide.convert("RGB").save(png,quality=95)
    clip=OUT/f"real_clip{i}.mp4"
    subprocess.run([
        "ffmpeg","-y","-loop","1","-t","2.6","-i",str(png),
        "-vf","fade=t=in:st=0:d=0.12,fade=t=out:st=2.48:d=0.12,format=yuv420p",
        "-r","24","-c:v","libx264","-preset","veryfast","-crf","25","-an",str(clip)
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    clips.append(clip)

lst=OUT/"concat.txt"
lst.write_text("\n".join("file '"+str(c)+"'" for c in clips),encoding="utf-8")
subprocess.run([
    "ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
    "-c","copy","-movflags","+faststart","hta-main-demo.mp4"
],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

slides[0].convert("RGB").save("hta-main-demo-poster.jpg",quality=88,optimize=True)
print("video bytes",os.path.getsize("hta-main-demo.mp4"))
