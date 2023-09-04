import unittest
import time
import random
import os

from recipes import Recipe

class BonAppetitTesting(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.pasta = Recipe('https://www.bonappetit.com/recipe/jammy-onion-and-miso-pasta')
        time.sleep(random.randrange(1, 6) + random.random())
        self.tart = Recipe('https://www.bonappetit.com/recipe/strawberry-biscoff-cheesecake-tart')
        time.sleep(random.randrange(1, 6) + random.random())
        self.cake = Recipe('https://www.bonappetit.com/recipe/appalachian-apple-stack-cake')
        time.sleep(random.randrange(1, 6) + random.random())
        self.bread = Recipe('https://www.bonappetit.com/recipe/flaky-bread')
        time.sleep(random.randrange(1, 6) + random.random())
        self.pancake = Recipe('https://www.bonappetit.com/recipe/peach-dutch-baby-pancake-with-cherry-compote')
        time.sleep(random.randrange(1, 6) + random.random())
        self.aloo = Recipe('https://www.bonappetit.com/recipe/aloo-tikki-with-hari-chutney')

    def test_url(self):
        self.assertEqual(self.pasta.url, 'https://www.bonappetit.com/recipe/jammy-onion-and-miso-pasta')
        self.assertEqual(self.tart.url, 'https://www.bonappetit.com/recipe/strawberry-biscoff-cheesecake-tart')
        self.assertEqual(self.cake.url, 'https://www.bonappetit.com/recipe/appalachian-apple-stack-cake')
        self.assertEqual(self.bread.url, 'https://www.bonappetit.com/recipe/flaky-bread')
        self.assertEqual(self.pancake.url,
                         'https://www.bonappetit.com/recipe/peach-dutch-baby-pancake-with-cherry-compote')
        self.assertEqual(self.aloo.url, 'https://www.bonappetit.com/recipe/aloo-tikki-with-hari-chutney')

    def test_source(self):
        self.assertEqual(self.pasta.source, 'Bon Appetit')
        self.assertEqual(self.tart.source, 'Bon Appetit')
        self.assertEqual(self.cake.source, 'Bon Appetit')
        self.assertEqual(self.bread.source, 'Bon Appetit')
        self.assertEqual(self.pancake.source, 'Bon Appetit')
        self.assertEqual(self.aloo.source, 'Bon Appetit')

    def test_title(self):
        self.assertEqual(self.pasta.title, 'Jammy Onion and Miso Pasta Recipe')
        self.assertEqual(self.tart.title, 'Strawberry-Biscoff Cheesecake Tart Recipe')
        self.assertEqual(self.cake.title, 'Appalachian Apple Stack Cake Recipe')
        self.assertEqual(self.bread.title, 'Flaky Bread (Malawah) Recipe')
        self.assertEqual(self.pancake.title, 'Peach Dutch Baby Pancake with Cherry Compote Recipe')
        self.assertEqual(self.aloo.title, 'Aloo Tikki With Hari Chutney Recipe')

    def test_times(self):
        self.assertIsNone(self.pasta.active_time)
        self.assertIsNone(self.pasta.total_time)
        self.assertIsNone(self.tart.active_time)
        self.assertIsNone(self.tart.total_time)
        self.assertIsNone(self.cake.active_time)
        self.assertEqual(self.cake.total_time, '1 hr 45 minutes (plus 45 minute chill time)')
        self.assertIsNone(self.bread.active_time)
        self.assertIsNone(self.bread.total_time)
        self.assertIsNone(self.pancake.active_time)
        self.assertIsNone(self.pancake.total_time)
        self.assertIsNone(self.aloo.active_time)
        self.assertIsNone(self.aloo.total_time)

    def test_servings(self):
        self.assertEqual(self.pasta.servings, '4 servings')
        self.assertEqual(self.tart.servings, '4–6 servings')
        self.assertEqual(self.cake.servings, '8–12 servings')
        self.assertEqual(self.bread.servings, 'Makes 10 Servings')
        self.assertEqual(self.pancake.servings, '6 to 8 Servings')
        self.assertIsNone(self.aloo.servings)

    def test_ingredients_list(self):
        self.assertEqual(len(self.pasta.ingredients), 11)
        self.assertEqual(len(self.tart.ingredients), 10)
        self.assertEqual(len(self.cake.ingredients), 21)
        self.assertEqual(len(self.bread.ingredients), 5)
        self.assertEqual(len(self.pancake.ingredients), 13)
        self.assertEqual(len(self.aloo.ingredients), 12)

    def test_do_ahead_handling_in_steps(self):
        # No "Do ahead"
        self.assertEqual(self.pasta.steps, ['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5'])
        # "Do ahead" is the last step
        self.assertEqual(self.tart.steps, ['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5', 'Step 6', 'Do ahead'])
        # "Do ahead" appears midway through steps
        self.assertEqual(self.cake.steps, ['Step 1', 'Step 2', 'Do ahead', 'Step 3', 'Step 4', 'Step 5'])
        # "Do ahead" is in a numbered step
        self.assertEqual(self.bread.steps, ['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5', 'Step 6', 'Do ahead'])
        # "Do ahead" is in the middle of instructions
        self.assertEqual(self.pancake.steps, ['Step 1', 'Do ahead', 'Step 2', 'Step 3', 'Step 4'])
        self.assertEqual(self.aloo.steps, ['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5', 'Step 6', 'Do ahead'])

    def test_steps_instructions_same_len(self):
        self.assertEqual(len(self.pasta.steps), len(self.pasta.instructions))
        self.assertEqual(len(self.tart.steps), len(self.tart.instructions))
        self.assertEqual(len(self.cake.steps), len(self.cake.instructions))
        self.assertEqual(len(self.bread.steps), len(self.bread.instructions))
        self.assertEqual(len(self.pancake.steps), len(self.pancake.instructions))
        self.assertEqual(len(self.aloo.steps), len(self.aloo.instructions))

    def test_image_and_delete(self):
        pasta_image_file = os.path.join(os.getcwd(), 'pdfs', self.pasta.title + '.png')
        tart_image_file = os.path.join(os.getcwd(), 'pdfs', self.tart.title + '.png')
        cake_image_file = os.path.join(os.getcwd(), 'pdfs', self.cake.title + '.png')
        bread_image_file = os.path.join(os.getcwd(), 'pdfs', self.bread.title + '.png')
        pancake_image_file = os.path.join(os.getcwd(), 'pdfs', self.pancake.title + '.png')
        aloo_image_file = os.path.join(os.getcwd(), 'pdfs', self.aloo.title + '.png')

        self.assertTrue(os.path.isfile(pasta_image_file))
        self.assertTrue(os.path.isfile(tart_image_file))
        self.assertTrue(os.path.isfile(cake_image_file))
        self.assertTrue(os.path.isfile(bread_image_file))
        self.assertTrue(os.path.isfile(aloo_image_file))

        os.remove(pasta_image_file)
        os.remove(tart_image_file)
        os.remove(cake_image_file)
        os.remove(bread_image_file)
        os.remove(pancake_image_file)
        os.remove(aloo_image_file)


if __name__ == '__main__':
    unittest.main()
