import telebot
import requests
from flask import Flask, request
import os

TOKEN = "6505930792:AAHvjEQugqviVc1JudOV7TiUpqGsCb0VA5E"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

API_URL = "https://www.tikwm.com/api/"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🔉 Dùng lệnh /tiktok [link] để lấy thông tin video TikTok.")

@bot.message_handler(commands=['tiktok'])
def tiktok_info(message):
    try:
        args = message.text.split(" ", 1)
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Vui lòng gửi link TikTok sau lệnh /tiktok")
            return

        processing_msg = bot.reply_to(message, "⏳ Đang chờ xử lí...")

        url = args[1]
        params = {'url': url}
        response = requests.get(API_URL, params=params).json()

        if response.get("code") != 0:
            bot.edit_message_text("❌ Không thể lấy dữ liệu. Vui lòng thử lại!", message.chat.id, processing_msg.message_id)
            return

        data = response["data"]

        music_url = data.get("music", "Không có")
        title = data.get("title", "Không có tiêu đề")
        author = data["author"]["nickname"]
        region = data.get("region", "Không xác định")
        duration = data.get("duration", 0)
        likes = data.get("digg_count", 0)
        comments = data.get("comment_count", 0)
        shares = data.get("share_count", 0)
        views = data.get("play_count", 0)
        unique_id = data["author"].get("unique_id", "Không có ID")

        info_text = (
            f"👤 Người đăng: {author}\n"
            f"🎬 Tiêu đề: {title}\n"
            f"🌍 Khu vực: {region}\n"
            f"⏳ Thời lượng: {duration} giây\n"
            f"👍 Lượt thích: {likes}\n"
            f"💬 Bình luận: {comments}\n"
            f"🔄 Chia sẻ: {shares}\n"
            f"👀 Lượt xem: {views}\n"
            f"🆔 ID TikTok: {unique_id}\n"
            f"🎵 Nhạc nền: {music_url}"
        )

        bot.delete_message(message.chat.id, processing_msg.message_id)

        if "images" in data and isinstance(data["images"], list) and len(data["images"]) > 0:
            images = data["images"]
            media_group = [telebot.types.InputMediaPhoto(image) for image in images[:10]]
            media_group[0].caption = info_text
            bot.send_media_group(message.chat.id, media_group)
        else:
            video_url = data.get("play")
            bot.send_video(message.chat.id, video_url, caption=info_text)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {e}")

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

if __name__ == '__main__':
    bot.remove_webhook()
    host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if host:
        bot.set_webhook(url=f"https://{host}/{TOKEN}")
    else:
        print("WARNING: RENDER_EXTERNAL_HOSTNAME không tồn tại. Không set webhook tự động.")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
