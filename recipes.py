from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
import os
import re
import json

def clean_text(text):
    text = re.sub('\n', ' ', text)
    text = re.sub('\xa0', '', text)
    text = text.split("Editor’s note: ")[0]
    text = text.strip()
    text = re.sub(' {2,}', ' ', text)
    return text

class Recipe:

    def __init__(self, url="", file="", source="", type=""):

        if file:
            recipe_dict = json.load(open(os.path.join(os.getcwd(), 'jsons', file + '.json')))
            self.url = recipe_dict['url']
            self.source = recipe_dict['source']
            self.title = recipe_dict['title']
            self.active_time = recipe_dict['active_time']
            self.total_time = recipe_dict['total_time']
            self.servings = recipe_dict['servings']
            self.ingredients = recipe_dict['ingredients']
            self.food_list = recipe_dict['food_list']
            self.steps = recipe_dict['steps']
            self.instructions = recipe_dict['instructions']
            if 'my_notes' in recipe_dict.keys():
                self.my_notes = recipe_dict['my_notes']
            else:
                self.my_notes = None
            if 'type' in recipe_dict.keys():
                self.type = recipe_dict['type']
            else:
                self.type = None

            # Transfer file to pdf folder
            os.rename(os.path.join(os.getcwd(), 'images', self.title + '.png'),
                      os.path.join(os.getcwd(), 'pdfs', self.title + '.png'))

        else:
            self.url = url
            if "bonappetit" in self.url:
                self.source = "Bon Appetit"
            elif "nytimes" in self.url:
                self.source = "New York Times Cooking"
            elif "seriouseats" in self.url:
                self.source = "Serious Eats"
            else:
                self.source = source
            self.type = type
            self.title = None
            self.active_time = None
            self.total_time = None
            self.soup = None
            self.servings = None
            self.ingredients = None
            self.food_list = None
            self.steps = None
            self.instructions = None
            self.my_notes = None
            self.pull_data()

        # Save json file
        self.to_json()

    def pull_data(self):
        """
        Pull html from website to parse recipe
        """

        if self.source in ['Bon Appetit', "New York Times Cooking", 'Serious Eats']:
            page = urlopen(self.url)
            html = page.read().decode("utf-8")
            self.soup = BeautifulSoup(html, "html.parser")

        if self.source == 'Bon Appetit':
            self.parse_bon_appetit()
        elif self.source == "New York Times Cooking":
            self.parse_nyt_cooking()
        elif self.source == 'Serious Eats':
            self.parse_serious_eats()
        else:
            self.enter_information_manually()

    def parse_bon_appetit(self):
        """
        Extract recipe from bon appetit html
        """
        self.title = clean_text(self.soup.title.text.split(' | ')[0])

        # Get active and total times
        for i in range(len(self.soup.find_all('p'))):
            if self.soup.find_all('p')[i].text == 'Active Time':
                self.active_time = clean_text(self.soup.find_all('p')[i+1].text)
            elif self.soup.find_all('p')[i].text == 'Total Time':
                self.total_time = clean_text(self.soup.find_all('p')[i+1].text)

        # Pull ingredients & preparations tags
        ingredients_tag = None
        preparation_tag = None

        for i in range(len(self.soup.find_all('h2'))):
            if self.soup.find_all('h2')[i].text == 'Ingredients':
                ingredients_tag = self.soup.find_all('h2')[i]
            elif self.soup.find_all('h2')[i].text == 'Preparation':
                preparation_tag = self.soup.find_all('h2')[i]
            else:
                pass

        # Create ingredients list
        if ingredients_tag:
            if len(ingredients_tag.parent.find_all('p')[0].text) <= 1:
                pass
            else:
                self.servings = clean_text(ingredients_tag.parent.find_all('p')[0].text)
            amounts = ingredients_tag.parent.find_all('p')[1:]
            amounts_list = [i.contents[0] if len(i)>0 else None for i in amounts]
            ingredients = ingredients_tag.parent.find_all('div')[1:]
            ingredients_list = [i.text if len(i)>0 else None for i in ingredients]
            final_ingredients = [amount + " " + ingredient if isinstance(amount, str) else ingredient
                                 for amount, ingredient in zip(amounts_list, ingredients_list)]
            final_ingredients = [clean_text(x) for x in final_ingredients]
            self.ingredients = final_ingredients

        # Pull preparation steps
        if preparation_tag:
            step_numbers = [item.contents[0] for item in preparation_tag.parent.find_all('h4')]
            instructions = [item.text for item in preparation_tag.parent.find_all('p')]
            if len(step_numbers) != len(instructions):
                for i, inst in enumerate(instructions):
                    if re.match("Do ahead: ", inst, flags=re.IGNORECASE):
                        instructions[i] = re.split("Do ahead: ", inst, flags=re.IGNORECASE)[1]
                        step_numbers.insert(i, "Do ahead")
                    else:
                        pass
            else:
                for i, inst in enumerate(instructions):
                    if re.match("Do ahead: ", inst, flags=re.IGNORECASE):
                        instructions[i] = re.split("Do ahead: ", inst, flags=re.IGNORECASE)[1]
                        step_numbers[i] = "Do ahead"
                    elif re.search("Do ahead: ", inst, flags=re.IGNORECASE):
                        instructions[i] = re.split("Do ahead: ", inst, flags=re.IGNORECASE)[0]
                        instructions.insert(i+1, re.split("Do ahead: ", inst, flags=re.IGNORECASE)[1])
                        step_numbers.insert(i+1, "Do ahead")
                    else:
                        pass
            instructions = [clean_text(x) for x in instructions]
            self.steps = step_numbers
            self.instructions = instructions

        # Pull image & save temporarily
        image_url = self.soup.find("source", {"media": "(max-width: 767px)"})['srcset'].split(' ')[-2]
        urlretrieve(image_url, filename=os.path.join(os.getcwd(), 'pdfs', self.title + '.png'))

    def parse_nyt_cooking(self):
        """
        Extract recipe from nytimes cooking html
        """
        self.title = self.soup.title.text.split(' - ')[0].replace(" Recipe", "")

        self.total_time = self.soup.find_all("dd", class_="pantry--ui")[0].text

        # Pull number of servings
        servings_tag = self.soup.find('div', class_=re.compile('ingredients_recipeYield_*'))
        servings_text = servings_tag.find_all('span',
                                              class_=re.compile('pantry--ui ingredients_fontOverride_*'))[0].text
        if re.search(r'\d+$', servings_text):
            if re.search('serv(es|ings)', servings_text, re.IGNORECASE):
                self.servings = servings_text
            else:
                self.servings = servings_text + ' Servings'
        else:
            self.servings = servings_text

        # Pull ingredients
        ingredients_list = self.soup.find("div", class_=re.compile("recipebody_ingredients-block_*")).find_all("li")
        ingredients = []
        for ingredient in ingredients_list:
            span = ingredient.find('span', class_=re.compile('ingredient_quantity_*'))
            if span:
                quantity = span.text
                ingredient_name = ingredient.text.strip()[len(quantity):]
                ingredients.append(f'{quantity} {ingredient_name}')
            else:
                ingredients.append(ingredient.text.strip())

        self.ingredients = ingredients

        # Pull preparation steps
        steps_list = self.soup.find("div", class_=re.compile("recipebody_prep-block_*")).find_all("li")
        step_numbers = []
        instructions = []
        for step in steps_list:
            if step.find("div", class_=re.compile("pantry--ui-lg-strong preparation_stepNumber_*")):
                step_numbers.append(step.find("div", class_=re.compile("pantry--ui-lg-strong preparation_stepNumber_*")).text)
                instructions.append(step.find("p", class_="pantry--body-long").text)

        # Pull optional Tip instructions
        if self.soup.find("div", class_=re.compile("tips_tips_*")):
            tips = self.soup.find("div", class_=re.compile("tips_tips_*"))
            step_numbers.append(tips.find("span", class_="pantry--label").text)
            instructions.append(tips.find("li", class_="pantry--body-long").text)

        self.steps = step_numbers
        self.instructions = instructions

        # Pull image & save temporarily
        image_url = self.soup.find("img")['src']
        urlretrieve(image_url, filename=os.path.join(os.getcwd(), 'pdfs', self.title + '.png'))

    def parse_serious_eats(self):

        self.title = self.soup.title.text.replace(" Recipe", "")

        # Find active and total times and servings
        active_tag = self.soup.find("div", class_="loc active-time project-meta__active-time")
        total_tag = self.soup.find("div", class_="loc total-time project-meta__total-time")
        serving_tag = self.soup.find("div", class_="loc recipe-serving project-meta__recipe-serving")
        self.active_time = clean_text(active_tag.find(class_="meta-text__data").text)
        self.total_time = clean_text(total_tag.find(class_="meta-text__data").text)
        self.servings = clean_text(serving_tag.find(class_="meta-text__data").text)

        # Get the ingredients from the recipe
        ingredients = []
        food_list = []
        ingredients_list = self.soup.find("ul", class_="structured-ingredients__list text-passage").find_all("p")
        for ingredient in ingredients_list:
            ingredients.append(ingredient.text)
            food_list.append(ingredient.find("span", {"data-ingredient-name": 'true'}).text.lower())

        self.ingredients = ingredients
        self.food_list = food_list

        instructions = []
        step_numbers = []
        step_index = 1
        instructions_tag = self.soup.find('ol', class_="comp mntl-sc-block-group--OL mntl-sc-block mntl-sc-block-startgroup")
        instruction_list = instructions_tag.find_all('p', class_="comp mntl-sc-block mntl-sc-block-html")
        for instruction in instruction_list:
            instructions.append(clean_text(instruction.text))
            step_numbers.append("Step {}".format(step_index))
            step_index += 1

        # Find if there are extra notes and add to the instructions
        extra_notes_block = self.soup.find_all("h2", id=re.compile("mntl-sc-block_*"),
                                               class_="comp mntl-sc-block lifestyle-sc-block-heading mntl-sc-block-heading")
        notes_tag = None
        for item in extra_notes_block:
            if re.search("Notes", item.text):
                notes_tag = item
        if notes_tag:
            split_id = notes_tag['id'].split('-')
            notes_id = int(split_id[-1]) + 1
            notes_text_id = '-'.join(split_id[:-1] + [str(notes_id)])
            notes_text = ''
            while self.soup.find("p", id=notes_text_id):
                notes_text += " " + self.soup.find("p", id=notes_text_id).text.strip()
                notes_id += 2
                notes_text_id = '-'.join(split_id[:-1] + [str(notes_id)])

            instructions.append(clean_text(notes_text))
            step_numbers.append("Notes")

        self.steps = step_numbers
        self.instructions = instructions

        # Pull image & save temporarily
        try:
            image_url = self.soup.find("figure").find("img")['src']
        except:
            image_url = self.soup.find("figure").find("img")['data-src']
        urlretrieve(image_url, filename=os.path.join(os.getcwd(), 'pdfs', self.title + '.png'))

    def enter_information_manually(self):

        self.title = input("Enter title:")
        self.active_time = input("Enter active time:")
        self.total_time = input("Enter total time:")
        self.servings = input("Enter number of servings:")

        self.ingredients = collect_list_of_things("ingredients")

        self.food_list = None

        num_steps = input("Enter the number of steps")
        steps_list = ['Step ' + str(i) for i in list(range(1, int(num_steps) + 1))]
        do_ahead = input("Do ahead instructions? (y/n)")
        if do_ahead == 'y':
            steps_list.append("Do ahead")

        self.steps = steps_list

        self.instructions = collect_list_of_things("instructions")

    def to_json(self):
        if os.path.isfile(os.path.join(os.getcwd(), 'jsons', self.title + '.json')):
            user_says = input("This json file already exists. Overwrite? (y/n): ")
            if user_says == 'y':
                recipe_dict = vars(self)
                if 'soup' in recipe_dict.keys():
                    recipe_dict.pop('soup')
                with open(os.path.join(os.getcwd(), 'jsons', self.title + '.json'), 'w', encoding='utf-8') as f:
                    json.dump(recipe_dict, f, ensure_ascii=False, indent=4)
            else:
                print("Did not overwrite the json file.")
        else:
            recipe_dict = vars(self)
            if 'soup' in recipe_dict.keys():
                recipe_dict.pop('soup')
            with open(os.path.join(os.getcwd(), 'jsons', self.title + '.json'), 'w', encoding='utf-8') as f:
                json.dump(recipe_dict, f, ensure_ascii=False, indent=4)



def collect_list_of_things(type_of_thing):
    more = 'y'
    thing_list = []
    while more == 'y':
        thing_list.append(input("Enter {}".format(type_of_thing)))
        more = input("More {}? (y/n)".format(type_of_thing))
    return thing_list
