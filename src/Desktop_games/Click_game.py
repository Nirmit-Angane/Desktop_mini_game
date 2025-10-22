import sys
import random
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath, QRegion
from PyQt6.QtMultimedia import QSoundEffect, QAudioOutput
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Click Speed Game")
        self.setGeometry(100, 100, 800, 600)
        
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
    
    def setup_ui(self):
        """Setup the initial UI with start button"""
        # Start button
        self.start_button = QPushButton("Start Game", self)
        self.start_button.setGeometry(300, 250, 200, 60)
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
    
    def start_game(self):
        """Start the game"""
        self.start_button.hide()
        self.score_label.show()
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
        
        # Fade in animation
        self.animate_fade_in()
        
        self.update()
    
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
        self.current_circle = None
        self.score_label.hide()
        self.update()
        
        # Show game over message
        msg = QMessageBox(self)
        msg.setWindowTitle("Game Over")
        msg.setText(f"Game Over!\n\nYour score: {self.score}")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: rgba(50, 50, 50, 250);
            }
            QLabel {
                color: white;
                font-size: 16px;
            }
            QPushButton {
                background-color: rgba(100, 200, 255, 200);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 20px;
                font-size: 14px;
            }
        """)
        msg.exec()
        
        # Reset game
        self.score = 0
        self.start_button.show()
    
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
                    self.animate_fade_out()
            else:
                # Allow dragging window when not in game
                if event.pos().y() < 50:  # Only drag from top area
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if not self.game_active and event.buttons() == Qt.MouseButton.LeftButton:
            if not self.drag_position.isNull():
                self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def paintEvent(self, event):
        """Draw the game elements"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw semi-transparent background
        if not self.game_active and not self.start_button.isVisible():
            # Darker background when game over
            painter.fillRect(self.rect(), QColor(30, 30, 30, 100))
        else:
            painter.fillRect(self.rect(), QColor(20, 20, 20, 50))
        
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
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        # Reposition close button
        self.close_button.move(self.width() - 40, 10)
        # Reposition start button
        self.start_button.setGeometry(
            self.width()//2 - 100,
            self.height()//2 - 30,
            200, 60
        )


def main():
    app = QApplication(sys.argv)
    game = ClickSpeedGame()
    game.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()