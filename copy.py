WELCOME = """
Welcome to Miss Candy’s booking system.

This bot handles screening, deposits, and confirmations.
No back-and-forth chatting.

Tap /book to start.
"""

BOOK_INTRO = """
🖤 SCREENING REQUIRED 🖤

Reply to the next prompts clearly.
Incomplete info = no hold.
"""

ASK_BOOKING_TYPE = """
📌 Booking type?

Reply with:
1) incall
2) outcall
"""

ASK_DATETIME = """
🕒 What date & time?

Reply in one of these formats:
• 2026-02-02 09:30
• 02/02 9:30am

(Seattle time)
"""

ASK_DURATION = """
⏳ Duration?

Reply with:
• 1
• 1.5
• 2
• 3

(hours)
"""

ASK_SCREENING = """
📸 Screening

Reply with ONE message including:
• Name
• Age (21+)
• Selfie OR brief physical description
"""

DEPOSIT_POLICY = """
💰 DEPOSIT POLICY 💰

Deposits are REQUIRED for:
• ALL outcalls
• Incalls booked 6+ hours in advance

Same-day incalls under 6 hours may not require a deposit.
Time is NOT held without confirmation.
"""

DEPOSIT_REQUIRED = """
💰 DEPOSIT REQUIRED 💰

A deposit is required to hold this time.
Deposit amount: ${amount}

No deposit = no hold.
"""

DEPOSIT_INSTRUCTIONS = """
Send the deposit, then reply “sent”.

Once received, your appointment is confirmed.
"""

NO_DEPOSIT = """
✅ No deposit required for this booking.

If the slot is still open, you’ll be confirmed shortly.
"""

CONFIRMED = """
✅ Booking confirmed.

Final details will be sent closer to your time.
Please arrive clean, punctual, and discreet.
"""

RELEASED = """
⛔ No deposit received.

This time is no longer held.
You may restart with /book if availability allows.
"""

LAST_SLOT = """
⚠️ LAST AVAILABILITY ⚠️

One remaining opening.
Downtown hosting.

First confirmed deposit secures it.
"""

MORNING_PUSH = """
Good morning.

Limited early-morning availability before the day fills up.
"""

DISCLAIMER = """
Professional companionship only.
No illegal activity.
21+ only.
"""