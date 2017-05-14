# Polly TTS basic

The aim of this project is to wrap and keep it simplest as possible Amazon's Polly API

The only dependency is the Amazon's SDK: `boto3`

## Configuration:
You need to take inspiration from `config_example.py` and create your own `config.py` file.

## How to use it:
```
>>> import polly
>>> polly.play('Hello world')
```

Any help (PR) is really appreciated
