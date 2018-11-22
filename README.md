# Welcome to Yay!

Yay is a scripting language in YAML. It is readable and light and meant to automate simple tasks. You can use it to glue API requests, user input and file manipulation together.

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
$ yay list-recipes
[
  "Crock Pot Roast",
  "Roasted Asparagus",
  "Curried Lentils and Rice",
  "Big Night Pizza",
  "Cranberry and Apple Stuffed Acorn Squash Recipe",
  "Mic's Yorkshire Puds",
  "Old-Fashioned Oatmeal Cookies",
  "Blueberry Oatmeal Squares",
  "Curried chicken salad"
]
```


## Variables and parameters

Note that we print something called `${result}`. `${...}` is the variable syntax in Yay. 

`${result}` is a special variable that always contains the result of the last task.

You can use variables in any value field.  Variables are resolved at the moment the task is going to be executed.

For example, let's do a search using a variable:

**File: search.yay**
```
Http GET:
  url:  http://localhost:5000
  path: /recipes/search?keyword=${keyword}
Print as YAML: ${result}
```

We also change the output to be YAML using the `Print as YAML` task.

You can pass variable values through the command line:

```
$ yay search keyword=Oatmeal
- Old-Fashioned Oatmeal Cookies
- Blueberry Oatmeal Squares
```
    
## Store your credentials

Suppose you need to authenticate. You don't want to type in your credentials all the time of have them displayed on the command line. Yay let you store them as a variable in a private file so they can be used in your script.

**File: ~/.yay/default-variables.yaml**
```
exampleUrl: http://user:pass@localhost:5000
```

**File: search2.yay**
```
Http GET:
  url:  ${exampleUrl}
  path: /recipes/search?keyword=${keyword}
Print as YAML: ${result}
```

This gives the same output as before:

```
$ yay search2 keyword=Oatmeal
- Old-Fashioned Oatmeal Cookies
- Blueberry Oatmeal Squares
```

## Ask for parameters

You can make the script interactive by asking the parameters on the command line.

**File: search-recipes.yay**
```
User Input:
  type: input
  name: keyword
  message: "Search recipes with keyword:"
Http GET:
  url:  ${exampleUrl}
  path: /recipes/search?keyword=${keyword}
Print as YAML: ${result}
```

You will now get a question on the command line. Very useful if you don't want to remember the command line options.

```
$ yay search-recipes
? Search recipes with keyword:  Oatmeal
- Old-Fashioned Oatmeal Cookies
- Blueberry Oatmeal Squares
```

## Multiple requests

You can do multiple requests in one file. Just use the YAML `---` syntax to separate them.

**File: list-options.yay**
```
Http GET:
  url:  ${exampleUrl}
  path: /recipes/options?vegetarian=true
Print: 'Vegetarian options:'
Print as YAML: ${result}
---
Http GET:
  url:  ${exampleUrl}
  path: /recipes/options?vegetarian=false
Print: 'Non-vegetarian options:'
Print as YAML: ${result}
```

We use a task called **Print**, which does what you would expect: printing regular text. Keep in mind that  you need to quote a printable string when using special YAML characters like `:`.
 
Here is the output:

```
$ yay list-options
Vegetarian options:
- Roasted Asparagus
- Curried Lentils and Rice
- Big Night Pizza
- Cranberry and Apple Stuffed Acorn Squash Recipe
- Mic's Yorkshire Puds
- Old-Fashioned Oatmeal Cookies
- Blueberry Oatmeal Squares

Non-vegetarian options:
- Crock Pot Roast
- Curried chicken salad
```

## Setting a default endpoint

Usually if you make multiple requests you will use the same endpoint, so we should it define it only once. Do this with the **Http endpoint** task.

**File: list-options2.yay**
```
Http endpoint: ${exampleUrl}
---
Http GET: /recipes/options?vegetarian=true
Print: 'Vegetarian options:'
Print as YAML: ${result}
---
Http GET: /recipes/options?vegetarian=false
Print: 'Non-vegetarian options:'
Print as YAML: ${result}

```

This will give the same output as above.

## Inspect results using JSON path

## Chain requests

## GET-modify-POST pattern

## Variable assignments

## Do some looping

## Perform a test

## Heavy lifting in Python

## Use Yay for templating

