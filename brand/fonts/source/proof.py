import sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from PIL import Image, ImageDraw, ImageChops

class Flat(BasePen):
    def __init__(self, gs):
        super().__init__(gs); self.contours=[]; self.cur=[]
    def _moveTo(self,p): self.cur=[p]
    def _lineTo(self,p): self.cur.append(p)
    def _curveToOne(self,a,b,c):
        p0=self.cur[-1]
        for i in range(1,13):
            t=i/12;u=1-t
            self.cur.append((u**3*p0[0]+3*u*u*t*a[0]+3*u*t*t*b[0]+t**3*c[0], u**3*p0[1]+3*u*u*t*a[1]+3*u*t*t*b[1]+t**3*c[1]))
    def _closePath(self):
        if len(self.cur)>2: self.contours.append(self.cur)
        self.cur=[]
    _endPath=_closePath

def render(fontpath, lines, out, size=110, width=2400, color=(47,107,98)):
    blob=hb.Blob.from_file_path(fontpath); face=hb.Face(blob); font=hb.Font(face)
    tt=TTFont(fontpath); gs=tt.getGlyphSet(); order=tt.getGlyphOrder()
    sc=size/1000; lh=int(size*1.35); pad=40
    H=pad*2+lh*len(lines)
    mask=Image.new('1',(width,H),0)
    for li,(text,feat) in enumerate(lines):
        buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        hb.shape(font,buf,feat)
        x=pad; base=pad+li*lh+int(size*0.95)
        for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
            name=order[info.codepoint]; pen=Flat(gs); gs[name].draw(pen)
            for c in pen.contours:
                m=Image.new('1',(width,H),0)
                ImageDraw.Draw(m).polygon([(x+(px+pos.x_offset)*sc, base-(py+pos.y_offset)*sc) for px,py in c],fill=1)
                mask=ImageChops.logical_xor(mask,m)
            x+=pos.x_advance*sc
    img=Image.new('RGB',(width,H),(255,255,255))
    img.paste(Image.new('RGB',(width,H),color),mask=mask.convert('L'))
    img.save(out)

if __name__=='__main__':
    f=sys.argv[1]; out=sys.argv[2]; size=int(sys.argv[3]) if len(sys.argv)>3 else 110
    lines=[(l,{}) if not l.startswith('~') else (l[1:],{'liga':False}) for l in sys.argv[4:]]
    render(f,lines,out,size)
