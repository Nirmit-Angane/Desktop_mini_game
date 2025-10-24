"""
Click Speed Game - Integrated version for launcher
Place this file as: games/click_game.py
"""

import random
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from collections import deque


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
    game_ended = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎯 Click Speed Game")
        
        # Get screen size and set window to full screen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Make window frameless and transparent
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Game variables
        self.score = 0
        self.game_active = False
        self.current_circle = None
        self.initial_radius = 75  # About 2cm on most screens
        self.min_radius = 20
        self.radius_decrease = 3
        self.time_limit = 2000  # 2 seconds in milliseconds
        self.circle_opacity = 1.0
        
        # For dragging window
        self.drag_position = QPoint()
        
        # Mouse trail
        self.mouse_trail = deque(maxlen=10)  # Store last 10 positions
        
        # Setup UI
        self.setup_ui()
        
        # Timer for game over
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_over)
        
        # Animation timer for fade effects
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        # Sound effect (optional, might not work if audio system unavailable)
        try:
            self.click_sound = QSoundEffect()
            self.click_sound.setSource(QUrl.fromLocalFile(""))  # No sound file, silent
            self.click_sound.setVolume(0.5)
        except:
            self.click_sound = None
        
        # Timer for mouse trail fading
        self.trail_timer = QTimer()
        self.trail_timer.timeout.connect(self.fade_trail)
        self.trail_timer.start(50)  # Update every 50ms
    
    def setup_ui(self):
        """Setup the initial UI with start button"""
        # Start button - centered in screen
        button_width = 200
        button_height = 60
        self.start_button = QPushButton("▶ Start Game", self)
        self.start_button.setGeometry(
            (self.width() - button_width) // 2,
            (self.height() - button_height) // 2,
            button_width,
            button_height
        )
        self.start_button.clicked.connect(self.start_game)
        
        # Modern button styling
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 200, 255, 200);
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: rgba(120, 220, 255, 230);
            }
            QPushButton:pressed {
                background-color: rgba(80, 180, 235, 200);
            }
        """)
        
        # Score label
        self.score_label = QLabel("Score: 0", self)
        self.score_label.setGeometry(20, 20, 150, 40)
        self.score_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                border-radius: 20px;
                padding: 10px;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.score_label.hide()
        
        # Timer label (shows remaining time)
        self.timer_label = QLabel("Time: 2.0s", self)
        self.timer_label.setGeometry(self.width() - 170, 20, 150, 40)
        self.timer_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                border-radius: 20px;
                padding: 10px;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.timer_label.hide()
        
        # Close button (small X in corner)
        self.close_button = QPushButton("✕", self)
        self.close_button.setGeometry(self.width() - 40, 10, 30, 30)
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 100, 100, 200);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 120, 120, 230);
            }
        """)
        
        # Title label - centered higher up
        self.title_label = QLabel("🎯 CLICK SPEED GAME", self)
        self.title_label.setGeometry(0, self.height() // 4, self.width(), 60)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                background: transparent;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }
        """)
    
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
        """Spawn a new circle at a random position"""
        # Calculate radius based on score
        radius = max(self.initial_radius - (self.score * self.radius_decrease), self.min_radius)
        
        # Random position within window bounds
        margin = radius + 20
        x = random.randint(margin, self.width() - margin)
        y = random.randint(margin + 60, self.height() - margin)  # Avoid top score area
        
        self.current_circle = Circle(x, y, radius)
        self.circle_opacity = 1.0
        
        # Start the game timer
        self.game_timer.start(self.time_limit)
        self.remaining_time = self.time_limit
        
        # Timer display update
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.update_timer_display)
        self.display_timer.start(100)  # Update every 100ms
        
        # Fade in animation
        self.animate_fade_in()
        
        self.update()
    
    def update_timer_display(self):
        """Update the timer display"""
        self.remaining_time -= 100
        if self.remaining_time <= 0:
            self.remaining_time = 0
            self.display_timer.stop()
        
        time_seconds = self.remaining_time / 1000.0
        self.timer_label.setText(f"Time: {time_seconds:.1f}s")
        
        # Change color when time is running out
        if time_seconds < 0.5:
            self.timer_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: rgba(255, 50, 50, 200);
                    border-radius: 20px;
                    padding: 10px;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
        else:
            self.timer_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: rgba(0, 0, 0, 150);
                    border-radius: 20px;
                    padding: 10px;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
    
    def animate_fade_in(self):
        """Fade in animation for new circle"""
        self.circle_opacity = 0.0
        self.fade_direction = 1
        self.animation_timer.start(20)
    
    def animate_fade_out(self):
        """Fade out animation when circle is clicked"""
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
    
    def update_score(self):
        """Update score display"""
        self.score_label.setText(f"Score: {self.score}")
    
    def game_over(self):
        """End the game"""
        self.game_active = False
        self.game_timer.stop()
        self.animation_timer.stop()
        if hasattr(self, 'display_timer'):
            self.display_timer.stop()
        self.current_circle = None
        self.score_label.hide()
        self.timer_label.hide()
        
        # Create game over label if it doesn't exist
        if not hasattr(self, 'game_over_label'):
            self.game_over_label = QLabel("", self)
            self.game_over_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.game_over_label.setGeometry(0, self.height()//2 - 100, self.width(), 200)
            
        # Set game over text with modern emoji and formatting
        self.game_over_label.setText(
            "⏱️ TIME'S UP! ⏱️\n" + f"🎯 Score: {self.score}\n" 
        )
        
        # Modern styling matching brick game
        self.game_over_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 220);
                border: 3px solid rgba(100, 200, 255, 200);
                border-radius: 40px;
                font-size: 32px;
                font-weight: bold;
                padding: 40px;
                margin: 20px;
                line-height: 1.5;
            }
        """)
        
        self.game_over_label.show()
        self.update()
        
        # Emit score signal
        self.game_ended.emit(self.score)
        
        # Hide game over label after delay
        QTimer.singleShot(2000, self.game_over_label.hide)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.game_active and self.current_circle:
                # Check if click is inside circle
                if self.current_circle.contains_point(event.pos()):
                    self.score += 1
                    self.update_score()
                    
                    # Play sound effect
                    if self.click_sound:
                        try:
                            self.click_sound.play()
                        except:
                            pass
                    
                    # Animate fade out and spawn new circle
                    self.game_timer.stop()
                    if hasattr(self, 'display_timer'):
                        self.display_timer.stop()
                    self.animate_fade_out()
            else:
                # Allow dragging window when not in game
                if event.pos().y() < 50:  # Only drag from top area
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging and track mouse movement for trail"""
        if not self.game_active and event.buttons() == Qt.MouseButton.LeftButton:
            if not self.drag_position.isNull():
                self.move(event.globalPosition().toPoint() - self.drag_position)
        elif self.game_active:
            self.mouse_trail.append((event.pos(), 1.0))  # Position and opacity
        
        super().mouseMoveEvent(event)
    
    def fade_trail(self):
        """Fade out trail points"""
        if self.mouse_trail:
            new_trail = deque(maxlen=10)
            for pos, opacity in self.mouse_trail:
                if opacity > 0.1:
                    new_trail.append((pos, opacity * 0.85))
            self.mouse_trail = new_trail
            self.update()
    
    def paintEvent(self, event):
        """Draw the game elements"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw semi-transparent background
        if not self.game_active and not self.start_button.isVisible():
            # Darker background when game over
            painter.fillRect(self.rect(), QColor(30, 30, 30, 100))
        else:
            # Gradient background
            from PyQt6.QtGui import QLinearGradient
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(20, 30, 50, 120))
            gradient.setColorAt(1, QColor(40, 20, 60, 120))
            painter.fillRect(self.rect(), gradient)
        
        # Draw mouse trail
        if self.game_active:
            for pos, opacity in self.mouse_trail:
                painter.setPen(QPen(QColor(255, 255, 255, int(255 * opacity)), 3))
                painter.drawPoint(pos)
        
        # Draw circle if game is active
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
            
            # Draw crosshair in center
            pen.setColor(QColor(255, 255, 255, int(150 * self.circle_opacity)))
            pen.setWidth(1)
            painter.setPen(pen)
            center_x = int(self.current_circle.x)
            center_y = int(self.current_circle.y)
            painter.drawLine(center_x - 5, center_y, center_x + 5, center_y)
            painter.drawLine(center_x, center_y - 5, center_x, center_y + 5)
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        # Reposition close button
        self.close_button.move(self.width() - 40, 10)
        # Reposition timer label
        self.timer_label.move(self.width() - 170, 20)
        # Reposition start button
        self.start_button.setGeometry(
            self.width()//2 - 100,
            self.height()//2 - 30,
            200, 60
        )
        # Reposition title
        self.title_label.setGeometry(0, self.height() // 4, self.width(), 60)