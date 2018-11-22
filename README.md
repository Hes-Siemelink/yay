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
Print: |
  Vegetarian options:
  ${result}
---
Http GET:
  url:  ${exampleUrl}
  path: /recipes/options?vegetarian=false
Print: |
  Non-vegetarian options:
  ${result}
```

We use a task called **Print**, which does what you would expect: printing regular text. You can refer to variables in the text and they will be expanded to YAML.
 
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
Print: |
  Vegetarian options:
  ${result}
---
Http GET: /recipes/options?vegetarian=false
Print: |
  Non-vegetarian options:
  ${result}
```

This will give the same output as above.

## Inspect results using JSON path

Suppose you get a structured response and you want need only part of the data.

For example, let's try to find the list of ingredients for a certain recipe using our example server.

First, we will get the entire recipe.

**File: show-recipe.yay**
```
Http endpoint: ${exampleUrl}
---
Http GET: /recipe/${recipe}
Print as YAML: ${result}
```

The result is:

```
$ yay show-recipe recipe='Roasted Asparagus'
ingredients:
- name: Asparagus
  quantity: 1 lb
  type: Produce
- name: olive oil
  quantity: 1 1/2 tbsp
  type: Condiments
- name: kosher salt
  quantity: 1/2 tsp
  type: Baking
name: Roasted Asparagus
steps:
- "Preheat oven to 425\xB0F."
- Cut off the woody bottom part of the asparagus spears and discard.
- With a vegetable peeler, peel off the skin on the bottom 2-3 inches of the spears
  (this keeps the asparagus from being all.",string.", and if you eat asparagus you
  know what I mean by that).
- Place asparagus on foil-lined baking sheet and drizzle with olive oil.
- Sprinkle with salt.
- With your hands, roll the asparagus around until they are evenly coated with oil
  and salt.
- Roast for 10-15 minutes, depending on the thickness of your stalks and how tender
  you like them.
- They should be tender when pierced with the tip of a knife.
- The tips of the spears will get very brown but watch them to prevent burning.
- They are great plain, but sometimes I serve them with a light vinaigrette if we
  need something acidic to balance out our meal.
vegetarian: true
```

We see that the ingredients are listed in the key `ingredients`. We can extract the ingredients by simply adding the key to the result variable using JSON path syntax.

**File: show-ingredients-only.yay**
```
Http endpoint: ${exampleUrl}
---
Http GET: /recipe/${recipe}
Print as YAML: ${result.ingredients}
```

The result is:

```
$ yay show-ingredients-only recipe='Roasted Asparagus'
- name: Asparagus
  quantity: 1 lb
  type: Produce
- name: olive oil
  quantity: 1 1/2 tbsp
  type: Condiments
- name: kosher salt
  quantity: 1/2 tsp
  type: Baking
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
  name: recipe
  choices: ${result}
---
Http GET: /recipe/${recipe}
Print: |
  Ingredients for ${recipe}:
  ${result.ingredients}
```

This will result in the following interaction:
```
$ yay show-ingredients
? Select recipe  (Use arrow keys)
   Crock Pot Roast
 > Roasted Asparagus
   Curried Lentils and Rice
   Big Night Pizza
   Cranberry and Apple Stuffed Acorn Squash Recipe
   Mic's Yorkshire Puds
   Old-Fashioned Oatmeal Cookies
   Blueberry Oatmeal Squares
   Curried chicken salad

Ingredients for Roasted Asparagus:
- name: Asparagus
  quantity: 1 lb
  type: Produce
- name: olive oil
  quantity: 1 1/2 tbsp
  type: Condiments
- name: kosher salt
  quantity: 1/2 tsp
  type: Baking

```

## GET-modify-POST pattern

## Variable assignments

## Do some looping

## Perform a test

## Heavy lifting in Python

## Use Yay for templating

