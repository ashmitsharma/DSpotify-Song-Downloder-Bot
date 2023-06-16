import html
import json
import logging
import traceback


from telegram import Update, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext

from app.telebot import donate, song, invalid_command, start, help_message, playlist, artist, album, search, sendMessageToAllUser, userCount, totalDownload

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to user"""

    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(
        msg="Exception while handling an update:", exc_info=context.error
    )

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update,
                                                Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode=ParseMode.HTML
    )

def create_app():
    updater = Updater("Your token here",use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('help', help_message, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('commands', help_message, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('cmd', help_message, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('comd', help_message, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('donate', donate, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('sendMsgToAllUser', sendMessageToAllUser, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('userCount', userCount, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('totaldownload', totalDownload, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('playlist', playlist, run_async=True, pass_job_queue=True,
                                                  pass_chat_data=True,))
    updater.dispatcher.add_handler(CommandHandler('artist', artist, run_async=True, pass_job_queue=True,
                                                  pass_chat_data=True,))
    updater.dispatcher.add_handler(CommandHandler('album', album, run_async=True, pass_job_queue=True,
                                                  pass_chat_data=True,))
    updater.dispatcher.add_handler(CommandHandler('search', search, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('song', search, run_async=True, pass_job_queue=True,
                                                  pass_chat_data=True,))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, song, pass_job_queue=True,
                                                  pass_chat_data=True, run_async=True))
    updater.dispatcher.add_handler(MessageHandler(Filters.command, invalid_command,
                                                  run_async=True))  # Filters out unknown commands
    #updater.dispatcher.add_error_handler(error_handler)
    # Filters out unknown messages.
    updater.start_polling()
    updater.idle()
