"""PastaSauce initialization for SauceLabs."""

try:
    from .pastasauce import PastaSauce, PastaDecorator
except ImportError:
    try:
        from pastasauce import PastaSauce, PastaDecorator
    except ImportError:
        try:
            from pastasauce.pastasauce import PastaSauce, PastaDecorator
        except:
            raise

a = PastaSauce
b = PastaDecorator
