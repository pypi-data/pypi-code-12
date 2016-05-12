# coding: utf-8
from comum.forms.anexo import AnexoForm
"""
Views associadas aos anexos
"""


def criar_anexo(request,
                modelo_dono,
                id_dono,
                template="anexo/anexo_criado_sucesso.html",
                template_anexar="anexo/anexar_arquivo.html"):

    """
    Anexa um arquivo a um objeto 'dono'.
    """

    dono = get_object_or_404(modelo_dono, pk=id_dono)

    form = AnexoForm(request.POST or None, request.FILES or None)

    if form.is_valid():

        anexo = form.save(commit=False)
        anexo.objeto = dono
        anexo.save()

        return render(request, template, {"instancia": anexo, "pai": dono})
    else:
        return render(request, template_anexar, {"pai": dono,
                                                 "form": form})


def excluir_anexo(request,
                  id_anexo,
                  template="anexo/anexo_excluido_sucesso.html",
                  template_confirmacao="anexo/excluir_anexo.html"):

    """
    Exclui um anexo
    """

    anexo = get_object_or_404(Anexo, pk=id_anexo)

    if request.POST:

        return render(request, template, {"instancia": anexo})

    else:

        return render(request, template_confirmacao, {"instancia": anexo})
