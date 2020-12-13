import urllib3
import re
import os
import datetime
from babel.dates import format_date

from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

from config import *

# output templates
DATE_HEADER_TEMPLATE = 'E, dd/MM'
IDK = r'¯\_(ツ)_/¯'
OUTPUT_HEAD = r"""
<b><u>{date}</u></b>{vac_text}
"""
OUTPUT_RESHET = """<u>רשת (13)</u>
{reshet}
"""
OUTPUT_KESHET = """<u>קשת (12)</u>
{keshet}
"""
OUTPUT_KAN = """<u>כאן (11)</u>
{kan}
"""
OUTPUT_FOOTER = """{seperator}
"""
VACATION_TEXT = ' #חופש 🏖'

# precompile regex for efficiency
compiled_regex = re.compile(YES_EXTRACTION_REGEX)

# init pool manager
http = urllib3.PoolManager()


def get_program_emoji(program):
    """
    gets the given program emoji
    @param program: program to look for
    @return: emoji of the program or None if no emoji for this program
    """
    for prog_key in programs_emojis:
        if prog_key in program:
            return programs_emojis[prog_key]
    return None


def get_program(day, ch_code, query=None):
    """
    search for programs for given day in YES website
    supports additional string query
    return also if this is a vacation day, meaning - no program with predefined emoji on this day
    @param day: day of programs to search
    @param ch_code: channel code to search
    @param query: additional query to search for
    @return: output for relevant programs, is a vacation day
    """
    url = YES_URL.format(day, ch_code)
    html = http.request('GET', url).data.decode('utf-8')

    try:
        is_vac = True
        output = ''
        programs = compiled_regex.findall(html)
        for program in programs:
            if not query or query in program:
                emoji = get_program_emoji(program)
                output += program

                if emoji:
                    is_vac = False
                    output += ' ' + emoji

                output += '\n'

        return output[:-1], is_vac  # cut the last \n

    except Exception as e:
        # for every unknown failure, at least let's print something
        return IDK, True


def respond(update, days, query=None):
    """
    respond to user request
    @param update: update object, used for replying
    @param days: list of days to look for
    @param query: additional query to look for
    """
    # get special separator for special predefined users
    # default separator is an invisible character since telegram trim regular spaces
    user = update.to_dict()['message']['from']['username']
    seperator = users_seperators.get(user, '‎')

    final_output = ''
    for day in days:
        requested_date_object = datetime.date.today() + datetime.timedelta(days=day)
        requested_date_string = format_date(requested_date_object, DATE_HEADER_TEMPLATE, locale='he')

        keshet, is_vac_keshet = get_program(day, YES_CHANNELS_MAPPING['keshet'], query=query)
        reshet, is_vac_reshet = get_program(day, YES_CHANNELS_MAPPING['reshet'], query=query)
        kan, is_vac_kan = get_program(day, YES_CHANNELS_MAPPING['kan'], query=query)

        # if all channels returns a vacation, than this is a vacation day
        vac_text = VACATION_TEXT if all((is_vac_keshet, is_vac_reshet, is_vac_kan)) else ''

        if keshet or reshet or kan:
            # print header fir this day only if one of the channels had programs
            final_output += OUTPUT_HEAD.format(date=requested_date_string, vac_text=vac_text)

            # add each channel programs
            if reshet:
                final_output += OUTPUT_RESHET.format(reshet=reshet)
            if keshet:
                final_output += OUTPUT_KESHET.format(keshet=keshet)
            if kan:
                final_output += OUTPUT_KAN.format(kan=kan)

            final_output += OUTPUT_FOOTER.format(seperator=seperator)

    if not final_output:
        # if nothing was found nowhere, at least print something
        final_output = IDK

    update.message.reply_text(final_output, parse_mode='HTML')


def ma(update, context):
    """
    gets today's programs
    """
    return respond(update, [0])


def mahar(update, context):
    """
    gets tomorrow's programs
    """
    return respond(update, [1])


def hashavoa(update, context):
    """
    gets next 7 days programs
    """
    return respond(update, list(range(0, 7)))


def search_menu(update, context):
    """
    custom search for specific program in next 7 days
    support both inline args and conversation response
    """
    if context.args:
        respond(update, list(range(0, 7)), query=' '.join(context.args))
        return ConversationHandler.END
    update.message.reply_text('מה אתה רוצה לחפש נו?')
    return 0


def search_program(update, context):
    query = update.message.text
    respond(update, list(range(0, 7)), query=query)

    return ConversationHandler.END


def main():
    """
    Starts the bot.
    """
    # create updater and dispatcher
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # add handlers
    dp.add_handler(CommandHandler("ma", ma))
    dp.add_handler(CommandHandler("mahar", mahar))
    dp.add_handler(CommandHandler("hashavoa", hashavoa))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('search', search_menu)],
        fallbacks=[],

        states={
            0: [MessageHandler(Filters.text, search_program)],
        },
    )
    dp.add_handler(conv_handler)

    # Start the Bot!
    updater.start_webhook(listen="0.0.0.0",
                          port=int(os.environ.get('PORT', 5000)),
                          url_path=TOKEN)
    updater.bot.setWebhook(HEROKUAPP_URL + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
