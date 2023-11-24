from recipes import Recipe
import re
from pylatex import Document, Section, Subsection, Itemize, Command, NoEscape, Package, Figure
from pylatex.utils import bold
import os
import argparse

def frac(a, b):
    return r'$\\frac{'+str(a)+'}{'+str(b)+'}$'

def clean_fractions(text):
    text = re.sub("¼", frac(1, 4), text)
    text = re.sub("1( |)/4", frac(1, 4), text)
    text = re.sub("⅓", frac(1, 3), text)
    text = re.sub("1( |)/3", frac(1, 3), text)
    text = re.sub("½", frac(1, 2), text)
    text = re.sub("1( |)/2", frac(1, 2), text)
    text = re.sub("⅔", frac(2, 3), text)
    text = re.sub("²⁄₃", frac(2, 3), text)
    text = re.sub("2( |)/3", frac(2, 3), text)
    text = re.sub('¾', frac(3, 4), text)
    text = re.sub("3( |)/4", frac(3, 4), text)
    text = re.sub('⅛', frac(1, 8), text)
    text = re.sub("1( |)/8", frac(1, 8), text)
    text = re.sub('⅜', frac(3, 8), text)
    text = re.sub("3( |)/8", frac(3, 8), text)
    text = re.sub('⅝', frac(5, 8), text)
    text = re.sub("5( |)/8", frac(5, 8), text)
    return text

def clean_special_characters(text):
    text = re.sub("˚", r"$\\degree$", text)
    text = re.sub("#", r"\\#", text)
    text = re.sub("&", r"\\&", text)
    text = re.sub("ồ", "o", text)
    return text

def create_latex_friendly_text(text):
    text = clean_fractions(text)
    text = clean_special_characters(text)
    return text

def generate_latex(recipe):
    """
    Takes a Recipe object containing necessary information about the recipe, then generates a latex
    string & compiles to produce the pdf
    """
    # Set up initial document packages
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

    # Add image to recipe)
    with doc.create(Figure(position='h!')) as food_picture:
        food_picture.add_image(recipe.title + ".png", width='240px')

    # Add recipe timing (active & total)
    if recipe.active_time:
        doc.append(Command("noindent"))
        doc.append(bold('Active Time: '))
        doc.append(recipe.active_time + " ")
    if recipe.total_time:
        doc.append(Command("noindent"))
        doc.append(bold('Total Time: '))
        doc.append(recipe.total_time)

    # Add list of ingredients
    with doc.create(Section('Ingredients', numbering=False)):
        if isinstance(recipe.servings, str):
            doc.append(bold(recipe.servings))
        with doc.create(Itemize()) as itemize:
            for ingredient in recipe.ingredients:
                itemize.add_item(NoEscape(create_latex_friendly_text(ingredient)))

    # Add preparation steps
    with doc.create(Section('Preparation', numbering=False)):
        for i in range(len(recipe.steps)):
            with doc.create(Subsection(recipe.steps[i], numbering=False)):
                doc.append(NoEscape(create_latex_friendly_text(recipe.instructions[i])))

    # Add optional notes
    if recipe.my_notes:
        with doc.create(Section('My Notes', numbering=False)):
            doc.append(recipe.my_notes)

    # Add source URL
    with doc.create(Section('Source', numbering=False)):
        doc.append(recipe.url)

    # Generate and save the final pdf document
    doc.generate_pdf(filepath=str(os.path.join(os.getcwd(), 'pdfs', recipe.title)), clean_tex=True)


if __name__ == "__main__":

    ## TODO: make graph database of the ingredients?!?!
    ## TODO: extract ingredients list from BA & NYTC

    parser = argparse.ArgumentParser(description='Enter a recipe URL')

    parser.add_argument("--url", type=str, required=False, help="Bon Appetit, NY Times Cooking, or Serious Eats")
    parser.add_argument("--file", type=str, required=False, help="Filename of existing recipe")
    parser.add_argument("--type", type=str, required=False, help="Type of dish")
    parser.add_argument("--source", type=str, required=False, help="Source of recipe")

    args = parser.parse_args()

    # Create the recipe object from the url and generate the pdf
    selected_recipe = Recipe(url=args.url, file=args.file, source=args.source, type=args.type)

    generate_latex(selected_recipe)

    if args.type:
        if not os.path.exists(os.path.join(os.getcwd(), 'pdfs', args.type)):
            os.mkdir(os.path.join(os.getcwd(), 'pdfs', args.type))
        os.rename(os.path.join(os.getcwd(), 'pdfs', selected_recipe.title + '.pdf'),
                  os.path.join(os.getcwd(), 'pdfs', args.type, selected_recipe.title + '.pdf'))
    # Remove the downloaded recipe image
    os.rename(os.path.join(os.getcwd(), 'pdfs', selected_recipe.title + '.png'),
              os.path.join(os.getcwd(), 'images', selected_recipe.title + '.png'))
