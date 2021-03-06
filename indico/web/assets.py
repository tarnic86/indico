# -*- coding: utf-8 -*-
##
##
## This file is part of Indico
## Copyright (C) 2002 - 2013 European Organization for Nuclear Research (CERN)
##
## Indico is free software: you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Indico.  If not, see <http://www.gnu.org/licenses/>.


"""
This file declares all core JS/CSS assets used by Indico
"""
# stdlib imports
import os

# 3rd party libs
from webassets import Bundle, Environment

# legacy imports
from MaKaC.common.Configuration import Config


class PluginEnvironment(Environment):
    def __init__(self, plugin_name, plugin_dir, url_path):
        config = Config.getInstance()
        output_dir = os.path.join(config.getHtdocsDir(), 'build', plugin_name)

        super(PluginEnvironment, self).__init__(output_dir, url_path)

        self.append_path(os.path.join(plugin_dir, 'htdocs'), url=url_path)


indico_core = Bundle('js/indico/Core/Presentation.js',
                     'js/indico/Core/Data.js',
                     'js/indico/Core/Components.js',
                     'js/indico/Core/Auxiliar.js',
                     'js/indico/Core/Buttons.js',
                     'js/indico/Core/Effects.js',
                     'js/indico/Core/Interaction/Base.js',
                     'js/indico/Core/Widgets/Base.js',
                     'js/indico/Core/Widgets/Inline.js',
                     'js/indico/Core/Widgets/DateTime.js',
                     'js/indico/Core/Widgets/Menu.js',
                     'js/indico/Core/Widgets/RichText.js',
                     'js/indico/Core/Widgets/Navigation.js',
                     'js/indico/Core/Widgets/UserList.js',
                     'js/indico/Core/Dialogs/Popup.js',
                     'js/indico/Core/Dialogs/PopupWidgets.js',
                     'js/indico/Core/Dialogs/Base.js',
                     'js/indico/Core/Dialogs/Util.js',
                     'js/indico/Core/Dialogs/Users.js',
                     'js/indico/Core/Dialogs/PopupWidgets.js',
                     'js/indico/Core/Browser.js',
                     'js/indico/Core/Services.js',
                     'js/indico/Core/Util.js',
                     'js/indico/Core/Login.js',
                     'js/indico/Core/Dragndrop.js',
                     filters='rjsmin', output='indico_core_%(version)s.min.js')

indico_management = Bundle('js/indico/Management/ConfModifDisplay.js',
                           'js/indico/Management/RoomBooking.js',
                           'js/indico/Management/eventCreation.js',
                           'js/indico/Management/Timetable.js',
                           'js/indico/Management/AbstractReviewing.js',
                           'js/indico/Management/NotificationTPL.js',
                           'js/indico/Management/Registration.js',
                           'js/indico/Management/Contributions.js',
                           'js/indico/Management/Sessions.js',
                           'js/indico/Management/CFA.js',
                           'js/indico/Management/RoomBookingMapOfRooms.js',
                           'js/indico/Management/EventUsers.js',
                           filters='rjsmin', output='indico_management_%(version)s.min.js')

indico_room_booking = Bundle('js/indico/RoomBooking/MapOfRooms.js',
                             'js/indico/RoomBooking/BookingForm.js',
                             'js/indico/RoomBooking/RoomBookingCalendar.js',
							 'js/indico/jquery/multiselect.js',
                             filters='rjsmin', output='indico_room_booking_%(version)s.min.js')

indico_admin = Bundle('js/indico/Admin/News.js',
                      'js/indico/Admin/Scheduler.js',
                      'js/indico/Admin/Upcoming.js',
                      filters='rjsmin', output='indico_admin_%(version)s.min.js')

indico_timetable = Bundle('js/indico/Timetable/Filter.js',
                          'js/indico/Timetable/Layout.js',
                          'js/indico/Timetable/Undo.js',
                          'js/indico/Timetable/Base.js',
                          'js/indico/Timetable/DragAndDrop.js',
                          'js/indico/Timetable/Draw.js',
                          'js/indico/Timetable/Management.js',
                          filters='rjsmin', output='indico_timetable_%(version)s.min.js')

indico_collaboration = Bundle('js/indico/Collaboration/Collaboration.js',
                              filters='rjsmin', output='indico_collaboration_%(version)s.min.js')

indico_legacy = Bundle('js/indico/Legacy/Widgets.js',
                       'js/indico/Legacy/Dialogs.js',
                       'js/indico/Legacy/Util.js',
                       filters='rjsmin', output='indico_legacy_%(version)s.min.js')

indico_common = Bundle('js/indico/Common/Export.js',
                       'js/indico/Common/TimezoneSelector.js',
                       'js/indico/Common/Social.js',
                       'js/indico/Common/htmlparser.js',
                       filters='rjsmin', output='indico_common_%(version)s.min.js')

indico_materialeditor = Bundle('js/indico/MaterialEditor/Editor.js',
                               filters='rjsmin', output='indico_materialeditor_%(version)s.min.js')

indico_display = Bundle('js/indico/Display/Dialogs.js',
                        filters='rjsmin', output='indico_display_%(version)s.min.js')

indico_jquery = Bundle('js/indico/jquery/defaults.js',
                       'js/indico/jquery/global.js',
                       'js/indico/jquery/multiselect.js',
                        filters='rjsmin', output='indico_jquery_%(version)s.min.js')

indico_jquery_authors = Bundle('js/indico/jquery/authors.js',
                               filters='rjsmin', output='indico_jquery_authors_%(version)s.min.js')

