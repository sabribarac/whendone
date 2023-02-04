# whendone

Python package to notify you when your function is done through Telegram and/or Slack!

## Installation

```bash
$ pip install whendone
```

## Usage

---------
#### Telegram Example
---------

First create a bot through ``@BotFather``
Start a conversation with the bot, only once required, ``/start``.
Obtain the token and add it, see code below.
```python
  # Import library
  from whendone import WhenDone
  # Initialize
  notifier = WhenDone(telegram_token='XXXXXXXXXXX')
  
 
  # Add decorator to function
  @notifier.whendone
  def Test():
      print('Hello World')
  
  # Function call
  Test()
```

---------

#### Slack Example

---------
Browse to ``https://api.slack.com/apps`` create a new app from scratch, give it a name and assign it to a group or person. On the app page, browse to ``OAuth & Permissions``, go to Scope and the following scope, ``chat:write``, reinstall the app and obtain the ``token``. From slack open the chatbot, and obtain the ``id``

The code is almost the same to the Telegram example, but with the addition of 1 line.

---------

```python
  # Import library
  from whendone import WhenDone
  # Initialize
  notifier = WhenDone(slack_token='XXXXXXXXXXX')
  notifier.addSlackChatID('XXXXX')
 
  # Add decorator to function
  @notifier.whendone
  def Test():
      print('Hello World')
  
  # Function call
  Test()
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms. If you like it, don't forget to give it a ⭐!

## License

`WhenDone` was created by Sabri Barac. It is licensed under the terms of the MIT license.

