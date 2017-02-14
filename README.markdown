# Wikidossier – Tools to stalk Wikipedia users

To filter out "strange" page titles, I used

    /[^\d9\d32-\d126“”‘’–—§éñãí¡áóâ°üčō×½êàëżıå]
    :g//d

in Vim, to find characters not in a whitelist, and then deleting all lines with
characters outside of that list.
We can work out something better later.
