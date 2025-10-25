"""
Full-Screen Click Speed Game with Transparent Background (Final Version)
Place this file as: games/click_game.py
"""

import random
import math
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QLinearGradient
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl


class Circle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.opacity = 1.0
        
    def contains_point(self, point):
        """Check if a point is inside the circle"""
        dx = point.x() - self.x
        dy = point.y() - self.y
        return math.sqrt(dx*dx + dy*dy) <= self.radius


class ClickSpeedGame(QMainWindow):
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
        self.setWindowTitle("Click Speed Game")
        
    def setup_game_variables(self):
        """Initialize game variables"""
        self.score = 0
        self.game_active = False
        self.current_circle = None
        self.initial_radius = 75
        self.min_radius = 20
        self.radius_decrease = 3
        self.time_limit = 2000
        self.circle_opacity = 1.0
        self.fade_direction = 1
        
    def setup_ui(self):
        """Setup UI elements"""
        # Title label
        self.title_label = QLabel("🎯 CLICK SPEED GAME", self)
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
                padding: 20px;
            }
            QPushButton:hover {
                background-color: rgba(90, 220, 120, 250);
                font-size: 26px;
            }
            QPushButton:pressed {
                background-color: rgba(60, 180, 90, 220);
            }
        """)
        
        # Score label
        self.score_label = QLabel("Score: 0", self)
        self.score_label.setGeometry(40, 40, 200, 60)
        self.score_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                border-radius: 30px;
                padding: 15px;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        self.score_label.hide()
        
        # Timer label
        self.timer_label = QLabel("Time: 2.0s", self)
        self.timer_label.setGeometry(self.width() - 240, 40, 200, 60)
        self.timer_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                border-radius: 30px;
                padding: 15px;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        self.timer_label.hide()
        
        # Game over label
        self.game_over_label = QLabel("", self)
        self.game_over_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_over_label.setGeometry(0, self.height()//2 - 150, self.width(), 180)
        self.game_over_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 200);
                border: 3px solid rgba(255, 100, 100, 200);
                border-radius: 40px;
                font-size: 36px;
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
        """Setup game timers"""
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_over)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.update_timer_display)
        
        try:
            self.click_sound = QSoundEffect()
            self.click_sound.setVolume(0.3)
        except:
            self.click_sound = None
    
    def start_game(self):
        """Start the game"""
        self.start_button.hide()
        self.title_label.hide()
        self.score_label.show()
        self.timer_label.show()
        self.game_active = True
        self.score = 0
        self.update_score()
        self.spawn_circle()
    
    def spawn_circle(self):
        """Spawn a new circle"""
        radius = max(self.initial_radius - (self.score * self.radius_decrease), self.min_radius)
        
        margin = radius + 50
        x = random.randint(margin, self.width() - margin)
        y = random.randint(margin + 100, self.height() - margin - 100)
        
        self.current_circle = Circle(x, y, radius)
        self.circle_opacity = 1.0
        
        self.game_timer.start(self.time_limit)
        self.remaining_time = self.time_limit
        self.display_timer.start(50)
        
        self.animate_fade_in()
        self.update()
    
    def animate_fade_in(self):
        """Fade in animation"""
        self.circle_opacity = 0.0
        self.fade_direction = 1
        self.animation_timer.start(20)
    
    def animate_fade_out(self):
        """Fade out animation"""
        self.fade_direction = -1
        self.animation_timer.start(20)
    
    def update_animation(self):
        """Update animation frame"""
        self.circle_opacity += 0.1 * self.fade_direction
        
        if self.fade_direction > 0 and self.circle_opacity >= 1.0:
            self.circle_opacity = 1.0
            self.animation_timer.stop()
        elif self.fade_direction < 0 and self.circle_opacity <= 0.0:
            self.circle_opacity = 0.0
            self.animation_timer.stop()
            if self.game_active:
                self.spawn_circle()
        
        self.update()
    
    def update_timer_display(self):
        """Update timer display"""
        self.remaining_time -= 50
        if self.remaining_time <= 0:
            self.remaining_time = 0
            self.display_timer.stop()
        
        time_seconds = self.remaining_time / 1000.0
        self.timer_label.setText(f"Time: {time_seconds:.1f}s")
        
        if time_seconds < 0.5:
            self.timer_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: rgba(255, 50, 50, 220);
                    border-radius: 30px;
                    padding: 15px;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
        else:
            self.timer_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: rgba(0, 0, 0, 180);
                    border-radius: 30px;
                    padding: 15px;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
    
    def update_score(self):
        """Update score display"""
        self.score_label.setText(f"Score: {self.score}")
    
    def return_to_launcher(self):
        """Return to the game launcher"""
        self.close()
    
    def game_over(self):
        """End the game"""
        self.game_active = False
        self.game_timer.stop()
        self.animation_timer.stop()
        self.display_timer.stop()
        self.current_circle = None
        self.score_label.hide()
        self.timer_label.hide()
        
        # Show game over message
        self.game_over_label.setText(
            f"⏱️ TIME'S UP!\n 🎯 Your Score: {self.score}"
        )
        self.game_over_label.show()
        self.return_menu_button.show()
        
        self.update()
        
        # Emit signal with score
        self.game_ended.emit(self.score)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.game_active and self.current_circle:
                if self.current_circle.contains_point(event.pos()):
                    self.score += 1
                    self.update_score()
                    
                    if self.click_sound:
                        try:
                            self.click_sound.play()
                        except:
                            pass
                    
                    self.game_timer.stop()
                    self.display_timer.stop()
                    self.animate_fade_out()
    
    def paintEvent(self, event):
        """Draw game elements"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Transparent gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(10, 20, 40, 120))
        gradient.setColorAt(0.5, QColor(20, 10, 50, 100))
        gradient.setColorAt(1, QColor(30, 20, 60, 140))
        painter.fillRect(self.rect(), gradient)
        
        # Draw circle
        if self.current_circle and self.game_active:
            pen = QPen(QColor(255, 255, 255, int(255 * self.circle_opacity)))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            painter.drawEllipse(
                int(self.current_circle.x - self.current_circle.radius),
                int(self.current_circle.y - self.current_circle.radius),
                int(self.current_circle.radius * 2),
                int(self.current_circle.radius * 2)
            )
            
            # Draw center crosshair
            pen.setWidth(2)
            painter.setPen(pen)
            cx, cy = int(self.current_circle.x), int(self.current_circle.y)
            painter.drawLine(cx - 8, cy, cx + 8, cy)
            painter.drawLine(cx, cy - 8, cx, cy + 8)
    
    def resizeEvent(self, event):
        """Handle resize"""
        super().resizeEvent(event)
        self.close_button.move(self.width() - 70, 20)
        self.timer_label.move(self.width() - 240, 40)
        self.start_button.setGeometry(
            self.width()//2 - 150,
            self.height()//2,
            300, 80
        )
        self.title_label.setGeometry(0, self.height()//3, self.width(), 80)
        self.game_over_label.setGeometry(0, self.height()//2 - 150, self.width(), 180)
        self.return_menu_button.setGeometry(
            self.width()//2 - 150,
            self.height()//2 + 80,
            300, 60
        )