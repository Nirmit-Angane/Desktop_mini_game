"""
Full-Screen Brick Breaker Game with Transparent Background (Final Version)
Place this file as: games/brick_game.py
"""

import random
import math
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl


class Paddle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = 15
        
    def move_left(self, screen_width):
        self.x = max(0, self.x - self.speed)
        
    def move_right(self, screen_width):
        self.x = min(screen_width - self.width, self.x + self.speed)
        
    def get_rect(self):
        return QRectF(self.x, self.y, self.width, self.height)


class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = 5
        self.speed_y = -5
        self.speed_multiplier = 1.0
        
    def move(self):
        self.x += self.speed_x * self.speed_multiplier
        self.y += self.speed_y * self.speed_multiplier
        
    def bounce_x(self):
        self.speed_x = -self.speed_x
        
    def bounce_y(self):
        self.speed_y = -self.speed_y
        
    def get_rect(self):
        return QRectF(self.x - self.radius, self.y - self.radius, 
                      self.radius * 2, self.radius * 2)


class Brick:
    def __init__(self, x, y, width, height, color, hits=1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hits = hits
        self.max_hits = hits
        self.destroyed = False
        
    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.destroyed = True
            return True
        return False
        
    def get_rect(self):
        return QRectF(self.x, self.y, self.width, self.height)


class BrickBreakerGame(QMainWindow):
    game_ended = pyqtSignal(int)  # Signal to emit score when game ends
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_window()
        self.setup_game_variables()
        self.setup_ui()
        self.setup_timers()
        
    def setup_window(self):
        """Configure full-screen transparent window"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("Brick Breaker")
        
    def setup_game_variables(self):
        """Initialize game variables"""
        self.score = 0
        self.lives = 3
        self.game_active = False
        self.game_started = False
        
        # Paddle
        paddle_width = 120
        paddle_height = 20
        self.paddle = Paddle(
            self.width() // 2 - paddle_width // 2,
            self.height() - 100,
            paddle_width,
            paddle_height
        )
        
        # Ball
        self.ball = Ball(self.width() // 2, self.height() - 150, 10)
        self.ball_attached = True
        
        # Bricks
        self.bricks = []
        self.create_bricks()
        
        # Keys pressed
        self.keys_pressed = set()
        
    def create_bricks(self):
        """Create brick layout"""
        self.bricks = []
        brick_width = 80
        brick_height = 30
        spacing = 5
        start_x = 50
        start_y = 100
        rows = 6
        cols = (self.width() - 100) // (brick_width + spacing)
        
        colors = [
            QColor(255, 100, 100),
            QColor(255, 180, 100),
            QColor(255, 255, 100),
            QColor(100, 255, 100),
            QColor(100, 180, 255),
            QColor(180, 100, 255),
        ]
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (brick_width + spacing)
                y = start_y + row * (brick_height + spacing)
                color = colors[row % len(colors)]
                hits = 1 if row < 4 else 2
                self.bricks.append(Brick(x, y, brick_width, brick_height, color, hits))
    
    def setup_ui(self):
        """Setup UI elements"""
        # Title
        self.title_label = QLabel("🧱 BRICK BREAKER", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setGeometry(0, self.height()//3, self.width(), 80)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 48px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # Start button
        self.start_button = QPushButton("▶  START GAME", self)
        self.start_button.setGeometry(
            self.width()//2 - 150,
            self.height()//2,
            300, 80
        )
        self.start_button.clicked.connect(self.start_game)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(70, 200, 100, 220);
                color: white;
                border: 3px solid rgba(100, 255, 150, 200);
                border-radius: 40px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(90, 220, 120, 250);
                font-size: 26px;
            }
        """)
        
        # Instructions
        self.instructions_label = QLabel(
            "Use ← → Arrow Keys or Mouse to Move Paddle\nPress SPACE to Launch Ball",
            self
        )
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructions_label.setGeometry(0, self.height()//2 + 100, self.width(), 60)
        self.instructions_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 200);
                font-size: 18px;
                background: transparent;
            }
        """)
        
        # Score label
        self.score_label = QLabel("Score: 0", self)
        self.score_label.setGeometry(40, 20, 200, 50)
        self.score_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                border-radius: 25px;
                padding: 12px;
                font-size: 22px;
                font-weight: bold;
            }
        """)
        self.score_label.hide()
        
        # Lives label
        self.lives_label = QLabel("Lives: ❤️❤️❤️", self)
        self.lives_label.setGeometry(self.width() - 240, 20, 200, 50)
        self.lives_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                border-radius: 25px;
                padding: 12px;
                font-size: 22px;
                font-weight: bold;
            }
        """)
        self.lives_label.hide()
        
        # Game over label
        self.game_over_label = QLabel("", self)
        self.game_over_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_over_label.setGeometry(0, self.height()//2 - 150, self.width(), 180)
        self.game_over_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 220);
                border: 3px solid rgba(255, 150, 100, 200);
                border-radius: 40px;
                font-size: 32px;
                font-weight: bold;
                padding: 30px;
            }
        """)
        self.game_over_label.hide()
        
        # Return to menu button
        self.return_menu_button = QPushButton("🏠 Return to Launcher", self)
        self.return_menu_button.setGeometry(
            self.width()//2 - 150,
            self.height()//2 + 80,
            300, 60
        )
        self.return_menu_button.clicked.connect(self.return_to_launcher)
        self.return_menu_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(70, 150, 230, 220);
                color: white;
                border: 3px solid rgba(100, 200, 255, 200);
                border-radius: 30px;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: rgba(90, 170, 250, 250);
                font-size: 22px;
            }
            QPushButton:pressed {
                background-color: rgba(60, 140, 220, 220);
            }
        """)
        self.return_menu_button.hide()
        
        # Close button
        self.close_button = QPushButton("✕", self)
        self.close_button.setGeometry(self.width() - 70, 20, 50, 50)
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 100, 100, 200);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 120, 120, 240);
            }
        """)
        
    def setup_timers(self):
        """Setup game timer"""
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_loop)
        
        try:
            self.hit_sound = QSoundEffect()
            self.hit_sound.setVolume(0.3)
        except:
            self.hit_sound = None
    
    def start_game(self):
        """Start the game"""
        self.start_button.hide()
        self.title_label.hide()
        self.instructions_label.hide()
        self.score_label.show()
        self.lives_label.show()
        self.game_active = True
        self.game_started = True
        self.score = 0
        self.lives = 3
        self.update_score()
        self.update_lives()
        self.game_timer.start(16)
    
    def game_loop(self):
        """Main game loop"""
        if not self.game_active:
            return
            
        # Handle key movements
        if Qt.Key.Key_Left in self.keys_pressed:
            self.paddle.move_left(self.width())
        if Qt.Key.Key_Right in self.keys_pressed:
            self.paddle.move_right(self.width())
        
        # Move ball if not attached
        if not self.ball_attached:
            self.ball.move()
            
            # Ball collision with walls
            if self.ball.x - self.ball.radius <= 0 or self.ball.x + self.ball.radius >= self.width():
                self.ball.bounce_x()
            if self.ball.y - self.ball.radius <= 0:
                self.ball.bounce_y()
            
            # Ball collision with paddle
            ball_rect = self.ball.get_rect()
            paddle_rect = self.paddle.get_rect()
            if ball_rect.intersects(paddle_rect) and self.ball.speed_y > 0:
                self.ball.bounce_y()
                hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width
                self.ball.speed_x = (hit_pos - 0.5) * 10
                
            # Ball collision with bricks
            for brick in self.bricks:
                if not brick.destroyed and ball_rect.intersects(brick.get_rect()):
                    if brick.hit():
                        self.score += 10
                        self.update_score()
                    else:
                        self.score += 5
                        self.update_score()
                    
                    if self.hit_sound:
                        try:
                            self.hit_sound.play()
                        except:
                            pass
                    
                    brick_rect = brick.get_rect()
                    if abs(self.ball.x - brick_rect.center().x()) > abs(self.ball.y - brick_rect.center().y()):
                        self.ball.bounce_x()
                    else:
                        self.ball.bounce_y()
                    break
            
            # Ball fell off screen
            if self.ball.y - self.ball.radius > self.height():
                self.lives -= 1
                self.update_lives()
                if self.lives <= 0:
                    self.end_game(False)
                else:
                    self.reset_ball()
            
            # Check win condition
            if all(brick.destroyed for brick in self.bricks):
                self.end_game(True)
        else:
            # Ball attached to paddle
            self.ball.x = self.paddle.x + self.paddle.width // 2
            self.ball.y = self.paddle.y - self.ball.radius - 5
        
        self.update()
    
    def reset_ball(self):
        """Reset ball to paddle"""
        self.ball.x = self.paddle.x + self.paddle.width // 2
        self.ball.y = self.paddle.y - self.ball.radius - 5
        self.ball.speed_x = 5
        self.ball.speed_y = -5
        self.ball_attached = True
    
    def update_score(self):
        """Update score display"""
        self.score_label.setText(f"Score: {self.score}")
    
    def update_lives(self):
        """Update lives display"""
        hearts = "❤️" * self.lives
        self.lives_label.setText(f"Lives: {hearts}")
    
    def return_to_launcher(self):
        """Return to the game launcher"""
        self.close()
    
    def end_game(self, won):
        """End the game"""
        self.game_active = False
        self.game_timer.stop()
        self.score_label.hide()
        self.lives_label.hide()
        
        if won:
            self.game_over_label.setText(
                f"🎉 VICTORY! 🎉\n🧱 Score: {self.score}\nAll Bricks Destroyed!"
            )
        else:
            self.game_over_label.setText(
                f"💥 GAME OVER 💥\n🧱 Score: {self.score}\nNo Lives Remaining!"
            )
        
        self.game_over_label.show()
        self.return_menu_button.show()
        self.update()
        
        # Emit signal with score
        self.game_ended.emit(self.score)
    
    def keyPressEvent(self, event):
        """Handle key press"""
        self.keys_pressed.add(event.key())
        if event.key() == Qt.Key.Key_Space and self.ball_attached:
            self.ball_attached = False
    
    def keyReleaseEvent(self, event):
        """Handle key release"""
        self.keys_pressed.discard(event.key())
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for paddle"""
        if self.game_active:
            mouse_x = event.pos().x()
            self.paddle.x = max(0, min(self.width() - self.paddle.width, 
                                       mouse_x - self.paddle.width // 2))
    
    def mousePressEvent(self, event):
        """Handle mouse click to launch ball"""
        if event.button() == Qt.MouseButton.LeftButton and self.ball_attached:
            self.ball_attached = False
    
    def paintEvent(self, event):
        """Draw game elements"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Transparent gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(20, 10, 40, 120))
        gradient.setColorAt(0.5, QColor(10, 20, 50, 100))
        gradient.setColorAt(1, QColor(30, 10, 60, 140))
        painter.fillRect(self.rect(), gradient)
        
        if not self.game_started:
            return
        
        # Draw paddle
        painter.setBrush(QBrush(QColor(100, 200, 255)))
        painter.setPen(QPen(QColor(150, 220, 255), 2))
        paddle_rect = self.paddle.get_rect()
        painter.drawRoundedRect(paddle_rect, 10, 10)
        
        # Draw ball
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.drawEllipse(
            int(self.ball.x - self.ball.radius),
            int(self.ball.y - self.ball.radius),
            int(self.ball.radius * 2),
            int(self.ball.radius * 2)
        )
        
        # Draw bricks
        for brick in self.bricks:
            if not brick.destroyed:
                color = QColor(brick.color)
                if brick.hits < brick.max_hits:
                    color.setAlpha(150)
                
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(color.lighter(120), 2))
                brick_rect = brick.get_rect()
                painter.drawRoundedRect(brick_rect, 8, 8)
    
    def resizeEvent(self, event):
        """Handle resize"""
        super().resizeEvent(event)
        self.close_button.move(self.width() - 70, 20)
        self.lives_label.move(self.width() - 240, 20)
        self.start_button.setGeometry(
            self.width()//2 - 150,
            self.height()//2,
            300, 80
        )
        self.title_label.setGeometry(0, self.height()//3, self.width(), 80)
        self.instructions_label.setGeometry(0, self.height()//2 + 100, self.width(), 60)
        self.game_over_label.setGeometry(0, self.height()//2 - 150, self.width(), 180)
        self.return_menu_button.setGeometry(
            self.width()//2 - 150,
            self.height()//2 + 80,
            300, 60
        )