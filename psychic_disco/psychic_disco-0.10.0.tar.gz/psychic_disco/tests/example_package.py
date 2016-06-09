import psychic_disco


@psychic_disco.lambda_entry_point
def handler(event, context):
    print event


@psychic_disco.api_method("GET", "/that/dirt/off/your/shoulder")
def hova(event, context):
    print event
