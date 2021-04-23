# Shopee coin getter
![CI status](https://img.shields.io/badge/build-passing-brightgreen.svg)

Shopee coin getter is a script to collect daily shopee coins.
This version is only available for Chinese Traditionanl Shopee Website.

![alt text](https://raw.githubusercontent.com/joe159119/crawler_shopee/master/readme/overall-1.png)

## Preface
I saw [charlie0227](https://github.com/charlie0227)/[crawler_shopee](https://github.com/charlie0227/crawler_shopee) and thought it was great,
but after the Shopee website was updated, it became unavailable,
so I rewritten it to make it work normally.

## dependencies
    python==3.6
    selenium==3.8.0

## Installation
 [Docker](https://www.docker.com)

## Getting Started
    git clone https://github.com/joe159119/crawler_shopee.git
    cd crawler_shopee
    cp env.py.sample env.py

	Filled in your username and password in env.py

    text_username = "<your shopee username>"
    text_password = "<your shopee password>"
    cookie_name = "cookie.pkl"

## Usage

build a docker image and run it

    docker build -t shopee:latest .
    docker run --rm -v <your-path>/crawler_shopee:/code shopee sh -c "python main.py"

You'll need to enter SMS authenticate first time if used password to login

![alt text](https://raw.githubusercontent.com/joe159119/crawler_shopee/master/readme/SMS.png)

    Please Enter SMS code in 60 seconds:

## Auto run by Crontab(Ubuntu)

Entry Root's crontab settings

    sudo crontab -e

Add following line in crontab. When you set up finished, the program will auto running at a random time between a range. For example, "0 10 * * * sleep $[($RANDOM\%120)+1]m" will run it in 10:00am ~ 12:00am. You can change time yourself.

    0 10 * * * sleep $[($RANDOM\%120)+1]m && bash <your_file_path>/autorun.sh > <set_a_path_to_save_log_file>/cron.log 2>&1 &

You may need to add system enviroment argument like this:

    SHELL=/bin/bash
    PATH=/sbin:/bin:/usr/sbin:/usr/bin
    MAILTO=root

Change <your_file_path> to directory your autorun.sh exists. (Must be Absolute path)
Change <set_a_path_to_save_log_file> to directory you want to save the log file. You can named this file whatever you want. (Must be Absolute path)

## Method

__checkPopModal()__

Auto close the advertisement modal shopee show first time

__checkLogin()__

check is login or not

__loginByCookie()__

First, check your cookie is able to login, if success goto clickCoin

__loginByPass()__

Second, use your account and password to login

__checkSMS()__

Third, if you login by password first time, you'll need to pass SMS authenticate.

__clickCoin()__

Last, goto https://shopee.tw/shopee-coins to own your shopee daily coin after login.

## Known issues

Testing...

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Donate
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/paypalme/joe159119)
