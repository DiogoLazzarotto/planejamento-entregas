from html import escape
from pathlib import Path

def preview(title, subtitle, metrics, sections, target):
    width, height = 1200, 760
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">', '<rect width="1200" height="760" fill="#0d1420"/>']
    def text(x,y,value,size=20,color='#edf4fb',bold=False):
        parts.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, Arial, sans-serif" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}">{escape(str(value))}</text>')
    text(44,58,title,32,bold=True)
    text(44,92,subtitle,17,'#a8bad0')
    for index,(label,value) in enumerate(metrics):
        x=44+index*374
        parts.append(f'<rect x="{x}" y="124" width="354" height="116" rx="14" fill="#162131" stroke="#2d3e54"/>')
        text(x+20,157,label,16,'#a8bad0')
        text(x+20,207,value,32,'#6cd9ed',True)
    y=280
    for heading,rows in sections:
        text(44,y,heading,22,bold=True);y+=36
        for label,value in rows:
            text(52,y,label,18,'#a8bad0');text(750,y,value,18,'#edf4fb',True)
            parts.append(f'<path d="M44 {y+12} H1156" stroke="#2d3e54"/>');y+=46
        y+=24
    text(44,727,'Dados fictícios · prévia dos resultados executados · sem métricas de produção real',15,'#a8bad0')
    parts.append('</svg>')
    Path(target).parent.mkdir(parents=True,exist_ok=True)
    Path(target).write_text('\n'.join(parts),encoding='utf-8')
