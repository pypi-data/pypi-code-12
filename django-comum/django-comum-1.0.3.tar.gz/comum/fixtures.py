# coding: utf-8
from comum.models import OperadoraTelefonia, TipoLinhaTempo
from django.utils.translation import ugettext as _


def criar_dominio_generico(modelo, codigo, valor):
    """
    Cria um registro em um determinado dominio
    """

    dominio = modelo()
    dominio.codigo = codigo
    dominio.valor = valor
    dominio.save()
    return dominio


def criar_dominio_ponderado_generico(modelo, codigo, valor, peso=1):
    dominio = modelo()
    dominio.codigo = codigo
    dominio.valor = valor
    dominio.peso = peso
    dominio.save()
    return dominio


def criar_tipo_linha_tempo_padrao():
    """
    Cria os registros padrão para tipo de linha do tempo
    """

    adicao = criar_dominio_generico(TipoLinhaTempo, "I", u"Adição")
    edicao = criar_dominio_generico(TipoLinhaTempo, "U", u"Edição")
    exclusao = criar_dominio_generico(TipoLinhaTempo, "D", u"Exclusão")


def criar_operadora(nome, codigo):
    """
    Cria um registro de uma operadora de telefonia
    """

    operadora = OperadoraTelefonia()
    operadora.nome = nome
    operadora.codigo = codigo
    operadora.save()
    return operadora


def criar_operadoras_padrao():
    """
    Cria os registros de operadora padrão
    """

    gente = criar_operadora("Gente Telecom", 10)
    liguemax = criar_operadora("Ligue Max", 11)
    ctbc = criar_operadora("CTBC", 12)
    fonar = criar_operadora("Fonar", 13)
    brasil_telecom = criar_operadora("Brasil Telecom", 14)
    vivo = criar_operadora("Vivo", 15)
    viacom = criar_operadora("Viacom", 16)
    transit = criar_operadora("Transit Telecom", 17)
    spin = criar_operadora("Spin", 18)
    epsilon = criar_operadora("Epsilon", 19)
    embratel = criar_operadora("Embratel/NET/Claro", 21)
    intelig = criar_operadora("Intelig", 23)
    primeira = criar_operadora("Primeira Escolha", 24)
    gvt = criar_operadora("GVT", 25)
    idt = criar_operadora("IDT", 26)
    aerotech = criar_operadora("Aerotech", 27)
    alpamayo = criar_operadora("Alpamayo", 28)
    oi = criar_operadora("Oi", 31)
    convergia = criar_operadora("Convergia", 32)
    teledados = criar_operadora("Teledados", 34)
    easytone = criar_operadora("Easytone", 35)
    dsli = criar_operadora("DSLI", 36)
    golden = criar_operadora("Golden Line", 37)
    viper = criar_operadora("Viper", 38)
    tim = criar_operadora("TIM", 41)
    gtg = criar_operadora("GT Group", 42)
    sercomtel = criar_operadora("Sercomtel", 43)
    global_cross = criar_operadora("Global Crossing (impsat)", 45)
    hoje = criar_operadora("Hoje", 46)
    btcom = criar_operadora("BT Comunications", 47)
    plenna = criar_operadora("Plenna", 48)
    cambridge = criar_operadora("Cambridge", 49)
    c51 = criar_operadora("51", 51)
    linknet = criar_operadora("Linknet", 52)
    ostara = criar_operadora("Ostara", 53)
    telebit = criar_operadora("Telebit", 54)
    espas = criar_operadora("Espas", 56)
    itaceu = criar_operadora("ITACEU", 57)
    voitel = criar_operadora("Voitel", 58)
    nexus = criar_operadora("Nexus", 61)
    ots = criar_operadora("OTS", 62)
    hello_brazil = criar_operadora("Hello Brazil", 63)
    neo = criar_operadora("Neo Telecom", 64)
    cgb = criar_operadora("CGB VOIP", 65)
    redevox = criar_operadora("Redevox", 69)
    dollar = criar_operadora("Dollarphone", 71)
    locaweb = criar_operadora("Locaweb", 72)
    vipway = criar_operadora("Vipway", 75)
    smart = criar_operadora("SmartTelecom/76Telecom", 76)
    sermatel = criar_operadora("Sermatel", 81)
    bbt = criar_operadora("BBT Brasil", 84)
    america = criar_operadora("America Net", 85)
    hit = criar_operadora(u"Hit Telecomunicações", 87)
    konecta = criar_operadora("Konecta", 89)
    falkland = criar_operadora("Falkland", 91)
    nebracam = criar_operadora("Nebracam", 95)
    amigo = criar_operadora("Amigo", 96)
    alpha = criar_operadora("Alpha Nobilis", 98)
