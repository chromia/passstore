# passstore
Simple password manager without particular features.<br>
This project is for practice python&Git and an <a href="https://kivy.org/">kivy</a> example.

## feature
* Simple key-value store
* Data is encrypted by AES
* Password is not saved( enter at startup every time )

## dependency
* Python3
* <a href="https://kivy.org/">kivy</a>
* <a href="https://www.dlitz.net/software/pycrypto/pycrypto">pycrypto</a>

## usage
1. open app/base.kv with text editor, edit below code.
> font_name: 'meiryo.ttc'

    if you are using multi-byte language( e.g. Japanese, Chinese, Korean, etc... ),
    you may be replace 'meiryo.ttc' to your language compatible font
    ( 'simsum.ttc', 'malgun.ttf', etc... )<br>
    \* kivy does not have multi-language fonts.<br>
    if you are using single-byte language, remove this line. Then the app use default font 'Roboto'.

2. run passstore.py
> python passstore.py

## notes
tested only on the following environment  for now
* windows10
* python3.5.2
* kivy v1.10.1
* pycrypto 2.6.1
