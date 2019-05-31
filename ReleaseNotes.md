# Yay Release Notes

## Yay 0.7 - May 31st, 2019

* BREAKING CHANGE: Renamed output variable from `${result}` to `${output}`. For backwards compatibility, ${result} is still stored but usage of it is deprecated. No longer supported:
 ** Setting ${result} explicitly / 'Result' command. Use 'Output' command that sets the `${output}` var directly.
 ** 'Expected result' is renamed to 'Expected output'

* BREAKING CHANGE: Renames 'item' in 'If' to 'object' so it aligns with 'equals'.

* Original recipes in the examples!

* Introduces `context.yay`. You can now invoke yay with a '-c context-name' command line option and it will populate variables from context.yay file in the same directory as the script.

* Allows composition of yay files.
  
  Adds 'Execute yay file' handler and automatically registers all yay files in the same directory as handlers.
  
  File names are transformed from 'kebab-case' to words. For example, 'Do-something-with-Yay.yay' is registered as 'Do something with Yay'
  
* Improves variable resolving to 'For each', 'Do' an if statements.

* Adds Arango support (tentative)

* Reads yay files from ~/.yay if not found in current directory

* List or dict variables in text are now rendered as YAML.

New commands:
* **Input** -- defines parameters and provides default values.
* **Output** -- simply sets the result.
* **Execute yay file** -- executes a file in the same directory
* **As** -- an alternative to 'Set variable' 
* **Assert that** -- assert with 'if' syntax
* **Merge** -- 
