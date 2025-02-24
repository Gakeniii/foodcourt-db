from app import app
from models import db, User, Outlet, OwnerMenu, MenuItem, Order, TableBooking
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
from sqlalchemy.dialects.postgresql import insert
from faker import Faker
import random


booking_time = datetime.now(timezone.utc) + timedelta(days=random.randint(1, 10), hours=random.randint(1, 24))

categories = ['Starter', 'Main Course', 'Dessert', 'Kids Menu', 'Snacks', 'Drinks']
cuisines = ['Italian', 'Japanese', 'Indian', 'American', 'French', 'Mexican', 'Chinese', 'Swahili', 'Malasyian','Turkish', 'Congolese']

outlet_data = [
    {"name": "Sapori d'Italia",
     "image_url": "https://images.pexels.com/photos/17588091/pexels-photo-17588091/free-photo-of-pasta-and-cake-on-table.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
     "menus":{
         "Starter": [
             {"name": "Cacio e pepe", "price": 700, "image_url": "https://media-cldnry.s-nbcnews.com/image/upload/t_fit-1000w,f_avif,q_auto:eco,dpr_2/newscms/2022_13/1859297/cacio-e-pepe-mc-2x1-220331.jpg", "cuisine": "Italian", "description": "Simple pasta", "waiting": 5},
             {"name": "Bruschetta", "price": 650, "image_url": "https://www.walderwellness.com/wp-content/uploads/2024/05/Burrata-Bruschetta-Walder-Wellness-5-1024x1536.jpg", "cuisine": "Italian", "description": "Grilled bread topped with garlic, olive oil and salt, served with toppings of tomatoes, vegetables, cured meat and cheese", "waiting": 10},
             {"name": "Caprese Salad", "price": 600, "image_url": "https://www.thespruceeats.com/thmb/2pjgFA7_nbZtlXr68BECvf6fO48=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/caprese-salad-tomato-salad-2217097-hero-03-75a0b89b30aa4a52b10fe4fdd9abfeb5.jpg", "cuisine": "Italian", "description": "Perfectly ripe tomatoes combines with stretchy mozzarella and fresh basil leaves", "waiting": 10},
             {"name": "Panzanella", "price": 500, "image_url": "https://www.onceuponachef.com/images/2019/08/Panzanella-Salad-1-1200x1500.jpg", "cuisine": "Italian", "description": "Sourdough bread freshened up with olive oil, fresh tomatoes, anchovies, black olives and torn basil", "waiting": 10},
             {"name": "Focaccia", "price": 450, "image_url": "https://www.feastingathome.com/wp-content/uploads/2024/10/focaccia-5-1.jpg", "cuisine": "Italian", "description": "Springy Italian bread dotted with fresh rosemary sprigs, sprinkled with flaky sea salt", "waiting": 6}
         ],
         "Main Course": [
             {"name": "Margharita Pizza", "price": 1200, "image_url": "https://images.pexels.com/photos/30737921/pexels-photo-30737921/free-photo-of-top-view-of-delicious-cheese-pizza-on-wooden-board.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "Italian", "description": "Classic Margherita pizza with fresh tomatoes, mozzarella, and basil.", "waiting": 15},
             {"name": "Chicken Scarpariello", "price": 2500, "image_url": "https://www.foodandwine.com/thmb/P5Vs7pUOnUKWuuX_1ro191x4BRc=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Chicken-Scarpariello-FT-RECIPE1023-c6c5d4c72b1f4c66bd8276106447c988.jpg", "cuisine": "Italian", "description": "Sauteed chicken in tangy lemon glaze with sweet pickeled bell peppers", "waiting": 20},
             {"name": "Italian Wedding Risotto", "price": 1850, "image_url": "https://www.foodandwine.com/thmb/a_r5T2LVyBlOe3s73zq1ZoHA6bc=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/FAW-recipes-italian-wedding-risotto-hero-01-f9c6681cf49f4b958882d2fb84acc61d.jpg", "cuisine": "Italian", "description": "Italian weeding soup, served with garlicky meatball and spinach risotto, drizzled with olive oil and grated parmesean and Parlsey", "waiting": 25},
             {"name": "Pasta Cabonara", "price": 1900, "image_url": "image_url", "cuisine": "Italian", "description": "Traditional Roman pasta made with spaghetti, eggs, pancetta, Pecorino cheese and black pepper", "waiting": 20},
             {"name": "Saltimbocca alla Romana", "price": 2500, "image_url": "https://images.immediate.co.uk/production/volatile/sites/57/2024/06/100620241718011871.jpeg", "cuisine": "Italian", "description": "Thin slices of veal wrapped with prosciutto and sage, pan-fried in butter and fine wine, with bold aromatic flavours", "waiting": 20}  
         ],
         "Dessert": [
             {"name": "Tiramisu", "price": 500, "image_url": "https://butternutbakeryblog.com/wp-content/uploads/2024/05/classic-tiramisu.jpg", "cuisine": "Italian", "description": "layers of espresso soaked ladyfingers, mascarpone cheese,cocoa powder and a hint of liquer. It has a creamy rich texture and a balance of coffee and sweetness", "waiting": 7},
             {"name": "Cannoli", "price": 650, "image_url": "https://hips.hearstapps.com/hmg-prod/images/cannoli-lead-66a82050a2a8e.jpg?resize=640:*", "cuisine": "Italian", "description": "Fried tube like shells filled with a sweet ricotta-based cream", "waiting": 20},
         ],
         "Kids Menu": [
             {"name": "Mini Pizza", "price": 800, "image_url": "https://www.littlesugarsnaps.com/wp-content/uploads/2021/07/Pizzette-featured-Image-.jpg", "cuisine": "Italian", "waiting": 10},
             {"name": "Cheese Ricotta", "price": 2500, "image_url": "https://media-cldnry.s-nbcnews.com/image/upload/t_social_share_1200x630_center,f_auto,q_auto:best/newscms/2023_37/2030421/honeymoon-cheese-and-herb-ravioli-mc-2x1-230911.jpg", "cuisine": "Italian", "description": "Sauteed chicken in tangy lemoon glaze with sweet pickeled bell peppers", "waiting": 20},
         ],
         "Snacks": [
             {"name": "Arancini", "price": 400, "image_url": "https://www.andy-cooks.com/cdn/shop/articles/20240912032016-andy-20cooks-20-20arancini-20ragu-20e-20piselli_da7d7d2f-d828-4ca8-80cd-c11b12807bc4.jpg?v=1726642856", "cuisine": "Italian", "description": "Golden fried rice balls stiffed with mozzarella", "waiting": 5},
             {"name": "Suppli", "price": 500, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRb-hSd6-V1C_bXbqe0_p3exdrx7jX3zbOBCQ&s", "cuisine": "Italian", "description": "Fried croquettes filled with ham, mozzarella and tomatoes", "waiting": 6},
         ],
         "Drinks": [
             {"name": "Espresso", "price": 300, "image_url": "https://blogstudio.s3.theshoppad.net/coffeeheroau/ec178d83e5f597b162cda1e60cb64194.jpg", "cuisine": "Italian", "description": "Concentrated coffee", "waiting": 3},
             {"name": "Aperol Spitz", "price": 1000, "image_url": "https://agratefulmeal.com/wp-content/uploads/2023/02/aperol-spritz-cocktail-featured.jpg", "cuisine": "Italian", "description": "Cocktail made with, Aperol,prsecco and a splash of soda water", "waiting": 20},
             {"name": "Limoncello", "price": 1100, "image_url": "https://www.threeolivesbranch.com/wp-content/uploads/2020/12/amalfi-martini-limoncello-gin-cocktail-threeolivesbranch-5-768x1024.jpg", "cuisine": "Italian", "description": "Sweet and tangy lemon liquer", "waiting": 20},
         ]
     }
    },

    {"name": "Kai Sushi Place", "image_url": "https://images.pexels.com/photos/3147493/pexels-photo-3147493.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
     "menus": {
         "Starter": [
             {"name": "Edamame", "price": 500, "image_url": "https://www.peanutbutterandfitness.com/wp-content/uploads/2023/07/Sweet-Spicy-Garlic-Edamame-Recipe-2.jpg", "cuisine": "Japanese", "decsription":"foodie eats", "waiting": 5},
             {"name": "Miso Soup", "price": 450, "image_url": "https://ik.imagekit.io/webtactics/changs/tr:w-750,h-1000/cgblog/id384/Chicken-Miso-Soup-3.jpg", "cuisine": "Japanese", "decsription":"foodie eats", "waiting": 4}
         ],
         "Main Course": [
             {"name": "Sushi Platter", "price": 3200, "image_url": "https://images.pexels.com/photos/3763816/pexels-photo-3763816.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "Japanese", "category": "Main Course","description": "Assorted sushi platter with fresh salmon, tuna, and avocado rolls.", "waiting": 20},
             {"name": "Teriyaki Beef", "price": 1100, "image_url": "https://simplehomeedit.com/wp-content/uploads/2023/11/Speedy-Beef-Teriyaki-9.webp", "cuisine": "Japanese", "decsription":"Grilled meat glazed with sweet soy sauce", "waiting": 10},
             {"name": "Tuna Sashimi", "price": 1250, "image_url": "https://getfish.com.au/cdn/shop/articles/Step_3_-_Tuna_Sashimi.png?v=1717040042", "cuisine": "Japanese", "decsription":"Sliced raw fish, served with soy sauce", "waiting": 12}
         ],
         "Dessert": [
              {"name": "Green Tea Ice Cream", "price": 300, "image_url": "https://foodbyjonister.com/wp-content/uploads/2016/08/gtmatcha.jpg", "cuisine": "Japanese", "decsription":"Sweet Matcha ice cream", "waiting": 5},
              {"name": "Mochi", "price": 450, "image_url": "https://jasmineandtea.com/wp-content/uploads/2021/06/ice-cream-mochi-768x1024.jpg", "cuisine": "Japanese", "decsription":"Soft chewy dumplings filled with red bean paste", "waiting": 5}
         ],
         "Kids Menu": [
             {"name": "Kid's Sushi Roll", "price": 700, "image_url": "https://kidseatincolor.com/wp-content/uploads/2022/04/Avocado-Sushi-Roll.jpg", "cuisine": "Japanese", "decsription":"foodie eats", "waiting": 8},
             {"name": "Onigiri", "price": 450, "image_url": "ghttps://moribyan.com/wp-content/uploads/2023/01/IMG_8680-2-735x1024.jpg", "cuisine": "Japanese", "decsription":"Rice balls with Tuna or Salmon fillings", "waiting": 5}
         ],
         "Snacks": [
             {"name": "Tempura", "price": 800, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRG09VdSKMlO8VhwgFLSZQRZhg_fAvYPKwT5Q&s", "cuisine": "Japanese", "decsription":"Deep fried Tempura", "waiting": 17},
             {"name": "Taiyaki", "price": 650, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR1jRLprtwTQ-OQDzpoRJUDrB0aoUsBnPbezg&s", "cuisine": "Japanese", "decsription":"Fish pastry filled with red bean paste", "waiting": 15}
         ],
         "Drinks": [
             {"name": "Matcha Latte", "price": 300, "image_url": "https://munchingwithmariyah.com/wp-content/uploads/2020/06/IMG_0748.jpg", "cuisine": "Japanese", "decsription":"Matcha espresso", "waiting": 5},
             {"name": "Sakura Tea", "price": 200, "image_url": "https://c8.alamy.com/comp/TD3H9G/cherry-blossom-tea-cup-of-fresh-pink-cherry-blossom-tea-and-cherry-blossoms-on-the-table-TD3H9G.jpg", "cuisine": "Japanese", "decsription":"Made with cherry blossom petals", "waiting": 10}
         ]
     }
    },

    {"name": "Mayora Indian cuisine", "image_url": "https://images.pexels.com/photos/28125427/pexels-photo-28125427/free-photo-of-naan-roti-tarkari-everest-tandoori-kitchen.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "menus": {
         "Starter": [
             {"name": "Samosa", "price": 250, "image_url": "https://satyamskitchen.com/wp-content/uploads/2021/05/website-700x525.jpg", "cuisine": "Indian", "description": "Deep fried pastry with mince meat stuffings", "waiting": 5},
             {"name": "Pan Puri", "price": 400, "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Pani_Puri1.JPG", "cuisine": "Indian", "description": "Deep fried balls with meat filling", "waiting": 9}
         ],
         "Main Course": [
             {"name": "Butter Chicken", "price": 1200, "image_url": "https://foodess.com/wp-content/uploads/2022/10/Foodess-Best-Butter-Chicken-1-2.jpg", "cuisine": "Indian","description": "Grilled chicken made with yoghurt and spices", "waiting": 25},
             {"name": "Goan Fish Curry", "price": 1000, "image_url": "https://satyamskitchen.com/wp-content/uploads/2021/05/website-700x525.jpg", "cuisine": "Indian", "description": "Coastal flavours and aromas", "waiting": 20},
             {"name": "Wazwan", "price": 1100, "image_url": "https://img.atlasobscura.com/b8dKI3n1Fm8gDa1jsKufrb8u65MJqteJqYuosNeWiXw/rs:fill:580:580:1/g:ce/q:81/sm:1/scp:1/ar:1/aHR0cHM6Ly9hdGxh/cy1kZXYuczMuYW1h/em9uYXdzLmNvbS91/cGxvYWRzL3RoaW5n/X2ltYWdlcy9iZjBh/NjQzNC03YzQyLTQ3/ZDktYjQxYi03NTkw/ZmFhNDIxMjlmYjU2/ZmU4ZmQyOTBjYzIw/Mzdfd2F6d2FuX21h/cnJ5YW1fMi5qcGc.jpg", "cuisine": "Indian", "description": "Roasted Lamb made with dreid fruits", "waiting": 25}
         ],
         "Desert": [
              {"name": "Jalebi", "price": 400, "image_url": "https://i0.wp.com/binjalsvegkitchen.com/wp-content/uploads/2023/10/Instant-Jalebi-H3.jpg?resize=600%2C904&ssl=1", "cuisine": "Indian", "description": "Deep fried, crisp sweets soaked in saffron infused sugar", "waiting": 5},
              {"name": "Kulfi", "price": 400, "image_url": "https://thebigmansworld.com/wp-content/uploads/2022/07/kulfi-ice-cream-recipe.jpg", "cuisine": "Indian", "description": "Ice cream with cardamon, saffron and pistachios", "waiting": 9}
         ],
         "Kids Menu": [
             {"name": "Butter Chicken", "price": 1000, "image_url": "https://foodess.com/wp-content/uploads/2022/10/Foodess-Best-Butter-Chicken-1-2.jpg", "cuisine": "Indian", "description": "Grilled chicken made with yoghurt and spices served with Naan", "waiting": 8},
             {"name": "Pan Puri", "price": 400, "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Pani_Puri1.JPG", "cuisine": "Indian", "description": "Deep fried balls with meat filling", "waiting": 9}
         ],
         "Snacks": [
             {"name": "Bhajia", "price": 600, "image_url": "https://www.jayne-rain.com/wp-content/uploads/2020/01/potato-bhajia-5.jpg", "cuisine": "Indian", "description": "Deep fried potatoes", "waiting": 10},
             {"name": "Dhokla", "price": 400, "image_url": "https://rakskitchen.net/wp-content/uploads/2011/09/khaman-besan.jpg", "cuisine": "Indian", "description": "Steamed cakecserved with green chutney", "waiting": 10}
         ],
         "Drinks": [
             {"name": "Masala chai", "price": 450, "image_url": "https://cdn.shopify.com/s/files/1/0528/5173/6769/files/1080-X-683-pxl-A12.jpg?v=1654750025", "cuisine": "Indian", "description": "Black tea spiced with cardamon, cinnamon, black pepper and cloves", "waiting": 5},
             {"name": "Laasi", "price": 400, "image_url": "https://assets.bonappetit.com/photos/6046f566051c297ccfc14827/1:1/w_2560%2Cc_limit/Holi-Mango-Lassi.jpg", "cuisine": "Indian", "description": "Thick Yoghurt flavoured with fruits", "waiting": 5}
         ]
        }
    },

    {"name": "Steak House Supreme", "image_url": "https://images.pexels.com/photos/236887/pexels-photo-236887.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "menus": {
         "Starter": [
             {"name": "Shrimp cocktails", "price": 1450, "image_url": "https://www.foodandwine.com/thmb/eJbvl3xF29aslGsseo5ekZrmL0s=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Dirty-Martini-Shrimp-Cocktail-FT-Recipe0624-17d9fd13705a402da5d673053929ba6a.jpg", "cuisine": "American", "description": "Chilled shrimp served with cocktail horseradish sauce", "waiting": 10},
             {"name": "Stuffed Mushrooms", "price": 1000, "image_url": "https://natashaskitchen.com/wp-content/uploads/2023/12/stuffed-mushrooms-sq.jpg", "cuisine": "American", "description": "Mushrooms filled cheese, garlic, bradcrumbs and herbs", "waiting": 10}
         ],
         "Main Course": [
             {"name": "Ribeye Steak", "price": 1200, "image_url": "https://tatyanaseverydayfood.com/wp-content/uploads/2019/06/Ribeye-Steak-Dinner-4-of-4-768x1024.jpg", "cuisine": "American","description": "Beef griled to perfection served with mashed potatoes or vegetables", "waiting": 25},
             {"name": "Porterhouse Steak", "price": 1000, "image_url": "https://d21klxpge3tttg.cloudfront.net/wp-content/uploads/2021/03/Reverse-seared-porterhouse-poblano-crema.jpg", "cuisine": "American", "description": "Large cut of tenderloin and strip steak", "waiting": 20},
             {"name": "T-Bone steak", "price": 1100, "image_url": "https://richmeats.capetown/wp-content/uploads/2017/03/T-Bone-1.jpg", "cuisine": "American", "description": "Tenderloin grilled to perfetion", "waiting": 25}
         ],
         "Desert": [
              {"name": "Cheese cake", "price": 700, "image_url": "https://www.lecremedelacrumb.com/wp-content/uploads/2019/03/steak-potatoes-skillet-3.jpg", "cuisine": "American", "description": "Creamy cheesecake topped with fruit, caramel and chocolate sauce", "waiting": 5},
              {"name": "Creme Brulee", "price": 800, "image_url": "https://www.lecremedelacrumb.com/wp-content/uploads/2019/03/steak-potatoes-skillet-3.jpg", "cuisine": "American", "description": "Silky  custard topped with a layer of caramelized sugar", "waiting": 9}
         ],
         "Kids Menu": [
             {"name": "Mini Steaks", "price": 1000, "image_url": "https://www.lecremedelacrumb.com/wp-content/uploads/2019/03/steak-potatoes-skillet-3.jpg", "cuisine": "American", "description": "Mini steaks", "waiting": 8},
             {"name": "Chicken tenders", "price": 800, "image_url": "https://www.lecremedelacrumb.com/wp-content/uploads/2019/03/steak-potatoes-skillet-3.jpg", "cuisine": "American", "description": "Crisp breaded chicken strips", "waiting": 10}
         ],
         "Snacks": [
             {"name": "Mini Quesadillas", "price": 600, "image_url": "https://s23209.pcdn.co/wp-content/uploads/2022/05/Mini-Chicken-Quesadillas211015_DAMN-DELICIOUS_Mini-Chicken-Quesadillas_030-760x1140.jpg", "cuisine": "American", "description": "Small cheesy tortillas", "waiting": 10},
             {"name": "Fruit kabobs", "price": 400, "image_url": "https://i2.wp.com/lmld.org/wp-content/uploads/2024/02/Rainbow-Fruit-Skewers-10.jpg", "cuisine": "American", "description": "Skewed pieces of fresh fruit", "waiting": 10}
         ],
         "Drinks": [
             {"name": "Lemonade", "price": 550, "image_url": "https://images.squarespace-cdn.com/content/v1/5ed13dd3465af021e2c1342b/a5b1e544-ee89-4268-b9af-ab49e9cc7006/IMG_1986+%281%29.jpg", "cuisine": "American", "description": "Creamy drink made with ice cream and milk", "waiting": 5},
             {"name": "Strawberry Margarita", "price": 900, "image_url": "https://creative-culinary.com/wp-content/uploads/strawberry-margarita-1.jpg", "cuisine": "American", "description": "Cocktail made with tequila, lime and orange liquer", "waiting": 5}
         ]
        }
    },

    {"name": "L'Atelier de paris", "image_url": "https://www.themanual.com/wp-content/uploads/sites/9/2021/06/french-cuisine-featured-image.jpg?fit=1340%2C782&p=1",
        "menus": {
         "Starter": [
             {"name": "Escargot de Bourgogne", "price": 2500, "image_url": "https://images.sbs.com.au/dims4/default/628e6ba/2147483647/strip/true/crop/1200x675+0+63/resize/1280x720!/quality/90/?url=http%3A%2F%2Fsbs-au-brightspot.s3.amazonaws.com%2Fdrupal%2Ffood%2Fpublic%2Fimg_7379-snails.jpg", "cuisine": "French", "description": "Snails cooked in butter, parley and wine", "waiting": 10},
             {"name": "French Onion soup", "price": 600, "image_url": "https://www.gimmesomeoven.com/wp-content/uploads/2015/01/French-Onion-Soup-Recipe-1-1.jpg", "cuisine": "French", "description": "Savoory soup with caramelized onions", "waiting": 10}
         ],
         "Main Course": [
             {"name": "Coq au vin", "price": 2800, "image_url": "https://images.immediate.co.uk/production/volatile/sites/30/2012/01/coq-au-vin-3740fe3.jpg?resize=768,574", "cuisine": "French","description": "Braised chicken in red wine, mushrooms, onions and garlic", "waiting": 25},
             {"name": "Ratatouille", "price": 3300, "image_url": "https://cdn.apartmenttherapy.info/image/upload/f_jpg,q_auto:eco,c_fill,g_auto,w_1500,ar_1:1/k%2FPhoto%2FRecipes%2F2024-07-ratatouille%2FRatatouille-", "cuisine": "French", "description": "Vegetable stew of zuchinni, eggplant, among others flavured with herbs", "waiting": 20},
             {"name": "Duck Confit", "price": 2100, "image_url": "https://www.sevenhillswinery.com/wp-content/uploads/2019/09/duck-confit_1920x900.jpg", "cuisine": "French", "description": "Duck leg slow-cooked in its own fat until tender", "waiting": 25}
         ],
         "Desert": [
              {"name": "Tarte Tatin", "price": 700, "image_url": "https://media-cdn2.greatbritishchefs.com/media/ioskqxie/img12633.jpg", "cuisine": "French", "description": "Caramelized upside down apple tart served with a scoop of ice-cream", "waiting": 15},
              {"name": "Mousse au Chocolat", "price": 800, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSVn5rJ-St5NCU3ChfItjxjdW9NrqXDVsBHCQ&s", "cuisine": "French", "description": "A fluffy chocolate mousse", "waiting": 9}
         ],
         "Kids Menu": [
             {"name": "Mini Steaks", "price": 1000, "image_url": "https://www.lecremedelacrumb.com/wp-content/uploads/2019/03/steak-potatoes-skillet-3.jpg", "cuisine": "French", "description": "Mini steaks", "waiting": 8},
             {"name": "Chicken tenders", "price": 800, "image_url": "https://www.lecremedelacrumb.com/wp-content/uploads/2019/03/steak-potatoes-skillet-3.jpg", "cuisine": "French", "description": "Crisp breaded chicken strips", "waiting": 10}
         ],
         "Snacks": [
             {"name": "Pomme Frites", "price": 600, "image_url": "https://www.joyfulhealthyeats.com/wp-content/uploads/2023/03/Crispy-Air-Fryer-Pomme-Frites-web-12.jpg", "cuisine": "French", "description": "Crispy french fries", "waiting": 10},
             {"name": "Gratin Dauphinois", "price": 400, "image_url": "https://www.delscookingtwist.com/wp-content/uploads/2019/04/French-Gratin-Dauphinois_6.jpg", "cuisine": "French", "description": "thily slicd potatoes, milk, cheese and cream cheese", "waiting": 10}
         ],
         "Drinks": [
             {"name": "Wine", "price": 950, "image_url": "https://winery.ph/cdn/shop/articles/WPH_Blog_Hero_Graphics_1_1500x901.jpg?v=1620291667", "cuisine": "French", "description": "Red White or Mulled", "waiting": 5},
             {"name": "Kir Royale", "price": 900, "image_url": "https://www.lemontreedwelling.com/wp-content/uploads/2023/05/kir-royale-featured.jpg", "cuisine": "French", "description": "Cocktail made with creme de cassis and champagne effect", "waiting": 5}
         ]
        }
    },

    {"name": "Casa de Sabor", "image_url": "https://www.facts-about-mexico.com/wp-content/uploads/2022/01/shutterstock-lunamaria-1080x675.jpg",
        "menus": {
         "Starter": [
             {"name": "Guacamole", "price": 250, "image_url": "https://californiaavocado.com/wp-content/uploads/2020/07/Guacamole-Autentico-1.jpeg", "cuisine": "Mexican", "description": "Creamy dip made fromavocadoes, tomatoes and onions", "waiting": 10},
             {"name": "Queso fundido", "price": 500, "image_url": "https://www.budgetbytes.com/wp-content/uploads/2023/01/Queso-Fundido-V1.jpg", "cuisine": "Mexican", "description": "Melted cheese served with chorio or mushrooms", "waiting": 10}
         ],
         "Main Course": [
             {"name": "Enchiladas", "price": 1200, "image_url": "https://images.immediate.co.uk/production/volatile/sites/30/2024/02/BeefEnchiladas-68c9381.jpg", "cuisine": "Mexican","description": "Corn tortillas filled wit meat, cheese or beans", "waiting": 25},
             {"name": "Burritos", "price": 1500, "image_url": "https://images.themodernproper.com/production/posts/BreakfastBurritos_13.jpg?w=1200&q=82&auto=format&fit=crop&dm=1712004278&s=74d57595cd6412657b898c59bb8f17dd", "cuisine": "Mexican", "description": "Large tortilla wrapped stuffed.", "waiting": 20},
             {"name": "Chiles Rellenos", "price": 1850, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSU5gfAV3U88Z34QnEV_yJYKNjJfbPLm2fApw&s", "cuisine": "Mexican", "description": "Roasted poblano peppers stuffed with cheese or meat", "waiting": 25}
         ],
         "Desert": [
              {"name": "Churros", "price": 700, "image_url": "https://hips.hearstapps.com/hmg-prod/images/churros-index-661d4692d05e4.jpg?crop=0.8888888888888888xw:1xh;center,top&resize=1200:*", "cuisine": "Mexican", "description": "Freid dough pastries coated with cinnamon sugar", "waiting": 5},
              {"name": "Tres Leche Cake", "price": 800, "image_url": "https://www.rainbownourishments.com/wp-content/uploads/2022/04/vegan-tres-leches-cake-1.jpg", "cuisine": "Mexican", "description": "A moist cake soaked in mixture of milk", "waiting": 9}
         ],
         "Kids Menu": [
             {"name": "Soft Tacos", "price": 1000, "image_url": "https://www.bama.no/siteassets/fotoware/2022/12/bama-sotpotettaco-05763.jpg?width=750&height=750&mode=crop", "cuisine": "Mexican", "description": "soft tortillas", "waiting": 8},
             {"name": "Tamales", "price": 800, "image_url": "https://keviniscooking.com/wp-content/uploads/2023/08/Pork-Tamales-Rojos-sauce.jpg", "cuisine": "Mexican", "description": "Doudh filled with cheese or shredded chicken", "waiting": 10}
         ],
         "Snacks": [
             {"name": "Mexican Rice", "price": 600, "image_url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fdamndelicious.net%2F2014%2F03%2F12%2Fmexican-rice%2F&psig=AOvVaw0zu3fxgcE1fUDWsJ7c_vPZ&ust=1740324321704000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCJji77jL14sDFQAAAAAdAAAAABAE", "cuisine": "Mexican", "description": "Fluffy rice", "waiting": 10},
             {"name": "Pico de Gallo", "price": 400, "image_url": "https://cookieandkate.com/images/2018/09/best-pico-de-gallo-recipe-2.jpg", "cuisine": "Mexican", "description": "Fresh salsa made from tomatoes, onions, cilantro, lime and chilli", "waiting": 10}
         ],
         "Drinks": [
             {"name": "Horchata", "price": 550, "image_url": "https://www.foodandwine.com/thmb/fa4Ny43jN22ouDZKSNAMN4Dqu_Q=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Horchata-Explainer-FT-BLOG0923-7b252e8f459f43c29655339daeb62a82.jpg", "cuisine": "Mexican", "description": "Sweet, creamy drink made from rice, cinnamon and vanilla, served cold", "waiting": 5},
             {"name": "Aqua Fresca", "price": 900, "image_url": "https://www.shape.com/thmb/7MZzTVFIq-WQJm3rsh3d_Rdi9pc=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/agua-fresca-shutterstock_2023599671-2000-aadf4aef373740dfa2bbaeb3cd88278c.jpg", "cuisine": "Mexican", "description": "Made from fruits mixed with water, refreshing", "waiting": 5}
         ]
        }
    },

    {"name": "Chun Li's Chinese Delicacies", "image_url": "https://images.chinahighlights.com/allpicture/2021/12/71879439c9ef4d0da835efb6_cut_750x400_39.jpg",
     "menus": {
         "Starter": [
             {"name": "Spring rolls", "price": 400, "image_url": "https://saltedmint.com/wp-content/uploads/2024/01/Vegetable-Spring-Rolls-4-500x375.jpg", "cuisine": "Chinese", "decsription":"Crispy rolls with filling", "waiting": 5},
             {"name": "Dumplings", "price": 500, "image_url": "https://thebigmansworld.com/wp-content/uploads/2023/02/chicken-chow-mein-recipe.jpg", "cuisine": "Chinese", "decsription":"Pork fillings", "waiting": 4}
         ],
         "Main Course": [
             {"name": "Chow mein", "price": 1900, "image_url": "https://thebigmansworld.com/wp-content/uploads/2023/02/chicken-chow-mein-recipe.jpg", "cuisine": "Chinese","description": "Stir fried noodles with vegetables and meat of choice", "waiting": 20},
             {"name": "Sweet and Sour Pork", "price": 2100, "image_url": "https://iankewks.com/wp-content/uploads/2023/10/IMG_0299.jpg", "cuisine": "Chinese", "decsription":"Crsipy pork buttered in a sweet and sour sauce", "waiting": 10},
             {"name": "Mapo Tofu", "price": 1250, "image_url": "https://omnivorescookbook.com/wp-content/uploads/2022/05/220510_Mapo-Tofu_550.jpg", "cuisine": "Chinese", "decsription":"Soft tofu and minced pork in a spicy flavourful sauce", "waiting": 12}
         ],
         "Dessert": [
              {"name": "Fortune cookies", "price": 100, "image_url": "https://lilluna.com/wp-content/uploads/2021/09/fortune-cookies-resize-6.jpg", "cuisine": "Chinese", "decsription":"Cookies with a small fortune message inside", "waiting": 5},
              {"name": "Chinese Almond cookies", "price": 350, "image_url": "https://lilluna.com/wp-content/uploads/2021/09/fortune-cookies-resize-6.jpg", "cuisine": "Chinese", "decsription":"Cookies with almond filling", "waiting": 5}
         ],
         "Kids Menu": [
             {"name": "Steamed Buns", "price": 700, "image_url": "https://omnivorescookbook.com/wp-content/uploads/2021/07/210714_Steamed-Pork-Buns-with-Chive_550.jpg", "cuisine": "Chinese", "decsription":"foodie eats", "waiting": 8},
             {"name": "Beef", "price": 450, "image_url": "https://www.beyondkimchee.com/wp-content/uploads/2022/09/Crispy-Beef-thumbnail.jpg", "cuisine": "Chinese", "decsription":"foodie eats", "waiting": 5}
         ],
         "Snacks": [
             {"name": "Egg fried rice", "price": 800, "image_url": "https://cjeatsrecipes.com/wp-content/uploads/2024/10/Egg-Fried-Rice-on-a-plate-1200x1800.jpg", "cuisine": "Chinese", "decsription":"Rice stir fried in eggs, vegs and light seasoning", "waiting": 17},
             {"name": "Chinese Broccoli in Oyster Sauce", "price": 750, "image_url": "https://apinchofsaffron.nl/wp-content/uploads/2024/05/22A1723.jpg", "cuisine": "Chinese", "decsription":"Broccoli cooked in oyster sauce", "waiting": 15}
         ],
         "Drinks": [
             {"name": "Apple Juice", "price": 300, "image_url": "https://images.prismic.io/goodnature/ZDIxNjE5ZTAtYjlhMi00ZTlmLTkxNTktODZiODA1YzkxNmFh_apple-juice-hero.jpg?auto=compress,format&rect=0,0,1200,628&w=1200&h=628", "cuisine": "Chinese", "decsription":"Freshly juiced apple juice", "waiting": 5},
             {"name": "Milk tea", "price": 200, "image_url": "https://teacultureoftheworld.com/cdn/shop/articles/taiwan-milk-tea-with-boba-bubble-pearl-on-plastic-2024-02-05-02-27-11-utc_2191x.jpg?v=1714023533", "cuisine": "Chinese", "decsription":"Traditional tea with boba pearls", "waiting": 10}
         ]
     }
    },

        {"name": "Chez Flore", "image_url": "https://blog.catchyz.com/wp-content/uploads/2021/03/congo-food.jpg",
     "menus": {
         "Starter": [
             {"name": "Makemba", "price": 500, "image_url": "https://mayvegrill.com/wp-content/uploads/2020/10/Makemba-820x450.jpg", "cuisine": "Congolese", "decsription":"Sliced plantains fried until golden and crispy", "waiting": 5},
             {"name": "Chkwangue", "price": 550, "image_url": "https://www.osina.ch/photo/data/chikwangue-kwanga-500-g-gemuese-gefroren-gemuese-fruechte-398-32964-4.jpg?ts=1724083354", "cuisine": "Congolese", "decsription":"Fermented Cassava dough, wrapped in banana leaves", "waiting": 4}
         ],
         "Main Course": [
             {"name": "Moambe Chicken", "price": 3200, "image_url": "https://explorers.kitchen/wp-content/uploads/2016/01/Congo-Moambe-Chicken-13.jpg", "cuisine": "Congolese", "category": "Main Course","description": " ", "waiting": 20},
             {"name": "Fufu and Sese", "price": 1100, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRyhaZwiihLG4n5HAtw-PhkucNfvBKVl8yrIA&s", "cuisine": "Congolese", "decsription":"pounded cassava or plantains served with goat stew", "waiting": 10},
             {"name": "Poulet à la Braise", "price": 1250, "image_url": "https://warehouse.canal-overseas.com/content/0001/09/c371caca888fd57c81891893298e263618393ed9.jpeg", "cuisine": "Congolese", "decsription":"Chicken Marinated in a blend of spices grilled over an open flame.", "waiting": 12}
         ],
         "Dessert": [
              {"name": "Chin Chin", "price": 400, "image_url": "https://www.mydiasporakitchen.com/wp-content/uploads/2021/04/5B32CC1A-7B2F-4283-B22B-F90FADE6F21B.jpeg", "cuisine": "Congolese", "decsription":"Sweet crucnhy fried dough", "waiting": 5},
              {"name": "Koko", "price": 400, "image_url": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhrntoJxHTM-_TyJiEo9uaEi461VFgnj9HSdfDcpQIsOcxrYNBJdTFDAEjbM_MgBAcenihg6bORHvtf1kVLBWL398MeMlARbm-xrO3sGTZrJlZoc9DzxH3kwZWeti2PfU6m1EYh0XS8irUO/s1600/P1060866.JPG", "cuisine": "Congolese", "decsription":"Sweet smooth porridge, flavoured with vanilla or coconut milk", "waiting": 5}
         ],
         "Drinks": [
             {"name": "Palm wine", "price": 700, "image_url": "https://i0.wp.com/greenviewsresidential.com/wp-content/uploads/2023/04/palm-wine-in-ghanaian-culture.webp?resize=1080%2C608&ssl=1", "cuisine": "Congolese", "decsription":"Traditional alcoholic beverage made from sap of palm trees", "waiting": 17},
             {"name": "Jus de Bissap", "price": 650, "image_url": "https://cuisinedecheznous.net/wp-content/uploads/2022/03/bissap-du-retour.jpg", "cuisine": "Congolese", "decsription":"Sweet tangy drink made from hibiscus flowers", "waiting": 15}
         ],
         "Snacks": [
             {"name": "Kanda", "price": 300, "image_url": "https://spotcovery.com/wp-content/uploads/2023/09/Kanda-Ti-Nyma-500x417.jpg", "cuisine": "Congolese", "decsription":"Savory meatballs", "waiting": 5},
             {"name": "Baked Yams", "price": 200, "image_url": "https://thenaturalnurturer.com/wp-content/uploads/2023/04/Oven-Baked-Sweet-Potatoes-24.jpg", "cuisine": "Congolese", "decsription":"Boiled and baked yams served with a special sauce", "waiting": 10}
         ]
     }
    },

    {"name": "Derwish Restaurant", "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS-gi_e54_jQoxpKq98MR0GEnMOLVTB26scFw&s",
     "menus": {
         "Starter": [
             {"name": "Meze", "price": 500, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQyiU1jHw2RDFBugpbjMlFIYyprwOTBWdoh5w&s", "cuisine": "Turkish", "decsription":"Appetizer served with bread", "waiting": 5},
             {"name": "Sigara Böreği", "price": 450, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQt890JxIGSO1B3GEbsTXxVvAlcz1KL6zmSjg&s", "cuisine": "Turkish", "decsription":"Crisp pastry rolla", "waiting": 4}
         ],
         "Main Course": [
             {"name": "Kebab", "price": 3200, "image_url": "https://cookingorgeous.com/wp-content/uploads/2021/06/lamb-shish-kebab-20.jpg", "cuisine": "Turkish", "description": "Grilled meat on a Skewer", "waiting": 20},
             {"name": "Lahmacun", "price": 1100, "image_url": "https://simplehomeedit.com/wp-content/uploads/2023/11/Speedy-Beef-Teriyaki-9.webp", "cuisine": "Turkish", "decsription":"Turkish pizza", "waiting": 30},
             {"name": "Manti", "price": 1250, "image_url": "https://www.panningtheglobe.com/wp-content/uploads/2013/11/turkish-manti-web-final.jpg", "cuisine": "Turkish", "decsription":"Turkish dumplings filled with mined meat", "waiting": 20}
         ],
         "Dessert": [
              {"name": "Kunefe", "price": 800, "image_url": "https://gastronomytours.com/wp-content/uploads/2023/09/kiounefe-com-600x377.jpg", "cuisine": "Turkish", "decsription":"Sweetened cheese and pastry", "waiting": 25},
              {"name": "Baklava", "price": 950, "image_url": "https://cleobuttera.com/wp-content/uploads/2018/03/lifted-baklava-720x540.jpg", "cuisine": "Turkish", "decsription":"layers of thin flaky pastries with crushed pistachios", "waiting": 20}
         ],
         "Kids Menu": [
             {"name": "Ayran", "price": 700, "image_url": "https://bakkali.app/cdn/shop/articles/Ayran1-be64bf78.jpg?v=1713563298&width=1600", "cuisine": "Turkish", "decsription":"Sweet refreshing yoghurt drink", "waiting": 8},
             {"name": "Kofte", "price": 650, "image_url": "https://images.getrecipekit.com/20221019021205-ko-cc-88fte-20baharat-20kebabs.jpg?aspect_ratio=1:1&quality=90&", "cuisine": "Turkish", "decsription":"Flavourful meatballs", "waiting": 15}
         ],
         "Snacks": [
             {"name": "Pide", "price": 700, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpNvQfvhwXJjYtP2MQHp_uk5fpyxdbN97j1g&s", "cuisine": "Turkish", "decsription":"Turkish flatbread ", "waiting": 17},
             {"name": "Ezme", "price": 650, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqTe49bHJjFm6bqJ46NAQypam9U7yVs0-D3g&s", "cuisine": "Turkish", "decsription":"Sweet tangy salad made from tomatoes, onions, pepers and spices", "waiting": 15}
         ],
         "Drinks": [
             {"name": "Turkish Coffee", "price": 300, "image_url": "https://livingthegourmet.com/wp-content/uploads/2021/03/Turkish-Coffee-Ibrik-9.jpg", "cuisine": "Turkish", "decsription":" ", "waiting": 5},
             {"name": "Salgam", "price": 200, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQiBJ4nMQSUZ9mnZjZLRMqjg4S-lU0VRxRsQQ&s", "cuisine": "Turkish", "decsription":" ", "waiting": 10}
         ]
     }
    },

    {"name": "Malasyian Bites", "image_url": "https://www.namesnack.com/images/namesnack-malaysian-restaurant-business-names-3264x2448-20200915.jpeg?crop=1:1,smart&width=1200&dpr=2",
     "menus": {
         "Starter": [
             {"name": "Roti Canai", "price": 300, "image_url": "https://recipeguru.org/wp-content/uploads/2024/05/roti-canai-recipe.jpg", "cuisine": "Malasyian", "decsription":"Flatbread served with spicy meat", "waiting": 5},
             {"name": "Satay", "price": 400, "image_url": "https://www.elmundoeats.com/wp-content/uploads/2024/07/Malaysian-chicken-satay-with-peanut-sauce.jpg", "cuisine": "Malasyian", "decsription":"Skewered meat", "waiting": 4}
         ],
         "Main Course": [
             {"name": "Laska", "price": 680, "image_url": "https://photos.bigoven.com/recipe/hero/chicken-laska-soup-98a9e4.jpg", "cuisine": "Malasyian", "description": "Foodie Eats", "waiting": 20},
             {"name": "Mee Goreng", "price": 1800, "image_url": "https://www.kitchensanctuary.com/wp-content/uploads/2014/06/Mee-goreng-square-FS-20.jpg", "cuisine": "Malasyian", "decsription":"Foodie eats", "waiting": 10},
             {"name": "Nasi Lemak", "price": 1450, "image_url": "https://www.elmundoeats.com/wp-content/uploads/2021/02/FP-Nasi-lemak-with-all-its-trimmings.jpg", "cuisine": "Malasyian", "decsription":"Foodie eats", "waiting": 12}
         ],
         "Dessert": [
              {"name": "Pisang Goreng", "price": 300, "image_url": "https://munchmalaysia.com/wp-content/uploads/2023/06/PisangGoreng_Ajinomoto.jpg", "cuisine": "Malasyian", "decsription":"Foodie eats", "waiting": 5},
              {"name": "Kuih", "price": 450, "image_url": "https://media.istockphoto.com/id/518885498/photo/malaysia-popular-assorted-sweet-dessert-or-known-as-kuih-kueh.jpg?s=612x612&w=0&k=20&c=481Pt0DO7IjFfRKBtXeN03RE1ZZfak3F_8UPnpFGKmM=", "cuisine": "Malasyian", "decsription":"Foodie eats", "waiting": 5}
         ],
         "Kids Menu": [
             {"name": "Roti Dhal", "price": 700, "image_url": "https://i.imgur.com/R3SSwgl.jpg", "cuisine": "Malasyian", "decsription":"foodie eats", "waiting": 8},
             {"name": "Pineapple rice", "price": 450, "image_url": "https://thai-foodie.com/wp-content/uploads/2024/04/pineapple-fried-rice.jpg", "cuisine": "Malasyian", "decsription":"Foodie eats", "waiting": 5}
         ],
         "Snacks": [
             {"name": "Murtabak", "price": 400, "image_url": "https://www.elmundoeats.com/wp-content/uploads/2021/04/FP-Whole-and-sliced-chicken-murtabak-flatbreads-stacked.jpg", "cuisine": "Malasyian", "decsription":"Foodie eats", "waiting": 17},
             {"name": "Curry puff", "price": 650, "image_url": "https://www.vegkit.com/wp-content/uploads/sites/2/2021/12/25078_ThaiCurryPuffs_detail.jpg", "cuisine": "Malasyian", "decsription":"Foodie eats", "waiting": 15}
         ],
         "Drinks": [
             {"name": "Teh Tarik", "price": 300, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRG2Sa-ENiEOGvjAnh_asO3BYgtaNrqT3XHag&s", "cuisine": "Malasyian", "decsription":"Foodie eats", "waiting": 5},
             {"name": "Air Mata Kucing", "price": 200, "image_url": "https://img.freepik.com/premium-photo/air-mata-kucing-is-famous-malaysian-drinks-juadah-ramadan-made-from-dried-longan-lo-han-kuo_581937-5181.jpg", "cuisine": "Malasyian", "decsription":"Foodie eats", "waiting": 10}
         ]
     }
    },

    {"name": "Kabudas Eats", "image_url": "https://www.nairobinationalparkkenya.com/wp-content/uploads/2024/02/132045025_1575383172669460_8723750846461443503_o-573305f0836c4744a37867458d78e888-750x450.jpg",
     "menus": {
         "Starter": [
             {"name": "Chilli prawns", "price": 500, "image_url": "https://img-global.cpcdn.com/recipes/e16e61be3886271d/1200x630cq70/photo.jpg", "cuisine": "Swahili", "decsription":"Marinated shrimp served with a tangy sauce", "waiting": 5},
             {"name": "Samosa", "price": 450, "image_url": "https://i.pinimg.com/736x/ed/a0/ed/eda0ed6d360b4f3403b93083b165a3e3.jpg", "cuisine": "Swahili", "decsription":"Deeps fried round potateos dipped in a buttery sauce", "waiting": 4}
         ],
         "Main Course": [
             {"name": "Pilau", "price": 900, "image_url": "https://img-global.cpcdn.com/recipes/e16e61be3886271d/1200x630cq70/photo.jpg", "cuisine": "Swahili", "description": "Rice dish made ith spices and meat(Beef or Goat)", "waiting": 20},
             {"name": "Biryani", "price": 800, "image_url": "https://www.pavaniskitchen.com/wp-content/uploads/2021/02/chbiryani.jpg", "cuisine": "Swahili", "decsription":"Richer than pilau, made with basmati rice and chicken", "waiting": 20},
             {"name": "Nyama Choma", "price": 1500, "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c4/Nyama_Choma_%28BBQ_the_Kenyan_way%29.jpg", "cuisine": "Swahili", "decsription":"Grilled meat typically goat, served with Ugali and kachumbari", "waiting": 30}
         ],
         "Dessert": [
              {"name": "Coconut Milk Pudding", "price": 300, "image_url": "https://img-global.cpcdn.com/recipes/04a5574be74c325d/400x400cq70/photo.jpg", "cuisine": "Swahili", "decsription":"Mixture of fruits", "waiting": 5},
              {"name": "Tropical Fruit salad", "price": 450, "image_url": "https://img-global.cpcdn.com/recipes/04a5574be74c325d/400x400cq70/photo.jpg", "cuisine": "Swahili", "decsription":"Creamy dessert made from coconut milk, sugar and cornstarch", "waiting": 5}
         ],
         "Kids Menu": [
             {"name": "Mahamri", "price": 400, "image_url": "https://img-global.cpcdn.com/recipes/04a5574be74c325d/400x400cq70/photo.jpg", "cuisine": "Swahili", "decsription":"Sweet coconut pastry", "waiting": 8},
             {"name": "Keki ya nazi", "price": 450, "image_url": "https://spicesnflavors.com/wp-content/uploads/2017/09/rose-ladoo-1-min.jpg", "cuisine": "Swahili", "decsription":"Moist coconut cake", "waiting": 5}
         ],
         "Snacks": [
             {"name": "Coconut sweets", "price": 300, "image_url": "https://spicesnflavors.com/wp-content/uploads/2017/09/rose-ladoo-1-min.jpg", "cuisine": "Swahili", "decsription":"Made from granulated sugar and water and grated coconut", "waiting": 17},
             {"name": "Kaimati", "price": 350, "image_url": "https://lh3.googleusercontent.com/proxy/UdDfWL0LUuR6Bdh8H_l4zgZLeST7tHs-GfMRSQ6m_lIW_Eytf5HWXiMYAXcw5BgAKoHNwnyLqHJiKpbWqBeIY2ueyPnT6LzFktvmJcVeMA", "cuisine": "Swahili", "decsription":"Sweet coconut pastry coated with sugar", "waiting": 15}
         ],
         "Drinks": [
             {"name": "Coconut water", "price": 300, "image_url": "https://i.ndtvimg.com/i/2017-09/coconut-water_650x400_71506595070.jpg?q=50", "cuisine": "Swahili", "decsription":"Water from the Coconut", "waiting": 5},
             {"name": "Coconut Tea", "price": 300, "image_url": "https://shoplakeandoak.com/cdn/shop/products/324066774_6155085464588219_2238385368481884744_n.jpg?v=1673988656", "cuisine": "Swahili", "decsription":"Tea made with Coconut milk", "waiting": 10}
         ]
     }
    },
]

order_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]
payment_methods = ["Apple Pay", "M-Pesa", "Cash", "Card"]

with app.app_context():
    db.drop_all()
    db.create_all()
    
    print("Database reset complete.")

    fake = Faker()

    NUM_OWNERS = 15
    NUM_CUSTOMERS = 30
    MAX_ORDERS = 40

    user_data = []
    for _ in range(NUM_OWNERS):
        user_data.append({
            "name": fake.name(),
            "email": fake.unique.email(),
            "password": generate_password_hash("owner123"),
            "role": "Owner"
        })

    for _ in range(NUM_CUSTOMERS):
        user_data.append({
            "name": fake.name(),
            "email": fake.unique.email(),
            "password": generate_password_hash("customer123"),
            "role": "Customer"
        })

    users = [User(**data) for data in user_data]
    db.session.add_all(users)
    db.session.commit()

    owners = User.query.filter_by(role='Owner').all()
    customers = User.query.filter_by(role='Customer').all()

    print(f"✅ {NUM_OWNERS} Owners and {NUM_CUSTOMERS} Customers added successfully!")

    for index, outlet in enumerate(outlet_data): 
        owner_index = index % len(owners)
        owner = owners[owner_index]
        stmt = insert(Outlet).values(
            name=outlet["name"],
            image_url=outlet["image_url"],
            owner_id=random.choice(owners).id  # Assign random owner
        ).on_conflict_do_nothing(index_elements=["name"])  # Prevent duplicates

        db.session.execute(stmt)
    
    db.session.commit()
    print("Outlets inserted without duplicates!")

    outlets = Outlet.query.all()
    menu_items = []
    for outlet in outlets:
        outlet_dict = next((o for o in outlet_data if o["name"] == outlet.name), None)
        
        if not outlet_dict:
            print(f"⚠️ No matching outlet found in outlet_data for {outlet.name}")
            continue

        if "menus" not in outlet_dict or not outlet_dict["menus"]:
            print(f"⚠️ No menus available for {outlet.name}")
            continue

        for category, items in outlet_dict["menus"].items():
            for menu_item in items:
                menu_item_db = MenuItem(
                    name=menu_item["name"],
                    price=menu_item["price"],
                    image_url=menu_item.get("image_url", ""),
                    cuisine=menu_item["cuisine"],
                    category=category,
                    waiting=menu_item["waiting"],
                    outlet_id=outlet.id
                )
                menu_items.append(menu_item_db)

    if menu_items:
        db.session.add_all(menu_items)
        db.session.commit()
        print(f"✅ {len(menu_items)} menu items successfully inserted!")
    else:
        print("❌ No menu items were added! Check outlet_data.")

    owner_menus = []
    for owner in owners:
        outlet = random.choice(outlets)
        outlet_menu_items = [item for item in menu_items if item.outlet_id == outlet.id]
        
        for menu_item in outlet_menu_items:
            owner_menu = OwnerMenu(
                owner_id=owner.id,
                outlet_id=outlet.id,
                name=menu_item.name,
                price=menu_item.price,
                image_url=menu_item.image_url,
                cuisine=menu_item.cuisine,
                category=menu_item.category,
                waiting=menu_item.waiting
            )
            owner_menus.append(owner_menu)

    db.session.add_all(owner_menus)
    db.session.commit()
    print("Database seeded successfully with OwnerMenu data!")

    orders = []
    order_count = 0

    random.shuffle(customers)
    for customer in customers:
        if order_count >= MAX_ORDERS:
            break

        num_orders = random.randint(1, 3)
        for _ in range(num_orders):
            if order_count >= MAX_ORDERS:
                break
            order = Order(
                customer_id=customer.id,
                outlet_id=random.choice(outlets).id,
                status=random.choice(order_statuses),
                table_number=random.randint(1, 20)
            )
            orders.append(order)
            order_count += 1

    db.session.add_all(orders)
    db.session.commit()
    print(f"✅Database seeded successfully with {len(orders)} Orders!")

    # order_items = []
    # for order in orders:
    #     for _ in range(random.randint(1, 3)):
    #         menu_item = random.choice(menu_items)
    #         quantity = random.randint(1, 20)
    #         total_price = float(menu_item.price) * quantity
            
    #         order_item = OrderItem(
    #             order_id=order.id,
    #             menu_item_id=menu_item.id,
    #             quantity=quantity,
    #             payment_method=random.choice(payment_methods),
    #             total_price=total_price
    #         )
    #         order_items.append(order_item)
        
    #     order.total_price = sum([item.total_price for item in order_items if item.order_id == order.id])
    
    # db.session.add_all(order_items)
    # db.session.commit()
    # print(f"✅ Database seeded successfully with {len(order_items)} Order Items data!")

    bookings = []
    for _ in range(10):
        booking_time = datetime.now(timezone.utc) + timedelta(days=random.randint(1, 10), hours=random.randint(1, 24))
        booking = TableBooking(
            customer_id=random.choice(customers).id,
            table_number=random.randint(1, 20),
            booking_time=booking_time
        )
        bookings.append(booking)
    db.session.add_all(bookings)
    db.session.commit()
    print("Database seeded successfully with Table bookings data!")

    
    print("Database seeded successfully!")