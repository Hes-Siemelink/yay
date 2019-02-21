# Welcome to Yay!

Yay is a scripting language in YAML. It is readable and light and meant to automate simple tasks. You can use it to glue API requests, user input and file manipulation together.

_Note: Yay is a pre-alpha prototype. Anything can change at any moment._

**Main features**

 * Simple and readable scripting in YAML syntax
 * Lightweight reuse of HTTP calls and REST interaction patterns 
 * Store parameters outside your scripts and easily switch contexts
 * Store passwords and other secrets outside your script
 * Easy JSON and YAML processing with JSON path
 * Out-of-the-box user interaction to create wizards
 * Create DSLs on the fly 
 
License: Apache 2.0

## Simple yay: reuse your request

The starting point for Yay is to reuse HTTP requests that you would do off the command line but are too long to actually remember.

Suppose you have this request:

    $ http GET http://localhost:5000/recipes
    
You can save it in a YAML file and reuse it using Yay.

**File: list-recipes.yay**
```
Http GET:
  url:  http://localhost:5000
  path: /recipes
Print as JSON: ${result}
```
  
Invoke it using the `yay` command:

    $ yay list-recipes


## _Try it out!_

Yay is bundled with a test application. Start it with the following command

    $ python -m yay.test_server

Running the above example will give the following output:

```
$ yay list-recipes
[
  "Mango and coconut ice cream",
  "Ratatouille",
  "Meatballs"
]
```

For more examples, read the [Tutorial](doc/Tutorial.md)


## Installation

Yay is written in Python 3.6. So you will need to install Python 3.6 on your local machine (Please Google the current recommended way to do so) or use the supplied [Dockerfile](Dockerfile) to run Yay in a container.

Use the following command to install Yay locally:

    $ python setup.py install

Test it out with the following command:

    $ yay example/Hello

This should result in a friendly greeting:

    Hello from Yay!


## Development

Use the following command to install Yay locally and have changes in the Yay code immediately available:

    $ python setup.py develop
    
Run the tests with the following command:

    $ pytest -v
    
Most of the tests are written in Yay and can be found in the [test/yay](test/yay) directory.    
    

