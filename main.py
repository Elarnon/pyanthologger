if __name__ == '__main__':
    import logging

    logging.warning(
        'You are runing the old `main.py` script to run pyanthologger. This '
        'will stop being supported in the future. Please switch to either '
        'installing the `pyanthologger` package, then run the `pyanthologger` '
        'command (preferred), or run it through `python -m pyanthologger`.'
    )

    import pyanthologger

    pyanthologger.main()
