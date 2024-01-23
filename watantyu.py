import pyxel

STAGE_WIDTH = 128 * 5
STAGE_HEIGHT = 128 * 1
LEFT_LINE = 48
RIGHT_LINE = 128 - 80
TILE_SPAWN1 = (8,18)
TILE_SPAWN2 = (9,18)

scroll_x = 0
scroll_y = 0
player = None
tails = []
enemies = []
deletes = []

PLAYER_ANIMA = [(16,0),(0,16),(16,16)]
SPIN_ATK_ANIMA = [(32,32),(48,32),(32,48),(48,48)]
ENEMY_ANIMA = [(16,96),(0,112),(16,112),(16,112),(0,112)]
IROHA_ANIMA = [(0,128),(8,128)]
DELETE_ANIMA = [(48,64),(56,64)]

chkpoint = [(0,0),(8,0),(15,0),(15,8),(15,15),(8,15),(0,15),(0,8)]
chktile =[(12,0),(12,1),(13,0),(13,1)]

def chkwall(cx,cy):
    c = 0
    if cx < 0 or STAGE_WIDTH -8 < cx:
        c = c + 1
    if STAGE_HEIGHT < cy:
        c = c + 1
    for cpx, cpy in chkpoint:
        xi = (cx + cpx)//8
        yi = (cy + cpy)//8
        tile = pyxel.tilemap(0).pget(xi,yi)
        if (12,0) == tile:
            c = c + 1
        if (12,1) == tile:
            c = c + 1
        if (13,0) == tile:
            c = c + 1
        if (13,1) == tile:
            c = c + 1
    return c

def spawn_enemy(left_x, right_x):
    left_x = pyxel.ceil(left_x / 4)
    right_x = pyxel.floor(right_x / 4)
    for x in range(left_x, right_x + 1):
        for y in range(16):
            tile = pyxel.tilemap(0).pget(x,y)
            if tile == TILE_SPAWN1:
                enemies.append(Enemy1(x * 8, y * 8))
            if tile == TILE_SPAWN2:
                enemies.append(Terget(x * 8, y * 8))

def update_list(list):
    for elem in list:
        elem.update()

def draw_list(list):
    for elem in list:
        elem.draw()

def cleanup_list(list):
    i = 0
    while i < len(list):
        elem = list[i]
        if not elem.is_alive:
            list.pop(i)
        else:
            i += 1

