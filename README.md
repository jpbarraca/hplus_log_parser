# hplus log parser

This script will parse either a `btsnoop` log or a Gadgetbridge log and will process all messages related to HPlus devices. If a message is known, its content will be interpreted.

If you know the meaning of other messages, please add the appropriate support and make a PR. They are much welcome.

## Requirements

* Python 2
* `btsnoop` from https://github.com/joekickass/python-btsnoop

## Usage:
```
python parse_hplus_log.py logfile
```
