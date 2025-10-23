"""
Full-Screen Memory Match Game with Transparent Background
Place this file as: games/memory_game.py
"""

import random
import sys
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QLabel, 
                              QWidget, QGridLayout, QVBoxLayout, QHBoxLayout)
from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, 
                          pyqtSignal, QRect, QParallelAnimationGroup)
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl


class Card(QPushButton):
    """Individual memory card with flip animation"""
    
    def __init__(self, pair_id, icon, parent=None):
        super().__init__(parent)
        self.pair_id = pair_id
        self.icon = icon
        self.is_flipped = False
        self.is_matched = False
        self.is_animating = False
        
        self.setFixedSize(120, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()
        
    def update_style(self):
        """Update card styling based on state"""
        if self.is_matched:
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(100, 200, 100, 200);
                    color: white;
                    border: 3px solid rgba(150, 255, 150, 200);
                    border-radius: 15px;
                    font-size: 48px;
                    font-weight: bold;
                }
            """)
            self.setText(self.icon)
        elif self.is_flipped:
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 220);
                    color: rgba(50, 50, 50, 255);
                    border: 3px solid rgba(200, 220, 255, 200);
                    border-radius: 15px;
                    font-size: 48px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 240);
                }
            """)
            self.setText(self.icon)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(70, 130, 200, 200);
                    color: white;
                    border: 3px solid rgba(120, 180, 255, 180);
                    border-radius: 15px;
                    font-size: 32px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(90, 150, 220, 220);
                    border: 3px solid rgba(140, 200, 255, 200);
                }
            """)
            self.setText("?")
    
    def flip(self):
        """Flip the card with animation"""
        if self.is_animating or self.is_matched:
            return
            
        self.is_animating = True
        self.is_flipped = not self.is_flipped
        
        # Simple flip animation (scale effect)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        start_rect = self.geometry()
        mid_rect = QRect(
            start_rect.x() + start_rect.width() // 4,
            start_rect.y(),
            start_rect.width() // 2,
            start_rect.height()
        )
        
        self.animation.setStartValue(start_rect)
        self.animation.setKeyValueAt(0.5, mid_rect)
        self.animation.setEndValue(start_rect)
        self.animation.finished.connect(self.on_animation_finished)
        self.animation.start()
        
        # Update appearance at midpoint
        QTimer.singleShot(100, self.update_style)
    
    def on_animation_finished(self):
        """Called when flip animation completes"""
        self.is_animating = False
    
    def set_matched(self):
        """Mark card as matched"""
        self.is_matched = True
        self.is_flipped = True
        self.update_style()
        self.setEnabled(False)


class MemoryMatchGame(QMainWindow):
    game_ended = pyqtSignal(int)  # Signal to emit score (moves) when game ends
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_window()
        self.setup_game_variables()
        self.setup_ui()
        self.setup_cards()
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
        self.setWindowTitle("Memory Match")
        
    def setup_game_variables(self):
        """Initialize game variables"""
        self.moves = 0
        self.matched_pairs = 0
        self.total_pairs = 8
        self.timer_seconds = 0
        self.game_started = False
        self.game_completed = False
        
        self.first_card = None
        self.second_card = None
        self.can_flip = True
        
        # Card icons (emojis)
        self.card_icons = [
            "🎮", "🎯", "🎨", "🎭",
            "🎪", "🎸", "🎹", "🎺"
        ]
        
    def setup_ui(self):
        """Setup UI elements"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)
        
        # Top status bar
        status_bar = QWidget()
        status_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 20, 30, 200);
                border-radius: 25px;
                padding: 15px;
            }
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setSpacing(40)
        
        # Moves label
        self.moves_label = QLabel("Moves: 0")
        self.moves_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # Matched label
        self.matched_label = QLabel(f"Matched: 0 / {self.total_pairs}")
        self.matched_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # Timer label
        self.timer_label = QLabel("Timer: 00:00")
        self.timer_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        status_layout.addWidget(self.moves_label)
        status_layout.addStretch()
        status_layout.addWidget(self.matched_label)
        status_layout.addStretch()
        status_layout.addWidget(self.timer_label)
        
        main_layout.addWidget(status_bar)
        
        # Title
        self.title_label = QLabel("🧠 MEMORY MATCH")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 48px;
                font-weight: bold;
                background: transparent;
                margin: 20px;
            }
        """)
        main_layout.addWidget(self.title_label)
        
        # Card grid container
        grid_container = QWidget()
        grid_container.setMaximumSize(600, 600)
        self.grid_layout = QGridLayout(grid_container)
        self.grid_layout.setSpacing(15)
        
        # Center the grid
        grid_wrapper = QWidget()
        grid_wrapper_layout = QHBoxLayout(grid_wrapper)
        grid_wrapper_layout.addStretch()
        grid_wrapper_layout.addWidget(grid_container)
        grid_wrapper_layout.addStretch()
        
        main_layout.addWidget(grid_wrapper)
        main_layout.addStretch()
        
        # Win message (hidden initially)
        self.win_label = QLabel("")
        self.win_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.win_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 220);
                border: 4px solid rgba(100, 255, 100, 200);
                border-radius: 40px;
                font-size: 36px;
                font-weight: bold;
                padding: 40px;
            }
        """)
        self.win_label.hide()
        
        # Position win label in center (overlay)
        self.win_label.setParent(self)
        self.win_label.setGeometry(
            self.width() // 2 - 300,
            self.height() // 2 - 150,
            600, 300
        )
        
        # Restart button
        self.restart_button = QPushButton("🔄", self)
        self.restart_button.setGeometry(self.width() - 80, 30, 50, 50)
        self.restart_button.clicked.connect(self.restart_game)
        self.restart_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 150, 50, 200);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(220, 170, 70, 240);
            }
        """)
        
        # Close button
        self.close_button = QPushButton("✕", self)
        self.close_button.setGeometry(self.width() - 140, 30, 50, 50)
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
        
    def setup_cards(self):
        """Create and shuffle cards"""
        # Create pairs
        card_pairs = []
        for i, icon in enumerate(self.card_icons):
            card_pairs.append((i, icon))
            card_pairs.append((i, icon))
        
        # Shuffle
        random.shuffle(card_pairs)
        
        # Create card widgets in 4x4 grid
        self.cards = []
        for idx, (pair_id, icon) in enumerate(card_pairs):
            row = idx // 4
            col = idx % 4
            
            card = Card(pair_id, icon)
            card.clicked.connect(lambda checked, c=card: self.on_card_clicked(c))
            
            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)
    
    def setup_timers(self):
        """Setup game timer"""
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_timer)
        
        # Sound effects
        try:
            self.flip_sound = QSoundEffect()
            self.flip_sound.setVolume(0.3)
            
            self.match_sound = QSoundEffect()
            self.match_sound.setVolume(0.4)
            
            self.win_sound = QSoundEffect()
            self.win_sound.setVolume(0.5)
        except:
            self.flip_sound = None
            self.match_sound = None
            self.win_sound = None
    
    def on_card_clicked(self, card):
        """Handle card click"""
        if not self.can_flip or card.is_flipped or card.is_matched:
            return
        
        # Start timer on first click
        if not self.game_started:
            self.game_started = True
            self.game_timer.start(1000)
        
        # Play flip sound
        if self.flip_sound:
            try:
                self.flip_sound.play()
            except:
                pass
        
        # Flip the card
        card.flip()
        
        if self.first_card is None:
            # First card of the pair
            self.first_card = card
        elif self.second_card is None:
            # Second card of the pair
            self.second_card = card
            self.can_flip = False
            
            # Increment moves
            self.moves += 1
            self.moves_label.setText(f"Moves: {self.moves}")
            
            # Check for match after animation
            QTimer.singleShot(600, self.check_match)
    
    def check_match(self):
        """Check if two flipped cards match"""
        if self.first_card.pair_id == self.second_card.pair_id:
            # Match found!
            self.first_card.set_matched()
            self.second_card.set_matched()
            
            self.matched_pairs += 1
            self.matched_label.setText(f"Matched: {self.matched_pairs} / {self.total_pairs}")
            
            # Play match sound
            if self.match_sound:
                try:
                    self.match_sound.play()
                except:
                    pass
            
            # Check if game is complete
            if self.matched_pairs == self.total_pairs:
                self.game_complete()
        else:
            # No match - flip back
            QTimer.singleShot(800, self.flip_back)
        
        self.first_card = None
        self.second_card = None
        self.can_flip = True
    
    def flip_back(self):
        """Flip cards back when they don't match"""
        if self.first_card and not self.first_card.is_matched:
            self.first_card.flip()
        if self.second_card and not self.second_card.is_matched:
            self.second_card.flip()
    
    def update_timer(self):
        """Update game timer"""
        self.timer_seconds += 1
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.timer_label.setText(f"Timer: {minutes:02d}:{seconds:02d}")
    
    def game_complete(self):
        """Handle game completion"""
        if self.game_completed:
            return
            
        self.game_completed = True
        self.game_timer.stop()
        
        # Play win sound
        if self.win_sound:
            try:
                self.win_sound.play()
            except:
                pass
        
        # Show win message
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        self.win_label.setText(
            f"🎉 YOU WIN! 🎉\n\n"
            f"Completed in {self.moves} moves\n"
            f"Time: {time_str}\n\n"
            f"Returning to launcher..."
        )
        self.win_label.show()
        
        # Confetti effect (simple scale animation)
        self.confetti_animation = QPropertyAnimation(self.win_label, b"geometry")
        self.confetti_animation.setDuration(500)
        self.confetti_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        start_geo = self.win_label.geometry()
        self.confetti_animation.setStartValue(QRect(
            start_geo.x() + 50,
            start_geo.y() + 50,
            start_geo.width() - 100,
            start_geo.height() - 100
        ))
        self.confetti_animation.setEndValue(start_geo)
        self.confetti_animation.start()
        
        # Emit score and return to launcher
        QTimer.singleShot(2000, lambda: self.game_ended.emit(self.moves))
    
    def restart_game(self):
        """Restart the game"""
        # Clear existing cards
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()
        
        # Reset variables
        self.moves = 0
        self.matched_pairs = 0
        self.timer_seconds = 0
        self.game_started = False
        self.game_completed = False
        self.first_card = None
        self.second_card = None
        self.can_flip = True
        
        # Reset UI
        self.moves_label.setText("Moves: 0")
        self.matched_label.setText(f"Matched: 0 / {self.total_pairs}")
        self.timer_label.setText("Timer: 00:00")
        self.win_label.hide()
        
        # Stop timer
        self.game_timer.stop()
        
        # Recreate cards
        self.setup_cards()
    
    def paintEvent(self, event):
        """Draw background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Transparent gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(30, 20, 50, 120))
        gradient.setColorAt(0.5, QColor(20, 30, 60, 100))
        gradient.setColorAt(1, QColor(40, 20, 70, 140))
        painter.fillRect(self.rect(), gradient)
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        self.restart_button.move(self.width() - 80, 30)
        self.close_button.move(self.width() - 140, 30)
        self.win_label.setGeometry(
            self.width() // 2 - 300,
            self.height() // 2 - 150,
            600, 300
        )


def start_memory_game():
    """Standalone game launcher"""
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MemoryMatchGame()
    window.showFullScreen()
    sys.exit(app.exec())


if __name__ == "__main__":
    start_memory_game()