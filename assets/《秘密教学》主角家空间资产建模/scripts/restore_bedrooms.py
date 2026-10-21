"""M3: enlarge bedrooms without moving the user-approved corridor/stair ensemble."""
import copy

def apply(D, old):
    previous=copy.deepcopy(D)
    D['revision']='P2.4-M3'
    D['status']='走廊已确认；卧室扩展修订，尺寸暂定'
    D['authorization']['bedrooms']='走廊对了，但是卧室空间被压缩了，调整一下；宽度也需要恢复，可调整房间外轮廓'
    boxes={'B3':[2.8,4.4,9,10.2],'B2':[9.2,4.4,14.5,11.4],'B1':[14.7,4.4,20.1,9.4],
           'WT':[.2,.2,2.6,10.2],'AB':[20.3,4.4,21.8,10.2]}
    D['bedroom_comparison']=[]
    for r in D['rooms']:
        if r['id'] in boxes:
            before=copy.deepcopy(r);r['box']=boxes[r['id']]
            x,y,X,Y=r['box'];r['net_area']=round((X-x)*(Y-y),2)
            if r['id'].startswith('B') and r['id']!='B':
                D['bedroom_comparison'].append(dict(id=r['id'],name=r['name'],before=before['box'],after=r['box'],before_area=before['net_area'],after_area=r['net_area']))
    # Horizontal door-wall remains coplanar. All three openings retain exact coordinates.
    coords={
      '2-B3S':([2.7,4.3],[9.1,4.3]),'2-B2S':([9.1,4.3],[14.6,4.3]),'2-B1S':([14.6,4.3],[20.2,4.3]),
      '2-B3E':([9.1,4.3],[9.1,11.5]),'2-B12':([14.6,4.3],[14.6,11.5]),
      '2-W':([7.7,1],[7.7,4.3]),'2-E':([18.7,1],[18.7,4.3]),
      '2-N':([2.7,10.3],[9.1,10.3])}
    for w in D['walls']:
        if w['id'] in coords:w['a'],w['b']=coords[w['id']]
    for id,a,b in [
      ('2-B3W',[2.7,4.3],[2.7,10.3]),('2-B2N',[9.1,11.5],[14.6,11.5]),
      ('2-B1N',[14.6,9.5],[20.2,9.5]),('2-B1E',[20.2,4.3],[20.2,9.5])]:
        D['walls'].append(dict(id=id,level=2,a=a,b=b,thickness=.2))
    opmap={
      'W207':('2-N',4.3,7.5),'W206':('2-B2N',10.4,13.6),
      'W205a':('2-B1N',15.1,17.15),'W205b':('2-B1N',17.45,19.25),
      'G201':('2-B1E',5.35,6.65)}
    for o in D['openings']:
        if o['id'] in opmap:o['wall'],o['start'],o['end']=opmap[o['id']]
    # Rear extension is a provisional architectural volume, not a structural design.
    D['architecture']['floor2_rects'].append([9.1,10.4,14.6,11.6])
    D['architecture']['roof_rects']=[[7.7,1,18.8,4.3],[2.6,4.3,9.1,10.4],[9.1,4.3,14.6,11.6],[14.6,4.3,20.3,9.6]]
    D['exterior_rails']=[[[0,-1.4],[22,-1.4]],[[0,-1.4],[0,10.4]],[[22,-1.4],[22,10.4]],
      [[20.2,10.4],[22,10.4]],[[20.3,4.4],[22,4.4]],[[14.6,10.4],[20.2,10.4]],[[0,10.4],[2.7,10.4]]]
    # Restore source furniture dimensions. Reposition individually, never stretch beds.
    original={f['id']:f for f in old['furniture']}
    b2={
      'B01':[12.1,5.9,14.3,7.7],'B02':[9.2,6.05,9.65,8],
      'B03':[9.2,9.4,9.85,11.05],'B04':[10.2,9.85,10.8,10.45],
      'B05':[13.85,10.1,14.5,11.4],'B06':[14.35,9.5,14.5,10.05],
      'B07':[13.9,8.5,14.5,8.9],'B08':[13.35,7.85,13.75,8.3],
      'B09':[11.8,10.25,12.65,11.15],'B10':[9.8,6.25,12.6,8.65],
      'B11':[10.2,7.1,11.4,7.8],'B12':[10.5,4.4,11.25,4.95],'B13':[13.2,4.4,14.4,4.8]}
    b3={
      'C01':[5.8,4.4,7.3,6.6],'C02':[6.2,6.75,6.9,7.35],
      'C03':[3,4.4,5,5.05],'C04':[3.65,5.45,4.25,6.05],
      'C05':[4.3,9.75,6.6,10.2],'C06':[2.8,6.2,3.45,10.2],
      'C07':[2.8,5.35,2.98,5.95],'C08':[4.2,6.4,7,9.2],'C09':[5.1,4.4,5.55,5]}
    for f in D['furniture']:
        if f['level']!=2:continue
        f.update(copy.deepcopy(original[f['id']]))
        if f['room']=='B1':
            x,y,X,Y=f['box'];f['box']=[round(x+1.5,3),y,round(X+1.5,3),Y]
        elif f['id'] in b2:f['box']=b2[f['id']]
        elif f['id'] in b3:f['box']=b3[f['id']]
    D['furniture_changes']=[dict(id=f['id'],before=next(p['box'] for p in previous['furniture'] if p['id']==f['id']),after=f['box']) for f in D['furniture'] if f['level']==2]
    D['preserved_corridor']={k:copy.deepcopy(previous[k]) for k in ['stairs','walk_route']}
    D['preserved_corridor']['walls']=[w for w in previous['walls'] if w['id'] in ['2-PAR','2-STB','2-STS']]
    D['preserved_corridor']['openings']=[o for o in previous['openings'] if o['level']==2 and o['id'] not in ['G201','W207','W206','W205a','W205b']]
    D['provisional_dimensions']=['层高3.30m，板厚0.22m；走廊和楼梯坐标不变',
      '舒亚6.20×5.80m：35.96㎡；子豪5.30×7.00m：37.10㎡；薇亚5.40×5.00m：27.00㎡',
      '子豪宽度从3.30增至5.30m，仍小于P2.3的6.40m；用增加进深恢复面积，不谎称宽度完全恢复',
      '大姐床2.25×2.10m，占房间面积17.5%；家具恢复P2.3实际占地尺寸',
      '子豪北侧体量超出原一楼外轮廓1.20m；为暂定体量，支承结构与外景需校准']
    D['unresolved'] += ['卧室扩展后的外墙与窗口随房间移位；走廊窗不变。子豪北侧1.20m外挑未进行结构设计，不能直接施工。']
    for c in D['cameras_override']:
        if c['id']=='F4_PLAN':c['pos']=[11,5.8,25];c['target']=[11,5.8,0];c['ortho_scale']=26
    return D
