import TelegramBot from 'node-telegram-bot-api';

// 🔑 Ganti token di bawah dengan token bot kamu
const token = '8280734566:AAGUXsXtLuVNTko3rSgkOmRuu1fJsYFYUXQ';

// Buat bot dengan polling
const bot = new TelegramBot(token, { polling: true });

// Saat ada pesan masuk
bot.on('message', (msg) => {
  const chatId = msg.chat.id;
  const text = msg.text;

  console.log(`Pesan dari ${msg.from.username || msg.from.first_name}: ${text}`);

  // Balasan otomatis
  bot.sendMessage(chatId, `Kamu bilang: ${text}\n🤖 Ini balasan otomatis dari bot Node.js`);
});