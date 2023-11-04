# Recipes codebase
A codebase to scrape recipe websites I like, parse the information I need, and convert them into PDFs using a 
standardized LaTeX template.

## Repository layout:
    - recipes/                        Repository home directory
        - pdfs/                       Location to store final PDFs
        - tests/                      Unit tests
            - test_ScrapedData.py     Tests various aspects of scraping code for different recipe examples based on identified edge cases
        - .gitignore                  Files and directories to exclude from git tracking
        - create_latex.py             Script to generate latex string and save final PDF of the recipe
        - README.md                   This document
        - recipes.py                  Scraping script to extract recipe elements from various recipe websites
        - requirements.txt            Contains required python packages and versions to run code

## To run
Clone this repository to run it locally, then create a new environment (e.g., to create an environment called `recipes` 
with Anaconda, use `conda create -n recipes python=3.10`). Next, activate the new environment (`conda activate recipes`) 
and install the required packages by running `pip install -r requirements.txt`.

Next select a url to a recipe from one of the available options and, from the main `recipes/` directory, run:
>python create_latex.py --url="selected recipe url as a string"

This will scrape the website using the `recipes.py` script, create a Recipe object to store the information for the 
recipe (recipe name, time, ingredients, preparation steps, etc.), save a picture from the website, then use the 
`create_latex.py` to generate the latex string with the recipe information then generate and save a standardized pdf. 

## To test
Unit tests to ensure data are correctly scraped and pulled from websites are in the `tests/` directory. These can be
run from the main `recipes/` directory (with the `recipes` environment activated) by running:
>pytest

Note: there are intentional random delays between each website being scraped.  

## Final note: 
I have subscriptions to the websites this code pulls information from (or they are available free to the public) and 
have just put this project together because I like having a standard format for recipes I save. I recommend 
supporting the organizations that put out these excellent recipes with your own subscription! Happy cooking!