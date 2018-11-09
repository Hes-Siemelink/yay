# Welcome to Yay!

Yay is a scripting language in YAML. It is readable and light and meant to automate simple tasks. You can use it to glue API requests, user input and file manipulation together.

_Note: Yay is a pre-alpha prototype. Anything can change at any moment._

## Simple yay: reuse your request

The starting point for Yay is to reuse HTTP requests that you would do off the command line but are too long to actually remember.

Suppose you have this request:

    $ http GET http://localhost:5000/rest/search?key=stuff
    
You can save it in a YAML file and reuse it using Yay.

**File: search.yay**
```
Http GET:
  url:  http://localhost:5000
  path: /rest/search?query=stuff
Print as JSON: ${result}
```
  
Invoke it using the `yay` command:

    $ yay search

What happens here:
1. Yay appends `.yay` and finds the file `search.yay`. 
2. `Http GET` is a Yay task that does a HTTP request. A task in Yay is a command name, in this case 'Http GET' followed by parameter data, `url` and `path`. By convention, commands in yay are spelled using a capital letter.
3. The result is printed in JSON format using the `Print as JSON` command.

### _Try it out!_

Yay is bundled with a test application. Start it with the followng command

    $ python -m yay.test_server

Running the above example will give the following output:

```
$ yay search
{
  "My stuff": [
    "apples, pears"
  ],
  "Other stuff": [
    "oranges",
    "lemons"
  ]
}
```


## Variables and parameters

Note that we print something called `${result}`. `${...}` is the variable syntax in Yay. 

`${result}` is a special variable that always contains the result of the last task.

You can use variables in any value field.  Variables are resolved at the moment the task is going to be executed.

For example, let's make the search term a variable:

**File: search2.yay**
```
Http GET:
  url:  http://localhost:5000
  path: /rest/search?query=${query}
Print as YAML: ${result}
```

We also change the output to be YAML using the `Print as YAML` task.

You can pass variable values through the command line:

```
$ yay search2 query=My
My stuff:
- apples, pears
```
    


## Store your credentials

Suppose you need to authenticate. You don't want to type in your credentials all the time of have them displayed on the command line. Yay let you store them as a variable in a private file so they can be used in your script.

**File: ~/.yay/default-variables.yaml**
```
exampleUrl: http://user:pass@localhost:5000
```

**File: search3.yay**
```
Http GET:
  url:  ${exampleUrl}
  path: /rest/search?query=stuff
Print as JSON: ${result}
```


## Chain requests

## Inspect result using JSON path

## Ask for parameters

## Do some looping

## Perform a test

## Heavy lifting in Python

## Use Yay for templating

