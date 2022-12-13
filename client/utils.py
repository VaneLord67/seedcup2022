import math

# dir = [(-1,1),(0,1),(1,0),(1,-1),(0,-1),(-1,0)]
dir = [(-1,1),(-1,0),(0,-1),(1,-1),(1,0),(0,1)]
s = 'wedxza'
def d2s(d):
    for i,j in enumerate(dir):
        if j == d:
            return i

def toward(pos1,pos2):
    '''给出两点坐标，返回下一个移动的方向'''
def cube_round(pos):
    q = round(pos[0]+1e-6)
    r = round(pos[1]+1e-6)
    z = -pos[0]-pos[1]-2e-6
    s = round(z)

    q_diff = abs(q - z)
    r_diff = abs(r - z)
    s_diff = abs(s - z)

    if q_diff > r_diff and q_diff > s_diff:
        q = -r-s
    elif r_diff > s_diff:
        r = -q-s
    else:
        s = -q-r
    return (q, r)
def cube_lerp(pos1, pos2, t):
    x1 = pos1[0]
    y1 = pos1[1] 
    z1 = -x1-y1
    x2 = pos2[0]
    y2 = pos2[1] 
    z2 = -x2-y2
    return (x1 + (x2 - x1) * t,y1 + (y2 - y1) * t,z1 + (z2 - z1) * t)

def distance(pos1,pos2):
    '''求出两点之间的距离返回int'''
    dx = pos1[0]-pos2[0]
    dy = pos1[1]-pos2[1]
    dz = -dx-dy
    return max(abs(dx),abs(dy),abs(dz))
def line(pos1,pos2):
    '''输入两个点,求出两点之间的格子返回list'''
    n = distance(pos1,pos2)
    result = []
    for i in range(n+1):
        result.append(cube_round(cube_lerp(pos1,pos2,1.0/n * i)))
    return result
def get_around_pos(pos,flag = 1):
    if flag == 1:
        return [(i+pos[0],j+pos[1]) for i,j in dir]
    if flag == 2:
        l1 = [(i+pos[0],j+pos[1]) for i,j in dir]
        l2 = []
        for p in l1:
            l2.extend(get_around_pos(p,flag=1))
        return list(set(l2))
def mweapon2(pos,d):
    (cx,cy) = (pos[0]+dir[d][0]*2,pos[1]+dir[d][1]*2)
    return get_around_pos((cx,cy))+[(cx,cy)]
def mweapon1(pos,d):
    d1 = d-1%6
    d2 = d+1%6
    c1 = (pos[0]+dir[d][0],pos[1]+dir[d][1])
    c2 = (pos[0]+dir[d1][0]*2,pos[1]+dir[d1][1]*2)
    c3 = (pos[0]+dir[d2][0]*2,pos[1]+dir[d2][1]*2)
    c4 = (pos[0]+dir[d][0]+dir[d1][0],pos[1]+dir[d][1]+dir[d1][1])
    c5 = (pos[0]+dir[d][0]+dir[d2][0],pos[1]+dir[d][1]+dir[d2][1])
    return [c1,c2,c3,c4,c5]
def sweapon1(pos,d,t = 8):
    l = []
    for i in range(t):
        j = (pos[0]+dir[d][0]*i,pos[1]+dir[d][1]*i)
        l.append(j)
    l.extend(get_around_pos(j))
    return(list(set(l)))
def sweapon2(pos):
    return get_around_pos(pos,flag=2)

def goTo(pos1,pos2):
    '返回下一步'
    l = line(pos1,pos2)
    pos = (l[1][0]-l[0][0],l[1][1]-l[0][1])
    return d2s(pos)
if __name__ == '__main__':
    print(goTo((11, -2), (9, -1)))