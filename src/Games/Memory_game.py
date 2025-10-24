"""
Full-Screen Memory Match Game with Transparent Background (Fixed & Improved)
Place this file as: games/memory_game.py
"""

import random
import sys
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QLabel, 
                              QWidget, QGridLayout, QVBoxLayout, QHBoxLayout)
from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, 
                          pyqtSignal, QRect, QSize)
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
        
        self.setMinimumSize(80, 80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()
        
    def update_style(self):
        """Update card styling based on state"""
        if self.is_matched:
            # Matched cards - green glow effect
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(100, 255, 100, 220);
                    color: white;
                    border: 4px solid rgba(150, 255, 150, 255);
                    border-radius: 15px;
                    font-size: 40px;
                    font-weight: bold;
                }
            """)
            self.setText(self.icon)
            self.setEnabled(False)  # Disable matched cards
        elif self.is_flipped:
            # Flipped cards - white background
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 240);
                    color: rgba(50, 50, 50, 255);
                    border: 3px solid rgba(200, 220, 255, 220);
                    border-radius: 15px;
                    font-size: 40px;
                    font-weight: bold;
                }
            """)
            self.setText(self.icon)
        else:
            # Hidden cards - blue background with question mark
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(70, 130, 200, 220);
                    color: white;
                    border: 3px solid rgba(120, 180, 255, 200);
                    border-radius: 15px;
                    font-size: 32px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(90, 150, 220, 240);
                    border: 3px solid rgba(140, 200, 255, 230);
                }
                QPushButton:disabled {
                    background-color: rgba(50, 90, 160, 180);
                }
            """)
            self.setText("❓")
    
    def flip_to_show(self):
        """Flip card to show icon"""
        if self.is_animating or self.is_matched:
            return False
        
        if not self.is_flipped:
            self.is_animating = True
            self.is_flipped = True
            
            # Scale animation
            self.animation = QPropertyAnimation(self, b"minimumSize")
            self.animation.setDuration(150)
            self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
            original_size = self.minimumSize()
            smaller_size = QSize(original_size.width() - 20, original_size.height())
            
            self.animation.setStartValue(original_size)
            self.animation.setKeyValueAt(0.5, smaller_size)
            self.animation.setEndValue(original_size)
            
            QTimer.singleShot(75, self.update_style)
            self.animation.finished.connect(self.on_animation_finished)
            self.animation.start()
            return True
        return False
    
    def flip_to_hide(self):
        """Flip card to hide icon"""
        if self.is_animating or self.is_matched:
            return
        
        if self.is_flipped:
            self.is_animating = True
            self.is_flipped = False
            
            # Scale animation
            self.animation = QPropertyAnimation(self, b"minimumSize")
            self.animation.setDuration(150)
            self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
            original_size = self.minimumSize()
            smaller_size = QSize(original_size.width() - 20, original_size.height())
            
            self.animation.setStartValue(original_size)
            self.animation.setKeyValueAt(0.5, smaller_size)
            self.animation.setEndValue(original_size)
            
            QTimer.singleShot(75, self.update_style)
            self.animation.finished.connect(self.on_animation_finished)
            self.animation.start()
    
    def on_animation_finished(self):
        """Called when flip animation completes"""
        self.is_animating = False
    
    def set_matched(self):
        """Mark card as matched with animation"""
        self.is_matched = True
        self.is_flipped = True
        
        # Pulse animation for matched cards
        self.match_animation = QPropertyAnimation(self, b"minimumSize")
        self.match_animation.setDuration(400)
        self.match_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        original_size = self.minimumSize()
        larger_size = QSize(original_size.width() + 15, original_size.height() + 15)
        
        self.match_animation.setStartValue(original_size)
        self.match_animation.setKeyValueAt(0.5, larger_size)
        self.match_animation.setEndValue(original_size)
        self.match_animation.start()
        
        self.update_style()


class MemoryMatchGame(QMainWindow):
    game_ended = pyqtSignal(int)  # Signal to emit score (moves) when game ends
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_window()
        self.setup_game_variables()
        self.setup_ui()
        self.setup_timers()
        
        # Initial card setup after UI is ready
        QTimer.singleShot(100, self.setup_cards)
        
    def setup_window(self):
        """Configure full-screen transparent window"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        
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
        self.is_checking = False
        
        # Card icons (emojis)
        self.card_icons = [
            "🎮", "🎯", "🎨", "🎭",
            "🎪", "🎸", "🎹", "🎺"
        ]
        
        self.cards = []
        
    def calculate_card_size(self):
        """Calculate optimal card size based on screen dimensions"""
        # Reserve space for UI elements
        available_width = self.screen_width - 200  # Margins
        available_height = self.screen_height - 300  # Top bar + margins
        
        # 4x4 grid with spacing
        cols = 4
        rows = 4
        spacing = 15
        
        # Calculate max card size
        max_card_width = (available_width - (spacing * (cols + 1))) // cols
        max_card_height = (available_height - (spacing * (rows + 1))) // rows
        
        # Use square cards (take minimum dimension)
        card_size = min(max_card_width, max_card_height, 150)  # Max 150px
        card_size = max(card_size, 80)  # Min 80px
        
        return card_size
        
    def setup_ui(self):
        """Setup UI elements"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 40, 50, 40)
        main_layout.setSpacing(20)
        
        # Top status bar
        status_bar = QWidget()
        status_bar.setFixedHeight(70)
        status_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 20, 30, 220);
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
                font-size: 22px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # Matched label
        self.matched_label = QLabel(f"Matched: 0 / {self.total_pairs}")
        self.matched_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # Timer label
        self.timer_label = QLabel("Timer: 00:00")
        self.timer_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
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
        
        # Spacer to center grid vertically
        main_layout.addStretch()
        
        # Card grid container (centered)
        grid_container = QWidget()
        self.grid_layout = QGridLayout(grid_container)
        
        # Calculate card size and spacing
        card_size = self.calculate_card_size()
        spacing = 15
        
        self.grid_layout.setSpacing(spacing)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Set fixed size for grid container
        grid_width = (card_size * 4) + (spacing * 3)
        grid_height = (card_size * 4) + (spacing * 3)
        grid_container.setFixedSize(grid_width, grid_height)
        
        # Center the grid horizontally
        grid_wrapper = QWidget()
        grid_wrapper_layout = QHBoxLayout(grid_wrapper)
        grid_wrapper_layout.addStretch()
        grid_wrapper_layout.addWidget(grid_container)
        grid_wrapper_layout.addStretch()
        
        main_layout.addWidget(grid_wrapper)
        
        # Bottom spacer
        main_layout.addStretch()
        
        # Win message (hidden initially, positioned as overlay)
        self.win_label = QLabel("")
        self.win_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.win_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 230);
                border: 5px solid rgba(100, 255, 100, 220);
                border-radius: 40px;
                font-size: 32px;
                font-weight: bold;
                padding: 40px;
            }
        """)
        self.win_label.hide()
        self.win_label.setParent(self)
        
        # Restart button
        self.restart_button = QPushButton("🔄", self)
        self.restart_button.setGeometry(self.width() - 80, 30, 50, 50)
        self.restart_button.clicked.connect(self.restart_game)
        self.restart_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 150, 50, 220);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(220, 170, 70, 250);
            }
        """)
        
        # Close button
        self.close_button = QPushButton("✕", self)
        self.close_button.setGeometry(self.width() - 140, 30, 50, 50)
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 100, 100, 220);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 120, 120, 250);
            }
        """)
        
    def setup_cards(self):
        """Create and shuffle cards with responsive sizing"""
        # Clear existing cards
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()
        
        # Create pairs
        card_pairs = []
        for i, icon in enumerate(self.card_icons):
            card_pairs.append((i, icon))
            card_pairs.append((i, icon))
        
        # Shuffle
        random.shuffle(card_pairs)
        
        # Calculate card size
        card_size = self.calculate_card_size()
        
        # Create card widgets in 4x4 grid
        for idx, (pair_id, icon) in enumerate(card_pairs):
            row = idx // 4
            col = idx % 4
            
            card = Card(pair_id, icon)
            card.setFixedSize(card_size, card_size)
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
        # Prevent clicks during checking or if card is already flipped
        if not self.can_flip or self.is_checking or card.is_flipped or card.is_matched:
            return
        
        # Start timer on first click
        if not self.game_started:
            self.game_started = True
            self.game_timer.start(1000)
        
        # Flip the card
        success = card.flip_to_show()
        if not success:
            return
        
        # Play flip sound
        if self.flip_sound:
            try:
                self.flip_sound.play()
            except:
                pass
        
        if self.first_card is None:
            # First card of the pair
            self.first_card = card
        elif self.second_card is None:
            # Second card of the pair
            self.second_card = card
            self.can_flip = False
            self.is_checking = True
            
            # Increment moves
            self.moves += 1
            self.moves_label.setText(f"Moves: {self.moves}")
            
            # Check for match after brief delay
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
            
            # Reset for next turn
            self.first_card = None
            self.second_card = None
            self.can_flip = True
            self.is_checking = False
            
            # Check if game is complete
            if self.matched_pairs == self.total_pairs:
                QTimer.singleShot(500, self.game_complete)
        else:
            # No match - flip both cards back after delay
            QTimer.singleShot(1000, self.flip_cards_back)
    
    def flip_cards_back(self):
        """Flip non-matching cards back to hidden"""
        if self.first_card and not self.first_card.is_matched:
            self.first_card.flip_to_hide()
        if self.second_card and not self.second_card.is_matched:
            self.second_card.flip_to_hide()
        
        # Reset for next turn
        self.first_card = None
        self.second_card = None
        self.can_flip = True
        self.is_checking = False
    
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
            f"🎉 YOU WIN! 🎉"
            f"Completed in {self.moves} moves\n"
            f"Time: {time_str}"
        )
        
        # Position and show win label
        win_width = 600
        win_height = 280
        self.win_label.setGeometry(
            self.width() // 2 - win_width // 2,
            self.height() // 2 - win_height // 2,
            win_width,
            win_height
        )
        self.win_label.show()
        
        # Bounce animation
        self.confetti_animation = QPropertyAnimation(self.win_label, b"geometry")
        self.confetti_animation.setDuration(600)
        self.confetti_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        start_geo = QRect(
            self.width() // 2 - win_width // 2,
            self.height() // 2 - win_height // 2 - 50,
            win_width - 60,
            win_height - 40
        )
        end_geo = QRect(
            self.width() // 2 - win_width // 2,
            self.height() // 2 - win_height // 2,
            win_width,
            win_height
        )
        self.confetti_animation.setStartValue(start_geo)
        self.confetti_animation.setEndValue(end_geo)
        self.confetti_animation.start()
        
        # Emit score and return to launcher after 2 seconds
        QTimer.singleShot(2000, lambda: self.game_ended.emit(self.moves))
        QTimer.singleShot(2000, self.close)
    
    def restart_game(self):
        """Restart the game"""
        # Reset variables
        self.moves = 0
        self.matched_pairs = 0
        self.timer_seconds = 0
        self.game_started = False
        self.game_completed = False
        self.first_card = None
        self.second_card = None
        self.can_flip = True
        self.is_checking = False
        
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
        
        # Transparent gradient background with blur effect
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(30, 20, 50, 130))
        gradient.setColorAt(0.5, QColor(20, 30, 60, 110))
        gradient.setColorAt(1, QColor(40, 20, 70, 150))
        painter.fillRect(self.rect(), gradient)
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        self.restart_button.move(self.width() - 80, 30)
        self.close_button.move(self.width() - 140, 30)
        
        if self.win_label.isVisible():
            win_width = 600
            win_height = 280
            self.win_label.setGeometry(
                self.width() // 2 - win_width // 2,
                self.height() // 2 - win_height // 2,
                win_width,
                win_height
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