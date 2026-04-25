# Testing Buddy Bird Game

## Overview
Buddy Bird is a Flappy Bird-style canvas game in a single HTML file (`buddy-bird.html`). It uses HTML5 Canvas for rendering and LocalStorage for persistence.

## How to Run
- Open `buddy-bird.html` directly in Chrome (file:// protocol works)
- Or use the Vercel preview deployment URL
- No build step, no dependencies, no server needed

## Testing Strategy

### Real-Time Gameplay Challenge
The game runs at 60fps with gravity pulling the bird down constantly. Manual click-by-click testing through computer-use tools is too slow (~5s between actions) to keep the bird alive. Use automated flapping via the browser console:

```javascript
// Start game and auto-navigate through pipes
resetGame();
gameState = 1; // STATE.PLAYING
window._autoFlap = setInterval(() => {
  if (gameState !== 1) { clearInterval(window._autoFlap); return; }
  let target = 250;
  for (let p of pipes) {
    if (p.x + 60 > bird.x - 20) {
      target = (p.gapTop + p.gapBottom) / 2;
      break;
    }
  }
  if (bird.y > target && bird.vy > -3) bird.vy = -7.5;
}, 33);
```

Stop auto-play with `clearInterval(window._autoFlap)` to let the bird die naturally.

### Key Variables to Check via Console
- `gameState` — 0=MENU, 1=PLAYING, 2=GAMEOVER
- `score` — pipes passed this round
- `coinCount` — coins collected this round
- `totalCoins` — lifetime coins (persisted)
- `highScore` — best score (persisted)
- `equippedSkin` — current skin ID
- `ownedSkins` — array of owned skin IDs
- `localStorage.getItem('buddyBirdSave')` — full persisted data JSON

### Shop Testing
- Shop button is on the canvas menu screen (purple button labeled "Shop")
- Clicking it opens an HTML overlay (`#shopOverlay`) with DOM elements
- To test purchases with specific coin amounts: `totalCoins = 100; saveSaveData();`
- 10 skins available: Classic (free), Sky Blue (15), Fire Red (20), Forest (20), Sunset (25), Royal (30), Sakura (30), Ice (35), Golden (50), Rainbow (100)

### Persistence Testing
- Data saved to `localStorage` key `buddyBirdSave`
- Refresh the page (F5) and verify bird color, coin count, and high score persist
- Console: `JSON.parse(localStorage.getItem('buddyBirdSave'))` to inspect saved data

### What to Test
1. Menu screen renders (title, bird, Shop button, coins display)
2. Gameplay mechanics (flap, gravity, pipes, scoring, coins)
3. Game Over screen (shows score, coins earned, best score)
4. Game state cycle (Menu → Playing → Game Over → Menu)
5. Shop: open, browse skins, buy, equip, insufficient coins rejection
6. Skin change reflected on bird (visual color change on canvas)
7. LocalStorage persistence across page refresh

## Devin Secrets Needed
None — this is a standalone HTML file with no backend or API keys.
