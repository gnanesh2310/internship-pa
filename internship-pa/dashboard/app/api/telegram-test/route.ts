import { NextResponse } from 'next/server'

export async function POST() {
  const token = process.env.TELEGRAM_BOT_TOKEN
  const chatId = process.env.TELEGRAM_CHAT_ID ?? '8394802242'

  if (!token) {
    return NextResponse.json({ error: 'TELEGRAM_BOT_TOKEN not set' }, { status: 500 })
  }

  const message = `🤖 Test message from your Internship PA!

✅ Telegram is working correctly.
📱 You'll get morning reports here every day.
🔴 Manual action alerts will appear here instantly.

Dashboard is live! Let's get you that internship 🚀`

  const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chatId, text: message }),
  })

  if (!res.ok) {
    return NextResponse.json({ error: 'Telegram API failed' }, { status: 500 })
  }

  return NextResponse.json({ success: true })
}