indico_badges_js = Bundle('js/indico/Management/ConfModifBadgePosterPrinting.js',
                          filters='jsmin', output='indico_badges_%(version)s.min.js')

indico_badges_css = Bundle('css/badges.css',
                           filters='cssmin', output='indico_badges_%(version)s.min.css')


jquery = Bundle('js/jquery/underscore.js',
                'js/jquery/jquery.js',
                'js/jquery/jquery-ui.js',
                'js/jquery/jquery.form.js',
                'js/jquery/jquery.custom.js',
                'js/jquery/jquery.daterange.js',
                'js/jquery/jquery.form.js',
                'js/jquery/jquery.qtip.js',
                'js/jquery/jquery.dttbutton.js',
                'js/jquery/jquery.colorbox.js',
                'js/jquery/jquery.menu.js',
                'js/jquery/date.js',
                'js/jquery/jquery.multiselect.js',
                'js/jquery/jquery.colorpicker.js',
                'js/jquery/jquery-extra-selectors.js',
                'js/jquery/jquery.typewatch.js',
                'js/jquery/jquery.multiselect.filter.js',
                'js/jquery/jstorage.js',
                'js/jquery/jquery.watermark.js',
                filters='rjsmin', output='jquery_code_%(version)s.min.js')

presentation = Bundle('js/jquery/underscore.js',
                      'js/presentation/Core/Primitives.js',
                      'js/presentation/Core/Iterators.js',
                      'js/presentation/Core/Tools.js',
                      'js/presentation/Core/String.js',
                      'js/presentation/Core/Type.js',
                      'js/presentation/Core/Interfaces.js',
                      'js/presentation/Core/Commands.js',
                      'js/presentation/Core/MathEx.js',
                      'js/presentation/Data/Bag.js',
                      'js/presentation/Data/Watch.js',
                      'js/presentation/Data/WatchValue.js',
                      'js/presentation/Data/WatchList.js',
                      'js/presentation/Data/WatchObject.js',
                      'js/presentation/Data/Binding.js',
                      'js/presentation/Data/Logic.js',
                      'js/presentation/Data/Json.js',
                      'js/presentation/Data/Remote.js',
                      'js/presentation/Data/DateTime.js',
                      'js/presentation/Ui/MimeTypes.js',
                      'js/presentation/Ui/XElement.js',
                      'js/presentation/Ui/Html.js',
                      'js/presentation/Ui/Dom.js',
                      'js/presentation/Ui/Style.js',
                      'js/presentation/Ui/Extensions/Lookup.js',
                      'js/presentation/Ui/Extensions/Layout.js',
                      'js/presentation/Ui/Text.js',
                      'js/presentation/Ui/Styles/SimpleStyles.js',
                      'js/presentation/Ui/Widgets/WidgetBase.js',
                      'js/presentation/Ui/Widgets/WidgetPage.js',
                      'js/presentation/Ui/Widgets/WidgetComponents.js',
                      'js/presentation/Ui/Widgets/WidgetControl.js',
                      'js/presentation/Ui/Widgets/WidgetEditor.js',
                      'js/presentation/Ui/Widgets/WidgetTable.js',
                      'js/presentation/Ui/Widgets/WidgetField.js',
                      'js/presentation/Ui/Widgets/WidgetEditable.js',
                      'js/presentation/Ui/Widgets/WidgetMenu.js',
                      'js/presentation/Ui/Widgets/WidgetGrid.js',
                      filters='rjsmin', output='presentation_%(version)s.min.js')

ie_compatibility = Bundle('js/selectivizr.js',
                          filters='rjsmin', output='ie_compatibility_%(version)s.min.js')

moment = Bundle('js/moment/moment.js',
                'js/moment/lang/es.js',
                'js/moment/lang/fr.js',
                filters='rjsmin', output='moment_%(version)s.min.js')

base_js = Bundle(jquery, presentation, indico_jquery, moment, indico_core,
                 indico_legacy, indico_common)


def register_all_js(env):
    env.register('jquery', jquery)
    env.register('presentation', presentation)
    env.register('indico_core', indico_core)
    env.register('indico_management', indico_management)
    env.register('indico_roombooking', indico_room_booking)
    env.register('indico_admin', indico_admin)
    env.register('indico_timetable', indico_timetable)
    env.register('indico_legacy', indico_legacy)
    env.register('indico_common', indico_common)
    env.register('indico_collaboration', indico_collaboration)
    env.register('indico_materialeditor', indico_materialeditor)
    env.register('indico_display', indico_display)
    env.register('indico_jquery', indico_jquery)
    env.register('indico_authors', indico_jquery_authors)
    env.register('indico_badges_js', indico_badges_js)
    env.register('base_js', base_js)
    env.register('ie_compatibility', ie_compatibility)


def register_all_css(env, main_css_file):
    env.register('indico_badges_css', indico_badges_css)
    env.register('base_css', Bundle('css/{0}'.format(main_css_file),
                                    'css/category_display.css',
                                    'css/core.css',
                                    'css/dashboard.css',
                                    'css/buttons.css',
                                    'css/dialogs.css',
                                    'css/icons.css',
                                    'css/inputs.css',
                                    'css/tables.css',
                                    'css/toolbars.css',
                                    'css/lists.css',

                                    'css/calendar-blue.css',
                                    'css/jquery-ui.css',
                                    'css/jquery.qtip.css',
                                    'css/jquery.colorbox.css',
                                    'css/jquery-ui-custom.css',
                                    'css/jquery.colorpicker.css',
                                    'css/jquery.multiselect.filter.css',
                                    'css/jquery.multiselect.css',
                                    filters=('cssmin', 'cssrewrite'),
                                    output='base_%(version)s.min.css'))
