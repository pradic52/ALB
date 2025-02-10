from .utils import get_global_setting

def global_settings(request):
    return {
        'company_name': get_global_setting('company_name', 'Default Company Name'),
        'company_logo': get_global_setting('company_logo', 'default_logo.png'),
        'company_phone': get_global_setting('company_phone', '0000000000'),
        'currency': get_global_setting('currency', 'EUR'),
    }
