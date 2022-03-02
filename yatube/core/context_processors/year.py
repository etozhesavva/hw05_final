import datetime as dt


def year(request):
    """ Текущий год для футера """
    return {"year": dt.datetime.now().year}
