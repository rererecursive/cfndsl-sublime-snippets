import math
import os
import sublime
import sublime_plugin
import webbrowser
from xml.dom import minidom

class CfndslListener(sublime_plugin.EventListener):
    def on_hover(self, view, point, hover_zone):
        selected_word = view.substr(view.word(point))
        filename = '%s.sublime-snippet' % selected_word
        attributes = {}

        # Function pop-up
        directory = os.path.dirname(os.path.realpath(__file__)) + '/fn-snippets'

        if filename in os.listdir(directory):
            doc = minidom.parse(directory + '/' + filename)
            url = doc.getElementsByTagName('url')[0].firstChild.nodeValue.strip()
            example = doc.getElementsByTagName('example')[0].firstChild.nodeValue.strip()

            if '\n' in example:
                example = '<br>'.join(example.split('\n'))

            popup = self.construct_function_popup(selected_word, example, url)
            self.show_popup(popup, view, point)
            return

        # Resource pop-up
        directory = os.path.dirname(os.path.realpath(__file__)) + '/snippets'

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
            popup = self.construct_resource_popup(selected_word, attributes)
            self.show_popup(popup, view, point)

    def construct_function_popup(self, function_name, example, url):
        """Construct the function pop-up.

        Produces (unformatted):

            FnAnd
            -----
            Example:
                FnAnd(FnEquals(...), FnNot(...))
        """
        text = '<b><a href="%s"><u>%s</u></a></b> (Intrinsic function)<br><br>' % (url, function_name)
        text += '<b>Example:</b><br>'
        text += ' %s' % example

        return text


    def construct_resource_popup(self, resource_name, resource_attributes):
        """Construct the resource pop-up.

        Produces (unformatted):

            EC2_VPC
            -------
            Outputs:
                SomeOutput1    String
                SomeOutput2   [String]
        """
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

        return text

    def show_popup(self, popup, view, point):
        # Display the popup on the line below the cursor
        (row, col) = view.rowcol(point)
        view.show_popup(popup, max_width=700, on_navigate=open_url, location=view.text_point(row,col))

def open_url(href):
    webbrowser.open(href)
