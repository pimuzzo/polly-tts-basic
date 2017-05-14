# -*- coding: utf-8 -*-

import hashlib
import logging
import os
import os.path
import subprocess
import sys
from contextlib import closing
from tempfile import gettempdir

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError

from config import LEVEL, CACHE, VOICE, AWS_PROFILE, AWS_ACCESS_KEY_ID, AWS_SECRECT_ACCESS_KEY, AWS_REGION

if AWS_PROFILE:
    # create a client using the credentials and region defined in the AWS_PROFILE section of the AWS credentials and config files
    session = Session(profile_name=AWS_PROFILE)
    logging.info('using profile name: {0}'.format(AWS_PROFILE))
else:
    session = Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRECT_ACCESS_KEY,
                      region_name=AWS_REGION)
    logging.info('using without credentials and config files')

polly = session.client('polly')


def describe_voices(language_code):
    # example 'it-IT' useful to retrieve voices
    response = polly.describe_voices(LanguageCode=language_code)
    logging.info(response)


def calculate_hash(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()


def retrieve_audio(sentence):
    output_format = 'mp3'
    hash = calculate_hash('{0}-{1}'.format(VOICE, sentence))
    file_name = '{0}.{1}'.format(hash, output_format)
    output = os.path.join(gettempdir(), file_name)
    logging.info(output)

    if CACHE and os.path.isfile(output):
        return output

    # call AWS
    try:
        response = polly.synthesize_speech(Text=sentence, OutputFormat=output_format, VoiceId=VOICE)

    except (BotoCoreError, ClientError) as err:
        logging.error(err)

    # access the audio stream from the response
    if 'AudioStream' in response:
        with closing(response['AudioStream']) as stream:
            try:
                # open a file for writing the output as a binary stream
                with open(output, 'wb') as file:
                    file.write(stream.read())
                    return output
            except IOError as error:
                logging.error(error)
                return None
    logging.error('No AudioStream in response')
    return None


def play(sentence):
    output = retrieve_audio(sentence)
    if output:
        # play the audio using the platform's default player
        if sys.platform == 'win32':
            os.startfile(output)
        else:
            # the following works on Mac and Linux. (Darwin = mac, xdg-open = linux).
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
        subprocess.call([opener, output])


if __name__ == '__main__':
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(stream=sys.stdout, level=LEVEL, format=log_format)

    sentence = 'This is just an example'

    play(sentence)
