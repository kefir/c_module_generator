#!/usr/bin/python3

import tomli

def toml_parse(filename):
    toml_data = None

    with open('module.toml') as file:
        content = file.read()
        toml_data = tomli.loads(content)
        file.close()

    return toml_data

def module_info_get(toml_data):
    if 'name' not in toml_data.keys():
        return None

    print('Module: {:s}\n  {:s}\n'.format(
        toml_data['name'],
        toml_data['description']
    ))

if __name__ == '__main__':
    toml_data = toml_parse('module.toml')
    module_info_get(toml_data)
