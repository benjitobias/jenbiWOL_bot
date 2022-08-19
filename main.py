import sys
import time
import json
import logging

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from wakeonlan import send_magic_packet

config_path = sys.argv[1]

print('Config path: ', config_path)

with open(config_path) as config_file:
    config = json.load(config_file)

BOT_TOKEN = config['bot_token']
CHAT_ID = int(config['chat_id'])
MACS = config['macs']

LOG_LEVEL = logging.INFO


class WolBot(object):
    def __init__(self):
        self.bot = telepot.Bot(BOT_TOKEN)
        self.log = logging.getLogger('jenbiWOL_bot')
        self.log.setLevel(LOG_LEVEL)

        self.log.info('[*] Started jenbiWOL_bot')

    def run_forever(self):
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query': self.on_callback_query}).run_as_thread()
        while 1:
            time.sleep(10)

    @staticmethod
    def gen_devices_keyboard():
        devices = []
        for name in MACS:
            text = name
            data = MACS[name]
            inline_kb = [InlineKeyboardButton(text=text, callback_data=data)]
            devices.append(inline_kb)

        return InlineKeyboardMarkup(inline_keyboard=devices)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if chat_id == CHAT_ID:
            keyboard = self.gen_devices_keyboard()
            self.bot.sendMessage(chat_id, 'Select device to WOL', reply_markup=keyboard)
        else:
            self.bot.sendMessage(CHAT_ID, 'Attempt to use WOL from %s' % msg["chat"])

    def on_callback_query(self, msg):
        query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
        self.log.info('WOL Request: ', msg['from'], query_data)
        if chat_id == CHAT_ID:
            send_magic_packet(query_data)
            self.bot.answerCallbackQuery(query_id, text='WOL packet sent')


def main():
    b = WolBot()
    b.run_forever()


if __name__ == '__main__':
    main()
