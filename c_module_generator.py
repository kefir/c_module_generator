#!/usr/bin/python3
import sys
import tomli

N_SPACES = 4

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
    str_out += h_defines_generate(module_dict['defines'])
    str_out += h_types_generate(module_dict['types'])
    # h_interfaces_generate(toml_data['interfaces'])

    return str_out

def h_footer_generate():
    str_out = '#ifdef __cplusplus\n}\n#endif\n'

    return str_out

def h_types_generate(types_dict):
    for type_name in types_dict.keys():
        type_obj = types_dict[type_name]
        # TODO: doxygen
        str_out = 'typedef enum {\n'
        for item in type_obj.keys():
            str_out += '    {:s} = {:d},\n'.format(item, type_obj[item])
        str_out += '}} {:s};\n\n'.format(type_name)

    return str_out

def h_defines_generate(defines_dict):
    str_out = ''
    for define in defines_dict.keys():
        str_out += '#define {:s} {:}\n'.format(define, defines_dict[define])
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
    str_out += '    typedef struct {\n'
    str_out += inputs_generate(module_dict['inputs'], 1)
    str_out += '    } inputs;\n'
    str_out += '    typedef struct {\n'
    str_out += outputs_generate(module_dict['outputs'], 1)
    str_out += '    } outputs;\n'
    str_out += '}} {:s};\n\n'.format(module_dict['name'])

    return str_out

def h_file_generate(toml_data):
    out_str = h_header_generate(toml_data)
    out_str += h_module_def_generate(toml_data)
    # h_functions_generate(toml_data)
    out_str += h_footer_generate()

    return out_str

def c_file_generate(toml_data, filename):
    out_str = '' # c_header_generate(toml_data)

    return out_str

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
