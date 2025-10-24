"""
Full-Screen Transparent Game Launcher
Place this file as: launcher.py
"""

import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                              QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                              QGraphicsOpacityEffect, QGraphicsBlurEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient

# Import games
from Games.Click_game import ClickSpeedGame
from Games.Brick_game import BrickBreakerGame
from Games.Memory_game import MemoryMatchGame


class ModernButton(QPushButton):
    """Modern styled button with glow effect"""
    
    def __init__(self, text, icon="🎮", parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.button_text = text
        self.setText(f"{icon}  {text}")
        self.setup_style()
        
    def setup_style(self):
        """Setup modern button styling"""
        # Reduce button size
        self.setFixedSize(180, 60)  # Reduced from 200x80
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(70, 150, 230, 200);
                color: white;
                border: 3px solid rgba(120, 200, 255, 180);
                border-radius: 20px;  /* Reduced from 25px */
                font-size: 16px;      /* Reduced from 18px */
                font-weight: bold;
                padding: 10px;        /* Reduced from 15px */
            }
            QPushButton:hover {
                background-color: rgba(90, 170, 250, 240);
                border: 3px solid rgba(140, 220, 255, 220);
                font-size: 17px;      /* Reduced from 19px */
            }
            QPushButton:pressed {
                background-color: rgba(60, 140, 220, 220);
            }
        """)


class GameLauncher(QMainWindow):
    """Main full-screen transparent game launcher"""
    
    def __init__(self):
        super().__init__()
        self.active_game = None
        self.settings_file = "data/settings.json"
        self.load_settings()
        self.setup_window()
        self.setup_ui()
        self.setup_animations()
        
    def load_settings(self):
        """Load settings and scores from JSON file"""
        os.makedirs("data", exist_ok=True)
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {
                    "high_scores": {
                        "click_game": 0,
                        "brick_game": 0,
                        "memory_game": 999  # Lower is better for memory game
                    }
                }
                self.save_settings()
        except:
            self.settings = {
                "high_scores": {
                    "click_game": 0,
                    "brick_game": 0,
                    "memory_game": 999
                }
            }
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except:
            pass
    
    def update_high_score(self, game_name, score):
        """Update high score if new score is higher"""
        if score > self.settings["high_scores"].get(game_name, 0):
            self.settings["high_scores"][game_name] = score
            self.save_settings()
            self.update_score_display()
    
    def setup_window(self):
        """Configure the main window as full-screen transparent"""
        # Get screen geometry and make full-screen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Make window transparent, frameless, and always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("Game Launcher")
        
        # Setup opacity effect for fade animations
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 35)  # 35px from bottom
        main_layout.setSpacing(0)
        
        # Top spacer (pushes content to bottom)
        main_layout.addStretch()
        
        # Title label (center of screen)
        self.title_label = QLabel("🎮 GAME LAUNCHER", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 48px;
                font-weight: bold;
                background: transparent;
                padding: 20px;
            }
        """)
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.addWidget(self.title_label)
        
        # Position title in center
        main_layout.addWidget(title_container)
        main_layout.addStretch()
        
        # Score display
        self.score_label = QLabel()
        self.update_score_display()
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 230);
                font-size: 16px;
                font-weight: bold;
                background-color: rgba(20, 20, 30, 180);
                border-radius: 20px;
                padding: 12px 25px;
                margin: 10px;
            }
        """)
        
        # Bottom container for scores and buttons
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(15)
        
        # Add score label
        score_wrapper = QWidget()
        score_wrapper_layout = QHBoxLayout(score_wrapper)
        score_wrapper_layout.addStretch()
        score_wrapper_layout.addWidget(self.score_label)
        score_wrapper_layout.addStretch()
        bottom_layout.addWidget(score_wrapper)
        
        # Button container
        button_container = QWidget()
        button_container.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 35, 180);
                border-radius: 30px;
                padding: 20px;
            }
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(30, 20, 30, 20)
        button_layout.setSpacing(25)
        
        # Game buttons
        self.click_game_btn = ModernButton("Click Game", "🎯")
        self.click_game_btn.clicked.connect(self.launch_click_game)
        
        self.brick_game_btn = ModernButton("Brick Game", "🧱")
        self.brick_game_btn.clicked.connect(self.launch_brick_game)
        
        self.memory_game_btn = ModernButton("Memory Game", "🧠")
        self.memory_game_btn.clicked.connect(self.launch_memory_game)
        
        button_layout.addWidget(self.click_game_btn)
        button_layout.addWidget(self.brick_game_btn)
        button_layout.addWidget(self.memory_game_btn)
        
        # Center button container
        button_wrapper = QWidget()
        button_wrapper_layout = QHBoxLayout(button_wrapper)
        button_wrapper_layout.addStretch()
        button_wrapper_layout.addWidget(button_container)
        button_wrapper_layout.addStretch()
        
        bottom_layout.addWidget(button_wrapper)
        main_layout.addWidget(bottom_container)
        
        # Exit button (top-right corner)
        self.exit_button = QPushButton("✕", self)
        self.exit_button.setGeometry(self.width() - 70, 20, 50, 50)
        self.exit_button.clicked.connect(self.close_launcher)
        self.exit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(230, 70, 70, 200);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(250, 90, 90, 240);
                font-size: 26px;
            }
            QPushButton:pressed {
                background-color: rgba(210, 60, 60, 220);
            }
        """)
        
    def update_score_display(self):
        """Update the score display label"""
        click_score = self.settings["high_scores"].get("click_game", 0)
        brick_score = self.settings["high_scores"].get("brick_game", 0)
        memory_score = self.settings["high_scores"].get("memory_game", 999)
        
        self.score_label.setText(
            f"🏆 High Scores  |  🎯 Click: {click_score}  |  "
            f"🧱 Brick: {brick_score}  |  "
            f"🧠 Memory: {memory_score} moves"
        )
        
    def setup_animations(self):
        """Setup fade animations"""
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(400)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
    def fade_out(self):
        """Fade out the launcher"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        
    def fade_in(self):
        """Fade in the launcher"""
        self.show()
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
        
    def launch_click_game(self):
        """Launch the Click Speed Game"""
        self.fade_out()
        QTimer.singleShot(450, self._show_click_game)
        
    def _show_click_game(self):
        """Show click game after fade out"""
        self.active_game = ClickSpeedGame(self)
        self.active_game.game_ended.connect(self.on_click_game_ended)
        self.active_game.show()
        
    def launch_brick_game(self):
        """Launch Brick Breaker Game"""
        self.fade_out()
        QTimer.singleShot(450, self._show_brick_game)
        
    def _show_brick_game(self):
        """Show brick game after fade out"""
        self.active_game = BrickBreakerGame(self)
        self.active_game.game_ended.connect(self.on_brick_game_ended)
        self.active_game.show()
        
    def launch_memory_game(self):
        """Launch Memory Match Game"""
        self.fade_out()
        QTimer.singleShot(450, self._show_memory_game)
        
    def _show_memory_game(self):
        """Show memory game after fade out"""
        self.active_game = MemoryMatchGame(self)
        self.active_game.game_ended.connect(self.on_memory_game_ended)
        self.active_game.show()
        
    def on_click_game_ended(self, score):
        """Handle click game ended"""
        self.update_high_score("click_game", score)
        QTimer.singleShot(2000, self.return_to_launcher)
        
    def on_brick_game_ended(self, score):
        """Handle brick game ended"""
        self.update_high_score("brick_game", score)
        QTimer.singleShot(2000, self.return_to_launcher)
        
    def on_memory_game_ended(self, moves):
        """Handle memory game ended"""
        # Update high score if moves is lower (better score)
        current_high = self.settings["high_scores"].get("memory_game", 999)
        if moves < current_high:
            self.settings["high_scores"]["memory_game"] = moves
            self.save_settings()
            self.update_score_display()
        QTimer.singleShot(2000, self.return_to_launcher)
        
    def return_to_launcher(self):
        """Return to launcher after game ends"""
        if self.active_game:
            self.active_game.close()
            self.active_game = None
        self.fade_in()
        
    def close_launcher(self):
        """Close the launcher and all games"""
        if self.active_game:
            self.active_game.close()
        self.close()
        
    def paintEvent(self, event):
        """Draw background with blur/dim effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dim gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(10, 10, 20, 100))
        gradient.setColorAt(0.5, QColor(15, 15, 30, 80))
        gradient.setColorAt(1, QColor(20, 20, 40, 120))
        
        painter.fillRect(self.rect(), gradient)
        
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        self.exit_button.move(self.width() - 70, 20)
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close_launcher()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    launcher = GameLauncher()
    launcher.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()