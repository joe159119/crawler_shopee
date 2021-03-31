# Shopee coin getter
![CI status](https://img.shields.io/badge/build-passing-brightgreen.svg)

Shopee coin getter is a script to collect daily shopee coins.

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
    docker run -it --rm -v <your-path>/crawler_shopee:/code shopee sh -c "python main.py"
    
You'll need to enter SMS authenticate first time if used password to login

![alt text](https://raw.githubusercontent.com/joe159119/crawler_shopee/master/readme/SMS.png)

    Please Enter SMS code in 60 seconds: 

crontab

    0 0 * * * /usr/bin/docker run --rm -v <your-path>/crawler_shopee:/code shopee sh -c "python main.py" >/dev/null
    
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


## License

[MIT](https://choosealicense.com/licenses/mit/)

## Donate
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/paypalme/joe159119)
