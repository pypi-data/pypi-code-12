import psychic_disco


@psychic_disco.lambda_entry_point
def handler_two(event, context):
    print event
