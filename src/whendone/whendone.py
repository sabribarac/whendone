import time
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import List
import os


class NoAPIKeys(Exception):
    """Exception raised when the message text is too long."""

    def __init__(self, message):
        super().__init__(message)


class TelegramAPIError(Exception):
    """Exception raised when the Telegram API returns an error response."""

    def __init__(self, response):
        super().__init__(response.text)
        self.response = response
class SlackChatIDError(Exception):
    def __init__(self, response):
        super().__init__(response.text)
        self.response = response

class WhenDone:
    def format_time(self, seconds: float) -> str:
        '''Format the time to display
        Seconds will be converted to the right time.

        Parameters
        ----------
        seconds : float
            Amount of seconds the code did run.

        Returns
        ----------
        formatted_time : str
            Seconds formated to the right amount of time.

        Examples
        --------
            format_time(61)
        '''
        total_seconds = int(seconds)
        decimal_seconds = int((seconds - total_seconds) * 100)
        days = total_seconds // 86400
        remaining_seconds = total_seconds % 86400
        hours = remaining_seconds // 3600
        minutes = (remaining_seconds % 3600) // 60
        remaining_seconds = remaining_seconds % 60
        if days > 0:
            return "{} days {:02} hours {:02} minutes {:02}.{:02} seconds".format(
                days, hours, minutes, remaining_seconds, decimal_seconds
            )
        elif hours > 0:
            return "{} hours {:02} minutes {:02}.{:02} seconds".format(
                hours, minutes, remaining_seconds, decimal_seconds
            )
        elif minutes > 0:
            return "{} minutes {:02}.{:02} seconds".format(
                minutes, remaining_seconds, decimal_seconds
            )
        else:
            return "{}.{:02} seconds".format(remaining_seconds, decimal_seconds)

    def __init__(self, telegram_token: str = "", slack_token: str = "") -> None:
        '''Initiliaze class with token(s)

        Parameters
        --------
        telegram_token : str
            Telegram token obtained form BotFather

        slack_token : str
            Telegram token obtained form SlackAPI

        Examples
        --------
        notifier = WhenDone(telegram_token='xxx',slack_token='xxx')
        '''
        self.telegram_api_key = telegram_token or None
        self.client = WebClient(token=slack_token) if slack_token else None
        if not telegram_token and not slack_token:
            raise NoAPIKeys("Put a Telegram or Slack Token!")
        self.chat_ids = [] if slack_token else []

        # if telegram_token:
        #     self.telegram_api_key = telegram_token
        # else:
        #     self.telegram_api_key = None
        # if slack_token:
        #     self.client = WebClient(token=slack_token)
        #     self.chat_ids = []
        # else:
        #     self.client = None
        # if not telegram_token and not slack_token:
        #     raise NoAPIKeys("Put a Telegram or Slack Token!")
        self.__seturl__(telegram_token)

    def addSlackChatID(self, id: str) -> None:
        '''Add Slack Chat ID, to send the message(s) to.

        Parameters
        --------
        id : str
            Slack chat ID obtained from Slack

        Examples
        --------
        notifier = WhenDone(telegram_token='xxx',slack_token='xxx')
        notifier.addSlackChatID(id='X1234')
        '''
        self.chat_ids.append(id)
        self.chat_ids = list(set(self.chat_ids))

    def __seturl__(self, telegram_token) -> None:
        if telegram_token != None:
            self.url = f"https://api.telegram.org/bot{telegram_token}/"

    def __dump_to_txt__(self, chat_ids):
        '''Dump telegram chat ID's to a .txt file, because Telegram Bot
         will restart and forget the current ID's. This will retrieve them and 
         still succesfully send the message.

        Parameters
        --------
        chat_ids : json
            Telegram chat ID's obtained from Telegram
        '''
        ids = set()
        if os.path.exists("chat_ids.txt"):
            with open("chat_ids.txt", "r") as f:
                for line in f:
                    ids.add(line.strip().split(",")[0])
        with open("chat_ids.txt", "a") as f:
            for i in range(len(chat_ids["result"])):
                chat_id = str(chat_ids["result"][i]["message"]["chat"]["id"])
                username = chat_ids["result"][i]["message"]["chat"]["username"]
                if chat_id not in ids:
                    f.write(chat_id + "," + username)

    def __getchatid__(self) -> List[str]:
        '''Will retrieve the chat ID's retrieved from the chat-bot.

        Returns
        --------
        lst : List[str]
            Telegram chat ID's obtained from Telegram
        '''
        url = self.url + "getUpdates"
        chat_id = requests.get(url).json()
        lst = []
        print(chat_id)
        if 'result' in chat_id:
            self.__dump_to_txt__(chat_ids=chat_id)
        else:
            if os.path.exists("chat_ids.txt"):
                with open("chat_ids.txt", "r") as f:
                    for line in f:
                        lst.append(line.strip().split(",")[0])
                    lst = list(set(lst))
                    return lst
            else:
                return lst
        for i in range(len(chat_id["result"])):
            lst.append(chat_id["result"][i]["message"]["chat"]["id"])
        return lst

    def __send_message__(self, message) -> None:
        '''Will send the message through Telegram and/or Slack

        Parameters
        --------
        message : str
            The message to send
        '''
        if self.telegram_api_key:

            resp = None
            try:
                chat_id = self.__getchatid__()
                if len(chat_id) == 0:
                    raise NoAPIKeys('No chat id available.')
                for i in chat_id:
                    url = self.url + f"sendMessage?chat_id={i}&text={message}"
                    resp = requests.get(url)
                    resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise TelegramAPIError(resp) from e

        if self.client:

            try:
                if self.chat_ids:
                    for i in self.chat_ids:
                        response = self.client.chat_postMessage(channel=i, text=message)
                else:
                    raise SlackApiError(None, "No chat ID found.")
            except SlackApiError as e:
                raise SlackApiError(None, f"Error posting message to Slack: {e}, check if chat id is correct or token.") from e



    def whendone(self, func):
        """Wrapper for timing and sending the message through Slack/Telegram"""

        def wrapper(*args, **kwargs):
            excep = False
            keyExcep = False
            start_time = time.time()

            try:
                func(*args, **kwargs)
            except Exception as e:
                excep = True
            except KeyboardInterrupt:
                keyExcep = True

            end_time = time.time()
            msg = ""
            if keyExcep:
                msg = f"The function, {func.__name__}, is done! It took , {self.format_time(end_time-start_time)}, due to Keyboard Interrupt."
                keyExcep = False
            elif excep:
                msg = f"The function, {func.__name__}, is done! It took , {self.format_time(end_time-start_time)}, due to an Exception."
                excep = False
            else:
                msg = f"The function, {func.__name__}, is done! It took , {self.format_time(end_time-start_time)}."

            self.__send_message__(msg)

        return wrapper
