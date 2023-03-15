from argparse import ArgumentParser

import pygame
import numpy as np
from HanoiDirector import HanoiDirector
pygame.init()

parser=ArgumentParser(prog='HanoiAnimation',
                                              description='汉诺塔动画程序, 使用-n 参数指定盘子个数')

# 设定参数默认值
n=3
fps=20
fpe=10

parser.add_argument('-n',help='The total number of plates')
parser.add_argument('--fps', help='Frames per second(speed of animation)')
parser.add_argument('--fpe',help='Frames per event(smoothness of motion)')

args=vars(parser.parse_args())

if not args['n']==None:
        n=int(args['n'])
if not args['fps']==None:
        fps=int(args['fps'])
if not args['fpe']==None:
        fpe=int(args['fpe'])

# 导演初始参数实例
params={'Canvas':(800,600),
       'Base':(100,480,600,100),
       'RodSize':(20,280),
       'RodPosX':(190,390,590),
       'BaseColor':(255,97,0),
        'fpe':fpe,
       'n':n}

director=HanoiDirector(params)
director.write_script()

win=pygame.display.set_mode(params['Canvas'])

pygame.display.set_caption('Demo1')


run=True
while run:
        pygame.time.delay(int(1000/fps)) # 延迟，控制帧率

        for event in pygame.event.get():
                if event.type==pygame.QUIT:
                        run=False

        director.step()
        
        win.fill((0,0,0))
        rects_to_draw=director.things_to_draw()
        for r in rects_to_draw:
                pygame.draw.rect(win,r[0],r[1])
        pygame.display.update()

pygame.quit()

    
