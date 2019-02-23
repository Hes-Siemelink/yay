# Welcome to Yay!

Yay is a scripting language in YAML. It is readable and light and meant to automate simple tasks. You can use it to glue API requests, user input and file manipulation together.


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

What happens here:
1. Yay appends `.yay` and finds the file `search.yay`. 
2. `Http GET` is a Yay command that does a HTTP request. A command in Yay is defined by a name, in this case 'Http GET' followed by parameter data, `url` and `path`. By convention, commands in yay are spelled using a capital letter.
3. The output of the server is printed in JSON format using the `Print as JSON` command.

### _Try it out!_

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


## Variables and parameters

Note that we print something called `${output}`. `${...}` is the variable syntax in Yay. 

`${output}` is a special variable that always contains the output of the last command.

You can use variables in any value field.  Variables are resolved at the moment the command is going to be executed.

For example, let's do a search using a variable:

**File: search.yay**
```
Http GET:
  url:  http://localhost:5000
  path: /recipes/search?keyword=${keyword}
Print as YAML: ${output}
```

We also change the output to be YAML using the `Print as YAML` command.

You can pass variable values through the command line:

```
$ yay search keyword=Mango
- Mango and coconut ice cream
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
Print as YAML: ${output}
```

This gives the same output as before:

```
$ yay search2 keyword=Mango
- Mango and coconut ice cream
```

## Ask for parameters

You can make the script interactive by asking the parameters on the command line.

**File: search-recipes.yay**
```
User Input:
  type: input
  message: "Search recipes with keyword:"
Http GET:
  url:  ${exampleUrl}
  path: /recipes/search?keyword=${output}
Print as YAML: ${output}
```

You will now get a question on the command line. Very useful if you don't want to remember the command line options.

```
$ yay search-recipes
? Search recipes with keyword:  Mango
- Mango and coconut ice cream
```

## Multiple requests

You can do multiple requests in one file. Just use the YAML `---` syntax to separate them.

**File: list-options.yay**
```
Http GET:
  url:  ${exampleUrl}
  path: /recipes/options?vegetarian=true
Print: |
  Vegetarian options:
  ${output}
---
Http GET:
  url:  ${exampleUrl}
  path: /recipes/options?vegetarian=false
Print: |
  Non-vegetarian options:
  ${output}
```

We use a command called **Print**, which does what you would expect: printing regular text. You can refer to variables in the text and they will be expanded to YAML.
 
Here is the output:

```
$ yay list-options
Vegetarian options:
- Mango and coconut ice cream
- Ratatouille

Non-vegetarian options:
- Meatballs
```

## Setting a default endpoint

Usually if you make multiple requests you will use the same endpoint, so we should it define it only once. Do this with the **Http endpoint** command.

**File: list-options2.yay**
```
Http endpoint: ${exampleUrl}
---
Http GET: /recipes/options?vegetarian=true
Print: |
  Vegetarian options:
  ${output}
---
Http GET: /recipes/options?vegetarian=false
Print: |
  Non-vegetarian options:
  ${output}
```

This will give the same output as above.

## Inspect variables using JSON path

Suppose you get a structured response and you want need only part of the data.

For example, let's try to find the list of ingredients for a certain recipe using our example server.

First, we will get the entire recipe.

**File: show-recipe.yay**
```
Http endpoint: ${exampleUrl}
---
Http GET: /recipe/${recipe}
Print as YAML: ${output}
```

The result is:

```
$ yay show-recipe recipe='Mango and coconut ice cream'
ingredients:
- name: Mangos
  quantity: '2'
  type: Fruit
- name: Coconut milk
  quantity: 1 can
  type: Diary
- name: Condensed milk
  quantity: 1 can
  type: Diary
- name: Cardamom
  quantity: 4 seeds
  type: Condiments
- name: Sugar
  quantity: 2 tbsp
  type: Condiments
name: Mango and coconut ice cream
steps:
- Put everything in the blender and mix it twice in 'Smoothie' mode.
- Let it cool in the fridge for two hours
- Mix in ice cream maker for 20 minutes
- Freeze for 30 minutes, mix with hand mixer. Do this twice
vegetarian: true
```

We see that the ingredients are listed in the key `ingredients`. We can extract the ingredients by simply adding the key to the output variable using JSON path syntax.

**File: show-ingredients-only.yay**
```
Http endpoint: ${exampleUrl}
---
Http GET: /recipe/${recipe}
Print as YAML: ${output.ingredients}
```

The result is:

```
$ yay show-ingredients-only recipe='Mango and coconut ice cream'
- name: Mangos
  quantity: '2'
  type: Fruit
- name: Coconut milk
  quantity: 1 can
  type: Diary
- name: Condensed milk
  quantity: 1 can
  type: Diary
- name: Cardamom
  quantity: 4 seeds
  type: Condiments
- name: Sugar
  quantity: 2 tbsp
  type: Condiments
```

## Chain requests

Yay makes it easy to chain requests, and allow for some interaction. In the previous example, we needed to specify the name of the recipe as a command-line parameter. This is awkward, because you need to type the precise name.

In this example, we get the list of recipes, then ask the user to choose a recipe and show the ingredients.

**File: show-ingredients.yay**
```
Http endpoint: ${exampleUrl}
---
Http GET: /recipes
---
User Input:
  type: list
  message: Select recipe
  choices: ${output}
Set: recipe
---
Http GET: /recipe/${recipe}
Print: |
  Ingredients for ${output.name}:
  ${output.ingredients}
```

This will result in the following interaction:

```
$ yay show-ingredients
? Select recipe  (Use arrow keys)
 > Mango and coconut ice cream
   Ratatouille
   Meatballs
   
Ingredients for Mango and coconut ice cream:
- name: Mangos
  quantity: '2'
  type: Fruit
- name: Coconut milk
  quantity: 1 can
  type: Diary
- name: Condensed milk
  quantity: 1 can
  type: Diary
- name: Cardamom
  quantity: 4 seeds
  type: Condiments
- name: Sugar
  quantity: 2 tbsp
  type: Condiments
```

## GET-modify-POST pattern

## Variable assignments

## Do some looping

## Perform a test

## Heavy lifting in Python

## Use Yay for templating

