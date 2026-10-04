"""Neutral, editable SVG schematics of information structures, not data charts."""

from html import escape
import math


def diagram(sample):
    parts = []

    def text(x, y, value, size=14, anchor='start'):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{escape(value)}</text>')

    def box(x, y, w, h, value='', shade=False, dash=False):
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{"#e6e6e6" if shade else "white"}" stroke="#555" stroke-dasharray="{"5 4" if dash else "none"}"/>')
        if value:
            text(x+w/2, y+h/2+5, value, anchor='middle')

    def line(x1, y1, x2, y2, arrow=False, dash=False):
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#555" stroke-width="1.5" stroke-dasharray="{"5 4" if dash else "none"}" marker-end="{"url(#arrow)" if arrow else "none"}"/>')

    def circle(x, y, r, value='', shade=False):
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{"#ddd" if shade else "white"}" fill-opacity="0.7" stroke="#555"/>')
        if value:
            text(x,y+5,value,anchor='middle')

    def table(columns, rows, x=40, y=120, w=740, h=220):
        cw=w/len(columns); rh=h/(len(rows)+1)
        for ci,label in enumerate(columns):
            box(x+ci*cw,y,cw,rh,label,shade=True)
        for ri,label in enumerate(rows):
            for ci in range(len(columns)):
                value=label if ci==0 else ('根拠・要点' if ri%2==0 else '条件・補足')
                box(x+ci*cw,y+(ri+1)*rh,cw,rh,value)

    def axes(x=65,y=355,w=540,h=210):
        line(x,y,x+w,y,True); line(x,y,x,y-h,True)

    def flow(labels, y=200, x=45, w=740, h=65):
        gap=30; bw=(w-gap*(len(labels)-1))/len(labels)
        for i,label in enumerate(labels):
            bx=x+i*(bw+gap)
            box(bx,y,bw,h,label,shade=i==0)
            if i<len(labels)-1: line(bx+bw,y+h/2,bx+bw+gap-4,y+h/2,True)

    def tree(vertical=False, x=65, y=140, w=550, h=210):
        if vertical:
            box(x+w/2-65,y,130,40,'問い・要点',True)
            for i in range(3):
                bx=x+i*w/3
                line(x+w/2,y+40,bx+60,y+100)
                box(bx,y+100,120,45,'要因 '+chr(65+i))
                line(bx+60,y+145,bx+60,y+h-35)
                box(bx,y+h-35,120,35,'具体要素')
        else:
            box(x,y+h/2-25,120,50,'全体',True)
            for i in range(3):
                yy=y+i*75
                line(x+120,y+h/2,x+220,yy+20)
                box(x+220,yy,120,40,'要因 '+chr(65+i))
                line(x+340,yy+20,x+420,yy+20)
                box(x+420,yy,120,40,'要素・根拠')

    n=sample['type_number']; variant=sample['kind']=='variant'
    text(24,35,sample['name'],22)
    text(24,64,'構成の骨格：領域・対応・関係を示す',14)
    if n==1:
        box(50,105,720,90,'章題' if variant else '全体テーマ',True)
        if variant:
            box(50,220,340,120,'問い A');box(430,220,340,120,'問い B')
        else:
            for i in range(3): box(50,220+i*45,720,35,'項目 '+chr(65+i))
    elif n==2:
        if variant:
            for i in range(3):
                box(50,110+i*85,300,60,'問い '+chr(65+i)); line(355,140+i*85,400,140+i*85,True);box(410,110+i*85,360,60,'答え・根拠')
        else: table(['要点','根拠','詳細の参照'],['項目 A','項目 B','項目 C'])
    elif n==3:
        table(['まとめ','留保','次の行動'],['項目 A','項目 B'],h=150)
        flow(['次に確かめる','進め方','条件'],y=300,h=60)
    elif n==4:
        for i in range(4):
            x=45+(i%2)*390;y=110+(i//2)*140
            box(x,y,350,120,'',shade=False); text(x+15,y+25,'対象 '+chr(65+i));text(x+15,y+55,'属性 A / 属性 B');text(x+15,y+90,'共通形式の図・注記')
    elif n==5:
        axes(h=140,y=280)
        for i in range(4): box(100+i*130,210-i*15,45,70+i*15,'量')
        table(['時点','時点 A','時点 B','時点 C'],['指標 A','指標 B'],y=315,h=75)
    elif n==6:
        axes();circle(180,240,32,'対象 A',True);circle(390,220,50,'対象 B');circle(510,310,28,'対象 C')
        box(655,150,130,170,'補足・凡例')
    elif n==7:
        def waterfall(y):
            for i in range(5):
                bx=70+i*95;by=y+min(i,3)*17
                box(bx,by,60,55,'合計' if i in (0,4) else '寄与',shade=i in (0,4))
                if i<4: line(bx+60,by+55,bx+95,by+55,dash=True)
        waterfall(130)
        if variant: waterfall(280)
        else:box(605,130,165,205,'要因と補足')
    elif n==8:
        for i in range(4):
            height=200-i*40;box(60+i*185,220-height/2,145,height,'段階 '+chr(65+i),shade=i==3)
            if i<3:line(205+i*185,220,235+i*185,220,True)
    elif n==9:
        flow(['工程 A','工程 B','工程 C','工程 D'],y=110,h=35)
        axes(y=310,h=125,w=700)
        for i in range(4):box(110+i*170,220-(i%2)*30,75,90,'量')
        if variant:
            line(125,360,295,340);line(295,340,465,355);line(465,355,635,330)
            text(50,385,'同じ工程列で別指標を対応')
    elif n==10:
        for i in range(4):
            text(45,130+i*65,'役割 '+chr(65+i));box(170+i*70,105+i*65,180-i*20,40,'配分')
            if i<3:line(340+i*55,125+i*65,260+i*70,170+i*65,True)
            box(610,105+i*65,100+i*18,40,'同単位の量')
    elif n in (11,46):
        tree(vertical=n==46)
        box(655,140,130,210,'評価・根拠')
    elif n==12:
        table(['式の要素','対象 A','対象 B','対象 C'],['要素 A ×','要素 B ＋','要素 C'])
    elif n==13:
        axes(w=680,h=230)
        for i in range(4):
            box(110+i*120,115+i*45,55,30,'実働',True);box(165+i*120,115+i*45,65,30,'待ち',dash=True)
        box(110,320,250,30,'実働合計',True);box(360,320,350,30,'待ち合計')
    elif n==14:
        for j in range(3):
            x=65+j*255;axes(x=x,w=215,h=210)
            for i in range(3):box(x+30+i*55,245-i*30+(j%2)*15,30,110+i*30-(j%2)*15,'')
            text(x+70,390,'対象 '+chr(65+j))
    elif n==15:
        flow(['工程 A','工程 B','工程 C'],y=105,x=175,w=605,h=45)
        for i in range(3):
            text(40,205+i*70,'対象 '+chr(65+i))
            for j in range(3):box(175+j*210,175+i*70,165,45,'指標')
    elif n==16:
        axes(w=690,h=240)
        for i in range(3):
            x=120+i*220;text(x,390,'対象 '+chr(65+i))
            for j in range(3):box(x,285-j*65-(i%2)*15,130,40,'階層 '+chr(65+j),shade=j==1)
    elif n in (17,18):
        for i in range(2):
            x=55+i*400;text(x,110,'対象 '+chr(65+i))
            if n==17:
                box(x,190,85,45,'起点');box(x+230,190,85,45,'終点');line(x+85,205,x+225,205,True);line(x+230,225,x+90,225,True,True)
            else:tree(vertical=True,x=x,y=145,w=320,h=190)
    elif n==19:
        if variant:
            axes(w=500);line(320,145,320,355);line(65,250,565,250)
            circle(170,200,20,'A');circle(390,300,20,'B',True);box(615,155,160,180,'対応する説明')
        else:
            table(['分類','区分 A','区分 B'],['観点 A','観点 B'],x=40,w=350)
            table(['分類','区分 A','区分 B'],['観点 A','観点 B'],x=430,w=350)
    elif n==20:
        flow(['要素 A','要素 B','要素 C'],y=145,h=50)
        text(45,130,'前');text(45,265,'後')
        for i in range(3):box(45+i*257,280,227,50,'残る' if i!=1 else '変わる',dash=i==1)
        for i in range(3):line(150+i*257,195,150+i*257,275,True,True)
    elif n==22:
        table(['観点','前の状態','後の状態'],['観点 A','観点 B','観点 C'])
    elif n in (21,23,24):
        def area(x,y,w,h,label):box(x,y,w,h,label,True)
        if n==21:
            for i in range(3 if variant else 2):
                x=55+i*(250 if variant else 430);area(x,180,170,150,'構成 '+chr(65+i))
                if variant:box(x,210,140,120,'前の輪郭',dash=True)
                if i<(2 if variant else 1):line(x+175,255,x+220,255,True)
        elif n==24 and variant:
            area(75,230,260,110,'対象 A');area(470,150,240,190,'対象 B')
        else:
            axes(w=690)
            for i,(w,h) in enumerate([(190,100),(150,180),(120,220)]):area(85+i*215,355-h,w,h,'対象 '+chr(65+i))
            if n==23:line(65,250,735,250,dash=True);text(650,240,'基準')
    elif n in (25,26,27):
        axes(w=570);pts=[(160,300),(310,225),(470,180),(555,240)]
        if n==25 and variant:pts=[(160,320),(290,255),(425,230),(555,220)]
        if n==27:
            parts.append('<path d="M 120 150 Q 160 300 580 330" fill="none" stroke="#555" stroke-dasharray="5 4"/>')
        else:
            for a,b in zip(pts,pts[1:]):line(*a,*b,arrow=n==26)
            if n==26:line(*pts[-1],*pts[0],True)
        for i,(x,y) in enumerate(pts):circle(x,y,7);text(x+12,y-10,('時点 ' if n==25 else '対象 ')+chr(65+i))
        if n==25 and variant:line(120,345,575,155,dash=True)
        box(660,150,120,180,'基準・解釈')
    elif n==28:
        for j in range(3):
            x=70+j*240;axes(x=x,y=260,w=180,h=125)
            for i in range(4):circle(x+35+i*35,235-(i%3)*25-j*5,5)
        table(['指標','対象 A','対象 B','対象 C'],['共通指標'],y=305,h=65)
    elif n==29:
        axes(w=690)
        for i in range(4):
            y=150+i*50;text(70,y-10,'対象 '+chr(65+i));line(120+i*60,y,440+i*70,y);circle(120+i*60,y,5);box(435+i*70,y-5,10,10)
        line(600,115,600,355,dash=True);text(610,125,'参照時点')
    elif n==30:
        circle(280,230,100,'集合 A');circle(410,210,80,'集合 B');circle(350,305,65,'集合 C')
        box(590,155,190,160,'重複と補足')
    elif n==31:
        axes(w=680)
        for i in range(3):
            y=355-i*65
            parts.append(f'<polygon points="70,{y} 750,{y-70} 750,{y-125} 70,{y-55}" fill="{["#eee","#ccc","#aaa"][i]}" stroke="#555"/>')
            text(600,y-35,'系列 '+chr(65+i))
    elif n==32:
        table(['','区分 A','区分 B'],['観点 A','観点 B'],x=45,w=490)
        line(535,235,600,235,True);box(615,140,165,205,'判断・説明')
    elif n==33:
        parts.append('<path d="M 70 230 Q 280 70 440 150 T 750 240" fill="none" stroke="#555"/>')
        line(435,135,435,370,dash=True)
        table(['段階 A','段階 B','段階 C'],['対応・方針'],y=285,h=85)
    elif n==34:
        table(['','対象 A','対象 B'],['強み','不足'],h=240)
        line(330,220,610,300,True);line(610,220,330,300,True)
    elif n in (35,36,37,38):
        top=115
        if n==38:flow(['連携 A','連携 B','連携 C'],y=110,h=40);top=210
        for i in range(3):
            y=top+i*55;text(40,y+22,('段階 ' if n==37 else '領域 ')+chr(65+i));line(150,y+45,775,y+45,dash=True)
            box(175+i*100,y,180+(i%2)*110,35,'担当・工程' if n==36 else '期間',shade=i==0,dash=n==37 and i>0)
        line(460,top-10,460,top+170,dash=True);text(470,top-15,'参照時点')
    elif n in (39,40,47):
        for i in range(3):text(35,155+i*85,'役割 '+chr(65+i));line(140,195+i*85,780,195+i*85,dash=True)
        box(160,125,125,45,'入力');box(360,210,125,45,'処理');box(650,295,125,45,'出力');line(285,150,360,230,True)
        if n!=47:line(485,235,650,315,True)
        if n==47:
            parts.append('<polygon points="540,195 580,230 540,265 500,230" fill="white" stroke="#555"/>');text(540,235,'判定',anchor='middle');line(485,235,500,230,True);line(580,230,650,315,True);line(540,195,285,150,True,True)
        elif n==40:line(650,340,285,180,True,True);text(495,335,'別の流れ')
        else:line(650,295,285,165,True,True);text(465,160,'受渡し・戻り')
    elif n==41:
        table(['層','系列 A','系列 B','系列 C'],['層 A','層 B','層 C'])
    elif n==42:
        flow(['工程 A','工程 B','工程 C'],y=110,h=40)
        table(['観点','工程 A','工程 B','工程 C'],['要因','担当範囲'],y=185,h=175)
    elif n==43:
        tree(vertical=True,x=60,y=110,w=530,h=170);box(650,125,130,155,'類型凡例')
        table(['類型','組織 A','組織 B'],['対応'],y=320,h=65)
    elif n==44:
        table(['全体','部分'],['要素 A','要素 B','要素 C'],x=45,w=300)
        line(345,225,440,225,True);box(455,120,325,240,'選択部分の詳細')
    elif n==45:
        suffix=sample['id'].rsplit('-',1)[1]
        columns={'1':['論点','対象 A','対象 B'],'2':['論点','時期 A','時期 B'],'3':['観点','選択肢 A','選択肢 B'],'4':['仮説','根拠','成立条件','反証条件']}[suffix]
        table(columns,['論点 A','論点 B','論点 C'])
    elif n==48:
        box(335,205,150,65,'中心対象',True)
        for i in range(6):
            angle=i*math.pi/3; x=410+260*math.cos(angle);y=235+115*math.sin(angle)
            line(410,235,x,y,True,dash=i%2==1);box(x-60,y-20,120,40,'関係者 '+chr(65+i))
    elif sample['id']=='principle-1':
        table(['観点','対象 A','対象 B','対象 C'],['異なる条件','共通条件','異なる情報'])
        box(225,235,555,55,'共通事項をまとめる',True)
    elif sample['id']=='principle-2':
        for i in range(3):
            y=125+i*80;text(40,y+35,'区分 '+chr(65+i));box(210,y,250,45,'要素 A');box(255,y+15,250,45,'要素 B');box(300,y+30,250,45,'要素 C')
    else:
        raise ValueError(f"No diagram implementation: {sample['id']}")
    text(24,425,'模式図：形・大きさ・色は実データや完成デザインを表さない',13)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 460" role="img">'
            f'<title>{escape(sample["id"]+": "+sample["name"])}</title>'
            '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#555"/></marker></defs>'
            '<rect width="840" height="460" fill="white"/>'
            '<g font-family="sans-serif" fill="#222">'+''.join(parts)+'</g></svg>\n')
