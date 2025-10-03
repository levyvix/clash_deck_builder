# 🚀 QUICK START - See It Working in 60 Seconds!

## Step 1: Start Everything (10 seconds)

### Windows Users:
**Double-click this file**: `start-dev.bat`

### Mac/Linux Users:
```bash
# Terminal 1
cd backend && uv run uvicorn src.main:app --reload

# Terminal 2 (new window)
cd frontend && npm start
```

---

## Step 2: Open Browser (5 seconds)

Your browser should auto-open to: **http://localhost:3000**

If not, manually open: http://localhost:3000

---

## Step 3: See It Work! (45 seconds)

### You Should See:
```
┌─────────────────────────────────────────────────────┐
│  Clash Royale Deck Builder                         │
│  [Deck Builder] [Saved Decks]                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Filters:                    Deck Slots:           │
│  ┌──────────────┐           ┌───┬───┬───┬───┐     │
│  │ Name: [____] │           │ + │ + │ + │ + │     │
│  │ Elixir: [All]│           ├───┼───┼───┼───┤     │
│  │ Rarity: [All]│           │ + │ + │ + │ + │     │
│  │ Type: [All]  │           └───┴───┴───┴───┘     │
│  │ [Clear]      │           Avg Elixir: 0.0       │
│  └──────────────┘           [Save Deck]            │
│                                                     │
│  Card Gallery:                                     │
│  ┌────┬────┬────┬────┬────┬────┐                 │
│  │🃏  │🃏  │🃏  │🃏  │🃏  │🃏  │                 │
│  │Knight│Archer│Giant│...│...│...│                │
│  ├────┼────┼────┼────┼────┼────┤                 │
│  │🃏  │🃏  │🃏  │🃏  │🃏  │🃏  │                 │
│  └────┴────┴────┴────┴────┴────┘                 │
└─────────────────────────────────────────────────────┘
```

### Try This:
1. **Type "Knight"** in the Name filter → See only Knight cards
2. **Click on a card** → See "Add to Deck" button
3. **Click "Add to Deck"** → Card appears in first slot
4. **Add 7 more cards** → Watch average elixir update
5. **Click "Save Deck"** → Enter a name and save
6. **Click "Saved Decks"** → See your saved deck!

---

## ✅ What's Working

- 🎴 **109 Clash Royale cards** with images
- 🔍 **Filters**: Name, Elixir, Rarity, Type
- 🎯 **Deck Building**: Add/remove cards, 8-card limit
- ⭐ **Evolution Slots**: Mark up to 2 cards as evolution
- 💾 **Save Decks**: Save with custom names
- 📋 **Saved Decks**: Load, rename, delete
- 📱 **Responsive**: Works on desktop, tablet, mobile
- ⚠️ **Error Handling**: User-friendly error messages
- 🔔 **Notifications**: Success/error toasts

---

## 🎮 Quick Demo

### 1. Filter Cards (10 sec)
- Type "Knight" → See filtered results
- Select "3" from Elixir → See 3-elixir cards
- Click "Clear Filters" → See all cards

### 2. Build a Deck (20 sec)
- Click 8 different cards
- Click "Add to Deck" for each
- Watch the deck fill up
- See average elixir calculate

### 3. Evolution Slots (10 sec)
- Click a card in your deck
- Click "Toggle Evolution"
- See star badge (⭐) appear
- Try to add 3rd evolution → See error

### 4. Save & Load (15 sec)
- Click "Save Deck"
- Name it "My Deck"
- Click "Saved Decks" in nav
- Click "Load Deck"
- See your deck loaded!

---

## 🐛 Troubleshooting

### Backend Won't Start?
```bash
cd backend
uv install
uv run uvicorn src.main:app --reload
```

### Frontend Won't Start?
```bash
cd frontend
npm install
npm start
```

### Cards Not Loading?
1. Check backend is running: http://localhost:8000/health
2. Check frontend .env file has: `REACT_APP_API_BASE_URL=http://localhost:8000`
3. Check browser console for errors (F12)

### Port Already in Use?
```bash
# Kill process on port 3000 (Windows)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

---

## 📚 More Information

- **Full Testing Guide**: `frontend/TESTING_GUIDE.md`
- **Test Checklist**: `frontend/MANUAL_TEST_CHECKLIST.md`
- **Detailed Startup**: `START_APPLICATION.md`
- **Task Summary**: `TASK_15_COMPLETION_SUMMARY.md`

---

## ✨ That's It!

You should now see a fully functional Clash Royale Deck Builder!

**Enjoy!** 🎉

---

*Need help? Check the troubleshooting section above or open an issue.*
