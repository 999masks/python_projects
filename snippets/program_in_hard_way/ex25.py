def break_words(stuff):
    """This function will break up words for us."""
    words = stuff.split(' ')
    return words

def sort_words(words):
    """Sorts the words."""
    return sorted(words)

def print_first_word(words):
    """Prints the first word after popping it off"""
    word = words.pop(0)
    print (word)

def print_last_word(words):
    """Prints the last word after popping it off"""
    word = words.pop(-1)
    print (word)

def sort_sentence(sentense):
    "Takes in full full full sentence and retrurns the sorted words."
    "This module was added after import"
    words = break_words(sentense)
    "This is a second comment"
    return sort_words(words)

def print_first_and_last(sentence):
    """Prints the first and last words of the sentece."""
    words = break_words(sentence)
    print_first_word(words)
    print_last_word(words)

def print_first_and_last_sorted(sentence):
    """Sorts the words then prints the first and last one."""
    words = sort_sentence(sentence)
    print_first_word(words)
    print_last_word(words)

"""
Conclusions:
1. python file can be imported directly from python enviorement
2. you can call functions from imported python file like you call modules functions
3. Doc string inside of function can be viewed /called when you import that file and do help(mudule_name)
if you want specific function help instead, do help(import_module.function_name)
4. only 1 comment block will be displayed when you invoke help.function_name
5. only 1 comment block will be displayed even whe you help entire module
6. reload- reload(module_name) will updated module with changes
7. to delete/unload imported module type del(module_name) not working 100%
8. by default python does not support importing module from diff locations, to do so:
    import sys, then- sys.path.insert(0, '/just/path/to/location' then- import module_name
9. yuo can call function even in returnm statement
"""
