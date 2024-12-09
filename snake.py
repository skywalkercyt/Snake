import pygame
import random
import sys
import os
import ctypes
import ctypes.wintypes

# 初始化 Pygame
pygame.init()
print(pygame.version.ver)

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 设置游戏窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SCORE_HEIGHT = 50  # 分数区域高度
GAME_HEIGHT = WINDOW_HEIGHT - SCORE_HEIGHT  # 实际游戏区域高度
BLOCK_SIZE = 20
GAME_SPEED = 15

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('贪吃蛇游戏')

try:
    font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'msyh.ttc')  # Windows 微软雅黑
    game_font = pygame.font.Font(font_path, 36)
except:
    print("无法加载系统字体，使用默认字体")
    game_font = pygame.font.Font(None, 36)

def create_head_image():
    surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(surface, GREEN, [
        (BLOCK_SIZE, BLOCK_SIZE/2),  # 尖端
        (0, 0),                      # 左上
        (0, BLOCK_SIZE)              # 左下
    ])
    return surface

def create_tail_image():
    surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(surface, GREEN, [
        (0, BLOCK_SIZE/2),           # 尖端
        (BLOCK_SIZE, 0),             # 右上
        (BLOCK_SIZE, BLOCK_SIZE)     # 右下
    ])
    return surface

def create_apple_image():
    surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(surface, RED, (BLOCK_SIZE/2, BLOCK_SIZE/2), BLOCK_SIZE/2)
    return surface

# 使用临时图形
HEAD_IMG = create_head_image()
BODY_IMG = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
pygame.draw.rect(BODY_IMG, GREEN, (0, 0, BLOCK_SIZE, BLOCK_SIZE))
TAIL_IMG = create_tail_image()
APPLE_IMG = create_apple_image()

# 蛇类
class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(WINDOW_WIDTH//2, GAME_HEIGHT//2 + SCORE_HEIGHT)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN
        self.score = 0
        self.head_angle = 0  # 添加头部角度属性

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (
            (cur[0] + (x*BLOCK_SIZE)) % WINDOW_WIDTH,
            ((cur[1] - SCORE_HEIGHT + (y*BLOCK_SIZE)) % GAME_HEIGHT) + SCORE_HEIGHT
        )
        if new in self.positions[3:]:
            return False
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
            return True

    def reset(self):
        self.length = 1
        self.positions = [(WINDOW_WIDTH//2, GAME_HEIGHT//2 + SCORE_HEIGHT)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0

    def render(self):
        # 计算头部方向
        if self.direction == UP:
            angle = 0
        elif self.direction == RIGHT:
            angle = 270
        elif self.direction == DOWN:
            angle = 180
        else:  # LEFT
            angle = 90
            
        # 绘制头部
        rotated_head = pygame.transform.rotate(HEAD_IMG, angle)
        screen.blit(rotated_head, (self.positions[0][0], self.positions[0][1]))
        
        # 绘制身体
        for i, p in enumerate(self.positions[1:-1], 1):
            screen.blit(BODY_IMG, (p[0], p[1]))
        
        # 绘制尾巴（如果蛇长度大于1）
        if len(self.positions) > 1:
            # 计算尾部方向
            last = self.positions[-1]
            second_last = self.positions[-2]
            dx = second_last[0] - last[0]
            dy = second_last[1] - last[1]
            if dx > 0:
                tail_angle = 270
            elif dx < 0:
                tail_angle = 90
            elif dy > 0:
                tail_angle = 0
            else:
                tail_angle = 180
            rotated_tail = pygame.transform.rotate(TAIL_IMG, tail_angle)
            screen.blit(rotated_tail, (last[0], last[1]))

# 食物类
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (
            random.randint(0, (WINDOW_WIDTH-BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE,
            random.randint(0, (GAME_HEIGHT-BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE + SCORE_HEIGHT
        )

    def render(self):
        screen.blit(APPLE_IMG, (self.position[0], self.position[1]))

# 定义方向
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def main():
    # 禁用输入法
    HWND_BROADCAST = 0xFFFF
    WM_INPUTLANGCHANGEREQUEST = 0x0050
    INPUTLANGCHANGE_FORWARD = 0x0002
    INPUTLANGCHANGE_BACKWARD = 0x0004
    windll = ctypes.windll
    windll.user32.PostMessageW(HWND_BROADCAST, WM_INPUTLANGCHANGEREQUEST, 0, 0)
    
    print("游戏开始运行...")
    clock = pygame.time.Clock()
    snake = Snake()
    food = Food()
    
    # 设置窗口位置到屏幕中央
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    # 创建窗口后立即设置焦点
    pygame.event.set_grab(True)  # 捕获鼠标
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == pygame.K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT
                elif event.key == pygame.K_ESCAPE:
                    pygame.event.set_grab(False)  # 释放鼠标
                    pygame.quit()
                    sys.exit()
            # 处理窗口焦点事件
            elif event.type == pygame.ACTIVEEVENT:
                if event.gain == 1:  # 获得焦点
                    pygame.event.set_grab(True)
            elif event.type == pygame.WINDOWFOCUSLOST:  # 窗口失去焦点
                pygame.event.set_grab(False)
            elif event.type == pygame.WINDOWFOCUSGAINED:  # 窗口获得焦点
                pygame.event.set_grab(True)

        # 更新蛇的位置
        if not snake.update():
            snake.reset()
            food.randomize_position()

        # 检查是否吃到食物
        head_rect = pygame.Rect(snake.get_head_position()[0], snake.get_head_position()[1], BLOCK_SIZE, BLOCK_SIZE)
        food_rect = pygame.Rect(food.position[0], food.position[1], BLOCK_SIZE, BLOCK_SIZE)
        
        if head_rect.colliderect(food_rect):
            snake.length += 1
            snake.score += 1
            food.randomize_position()
            # 确保食物不会出现在蛇身上
            while any(food_rect.colliderect(pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE)) for pos in snake.positions):
                food.randomize_position()
                food_rect = pygame.Rect(food.position[0], food.position[1], BLOCK_SIZE, BLOCK_SIZE)

        # 绘制游戏界面
        screen.fill(BLACK)  # 整个窗口填充黑色
        
        # 绘制分数区域（灰色背景）
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, WINDOW_WIDTH, SCORE_HEIGHT))
        
        # 显示分数（居中显示）
        score_text = game_font.render(f'得分: {snake.score}', True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH/2, SCORE_HEIGHT/2))
        screen.blit(score_text, score_rect)
        
        # 绘制游戏区域分隔线
        pygame.draw.line(screen, WHITE, (0, SCORE_HEIGHT), (WINDOW_WIDTH, SCORE_HEIGHT), 2)
        
        # 绘制蛇和食物
        snake.render()
        food.render()
        
        pygame.display.update()
        clock.tick(GAME_SPEED)

if __name__ == '__main__':
    main()