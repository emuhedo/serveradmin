from serveradmin.api.decorators import api_function
from serveradmin.dataset.models import ServerType

@api_function(group='dataset')
def get_servertypes():
    """Returns a list of available servertypes"""
    return [stype.name for stype in ServerType.objects.all()]