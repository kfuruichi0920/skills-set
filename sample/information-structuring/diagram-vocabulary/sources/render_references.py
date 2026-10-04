"""Render retained editable references locally. Requires Draw.io desktop and Pillow."""
from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
IDS=list(range(1,61))
def main():
 doc=json.loads((ROOT/'official-assets.json').read_text(encoding='utf-8'));target=ROOT/'reference-previews';target.mkdir(exist_ok=True)
 items=[]
 for n in IDS:
  asset=doc['assets'][n-1];src=ROOT/asset['local_path'];out=target/(asset['id']+'.png')
  r=subprocess.CompletedProcess([],0) if out.exists() else subprocess.run(['C:/Program Files/draw.io/draw.io.exe','--export','--format','png','--scale','0.7','--border','20','--page-index','1','--output',str(out.resolve()),str(src.resolve())],capture_output=True,text=True,timeout=90)
  asset['render_status']='ok' if out.exists() else 'failed';asset['preview_path']='reference-previews/'+out.name
  if out.exists():items.append(asset)
  print(asset['id'],asset['render_status'],flush=True)
 for start in range(0,len(items),12):
  canvas=Image.new('RGB',(1800,1280),'#eeeeee');d=ImageDraw.Draw(canvas)
  for j,a in enumerate(items[start:start+12]):
   im=Image.open(ROOT/a['preview_path']).convert('RGB');im.thumbnail((560,265));x=20+(j%3)*600;y=20+(j//3)*320;canvas.paste(im,(x+(560-im.width)//2,y+30));d.text((x,y),a['id']+' '+a['repository_path'].split('/')[-1],fill='black')
  canvas.save(target/f'contact-{start//12+1:02}.png')
 (ROOT/'official-assets.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
