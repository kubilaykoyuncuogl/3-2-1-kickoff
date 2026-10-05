def lum(h):
    r,g,b=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    f=lambda c: c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
def cr(a,b):
    la,lb=lum(a),lum(b); return round((max(la,lb)+0.05)/(min(la,lb)+0.05),2)
L=dict(bg="#F2F2F5",surf="#FFFFFF",fg="#1B1A21",muted="#5F5D6B",vi="#4A3AAE",vb="#5E4BC9",vs="#E9E5FA",ai="#9A6207",ab="#E9A23B",as_="#FBEFD8",ok="#1F8F5F",oks="#DCF3E8",no="#CC3A5B",nos="#FBE1E7")
D=dict(bg="#131218",surf="#1C1B23",fg="#ECEBF2",muted="#A09EAD",vi="#B3A7FF",vb="#8C7CF0",vs="#272443",ai="#F4C77A",ab="#F0B45A",as_="#3A2D14",ok="#4FCF93",oks="#163528",no="#FF7D96",nos="#3C1B25")
for name,P in (("LIGHT",L),("DARK",D)):
    print(name)
    for k in ("fg","muted","vi","ai","ok","no"): print(f"  {k} on bg {cr(P[k],P['bg'])}  on surf {cr(P[k],P['surf'])}")
    print("  white on vb",cr("#FFFFFF",P["vb"]),"| fg on vb",cr(P["fg"],P["vb"]),"| fg on ab",cr(P["fg"],P["ab"]),"| white on ab",cr("#FFFFFF",P["ab"]))
    print("  vi on vs",cr(P["vi"],P["vs"]),"ai on as",cr(P["ai"],P["as_"]),"ok on oks",cr(P["ok"],P["oks"]),"no on nos",cr(P["no"],P["nos"]))
    print("  vb vs ab",cr(P["vb"],P["ab"]))
