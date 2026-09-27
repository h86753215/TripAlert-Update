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

def fit_box(im,max_w,max_h):
    ratio=min(max_w/im.width,max_h/im.height)
    return im.resize((max(1,int(im.width*ratio)),max(1,int(im.height*ratio))),Image.LANCZOS)

app=Image.open(APP).convert("RGB")
aw,ah=app.size
print("APP screenshot", aw, ah)

slides=[]

# 1 — actual app full screen
im=bg(); d=ImageDraw.Draw(im)
txt(d,(52,45),"HTA 趟訊｜APP 實際畫面",20,(241,214,152))
txt(d,(52,112),"這才是實際使用時",47)
txt(d,(52,174),"你會看到的程式畫面。",47,(241,214,152))
txt(d,(52,270),"車單列表・快速篩選・距離・估價",23,(182,190,202),False)
txt(d,(52,307),"全部直接看真實 APP。",23,(182,190,202),False)
screen=fit_box(app,540,640)
rounded_paste(im,screen,(1200-screen.width,40),30)
d=ImageDraw.Draw(im)
d.rounded_rectangle((52,470,410,535),radius=18,fill=(97,228,162,24),outline=(97,228,162,150),width=2)
txt(d,(231,503),"真實程式畫面，不是假 UI",20,(97,228,162),True,"mm")
slides.append(im)

# 2 — actual filter area enlarged
im=bg(); d=ImageDraw.Draw(im)
txt(d,(52,45),"01｜快速篩選",20,(241,214,152))
txt(d,(52,110),"肥單、順路、即時、預約",43)
txt(d,(52,168),"直接從 APP 第一屏操作。",38,(97,228,162))
txt(d,(52,285),"距離近 → 遠",27,(99,219,228))
txt(d,(52,335),"金額高 → 低",27,(241,201,109))
txt(d,(52,385),"主群／免回金",27,(255,103,126))
# upper-middle section of the actual screenshot
crop=app.crop((int(aw*.02),int(ah*.12),int(aw*.98),int(ah*.55)))
crop=fit_box(crop,720,610)
rounded_paste(im,crop,(1230-crop.width,75),28)
slides.append(im)

# 3 — actual trip card area enlarged
im=bg(); d=ImageDraw.Draw(im)
txt(d,(52,45),"02｜實際車單",20,(241,214,152))
txt(d,(52,110),"直接看上下車、接駕、",43)
txt(d,(52,168),"行程、系統估價。",43,(241,214,152))
txt(d,(52,270),"不用先回 LINE",25,(182,190,202),False)
txt(d,(52,310),"才知道這張值不值得看。",25,(182,190,202),False)
crop=app.crop((int(aw*.02),int(ah*.45),int(aw*.98),int(ah*.97)))
crop=fit_box(crop,720,640)
rounded_paste(im,crop,(1230-crop.width,40),28)
slides.append(im)

# 4 — actual screen + CTA
im=bg(); d=ImageDraw.Draw(im)
txt(d,(52,45),"03｜看完直接往下做",20,(241,214,152))
txt(d,(52,112),"看單 → 篩選 → 導航",44)
txt(d,(52,170),"操作都接在同一個流程。",40,(97,228,162))
txt(d,(52,278),"48 小時免費試用",30)
txt(d,(52,330),"首月體驗價 NT$499",38,(241,214,152))
txt(d,(52,385),"之後月繳 NT$599",20,(176,184,197),False)
txt(d,(52,423),"不綁卡・不自動續費",20,(176,184,197),False)
d.rounded_rectangle((52,515,430,580),radius=18,fill=(226,42,75))
txt(d,(241,548),"加入官方 LINE 申請",21,(255,255,255),True,"mm")
screen=fit_box(app,500,600)
rounded_paste(im,screen,(1200-screen.width,70),30)
slides.append(im)

clips=[]
for i,slide in enumerate(slides,1):
    png=OUT/f"real_slide{i}.png"
    slide.convert("RGB").save(png,quality=95)
    clip=OUT/f"real_clip{i}.mp4"
    subprocess.run([
        "ffmpeg","-y","-loop","1","-t","2.45","-i",str(png),
        "-vf","fade=t=in:st=0:d=0.10,fade=t=out:st=2.35:d=0.10,format=yuv420p",
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
