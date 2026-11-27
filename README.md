# WIRA NUSA — 10 NOVEMBER 1945 (Draft-based build)

This project follows the uploaded **Draft Wira Nusa** and the uploaded **Game kayak Undertale** project as the UI/gameplay reference.

## Source fidelity and scope
The uploaded draft file contains story material through **Chapter 2, Choice 2 Option 2 / Battle 6** (14 pages).
The draft lists Chapter 2 Option 3, but does not provide its dialogue or Battle 7 content. It also does not contain Chapter 3, Battles 8–10, or the endings. The game intentionally stops at this documented boundary rather than inventing story text.

## Features implemented from the uploaded draft
- Intro with the embedded Word backgrounds: peaceful proclamation scene, conflict scene, and frontline scene.
- Chapter 1 story with Budi and Yanto, followed by Battle 1.
- Choice 1: Stay at frontline (Nyali), open evacuation route (Harapan), or make a coordinated tactic (Gema).
- Option 3 contains a village overworld map; movement is restricted to the bright road paths and the player must find/interact with the kentongan.
- Battles 2, 3, and 4 branch from Choice 1.
- Chapter 2 with Sari and Putri.
- Choice 2: medicine run (Nyali), care for all injured (Harapan), or strengthen refugees (Gema).
- Battle 5: medicine objective while being chased.
- Battle 6: collect evacuation/rescue objectives while avoiding abstract hazards.
- Undertale-inspired UI: black screen, crisp white outlines, text box, name plaque, selectable choice boxes, battle arena, pixel heart.
- Dialog pages wrap text and paginate if it exceeds the text box.

## Controls
- Start: Enter or Space
- Dialog: Z, Enter, Space, or mouse click
- Choices: Up/Down or W/S; Enter/Space to confirm
- Village map: WASD/Arrow keys to walk, E to interact with kentongan, Enter after finding it
- Battle: WASD/Arrow keys to move
- Failed battle: Enter to retry

## Run
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Install Pygame: `python -m pip install pygame`
4. Run: `python main.py`

## Testing status
- Python syntax compile: checked.
- Asset paths: checked against included assets.
- Runtime test: not performed in this environment because Pygame is not installed here.

## Update: scrollable exploration map (v3)
- Choice 1 Option 3: Budi explores the supplied sepia Surabaya village landscape to find the kentongan. Camera scrolls horizontally; movement is WASD/arrow keys; E interacts; Enter continues once found.
- Battle 5: Sari explores the same landscape to collect 3 medicine packages. The map camera follows the player and packages are placed along the village road.
- Road-only movement: player collision checks the four corners against manually defined road bands on the landscape.
- Controls are continuous while keys are held (not only one-step keydown).


V4 visual fixes: alpha-safe sprite crop, larger map character, dialogue portrait integrated inside lower dialogue panel, compact scene inset, and kentongan branch dialogue uses village-map scene.
