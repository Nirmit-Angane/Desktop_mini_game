## 🧩 About the Project  
**Desktop Mini Game Launcher** is a modern Python + PyQt6 based desktop application that launches multiple mini-games — all in one place!  
It features a **transparent, frameless launcher window** that floats above the taskbar.  
Each game runs **fullscreen**, automatically fits **any screen size**, and **returns to the launcher** after the game ends.  
Everything is built purely with **Python and PyQt6** — no external UI engines used.



## ⚡ Included Mini Games  


- ⚡ **Speed Click Game** – Click circles as fast as possible.  
- 🧠 **Memory Match Game** – Match the correct pairs of cards.  
- 🧱 **Brick Break Game** – Classic paddle-and-ball brick breaker.  

All games are fully responsive and optimized for smooth performance.


## 🌟 Features  

✅ Transparent, frameless floating launcher  
✅ Fullscreen adaptive mini-games  
✅ Smooth transitions and animations  
✅ Cross-platform scaling for any screen  
✅ Minimal, modern, and responsive UI  
✅ Built completely with **Python + PyQt6**



## 📁 Project Structure  

<b>DESKTOP_MINI_GAME</b><br>
├── <b>.vscode</b><br>
├── <b>data</b><br>
│   └── settings.json<br>
├── <b>Desktop_mini_game</b><br>
│   └── Game_launcher.exe<br>
├── <b>src</b><br>
│   ├── <b>Games</b><br>
│   │   ├── __pycache__<br>
│   │   │   ├── Brick_game.cpython-313.pyc<br>
│   │   │   ├── Click_game.cpython-313.pyc<br>
│   │   │   └── Memory_game.cpython-313.pyc<br>
│   │   ├── Brick_game.py<br>
│   │   ├── Click_game.py<br>
│   │   ├── Memory_game.py<br>
│   │   └── __init__.py<br>
│   └── Game_launcher.py<br>
└── <b>README.md</b><br>

<style>
.code-box {
  background-color: #21252b;   /* Dark background */
  color: #abb2bf;              /* Light text */
  font-family: 'Consolas', 'Monaco', 'Lucida Console', monospace; /* Code font */
  padding: 15px;               /* Inner spacing */
  border-radius: 4px;          /* Rounded corners */
  line-height: 1.5;            /* Comfortable line height */
  white-space: pre;            /* Preserve spacing and line breaks */
  overflow-x: auto;            /* Allow horizontal scrolling if needed */
  border: 1px solid #3a3f4b;   /* Subtle border for contrast */
  width: 500px;
}
</style>

## ⚙️ Installation & Setup  

### 1️⃣ Clone the Repository  
<div class="code-box">git clone 
https://github.com/username/Desktop_Mini_Game.git
cd Desktop_Mini_Game</div>

### 2️⃣ Install Python
Make sure Python 3.10+ is installed.
👉 Download Python here
<div class="code-box">https://www.python.org/downloads/</div>

### 3️⃣ Install Dependencies

<div class="code-box">pip install PyQt6 pyautogui</div><br>


--- 

### ▶️ Run the Game Launcher

<div class="code-box">python src/Game_launcher.py</div>
<h3>OR</h3>
<div class="code-box">Desktop_mini_game/Game_luncher.exe</div><br>

---

### 💾 Pre-Installed Libraries
<div class="code-box"><table>
    <thead>
        <tr>
            <th>Library</th>
            <th>Purpose</th>
        </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>PyQt6</strong></td>
        <td>GUI creation, transparency, and animation</td>
      </tr>
      <tr>
        <td><strong>pyautogui</strong></td>
        <td>Screen size detection</td>
      </tr>
      <tr>
        <td><strong>json</strong></td>
        <td>Score storage and settings management</td></tr></tbody></table></div>

### 🚀 Future Enhancements

- 🏆 Online & local leaderboard
- 🎮 Add more games
- 🌈 Visual effects and sound improvements
- ☁️ Cloud-based score saves<br><br>

---

### 👨‍💻 Credits

Developed by Nirmit Angane<br>
Built with ❤️ using Python + PyQt6

### ✨ Enjoy gaming on your desktop — simple, light, and fun!