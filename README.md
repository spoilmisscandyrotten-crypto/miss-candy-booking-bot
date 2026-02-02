Miss Candy Booking Bot (GitHub source of truth)

Features:
- Booking flow: incall/outcall -> time -> duration -> screening
- Deposit rules:
  - ALL outcalls require deposit
  - Incalls require deposit if booked 6+ hours in advance
- Deposit amount: $100 per hour
- Admin commands:
  - /myid (get your chat id)
  - /lastslot (admin broadcast)
  - /morning (admin broadcast)

Setup:
1) Create bot token in Telegram @BotFather
2) Paste token into config.py
3) Run on Replit/VPS