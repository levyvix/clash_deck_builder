# Quick Start Guide - See It Working!

## Step 1: Start the Backend

Open a **new terminal window** and run:

```bash
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
Starting Clash Royale Deck Builder API v1.0.0
Database connection pool initialized
INFO:     Application startup complete.
```

**Test it**: Open http://localhost:8000 in your browser
- You should see: `{"message":"Welcome to Clash Royale Deck Builder API","version":"1.0.0","status":"healthy"}`

**Test health**: Open http://localhost:8000/health
- You should see database status and health information

**Test cards API**: Open http://localhost:8000/cards
- You should see a list of Clash Royale cards with images

---

## Step 2: Start the Frontend

Open a **second terminal window** and run:

```bash
cd frontend
npm start
```

You should see:
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

The browser should automatically open to http://localhost:3000

---

## Step 3: See It Working!

### What You Should See:

1. **Deck Builder Page** (default page)
   - Navigation bar at top with "Deck Builder" and "Saved Decks" links
   - Card gallery showing all Clash Royale cards with images
   - Filter controls on the left/top:
     - Name search box
     - Elixir cost dropdown
     - Rarity dropdown
     - Type dropdown
     - Clear Filters button
   - Deck slots (8 empty slots) showing dashed borders with "+" icons
   - Average Elixir display showing "0.0"
   - Save Deck button (disabled until 8 cards added)

2. **Try These Actions**:

   ✅ **Filter Cards**:
   - Type "Knight" in the name filter → Only Knight cards show
   - Select "3" from elixir cost → Only 3-elixir cards show
   - Select "Epic" from rarity → Only Epic cards show
   - Click "Clear Filters" → All cards show again

   ✅ **Build a Deck**:
   - Click on any card in the gallery
   - Click "Add to Deck" button
   - Watch the card appear in the first deck slot
   - Add 7 more cards (total 8)
   - Watch the average elixir update in real-time
   - Try to add a 9th card → You'll see "Deck is full" error

   ✅ **Manage Deck Slots**:
   - Click on a card in your deck
   - Click "Remove from Deck" → Slot becomes empty
   - Click on a card in your deck
   - Click "Toggle Evolution" → Star badge (⭐) appears
   - Try to toggle evolution on 3 cards → Error after 2nd

   ✅ **Save Your Deck**:
   - Build a complete deck (8 cards)
   - Click "Save Deck" button
   - Enter a name like "My First Deck"
   - Click Save
   - See success notification: "Deck saved successfully!"

   ✅ **View Saved Decks**:
   - Click "Saved Decks" in navigation
   - See your saved deck with:
     - Deck name
     - 8 card thumbnails
     - Average elixir
     - Card count (8/8)
   - Click "Load Deck" → Returns to builder with deck loaded
   - Click "Rename" → Edit the name inline
   - Click "Delete" → Confirmation dialog appears

---

## Step 4: Test Responsive Design

### Desktop View (Current)
- Card gallery: 6 columns
- Deck slots: 2 rows of 4
- All controls visible

### Tablet View
1. Open browser DevTools (F12)
2. Click the device toolbar icon (or Ctrl+Shift+M)
3. Select "iPad" or set to 768x1024
4. See card gallery adjust to 4 columns

### Mobile View
1. In DevTools, select "iPhone SE" or set to 375x667
2. See card gallery adjust to 2 columns
3. Deck slots stack or adjust for mobile
4. Filters stack vertically

---

## Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: 
```bash
cd backend
uv install
```

**Error**: `Database connection failed`
**Solution**: Check if MySQL is running:
```bash
# Windows
net start MySQL80

# Or check docker-compose
docker-compose ps
```

### Frontend Won't Start

**Error**: `Cannot find module 'react'`
**Solution**:
```bash
cd frontend
npm install
```

**Error**: `Port 3000 is already in use`
**Solution**: Kill the process or use a different port:
```bash
# Kill process on port 3000 (Windows)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or start on different port
set PORT=3001 && npm start
```

### Cards Not Loading

**Error**: Network error or "Cannot connect to server"
**Solution**:
1. Check backend is running on port 8000
2. Check `.env` file in frontend has:
   ```
   REACT_APP_API_BASE_URL=http://localhost:8000
   ```
3. Check browser console for CORS errors
4. Verify backend CORS settings allow localhost:3000

### No Cards in Database

**Solution**: The backend should fetch cards from Clash Royale API automatically. If not:
1. Check backend logs for API errors
2. Verify Clash Royale API key is configured
3. Check database has cards table populated

---

## Quick Demo Script

Follow this 2-minute demo to see all features:

1. **Start** (0:00)
   - Open http://localhost:3000
   - See card gallery load

2. **Filter** (0:15)
   - Type "Knight" → See filtered results
   - Clear filters

3. **Build Deck** (0:30)
   - Click 8 different cards
   - Click "Add to Deck" for each
   - Watch average elixir update

4. **Evolution** (1:00)
   - Click deck slot 1
   - Toggle evolution → See star badge
   - Click deck slot 2
   - Toggle evolution → Works
   - Try slot 3 → Error (max 2)

5. **Save** (1:20)
   - Click "Save Deck"
   - Name it "Demo Deck"
   - See success notification

6. **Saved Decks** (1:40)
   - Click "Saved Decks" nav link
   - See your deck listed
   - Click "Load Deck"
   - See deck loaded in builder

7. **Done!** (2:00)

---

## What's Working

✅ All 109 Clash Royale cards display with images  
✅ Card filtering by name, elixir, rarity, type  
✅ Deck building with 8-card limit  
✅ Evolution slot management (max 2)  
✅ Real-time average elixir calculation  
✅ Deck saving with custom names  
✅ Saved decks list with load/rename/delete  
✅ Error handling and notifications  
✅ Responsive design (desktop/tablet/mobile)  
✅ Loading states and error messages  
✅ Navigation between pages  
✅ Rarity color coding  
✅ Image fallback handling  

---

## Next Steps

After seeing it work:
1. ✅ Follow MANUAL_TEST_CHECKLIST.md for comprehensive testing
2. ✅ Test all 130+ test cases
3. ✅ Test on multiple browsers
4. ✅ Test responsive design
5. ✅ Mark Task 15 as complete

---

## Need Help?

- Backend not starting? Check `backend/README.md`
- Frontend issues? Check `frontend/README.md`
- API errors? Check `docs/api.md`
- Testing questions? Check `frontend/TESTING_GUIDE.md`

**Enjoy exploring the Clash Royale Deck Builder!** 🎮⚔️
