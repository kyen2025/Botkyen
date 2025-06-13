
import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
)

PHOTO1, PHOTO2, PHOTO3, PIANI, NOTE = range(5)
DESTINATARIO_ID = 587193993

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Benvenuto nel bot per il preventivo cambio caldaia!"


        "Per favore, inviami una foto della caldaia (visibili muri dx, sx e sopra)."
    )
    return PHOTO1

async def photo1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo1'] = update.message.photo[-1].file_id
    await update.message.reply_text("Ora inviami una foto sotto al lavandino (scarico condensa).")
    return PHOTO2

async def photo2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo2'] = update.message.photo[-1].file_id
    await update.message.reply_text("Ora inviami una foto delle pareti perimetrali dove scarica la caldaia.")
    return PHOTO3

async def photo3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo3'] = update.message.photo[-1].file_id
    await update.message.reply_text("Quanti piani sono da intubare?")
    return PIANI

async def piani(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['piani'] = update.message.text
    await update.message.reply_text("Hai altri dettagli da aggiungere? Scrivili qui.")
    return NOTE

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['note'] = update.message.text

    text = (
        "📩 *Nuova richiesta preventivo caldaia:*"


        f"🧱 *Piani da intubare:* {context.user_data['piani']}"

        f"📝 *Note cliente:* {context.user_data['note']}"
    )
    await context.bot.send_message(chat_id=DESTINATARIO_ID, text=text, parse_mode="Markdown")

    for i in range(1, 4):
        await context.bot.send_photo(chat_id=DESTINATARIO_ID, photo=context.user_data[f'photo{i}'])

    await update.message.reply_text("Grazie! Abbiamo ricevuto tutte le informazioni.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Conversazione annullata.")
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHOTO1: [MessageHandler(filters.PHOTO, photo1)],
            PHOTO2: [MessageHandler(filters.PHOTO, photo2)],
            PHOTO3: [MessageHandler(filters.PHOTO, photo3)],
            PIANI: [MessageHandler(filters.TEXT & ~filters.COMMAND, piani)],
            NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, note)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
