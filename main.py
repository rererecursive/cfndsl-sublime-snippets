import json
import os
import yaml

primitive_types = ['String', 'Boolean', 'JSON', 'Integer', 'Number']
field_count = 1

with open('resource_specification.json') as fh:
    spec = json.load(fh)
    spec['ResourceTypes'] = dict(sorted(spec['ResourceTypes'].items()))
    spec['PropertyTypes'] = dict(sorted(spec['PropertyTypes'].items()))

print("Collected %d resources." % len(spec['ResourceTypes']))

def main():
    definition = ''
    snippets = {}
    directory = 'snippets'

    for resource_name, properties in spec['ResourceTypes'].items():
        # Convert e.g.: AWS::EC2::SpotFleet -> EC2_SpotFleet
        name = '_'.join(resource_name.split('::')[1:])
        definition = '%s("${1:name}") do\n' % name
        definition += '\t# %s\n' % properties['Documentation']

        for property_name, property_fields in sorted(properties['Properties'].items()):
            definition += property_as_str(property_name, property_fields, resource_name)

        definition += "end\n"
        global field_count
        field_count = 1

        snippets[name] = create_snippet(definition, name, resource_name)

    print("Collected %d snippets." % len(snippets))

    try:
        os.makedirs(directory)
    except FileExistsError:
        pass # Directory already exists

    for filename, contents in snippets.items():
        with open(directory + '/' + filename + '.sublime-snippet', 'w') as fh:
            fh.write(contents)

    print("Wrote %d files in directory '%s'." % (len(snippets), directory))


def create_snippet(resource_definition, resource_name, original_resource_name):
    return """
<snippet>
\t<description>    %s</description>
\t<tabTrigger>%s</tabTrigger>
\t<scope> source.ruby </scope>
<content><![CDATA[
%s
]]></content>
</snippet>
""".strip() % (original_resource_name, resource_name, resource_definition.strip())


def property_as_str(property_name, property_fields, resource_name, tab_count=1):
    """
    A property can be:
        1. Key, PrimitiveType
        2. Key, [PrimitiveType]
        3. Key, ItemType
        4. Key, [ItemType]
    """
    global field_count
    tc = ('\t' * tab_count)
    is_list = False
    definition = ''

    if property_fields['Required']:
        optional = ''
    else:
        optional = ' # Optional'

    # 1. Key, PrimitiveType
    if 'PrimitiveType' in property_fields:
        field_count += 1
        return ('\t' * tab_count) + ('%s ${%d:%s}%s\n' % (property_name, field_count, property_fields['PrimitiveType'], optional))

    # 2. Key, [PrimitiveType]
    if 'PrimitiveItemType' in property_fields:
        field_count += 1
        if property_fields['Type'] == 'List':
            return ('\t' * tab_count) + ('%s [${%d:%s}]%s\n' % (property_name, field_count, property_fields['PrimitiveItemType'], optional))
        else:
            # The same as 1., but with a different key
            return ('\t' * tab_count) + ('%s ${%d:%s}%s\n' % (property_name, field_count, property_fields['PrimitiveItemType'], optional))

    # 4. Key, [ItemType]
    if 'Type' in property_fields and property_fields['Type'] in ('List', 'Map'):
        item_type = property_fields['ItemType']

        if property_fields['Type'] == 'List':
            is_list = True
    else:
        # 3. Key, ItemType
        item_type = property_fields['Type']

    # Fix 1: for some reason, the EMR docs define this property in a recursive way. Ignore it.
    if property_name == 'Configurations' and item_type == 'Configuration':
        field_count += 1
        return ('\t' * tab_count) + ('%s [${%d:%s}]%s\n' % (property_name, field_count, item_type, optional))

    # Fix 2: the spec's types all begin with "AWS::" except for "Tag" ...
    if item_type == 'Tag':
        prop_name = 'Tag'
    else:
        prop_name = '%s.%s' % (resource_name, item_type)

    # Recursively process the nested properties
    for name, fields in sorted(spec['PropertyTypes'][prop_name]['Properties'].items()):
        definition += property_as_str(name, fields, resource_name, tab_count+1)

    if is_list:
        return tc + ('%s [{%s\n%s\n%s}]\n' % (property_name, optional, definition.rstrip(), tc))
    else:
        return tc + ('%s {%s\n%s\n%s}\n' % (property_name, optional, definition.rstrip(), tc))


main()

# TODO: get the max length of each line for formatting purposes (i.e. printing '# Optional')
# TODO: provide a link to the AWS docs on hover
