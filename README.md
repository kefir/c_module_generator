# C boilerplate code generator

## What is this project and why it exists?
Often times when it is needed to create a class-like modules in C, programmers tend to write lots of boilerplate code: getter and setter functions, data structures and so on.

This project aims at replacing tidious and unproductive work with a work that matters:
 - Defining data structures, types, ennumerators and so on
 - Planning out interface functions
 - Planning out inputs and outputs
 - Writing logic

Target audience of this project are mainly embedded developers writing for RTOS.

### Used tech
It is written in Python and resulting modules themselves are defined using TOML.

### Styling
Resulting C files adhere to a pep8-like style.
 - Types are CamelCase
 - Functions and variables are snake_case
 - Definitions are CAPITALIZED_SNAKE_CASE

Using other styling may result in an ugly code.

## Configuration file structure
This repository contains module.toml - an example module definition.
This example creates a power relay module template with single control input and single output, containing state of the relay. Also there are diagnostics inputs that can be used to gather feedback from relay to determine the output.

```toml
name = "PowerRelay" # Desired module name
name_snake_case = "power_relay" # Temproary solution for providing snake_case styled name
description = "Power relay module with optional diagnostics" 
version = "1.0.0"

include.global = [ "stdint.h", "stdbool.h" ] # Includes that will be added to h-file with <>
include.user = [ ] # Optional project-scope includes
is_syncronous = true # Defines if module logic is intended to be time-dependant
run_interval_ms = 10 # Defines time interval
```

Following that are defines, types (as of now only enums are supported), interfaces (WIP) and inputs/outputs

### Defines
```toml
[defines]
ERROR_INTERVAL_MS = 250 # Desired arbitrary define
```

This will result in define like this:

```c
#define POWER_RELAY_ERROR_INTERVAL_MS 250
```

### Types
```toml
[types]
State = { OFF = 0, ON = 1, ERROR = 2 }
```

Gives

```c
typedef enum {
    POWER_RELAY_STATE_OFF = 0,
    POWER_RELAY_STATE_ON = 1,
    POWER_RELAY_STATE_ERROR = 2,
} PowerRelayState;
```

### Inputs and outputs
```toml
[inputs.enable] # Each input should be prefixed with `inputs.` for script to understand
type = "bool" # Defines variable type
init_value = "false" # Defines initial value that will be assigned to vaiable when running _init() function
description = "Relay enable request"
```

Outputs are devined similarly. If some inputs should be grouped within a struct following scheme should be used:

```toml
[inputs.diag.enable]
type = "bool"
init_value = "false"
description = "Diagnostics enable"

[inputs.diag.relay_enabled]
type = "bool"
init_value = "false"
description = "Relay enable diagnostics input"

[inputs.diag.current]
type = "uint16_t"
init_value = "0"
description = "Relay current ADC value"
```

## Limitations and roadmap
Currently only bare minimum code is generated. In the future generated code will include:
 - Pointer validity checks
 - Assignment of variables
 - Returning of values in OOP way
 - Basic syncronous checks
 - Addition of interfaces (aka callback function pointers)

## Usage
```bash
python3 c_module_generator.py [toml file] [desired module name]
```

## License
MIT
