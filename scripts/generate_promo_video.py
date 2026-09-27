from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import subprocess, os

W,H=1280,720
OUT=Path("/tmp/hta-real-demo")
OUT.mkdir(parents=True,exist_ok=True)

FONT_B="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SPRITE="hta-real-app-sprite.jpg"

def F(size,bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT_R,size)

def text(draw,xy,s,size,color=(247,248,251),bold=True,anchor=None):
    draw.text(xy,s,font=F(size,bold),fill=color,anchor=anchor)

def background():
    im=Image.new("RGBA",(W,H),(7,8,12,255))
    glow=Image.new("RGBA",(W,H),(0,0,0,0))
    g=ImageDraw.Draw(glow)
    g.ellipse((760,-180,1450,500),fill=(239,54,86,72))
    g.ellipse((-220,420,520,1100),fill=(216,171,93,45))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(110)))
    return im

def round_paste(base,src,x,y,r=28):
    src=src.convert("RGB")
    sh=Image.new("RGBA",(src.width+60,src.height+60),(0,0,0,0))
    sd=ImageDraw.Draw(sh)
    sd.rounded_rectangle((24,24,24+src.width,24+src.height),radius=r,fill=(0,0,0,185))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)),(x-24,y-20))
    mask=Image.new("L",src.size,0)
    md=ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,src.width,src.height),radius=r,fill=255)
    base.paste(src,(x,y),mask)

sprite=Image.open(SPRITE).convert("RGB")
sw,sh=sprite.size
hw,hh=sw//2,sh//2
screens=[
    sprite.crop((0,0,hw,hh)),
    sprite.crop((hw,0,sw,hh)),
    sprite.crop((0,hh,hw,sh)),
    sprite.crop((hw,hh,sw,sh)),
]

# Slightly blur areas containing sender/group names while keeping the real UI visible.
def privacy(screen, mode):
    im=screen.copy()
    if mode in (0,1):
        # group/sender text is in the middle of the card
        box=(18,int(im.height*.30),im.width-14,int(im.height*.47))
    else:
        # original-preview dialog names / raw sender content
        box=(20,int(im.height*.28),im.width-18,int(im.height*.51))
    crop=im.crop(box).filter(ImageFilter.GaussianBlur(4))
    im.paste(crop,box)
    return im

screens=[privacy(s,i) for i,s in enumerate(screens)]

scenes=[
    ("APP 實際畫面","車單進來，直接看重點。","接駕・行程・效益・10/15/20 分報時",0),
    ("快速操作","看到適合的單，直接處理。","導航・看原文・複製上車地址",1),
    ("原文核對","需要確認時，直接看 LINE 原文。","複製原文・開啟 LINE 原群",2),
    ("接單流程","從看單到操作，都留在同一個流程。","48 小時免費試用｜首月 NT$499",3),
]

slides=[]
for idx,(tag,headline,sub,screen_idx) in enumerate(scenes):
    im=background()
    d=ImageDraw.Draw(im)
    text(d,(55,45),"HTA 趟訊｜APP 實機操作",19,(241,214,152),True)
    text(d,(55,112),tag,24,(241,214,152),True)
    text(d,(55,160),headline,43,(248,249,251),True)
    text(d,(55,225),sub,22,(177,185,198),False)

    src=screens[screen_idx]
    ratio=min(570/src.height,610/src.width)
    src=src.resize((int(src.width*ratio),int(src.height*ratio)),Image.LANCZOS)
    x=1230-src.width
    y=(H-src.height)//2
    round_paste(im,src,x,y,30)

    # only supporting copy — no fake UI
    if idx==0:
        text(d,(55,340),"真的 APP 畫面",31,(97,228,162),True)
        text(d,(55,390),"不是概念示意。",24,(177,185,198),False)
    elif idx==1:
        text(d,(55,340),"10 分・15 分・20 分",30,(255,104,126),True)
        text(d,(55,390),"按完就接續導航／看原文。",22,(177,185,198),False)
    elif idx==2:
        text(d,(55,340),"原文預覽",30,(113,170,255),True)
        text(d,(55,390),"必要時直接回到 LINE 原群。",22,(177,185,198),False)
    else:
        text(d,(55,340),"先免費試 48 小時",31,(248,249,251),True)
        text(d,(55,390),"首月體驗價 NT$499",31,(241,214,152),True)
        d.rounded_rectangle((55,485,455,552),radius=18,fill=(226,42,75))
        text(d,(255,519),"加入官方 LINE 申請",21,(255,255,255),True,"mm")
    slides.append(im)

clips=[]
for i,slide in enumerate(slides,1):
    png=OUT/f"slide{i}.png"
    slide.convert("RGB").save(png,quality=94)
    clip=OUT/f"clip{i}.mp4"
    subprocess.run([
        "ffmpeg","-y","-loop","1","-t","2.35","-i",str(png),
        "-vf","fade=t=in:st=0:d=0.10,fade=t=out:st=2.25:d=0.10,format=yuv420p",
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
