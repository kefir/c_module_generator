#!/usr/bin/python3
import sys
import tomli

N_SPACES = 4
DEFAULT_FUNCTIONS = ['init', 'run']
TICK_FUNCTIONS = ['tick_advance']

def toml_parse(filename):
    toml_data = None

    with open(filename) as file:
        content = file.read()
        toml_data = tomli.loads(content)
        file.close()

    return toml_data

def h_header_generate(module_dict):
    # TODO: doxygen
    str_out = '#pragma once\n\n'
    str_out += '#ifdef __cplusplus\nextern "C" {\n#endif\n\n'
    for include in module_dict['include']['global']:
        str_out += '#include <{:s}>\n'.format(include)
    str_out += '\n'
    for include in module_dict['include']['user']:
        str_out += '#include "{:s}"\n'.format(include)
    str_out += h_defines_generate(module_dict)
    str_out += h_types_generate(module_dict)
    # h_interfaces_generate(toml_data['interfaces'])

    return str_out

def h_footer_generate():
    str_out = '#ifdef __cplusplus\n}\n#endif\n'

    return str_out

def h_types_generate(module_dict):
    types_dict = module_dict['types']
    for type_name in types_dict.keys():
        type_obj = types_dict[type_name]
        # TODO: doxygen
        str_out = 'typedef enum {\n'
        for item in type_obj.keys():
            str_out += '    {:s}_{:s}_{:s} = {:d},\n'.format(
                module_dict['name_snake_case'].upper(),
                type_name.upper(),
                item.upper(),
                type_obj[item]
            )
        str_out += '}} {:s}{:s};\n\n'.format(module_dict['name'], type_name)

    return str_out

def h_defines_generate(module_dict):
    str_out = ''
    defines_dict = module_dict['defines']
    for define in defines_dict.keys():
        str_out += '#define {:s}_{:s} {:}\n'.format(
            module_dict['name_snake_case'].upper(),
            define,
            defines_dict[define]
        )
    if module_dict['is_syncronous']:
        str_out += '#define {:s}_RUN_INTERVAL_MS {:d}\n'.format(
            module_dict['name_snake_case'].upper(),
            module_dict['run_interval_ms'],
        )
    str_out += '\n'
    return str_out


def inputs_generate(inputs_dict, indent=0):
    str_out = ''
    for input in inputs_dict.keys():
        is_var = ('type' in inputs_dict[input].keys())
        indent_str = ' ' * ((indent + 1) * N_SPACES)
        if is_var:
            str_out += '{:s}{:s} {:s}; /** {:s} */\n'.format(
                indent_str,
                inputs_dict[input]['type'],
                input,
                inputs_dict[input]['description']
            )
        else:
            str_out += '{:s}struct {{\n'.format(indent_str)
            str_out += inputs_generate(inputs_dict[input], (indent + 1))
            str_out += '{:s}}} {:s};\n'.format(indent_str, input)

    return str_out

def outputs_generate(outputs_dict, indent=0):
    str_out = ''
    for output in outputs_dict.keys():
        is_var = ('type' in outputs_dict[output].keys())
        indent_str = ' ' * ((indent + 1) * N_SPACES)
        if is_var:
            str_out += '{:s}{:s} {:s}; /** {:s} */\n'.format(
                indent_str,
                outputs_dict[output]['type'],
                output,
                outputs_dict[output]['description']
            )
        else:
            str_out += '{:s}struct {{\n'.format(indent_str)
            str_out += outputs_generate(outputs_dict[output], (indent + 1))
            str_out += '{:s}}} {:s};\n'.format(indent_str, output)

    return str_out

def h_module_def_generate(module_dict):
    str_out = 'typedef struct {\n'
    str_out += '    struct {\n'
    if module_dict['is_syncronous']:
        str_out += '        uint32_t systick; /** System tick */\n'
    str_out += inputs_generate(module_dict['inputs'], 1)
    str_out += '    } inputs;\n'
    str_out += '    struct {\n'
    str_out += outputs_generate(module_dict['outputs'], 1)
    str_out += '    } outputs;\n'
    str_out += '}} {:s};\n\n'.format(module_dict['name'])

    return str_out

def h_inputs_access_function_generate(inputs_dict, module_name, module_name_snake_case, parent=None):
    str_out = ''
    for input in inputs_dict.keys():
        is_var = ('type' in inputs_dict[input].keys())
        if is_var:
            parent_str = ''
            if parent is not None:
                parent_str = '{:s}_'.format(parent)
            str_out += 'void {:s}_{:s}{:s}_set({:s}* {:s}, {:s} {:s});\n'.format(
                module_name_snake_case,
                parent_str,
                input,
                module_name,
                module_name_snake_case,
                inputs_dict[input]['type'],
                input
            )
        else:
            str_out += h_inputs_access_function_generate(
                inputs_dict[input],
                module_name,
                module_name_snake_case,
                input
            )

    return str_out

