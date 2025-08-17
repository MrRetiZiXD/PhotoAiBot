import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from logic import FusionBrainAPI

TOKEN = "7570862810:AAHLnYjq6HzAF8LEe9h5XPQ4-NKCysO3ZYQ"
API_KEY = "2CD3909F6918E287A13414C3F44F5E19"
SECRET_KEY = "C2609E2C0D89645FE07B69DA92E40575"

fusion_brain = FusionBrainAPI(
    url='https://api-key.fusionbrain.ai/',
    api_key=API_KEY,
    secret_key=SECRET_KEY
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для генерации изображений с помощью ИИ.\n"
        "Просто напиши мне описание картинки, которую хочешь создать"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    user_id = update.message.from_user.id
    
    try:
        await update.message.reply_text(f"🖌️ Начинаю генерацию изображения...")
        
        pipeline_id = fusion_brain.get_pipeline()
        if not pipeline_id:
            await update.message.reply_text("Ошибка: не удалось получить pipeline ID")
            return
        
        task_id = fusion_brain.generate(user_prompt, pipeline_id)
        if not task_id:
            await update.message.reply_text("Ошибка: не удалось запустить генерацию")
            return
        
        await update.message.reply_text("⏳ Ожидайте, это может занять несколько минут...")
        image_data = fusion_brain.check_generation(task_id, attempts=15, delay=10)
        
        if not image_data:
            await update.message.reply_text("Ошибка: генерация не завершилась или произошла ошибка")
            return
        
        output_file = f"temp_{user_id}.png"
        fusion_brain.saveimage(image_data[0], output_file)
        
        with open(output_file, 'rb') as photo:
            await update.message.reply_photo(photo, caption=f"Вот ваше изображение по запросу: {user_prompt}")
        
        os.remove(output_file)
        
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

def main():
    print("Запуск бота...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()