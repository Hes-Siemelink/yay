# Welcome to Yay!

Yay is a scripting language in YAML. It is readable and light and meant to automate simple tasks. You can use it to glue API requests, user input and file manipulation together.

**Main features**

 * Simple and readable scripting in YAML syntax
 * Lightweight reuse of HTTP calls and REST interaction patterns 
 * Store parameters outside your scripts and easily switch contexts
 * Store passwords and other secrets outside your script
 * Easy JSON and YAML processing with JSON path
 * Out-of-the-box user interaction to create wizards
 * Create DSLs on the fly 
 
License: Apache 2.0

_Note: Yay is a pre-alpha prototype. Anything can change at any moment._

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
Print as JSON: ${output}
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

For more examples, read the [Tutorial](doc/Tutorial.md).

For a more detailed look at Yay code, take a look at the [test/yay](test/yay) directory, containing the Yay unit tests -- written in Yay of course.


## Installation

Yay is written in Python 3.7. So you will need to install Python 3.7 on your local machine (Please Google the current recommended way to do so) or use the supplied [Dockerfile](Dockerfile) to run Yay in a container.

Use the following command to install Yay locally:

    $ python setup.py install

Test it out with the following command:

    $ yay example/Hello

This should result in a friendly greeting:

    Hello from Yay!


## Yay directory

Create a directory `.yay` in your home folder to store defaults.

### default-variables.yaml

The `default-variables.yaml` file contains default variables. Useful for server endpoints and passwords. By storing server addresses and passwords in this file, you don't have to hardcode them in your scripts.

Example:

    exampleUrl: http://user:pass@example.com:5000
    exampleEndpoint:
        url: http://example.com
        username: user
        password: pass
        headers:
            X-My-Header: Header value

In a Yay script you would be able to refer to `${exampleUrl}` or `${exampleEndpoint}` respectively

    Http endpoint: ${exampleEndpoint}
    Http GET: /hello

    
### Default scripts

Any script that in the `~/.yay` directory can be called directly from Yay. For example, by creating `.yay/Hello.yay`, you can invoke 

    $ yay Hello

from any directory.

## Development

Use the following command to install Yay locally and have changes in the Yay code immediately available:

    $ python setup.py develop
    
Run the tests with the following command:

    $ pytest -v
    
Most of the tests are written in Yay and can be found in the [test/yay](test/yay) directory.    
    

## Releasing a new version

First, check the version in `setup.py` and make sure it is correct. 
Also make sure all files are committed to Git.

Create a local installaion

    $ python setup.py install
    
Tag latest commit with the version that was produced, e.g. `yay-0.11`.

To create the Dockerfile, run the following command, then tag the image and upload it to Dockerhub

    $ docker build .
    $ docker tag <IMAGE_ID> hsiemelink/yay:<VERSION>
    $ docker push hsiemelink/yay:<VERSION>
    
Now update the version in `setup.py` to reflect the new version, e.g. `0.12-SNAPSHOT` and commit. Don't forget to push the tag...



