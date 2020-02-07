import math
import os
import sublime
import sublime_plugin
from xml.dom import minidom

class CfndslListener(sublime_plugin.EventListener):
    def on_hover(self, view, point, hover_zone):
        selected_word = view.substr(view.word(point))
        filename = '%s.sublime-snippet' % selected_word
        directory = '/home/professor/.config/sublime-text-3/Packages/User/snippets'
        attributes = {}

        if filename in os.listdir(directory):
            doc = minidom.parse(directory + '/' + filename)
            items = doc.getElementsByTagName('attribute')

            # Convert the XML to a dictionary of: {name: type}
            for item in items:
                attr_name = item.attributes['name'].value
                attr_type = item.attributes['type'].value
                attributes[attr_name] = attr_type

        #print("attrs:", attributes)
        if attributes:
            self.show_popup(view, attributes, selected_word)

    def show_popup(self, view, resource_attributes, resource_name):
        text = '<b><u>%s</u></b><br>' % resource_name
        text += '<b>Outputs:</b><br>'

        # Calculate the longest item for formatting purposes.
        lengths = [len(k) + len(v) for k,v in resource_attributes.items()]
        longest = sorted(lengths)[-1]

        # Items have to be separated with a mixture of
        # whitespace and HTML nbsp.
        for attr_name, attr_type in sorted(resource_attributes.items()):
            diff = longest - (len(attr_name) + len(attr_type))
            if diff:
                spaces = '&nbsp; ' * math.ceil(diff/2)
                if diff % 2 == 0:
                    spaces = ' ' + spaces
            else:
                spaces = ' '
            text += ' %s%s<i>%s</i><br>' % (attr_name, spaces, attr_type)

        # TODO: show the popup on the line below the hovered line
        view.show_popup(text, on_navigate=print)
        #, <flags>, <location>, <max_width>, <max_height>, <on_navigate>, <on_hide>):
