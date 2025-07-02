🏃‍♂️ Runner Game AI Utilities
=============================

This repository provides Python support modules and a Unity C# script to enable AI-driven dynamic asset selection and real-time pose-based player control for a runner-style game.

---

📄 Overview
-----------

1️⃣ pose_control_udp.py
- Uses MediaPipe and OpenCV to detect player gestures via webcam (jump, left, right, pause/play).
- Sends these control commands to Unity via UDP.

2️⃣ ai_asset_selector.py
- Flask server that uses OpenAI GPT to classify user-provided game environment concepts into environment and obstacle types.
- Copies matching asset files (textures, prefabs) into Unity project folders.

3️⃣ PlayerController.cs
- Unity C# script that receives UDP messages and controls player movement and animations (jumping, shifting lanes, pausing).

---

🚀 Running Pose Control
-----------------------

Start the pose control script:

    python pose_control_udp.py

- Uses webcam to detect poses.
- Sends commands (Jump, Left, Right, Play, Pause) to Unity at 127.0.0.1:5005.

---

💬 Running AI Asset Selector
----------------------------

Start the Flask server:

    python ai_asset_selector.py

- Endpoint: GET /generate/<concept>
- Example:

        http://localhost:5000/generate/post-apocalyptic city with zombies

- Automatically copies environment and obstacle assets to Unity Resources folders. (You must adjust the paths in the script to your own project structure.)

---

🎮 Unity Integration
--------------------

- Place `PlayerController.cs` inside your Unity project's `Assets/Scripts/` folder.
- Attach it to your player GameObject.
- Player movement and animations will react to UDP messages received from pose_control_udp.py.

---

⚠️ Note
--------

- This repo includes support scripts only. The main Unity project is not included.
- Update asset file paths in `ai_asset_selector.py` as per your Unity setup.

---


📄 License
----------

MIT

---

✨ Happy Running!
