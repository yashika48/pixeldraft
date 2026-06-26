"""
label_tool.py — Tiny local tool to hand-label real screenshots.

You need ~50-100 labeled REAL screenshots (not synthetic) to measure the
sim-to-real gap honestly. This serves a one-page browser UI: pick a class, drag
boxes on the image, export YOLO labels. No internet needed.

Usage:
    python label_tool.py --images real_test_set/images
    # open http://localhost:7000 ; label; click "Download labels"; save the .txt
    # next to images under real_test_set/labels/<same_name>.txt

This is intentionally minimal — labeling 50-100 images is a couple of focused hours.
"""

import argparse
import glob
import http.server
import json
import os
import pathlib
import socketserver

CLASSES = [
    "button", "input", "textarea", "checkbox", "radio", "toggle", "select",
    "label", "heading", "paragraph", "link", "badge", "avatar", "icon_button",
    "image", "card", "navbar", "list_item",
]

PAGE = """<!DOCTYPE html><html><head><meta charset=utf-8><title>PixelDraft labeler</title>
<style>
 body{font:14px system-ui;margin:0;display:flex;height:100vh}
 #side{width:200px;padding:12px;background:#f1f5f9;overflow:auto}
 #main{flex:1;overflow:auto;position:relative;background:#334155}
 .cls{display:block;padding:6px 8px;margin:2px 0;border-radius:6px;cursor:pointer;background:#fff;border:1px solid #cbd5e1}
 .cls.active{background:#2563eb;color:#fff}
 #wrap{position:relative;display:inline-block}
 #img{display:block;max-width:none}
 .box{position:absolute;border:2px solid #22c55e;font:11px monospace;color:#fff;background:rgba(34,197,94,.15)}
 button{width:100%;padding:8px;margin-top:8px;border:0;border-radius:6px;background:#0f172a;color:#fff;cursor:pointer}
</style></head><body>
<div id=side>
  <b>Class</b><div id=classes></div>
  <button onclick=prev()>&larr; Prev</button>
  <button onclick=next()>Next &rarr;</button>
  <button onclick=undo()>Undo box</button>
  <button onclick=download()>Download labels</button>
  <p id=info></p>
</div>
<div id=main><div id=wrap><img id=img></div></div>
<script>
let imgs=[],idx=0,cls=0,boxes=[],drawing=null;
const CLASSES=%CLASSES%;
fetch('/list').then(r=>r.json()).then(d=>{imgs=d;load()});
const cdiv=document.getElementById('classes');
CLASSES.forEach((c,i)=>{const e=document.createElement('div');e.className='cls';e.textContent=i+' '+c;
 e.onclick=()=>{cls=i;document.querySelectorAll('.cls').forEach(x=>x.classList.remove('active'));e.classList.add('active')};
 cdiv.appendChild(e)});cdiv.children[0].classList.add('active');
const img=document.getElementById('img'),wrap=document.getElementById('wrap');
function load(){boxes=[];img.src='/img/'+imgs[idx];img.onload=()=>{render();info()}}
function info(){document.getElementById('info').textContent=(idx+1)+'/'+imgs.length+' — '+imgs[idx]+' — '+boxes.length+' boxes'}
wrap.onmousedown=e=>{const r=img.getBoundingClientRect();drawing={x:e.clientX-r.left,y:e.clientY-r.top,cls:cls}};
wrap.onmousemove=e=>{if(!drawing)return;const r=img.getBoundingClientRect();drawing.x2=e.clientX-r.left;drawing.y2=e.clientY-r.top;render(drawing)};
wrap.onmouseup=e=>{if(drawing&&drawing.x2){boxes.push(drawing)}drawing=null;render();info()};
function render(temp){document.querySelectorAll('.box').forEach(b=>b.remove());
 const all=temp?boxes.concat([temp]):boxes;
 all.forEach(b=>{const x1=Math.min(b.x,b.x2||b.x),y1=Math.min(b.y,b.y2||b.y);
  const w=Math.abs((b.x2||b.x)-b.x),h=Math.abs((b.y2||b.y)-b.y);
  const d=document.createElement('div');d.className='box';d.style.left=x1+'px';d.style.top=y1+'px';
  d.style.width=w+'px';d.style.height=h+'px';d.textContent=CLASSES[b.cls];wrap.appendChild(d)})}
function undo(){boxes.pop();render();info()}
function next(){if(idx<imgs.length-1){idx++;load()}}
function prev(){if(idx>0){idx--;load()}}
function download(){const W=img.naturalWidth,H=img.naturalHeight;
 const lines=boxes.map(b=>{const x1=Math.min(b.x,b.x2),y1=Math.min(b.y,b.y2);
  const w=Math.abs(b.x2-b.x),h=Math.abs(b.y2-b.y);
  return b.cls+' '+((x1+w/2)/W).toFixed(6)+' '+((y1+h/2)/H).toFixed(6)+' '+(w/W).toFixed(6)+' '+(h/H).toFixed(6)});
 const blob=new Blob([lines.join('\\n')],{type:'text/plain'});
 const a=document.createElement('a');a.href=URL.createObjectURL(blob);
 a.download=imgs[idx].replace(/\\.(png|jpg)$/,'.txt');a.click()}
</script></body></html>""".replace("%CLASSES%", json.dumps(CLASSES))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True)
    ap.add_argument("--port", type=int, default=7000)
    args = ap.parse_args()
    images = [os.path.basename(p) for p in sorted(
        glob.glob(os.path.join(args.images, "*.png")) +
        glob.glob(os.path.join(args.images, "*.jpg")))]

    class H(http.server.BaseHTTPRequestHandler):
        def _send(self, body, ctype="text/html", binary=False):
            self.send_response(200); self.send_header("Content-Type", ctype); self.end_headers()
            self.wfile.write(body if binary else body.encode())

        def do_GET(self):
            if self.path == "/":
                self._send(PAGE)
            elif self.path == "/list":
                self._send(json.dumps(images), "application/json")
            elif self.path.startswith("/img/"):
                fn = os.path.join(args.images, self.path[5:])
                self._send(pathlib.Path(fn).read_bytes(),
                           "image/png" if fn.endswith("png") else "image/jpeg", binary=True)
            else:
                self.send_error(404)

        def log_message(self, *a):
            pass

    print(f"Labeler at http://localhost:{args.port}  ({len(images)} images)")
    print("Label boxes, click 'Download labels', save each .txt under real_test_set/labels/")
    with socketserver.TCPServer(("", args.port), H) as srv:
        srv.serve_forever()


if __name__ == "__main__":
    main()
