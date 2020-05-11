# Yay Release Notes

## Yay 0.11 - unreleased

### BREAKING CHANGES

* Removes deprecated 'result' variable. Use `${output}` instead of `${result}`
* Removes deprecated 'For each' syntax. Use `${var}: [list]` assignment.
* Removes '!any' YAML syntax. Use 'in' operator for tests.

### New commands

* **Do in parallel** -- To divide work in parallel threads


## Yay 0.10 - April 24th, 2020

### BREAKING CHANGES
* Removes 'Name' command. Use 'Task' instead

### New commands

* **On Http request** -- Basic webhook support allows you to run Yay as a web server listening to requests.

### Features
* New **For each** syntax. Old syntax is deprecated but still works
* **For each** command returns a list of results
* Major refactoring of code base

## Yay 0.9 - February 21st, 2020

### BREAKING CHANGES
* Replaced `context.yay` with `yay-context.yaml` that has a different structure. 

Old `context.yay`:

    default:
      myvar: some value
    production:
      myvar: important
      
New `yay-context.yaml`:

    variables:
      myVar: some value
    
    path:
    - ~/yay-snippets
    
    dependencies:
      XL Release: 1.0
      
    profiles:
      production:
        variables:
           myVar: important

* Renamed command line option to select a different context profile from `-c` to `-p`.
* Data loaded with `Read file` no longer interprets `${...}` variable syntax in the file. 

### New commands

* **Apply variables** -- Substitutes variables in raw YAML, for when content was loaded from a file.

### Features

* Composability -- refer to scripts from a different directory by specifying them in the `path` section of the `yay-context.yaml` file.
* Basic package support -- decalre packages in the `dependencies` section of the `yay-context.yaml` file and Yay wil look for them in the  `~/.yay/packages` directory by specifying them in the 
* Properly supports JSONPath in `${...}` variable syntax 
* Supports loading files that contain `${...}` syntax unrelated to Yay variables and keeps them as 'raw' YAML
* Support for headers in HTTP commands
* Support for Basic Authentication in HTTP commands
* **Http endpoint** command now also takes nested arguments that serve as defaults for any HTTP command
* **Merge** command supports merging object with output variable


## Yay 0.8 - August 22nd, 2019

### New commands

* **Repeat** -- Introduces Repeat / until control structure
* **Wait** -- Wait for a number of seconds.

### Features

* Adds 'save as' property to Http commands that saves the result to a file.
* Removes Yaml warnings


## Yay 0.7 - May 31st, 2019

### BREAKING CHANGES

* Renamed output variable from `${result}` to `${output}`. For backwards compatibility, ${result} is still stored but usage of it is deprecated. No longer supported:
 ** Setting ${result} explicitly / 'Result' command. Use 'Output' command that sets the `${output}` var directly.
 ** 'Expected result' is renamed to 'Expected output'

* Renames 'item' in 'If' to 'object' so it aligns with 'equals'.

### New commands
* **Input** -- defines parameters and provides default values.
* **Output** -- simply sets the result.
* **Execute yay file** -- executes a file in the same directory
* **As** -- an alternative to 'Set variable' 
* **Assert that** -- assert with 'if' syntax
* **Merge** -- 

### Features

* Original recipes in the examples!

* Introduces `context.yay`. You can now invoke yay with a '-c context-name' command line option and it will populate variables from context.yay file in the same directory as the script.

* Allows composition of yay files.
  
  Adds 'Execute yay file' handler and automatically registers all yay files in the same directory as handlers.
  
  File names are transformed from 'kebab-case' to words. For example, 'Do-something-with-Yay.yay' is registered as 'Do something with Yay'
  
* Improves variable resolving to 'For each', 'Do' an if statements.

* Adds Arango support (tentative)

* Reads yay files from ~/.yay if not found in current directory

* List or dict variables in text are now rendered as YAML.

