version = '2016.05.06'
try: # For import from setup.py
    import supybot.utils.python
    supybot.utils.python._debug_software_version = version
except ImportError:
    pass