def h_outputs_access_function_generate(outputs_dict, module_name, module_name_snake_case, parent=None):
    str_out = ''
    for output in outputs_dict.keys():
        is_var = ('type' in outputs_dict[output].keys())
        if is_var:
            parent_str = ''
            if parent is not None:
                parent_str = '{:s}_'.format(parent)
            str_out += '{:s} {:s}_{:s}{:s}_get({:s}* {:s});\n'.format(
                outputs_dict[output]['type'],
                module_name_snake_case,
                parent_str,
                output,
                module_name,
                module_name_snake_case
            )
        else:
            str_out += c_outputs_access_function_generate(
                outputs_dict[output],
                module_name,
                module_name_snake_case,
                output
            )

    return str_out

def h_access_functions_generate(module_dict):
    str_out = ''
    str_out += h_inputs_access_function_generate(
        module_dict['inputs'],
        module_dict['name'],
        module_dict['name_snake_case']
    )
    str_out += h_outputs_access_function_generate(
        module_dict['outputs'],
        module_dict['name'],
        module_dict['name_snake_case']
    )
    return str_out

def h_functions_generate(module_dict):
    str_out = ''

    for function in DEFAULT_FUNCTIONS:
        str_out += 'void {:s}_{:s}({:s}* {:s});\n'.format(
            module_dict['name_snake_case'],
            function,
            module_dict['name'],
            module_dict['name_snake_case'],
        )
    if module_dict['is_syncronous']:
        for function in TICK_FUNCTIONS:
            str_out += 'void {:s}_{:s}({:s}* {:s}, uint32_t systick);\n'.format(
                module_dict['name_snake_case'],
                function,
                module_dict['name'],
                module_dict['name_snake_case'],
            )

    str_out += h_access_functions_generate(module_dict)
    str_out += '\n'

    return str_out

def h_file_generate(toml_data):
    str_out = h_header_generate(toml_data)
    str_out += h_module_def_generate(toml_data)
    str_out += h_functions_generate(toml_data)
    str_out += h_footer_generate()

    return str_out

def c_header_generate(toml_data, filename):
    fname = filename.replace('.c','.h')
    str_out = '#include "{:s}"\n\n'.format(fname)

    return str_out

def c_inputs_access_function_generate(inputs_dict, module_name, module_name_snake_case, parent=None):
    str_out = ''
    for input in inputs_dict.keys():
        is_var = ('type' in inputs_dict[input].keys())
        if is_var:
            parent_str = ''
            if parent is not None:
                parent_str = '{:s}_'.format(parent)
            str_out += 'void {:s}_{:s}{:s}_set({:s}* {:s}, {:s} {:s})\n{{\n}}\n\n'.format(
                module_name_snake_case,
                parent_str,
                input,
                module_name,
                module_name_snake_case,
                inputs_dict[input]['type'],
                input
            )
        else:
            str_out += c_inputs_access_function_generate(
                inputs_dict[input],
                module_name,
                module_name_snake_case,
                input
            )

    return str_out

def c_outputs_access_function_generate(outputs_dict, module_name, module_name_snake_case, parent=None):
    str_out = ''
    for output in outputs_dict.keys():
        is_var = ('type' in outputs_dict[output].keys())
        if is_var:
            parent_str = ''
            if parent is not None:
                parent_str = '{:s}_'.format(parent)
            str_out += '{:s} {:s}_{:s}{:s}_get({:s}* {:s})\n{{\n}}\n\n'.format(
                outputs_dict[output]['type'],
                module_name_snake_case,
                parent_str,
                output,
                module_name,
                module_name_snake_case
            )
        else:
            str_out += c_outputs_access_function_generate(
                outputs_dict[output],
                module_name,
                module_name_snake_case,
                output
            )

    return str_out

def c_access_functions_generate(module_dict):
    str_out = ''
    str_out += c_inputs_access_function_generate(
        module_dict['inputs'],
        module_dict['name'],
        module_dict['name_snake_case']
    )
    str_out += c_outputs_access_function_generate(
        module_dict['outputs'],
        module_dict['name'],
        module_dict['name_snake_case']
    )
    return str_out

def c_functions_generate(toml_data):
    str_out = ''

    for function in DEFAULT_FUNCTIONS:
        str_out += 'void {:s}_{:s}({:s}* {:s})\n{{\n'.format(
            toml_data['name_snake_case'],
            function,
            toml_data['name'],
            toml_data['name_snake_case'],
        )
        str_out += '}\n\n'

    for function in TICK_FUNCTIONS:
        str_out += 'void {:s}_{:s}({:s}* {:s})\n{{\n'.format(
            toml_data['name_snake_case'],
            function,
            toml_data['name'],
            toml_data['name_snake_case'],
        )
        str_out += '}\n\n'

    str_out += c_access_functions_generate(toml_data)

    return str_out

def c_file_generate(toml_data, filename):
    str_out = c_header_generate(toml_data, filename)
    str_out += c_functions_generate(toml_data)
    return str_out

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:\n  python3 c_module_generate.py [toml file] [c/h pair name]')
    else:
        toml_data = toml_parse(sys.argv[1])
        if toml_data is not None:
            with open('{:s}.h'.format(sys.argv[2]), 'w+') as f:
                f.write(h_file_generate(toml_data))
                f.close()
            c_filename = '{:s}.c'.format(sys.argv[2])
            with open(c_filename, 'w+') as f:
                f.write(c_file_generate(toml_data, c_filename))
                f.close()
