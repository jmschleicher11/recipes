from recipes import Recipe
import re
from pylatex import Document, Section, Subsection, Itemize, Command, NoEscape, Package, Figure
from pylatex.utils import bold
import os
import argparse
import pickle

def frac(a, b):
    return r'$\\frac{'+str(a)+'}{'+str(b)+'}$'

def clean_fractions(text):
    text = re.sub("¼", frac(1, 4), text)
    text = re.sub("⅓", frac(1, 3), text)
    text = re.sub("½", frac(1, 2), text)
    text = re.sub("⅔", frac(2, 3), text)
    text = re.sub('¾', frac(3, 4), text)
    text = re.sub('⅛', frac(1, 8), text)
    return text

def clean_degrees(text):
    return re.sub("˚", r"$\\degree$", text)

def create_latex_friendly_text(text):
    text = clean_fractions(text)
    text = clean_degrees(text)
    return text

def generate_latex(recipe):
    """
    Takes a Recipe object containing necessary information about the recipe, then generates a latex
    string & compiles to produce the pdf
    """
    geometry_options = {"tmargin": "1cm", "lmargin": "2cm", "rmargin": "2cm", "bmargin": "1cm"}
    doc = Document(fontenc="T1", geometry_options=geometry_options)
    doc.packages.append(Package('amsmath'))
    doc.packages.append(Package('nopageno'))
    doc.packages.append(Package('gensymb'))
    doc.packages.append(Package('times'))
    doc.preamble.append(Command('title', recipe.title))
    doc.preamble.append(Command('author', recipe.source))
    doc.preamble.append(Command('date', ""))
    doc.append(NoEscape(r'\maketitle'))

    with doc.create(Figure(position='h!')) as food_picture:
        food_picture.add_image(recipe.title + ".png", width='240px')

    # with doc.create(Subsection('Timing', numbering=False)):
    if recipe.active_time:
        doc.append(Command("noindent"))
        doc.append(bold('Active Time: '))
        doc.append(recipe.active_time + " ")
    if recipe.total_time:
        doc.append(Command("noindent"))
        doc.append(bold('Total Time: '))
        doc.append(recipe.total_time)

    with doc.create(Section('Ingredients', numbering=False)):
        doc.append(bold(recipe.servings))
        with doc.create(Itemize()) as itemize:
            for ingredient in recipe.ingredients:
                itemize.add_item(NoEscape(create_latex_friendly_text(ingredient)))

    with doc.create(Section('Preparation', numbering=False)):
        for i in range(len(recipe.steps)):
            with doc.create(Subsection(recipe.steps[i], numbering=False)):
                doc.append(NoEscape(create_latex_friendly_text(recipe.instructions[i])))

    with doc.create(Section('Source', numbering=False)):
        doc.append(recipe.url)

    doc.generate_pdf(filepath=str(os.path.join(os.getcwd(), 'pdfs', recipe.title)), clean_tex=True)


if __name__ == "__main__":

    ## TODO: make graph database of the ingredients?!?!
    ## TODO: pass folder as an argument (recipe type)
    ## TODO: expand to incorporate freely entered or csv recipes somehow
    ## TODO: extract ingredients list from BA & NYTC

    parser = argparse.ArgumentParser(description='Enter a recipe URL')

    parser.add_argument("--url", type=str, required=True, help="Bon Appetit or NY Times Cooking")
    parser.add_argument("--folder", type=str, )

    args = parser.parse_args()

    # Create the recipe object from the url and generate the pdf
    selected_recipe = Recipe(args.url)
    generate_latex(selected_recipe)
    # Remove the downloaded recipe image
    os.remove(os.path.join(os.getcwd(), 'pdfs', selected_recipe.title + '.png'))

    # Remove the soup property and save the recipe object
    # selected_recipe.soup = None
    # filename = re.sub(' ', '_', selected_recipe.title.lower()) + '.pkl'
    # file_object = open(os.path.join(os.getcwd(), 'pickled_recipes', filename), 'wb')
    # pickle.dump(selected_recipe, file_object)
    # file_object.close()