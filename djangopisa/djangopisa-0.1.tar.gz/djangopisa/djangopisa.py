from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import render_to_string
from django.http import HttpResponse


def render_to_pdf_response(template_name, context=None, filename="output.pdf"):
    # Generate HTML from the template
    source = render_to_string(template_name, context)

    # File like output object needed for pisa
    output_buffer = BytesIO()

    # Bake the pizza
    pisaStatus = pisa.CreatePDF(source, output_buffer)

    # Create the HttpResponse object with the appropriate PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    # Get the value of the BytesIO buffer and write it to the response
    pdf = output_buffer.getvalue()
    output_buffer.close()
    response.write(pdf)
    return response

