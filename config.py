# update these
HEROKUAPP_URL = ''
TOKEN = ""

YES_URL = 'http://www.yes.co.il/content/YesChannelsHandler.ashx?action=GetDailyShowsByDayAndChannelCode&dayValue={}&dayPartByHalfHour=43&channelCode=CH{}'
YES_EXTRACTION_REGEX = r'(21:\d\d - .*?)</span>'  # catch only "primetime" programs, meaning - programs at 9:x pm
YES_CHANNELS_MAPPING = {
    'keshet': '34',
    'reshet': '36',
    'kan': '30',
}

programs_emojis = {
    'מירוץ':  '🏃‍♂️🏃‍♀️',
    'במסכה': '🎭🎤' ,
    'אהבה חדשה': '❤️🏨',
    r"נינג'ה": '🧗🥋',
    'שעת נעילה': '⏰🔐',
    'האח הגדול': '💩👁',
    'חזרות': '🎭🎭',
    'מאסטר שף': '🧑‍🍳🍅'
}

#example
users_seperators = {
    'mylover': '❤',
    'creator': r'👑',
    'thetroller': '🖕🏽'
}