class Player:
    def __init__(self,x,y):
        self.x = x + 16
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = 1
        self.jump = 0
        self.keyz = 0
        self.right = 0
        self.left = 0
        self.atk = 0
        self.atk = 0
        self.atk_count = 0
        self.atk_spin = 0
        self.atk_neu = 0
        self.atk_up = 0
        self.atk_down = 0
        self.atk_ju = 0
        self.tackle = 0
        self.bck_ju = 0
        self.tx = 0
        self.ty = 0
        self.damage = 0
        self.damage_count = 0
        self.tmr = 0
        self.hp = 28
        
    def update(self):
        global scroll_x, scroll_y
        self.tmr += 1

        if ((self.jump == 1) or (self.jump == 2)) and (pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)):
            self.down = 1
            self.up = 0
        else:
            self.down = 0
        if pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
            self.keyz = 1
        else:
            self.keyz = 0

        if self.atk_count == 0:
            if pyxel.btnp(pyxel.KEY_S) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                self.dy = 4
                self.atk = 1
                self.atk_spin = 1
                self.atk_count = 1
                pyxel.play(0,4)
            elif self.down == 1:
                if pyxel.btnp(pyxel.KEY_S) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                    self.dy = -8
                    self.atk = 1
                    self.atk_down = 1
                    self.atk_count = 1
                    pyxel.play(0,4)
            elif pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
                Tail1(self.x, self.y)
                Tail2(self.x, self.y)
                Tail3(self.x, self.y)
                self.atk = 1
                self.atk_neu = 1
                self.atk_count = 1
                pyxel.play(0,3)
        else:
            self.atk_count += 1
            if self.atk_count > 8:
                self.atk = 0
                self.atk_spin = 0
                self.atk_neu = 0
                self.atk_up = 0
                self.atk_down = 0
                self.tackle = 0
                self.atk_count = 0

        if self.tackle == 0:
            if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                self.left = 1
                self.dx = -3            
                self.direction = -1
            elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                self.right = 1
                self.dx = 3
                self.direction = 1
            else:
                self.dx = int(self.dx*0.8)
                self.left = 0
                self.right = 0

        if self.atk_neu:
            for enemy in enemies:
                for tail in tails:
                    if abs(tail.x - enemy.x) < 16 and abs(tail.y - enemy.y) < 8:
                        self.tackle = 1
                        self.atk = 1
                        self.tx = enemy.x - self.x
                        self.ty = self.y - enemy.y
                        sq_dist = self.tx**2 + self.ty**2
                        if sq_dist < 60**2:
                            dist = pyxel.sqrt(sq_dist)
                            self.dx = self.tx/dist * 12
                            self.dy = self.ty/dist * 12

        Ir = pyxel.sgn(self.dx)
        loop = abs(self.dx)
        while  0 < loop:
            if chkwall(self.x + Ir, self.y) != 0:
                self.dx = 0
                break
            self.x += Ir
            loop -= 1
        
        if self.jump == 0:
            if chkwall(self.x, self.y + 1) == 0:
                self.jump = 2
            if self.keyz == 1:
                self.dy = 7
                self.jump = 1
                pyxel.play(0,2)
        else:
            if self.atk_ju == 0:
                self.dy -= 0.75
                if self.dy < 0 or self.atk == 1:
                    self.jump = 2
                elif self.keyz == 0:
                    self.dy = 0
            elif self.atk_ju == 1:
                self.dy -= 0.5
                if self.dy < 0 or self.atk == 1:
                    self.jump = 2

        ud = pyxel.sgn(self.dy)
        loop = abs(self.dy)
        while 0 < loop:
            if chkwall(self.x, self.y - ud) != 0:
                self.dy = 0
                if self.atk_ju == 0:
                    if self.jump == 1:
                        self.jump = 2
                    elif (self.jump == 2 and self.keyz == 0):
                        self.jump = 0
                if self.atk_ju == 1:
                    if self.jump == 1:
                        self.jump = 2
                    elif self.jump == 2:
                        self.jump = 0
                        self.atk_ju = 0
                break
            self.y -= ud
            loop -= 1

        if self.damage_count == 0:
            if self.damage == 1:
                self.dx = self.direction * -10
                self.dy = 5
                self.damage_count = 1
                pyxel.play(0,5)
        else:
            self.damage_count += 1
            if self.damage_count < 60:
                self.damage = 1
            if self.damage_count >= 60:
                self.damage_count = 0
                self.damage = 0

        if self.x < scroll_x + LEFT_LINE:
            scroll_x = self.x - LEFT_LINE
            if scroll_x < 0:
                scroll_x = 0
            spawn_enemy(LEFT_LINE + 128, scroll_x + 127)

        if scroll_x + RIGHT_LINE < self.x:
            scroll_x = self.x - RIGHT_LINE
            if STAGE_WIDTH - 128 < scroll_x:
                scroll_x = STAGE_WIDTH - 128
            spawn_enemy(RIGHT_LINE + 128, scroll_x + 127)

        if self.y >=128:
            game_over()
        return
    
    def draw(self):
        u,v = PLAYER_ANIMA[(self.tmr//3)%3]
        us,vs = SPIN_ATK_ANIMA[self.tmr%4] 
        w = self.direction*16
        
        if 1 < self.damage_count < 8:
            pyxel.blt(self.x, self.y, 0, 0, 80, w, 16, 5)
            pyxel.blt(self.x-self.direction*12, self.y-5, 0, 32, 64, w, 16, 5)
        elif self.atk_spin == 1:
            pyxel.blt(self.x, self.y, 0, us, vs, w, 16, 5)
        elif self.atk_neu == 1:
            pyxel.blt(self.x, self.y, 0, 0, 32, w, 16, 5)
        elif self.jump == 1:
            pyxel.blt(self.x, self.y, 0, 16, 16, w, 16, 5)
        elif self.left == 1 or self.right == 1:
            pyxel.blt(self.x, self.y, 0, u, v, w, 16, 5)
        else:
            pyxel.blt(self.x, self.y, 0, 0, 0, w, 16, 5)

class Tail1:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.is_alive = True
        tails.append(self)
    def update(self):
        a = player.direction*48
        self.x = player.x + a
        self.y = player.y
    def draw(self):
        if player.atk_count > 2:
            if player.atk_neu == 1:
                pyxel.blt(self.x,self.y,0,16,40,player.direction*16,8,5)

class Tail2:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.is_alive = True
        tails.append(self)
    def update(self):
        b = player.direction*32
        self.x = player.x + b
        self.y = player.y
    def draw(self):
        if player.atk_count > 1:
            if player.atk_neu == 1:
                pyxel.blt(self.x,self.y,0,16,32,player.direction*16,8,5)

class Tail3:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.is_alive = True
        tails.append(self)
    def update(self):
        c = player.direction*16
        self.x = player.x + c
        self.y = player.y
    def draw(self):
        if player.atk_neu == 1:
            pyxel.blt(self.x,self.y,0,16,32,player.direction*16,8,5)

class Enemy1:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = -1
        self.tmr = 0
        self.is_alive = True
        enemies.append(self)

    def update(self):
        self.dx = self.direction
        self.dy = min(self.dy + 1, 4)
        if self.direction < 0 and chkwall(self.x - 1, self.y - 4):
            self.direction = 1
        elif self.direction > 0 and chkwall(self.x + 1, self.y - 4):
            self.direction = -1
        if player.tackle == 0:
            self.tmr += 1
            Ir = pyxel.sgn(self.dx)
            self.x += Ir
            self.y -= 1
            ud = pyxel.sgn(self.dy)
            loop = abs(self.dy)
            while 0 < loop:
                if chkwall(self.x, self.y + ud) != 0:
                    self.dy = 0
                self.y += ud
                loop -= 1
        
    def draw(self):
        u,v = ENEMY_ANIMA[(self.tmr//8)%5]
        pyxel.blt(self.x, self.y, 0, u, v, -self.direction*16, 16, 5)

class Terget:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.is_alive = True
        self.tmr = 0
        enemies.append(self)
    def update(self):
        self.tmr += 1
    def draw(self):
        u,v = IROHA_ANIMA[(self.tmr//30)%2]
        pyxel.blt(self.x, self.y, 0, u, v, -8, 16, 5)

class Delete:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.is_alive = True
        self.tmr = 0
        self.radius = 0
        deletes.append(self)
    def update(self):
        self.tmr += 1
        self.radius += 1
        if self.radius > 16:
            self.is_alive = False

    def draw(self):
        u,v = DELETE_ANIMA[(self.tmr//3)%2]
        pyxel.blt(self.x, self.y, 0, u, v, 8, 8, 5)

class App:
    def __init__(self):
        pyxel.init(128,128,title = "わたんちゅている")
        pyxel.load("./wata.pyxres")
        global player
        player = Player(0,0)
        spawn_enemy(0, 127)
        pyxel.run(self.update,self.draw)
    def update(self):
        if pyxel.btn(pyxel.KEY_ALT) and pyxel.btn(pyxel.KEY_F4):
            pyxel.quit()

        player.update()
        if player.hp <= 0:
            game_over()
            return
        for enemy in enemies:
            if abs(player.x - enemy.x) < 15 and abs(player.y - enemy.y) < 14:
                if player.atk == 0:
                    if player.damage == 0:
                        player.damage = 1
                        player.hp -= 7
                if player.atk == 1:
                    deletes.append(Delete(enemy.x+6,enemy.y+6))
                    if abs(player.x - enemy.x) < 15 and abs(player.y - enemy.y) < 15:
                        player.atk_count = 8
                        player.jump = 1
                        player.atk_ju = 1
                        player.dy = 7
                        player.dx = 0
                        pyxel.play(0,6)
                    enemy.is_alive = False
            if enemy.y > 128:
                enemy.is_alive = False
                
        update_list(enemies)
        update_list(tails)
        update_list(deletes)
        cleanup_list(enemies)
        cleanup_list(tails)
        cleanup_list(deletes)

    def draw(self):
        pyxel.cls(0)
        
        pyxel.camera()
        pyxel.bltm(0,0,0,0,128,128,128,0)
        pyxel.bltm(0,0,0,scroll_x,scroll_y,128,128,5)

        pyxel.camera(scroll_x,scroll_y)
        player.draw()
        draw_list(enemies)
        draw_list(tails)
        draw_list(deletes)
        pyxel.text(scroll_x + 5,scroll_y + 5,f"HP{player.hp:4}",11)
        pyxel.text(scroll_x + 4,scroll_y + 4,f"HP{player.hp:4}",0)

def game_over():
    global scroll_x
    player.x = 16
    player.y = 80
    player.dx = 0
    player.dy = 0
    spawn_enemy(0, 127)
    player.hp = 28

App()