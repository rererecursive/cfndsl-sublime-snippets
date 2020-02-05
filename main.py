import yaml

types = ['String', 'Boolean', 'JSON', 'Integer', 'Number']
field_count = 1

with open('types.yaml') as fh:
    contents = yaml.load(fh, Loader=yaml.FullLoader)


def main():
    output = ''

    for resource, properties in contents['Resources'].items():
        # Convert: AWS::EC2::SpotFleet -> EC2_SpotFleet
        name = '_'.join(resource.split('::')[1:])
        output = '%s("${1:name}") do\n' % name

        # (property, type)
        for prop in properties['Properties'].items():
            # print("Processing", name, prop)
            output += field_as_str(prop)

        output += "end\n"
        global field_count
        field_count = 1
        print(output)


def field_as_str(field, tab_count=1):
    """
    I need a way to process the (key, value) recursively, and to add the appropriate tab width
    A Field can be:
      1. Key, Type
      2. Key, [Type]
      3. Key, Field
      4. Key, [Field]
    """
    global field_count
    field_count += 1
    is_list = False
    # print("Field", field)
    key, value = field

    # 1. Key, Type
    if value in types:
        # print("1.")
        return ('\t' * tab_count) + ('%s ${%d:%s}\n' % (key, field_count, value))

    # 2. Key, [Type]
    if type(value) == list and value[0] in types:
        # print("2.")
        return ('\t' * tab_count) + ('%s [${%d:%s}]\n' % (key, field_count, value[0]))

    # 3. Key, [Field]
    if type(value) == list:
        # print("3.")
        is_list = True
        value = value[0]
    # else:
        # print("4.")

    # 4. Key, Field
    output = ''
    tc = ('\t' * tab_count)
    nested_field = contents['Types'][value]

    if type(nested_field) != dict:
        output += field_as_str((value, nested_field), tab_count+1)
    else:
        for nf in nested_field.items():
            output += field_as_str(nf, tab_count+1)

    if is_list:
        return tc + ('%s [{\n%s\n%s}]\n' % (key, output, tc))
        # return tc + ('%s [{%s}]\n' % (key, output))
    else:
        return tc + ('%s {\n%s\n%s}\n' % (key, output, tc))


main()

# TODO: get the max length of each line for formatting purposes (i.e. printing '# Optional')
