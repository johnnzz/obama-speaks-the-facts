#!/usr/bin/env python3
import os
import requests
from flask import Flask, send_file, Response
from bs4 import BeautifulSoup
import time


app = Flask(__name__)


def get_fact():
    """
    get a fact

    gets a fact from unkno.com and returns it as a string
    """
    response = requests.get("http://unkno.com")

    soup = BeautifulSoup(response.content, "html.parser")
    facts = soup.find_all("div", id="content")

    return facts[0].getText().strip()


@app.route('/')
def please_wait():
    """
    print instructions, then redirect

    because we may have to try the server many times, ask the user to 
    wait, then redirect them to the route that will (eventually) give
    them a quote
    """
    # redirect in 3 seconds
    # use relative path to the "obama" route
    wait_msg = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
        <head>
        <meta content="text/html; charset=ISO-8859-1"
        http-equiv="content-type">
        <meta http-equiv="refresh" content="3; url=./obama" />
        <title></title>
        </head>
        <body>
        You've come to the right place to hear Obama speak gripping facts!
        &nbsp;Please wait while we find your fact. &nbsp;This may take
        a few minutes, hang on!<br>
        </body>
        </html>
        """
    return wait_msg


@app.route('/obama')
def home():
    """
    ask Obama to speak a fact
    """
    video = False
    while not video:
        # because the server is unreliable, try the server until you get a response
        # print a message so we can see that we're trying
        print("...trying server")
        # get a fact from the server
        fact = get_fact()
        # submit that quote to talkobamato.me
        response = requests.post("http://talkobamato.me/synthesize.py", {"input_text": fact, "allow_redirects": False})
        zoup = BeautifulSoup(response.content, "html.parser")
        # pull out the video.  only if we get a response will this evaluate
        # as True, and satisfy the while condition
        video = zoup.find("video")
        # don't hammer the server, wait for a few seconds
        time.sleep(2)
    # declare the fact that succeeded
    print("FACT:",fact)
    # extract the url info we need from the response
    tag = video.select("source")
    _, source, zype = str(tag[0]).split()
    source = source.split('"')[1]
    zype = zype.split('"')[1]
    # take the info and make a proper url ou tof it
    url = "http://talkobamato.me/{}".format(source)
    # declare our url
    print("URL IS",url)
    # build a page around the url to be a bit more user friendly
    page = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html><head><meta content="text/html; charset=ISO-8859-1"
        http-equiv="content-type">
        <title></title></head>
        <body>
        To hear Obama say "{}",&nbsp;<a href="{}"
        target="_top">click here</a>.
        </body>
        </html>
        """.format(fact, url)
    return page

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6787))
    app.run(host='0.0.0.0', port=port)
