from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": 'Nome do APP',
    "SITE_HEADER": 'Nome do APP',
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    # "DASHBOARD_CALLBACK": "admin_interface.views.dashboard_callback",
    "STYLES": [
        lambda request: static("css/admin_interface.min.css"),
    ],
    "SCRIPTS": [
        lambda request: static("../static/libs/jquery/jquery.min.js"),
        lambda request: static("../static/libs/masks/jquery.mask.min.js"),
        lambda request: static("js/admin_interface.min.js"),
    ],
    # "SIDEBAR": {
    #     "show_search": True,  # Search in applications and models names
    #     "show_all_applications": False,  # Dropdown with all applications and models
    #     "navigation": [
    #         {
    #             "separator": False,
    #             "collapsible": False,
    #             "items": [
    #                 {
    #                     "title": _("Dashboard"),
    #                     "icon": "dashboard", # Supported icon set: https://fonts.google.com/icons
    #                     "link": reverse_lazy("admin:index"),
    #                     # "permission": lambda request: request.user.is_superuser,
    #                 },
    #                 # {
    #                 #     "title": _("Perfil Profissional"),
    #                 #     "icon": "business_center",
    #                 #     "link": reverse_lazy("admin:person_professional_changelist"),
    #                 #     "permission":
    #                 #         lambda request: not request.user.is_superuser
    #                 #         and request.user.has_perm("person.view_professional"),
    #                 # },
    #             ],
    #         },
    #         {
    #             "title": _("Administração"),
    #             "separator": True,
    #             "collapsible": False,
    #             "items": [
    #                 {
    #                     "title": _("Users"),
    #                     "icon": "people",
    #                     "link": reverse_lazy("admin:auth_user_changelist"),
    #                     "permission": lambda request: request.user.is_superuser,
    #                 },
    #                 {
    #                     "title": _("Groups"),
    #                     "icon": "groups",
    #                     "link": reverse_lazy("admin:auth_group_changelist"),
    #                     "permission": lambda request: request.user.is_superuser,
    #                 },
    #             ],
    #         },
    #         # {
    #         #     "title": _("Agenda e serviços"),
    #         #     "separator": True,
    #         #     "collapsible": False,
    #         #     "items": [
    #         #         {
    #         #             "title": _("Calendário"),
    #         #             "icon": "event",
    #         #             "link": reverse_lazy("admin:schedule_calendar_changelist"),
    #         #             # "permission": lambda request: request.user.has_perm("schedule.view_service"),
    #         #         },
    #         #         {
    #         #             "title": _("Meus Serviços"),
    #         #             "icon": "work",
    #         #             "link": reverse_lazy("admin:schedule_service_changelist"),
    #         #             "permission": lambda request: request.user.has_perm("schedule.view_service"),
    #         #         },
    #         #         {
    #         #             "title": _("Serviços Únicos"),
    #         #             "icon": "event",
    #         #             "link": reverse_lazy("admin:schedule_treatment_changelist"),
    #         #             "permission": lambda request: request.user.has_perm("schedule.view_treatment"),
    #         #         },
    #         #         {
    #         #             "title": _("Servicos Recorrentes/Pacotes"),
    #         #             "icon": "event",
    #         #             "link": reverse_lazy("admin:schedule_package_changelist"),
    #         #             "permission": lambda request: request.user.has_perm("schedule.view_package"),
    #         #         },
    #         #     ],
    #         # },
    #         # {
    #         #     "title": _("Gestão de usuários"),
    #         #     "separator": True,
    #         #     "collapsible": False,
    #         #     "items": [
    #         #         {
    #         #             "title": _("Clientes"),
    #         #             "icon": "groups",
    #         #             "link": reverse_lazy("admin:person_client_changelist"),
    #         #             "permission": lambda request: request.user.is_superuser
    #         #         },
    #         #         {
    #         #             "title": _("Meus Clientes"),
    #         #             "icon": "groups",
    #         #             "link": reverse_lazy("admin:person_client_changelist"),
    #         #             "permission": 
    #         #                 lambda request: not request.user.is_superuser
    #         #                 and request.user.has_perm("person.view_client"),
    #         #         },
    #         #         {
    #         #             "title": _("Profissionais"),
    #         #             "icon": "groups",
    #         #             "link": reverse_lazy("admin:person_professional_changelist"),
    #         #             "permission":
    #         #                 lambda request: request.user.is_superuser
    #         #                 and request.user.has_perm("person.view_professional"),
    #         #         },
    #         #     ],
    #         # },
    #         # {
    #         #     "title": _("Financeiro"),
    #         #     "separator": True,
    #         #     "collapsible": False,
    #         #     "items": [
    #         #         {
    #         #             "title": _("Conf. cupons por indicação"),
    #         #             "icon": "settings",
    #         #             "link": reverse_lazy("admin:finances_indicationcouponconfiguration_changelist"),
    #         #             "permission": lambda request: request.user.has_perm("finances.view_indicationcouponconfiguration"),
    #         #         },
    #         #         {
    #         #             "title": _("Cupons de Desconto"),
    #         #             "icon": "confirmation_number",
    #         #             "link": reverse_lazy("admin:finances_discountcoupon_changelist"),
    #         #             "permission": lambda request: request.user.has_perm("finances.view_discountcoupon"),
    #         #         },
    #         #     ],
    #         # },
    #         # {
    #         #     "title": _(""),
    #         #     "separator": True,  # Top border
    #         #     "collapsible": False,  # Collapsible group of links
    #         #     "items": [
    #         #         {
    #         #             "title": _(""),
    #         #             "icon": "",
    #         #             "link": reverse_lazy("admin:finances_changelist"),
    #         #             "permission": lambda request: request.user.has_perm("finances.view_indicationcouponconfiguration"),
    #         #         },
    #         #     ],
    #         # },
    #     ],
    # },
}
