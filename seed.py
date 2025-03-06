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

    {"name": "Kai Sushi Place", "image_url": "https://labellakosher.com/wp-content/uploads/2024/09/Sushi-Platters.jpg",
     "menus": {
         "Starter": [
             {"name": "Edamame", "price": 500, "image_url": "https://www.peanutbutterandfitness.com/wp-content/uploads/2023/07/Sweet-Spicy-Garlic-Edamame-Recipe-2.jpg", "cuisine": "Japanese", "decsription":"foodie eats", "waiting": 5},
            #  {"name": "Miso Soup", "price": 450, "image_url": "https://ik.imagekit.io/webtactics/changs/tr:w-750,h-1000/cgblog/id384/Chicken-Miso-Soup-3.jpg", "cuisine": "Japanese", "decsription":"foodie eats", "waiting": 4}
         ],
         "Main Course": [
             {"name": "Sushi Platter", "price": 3200, "image_url": "https://images.stockcake.com/public/f/3/9/f39b142f-9648-46cf-8267-2d1d74b4dbf4_large/delicious-sushi-platter-stockcake.jpg", "cuisine": "Japanese", "category": "Main Course","description": "Assorted sushi platter with fresh salmon, tuna, and avocado rolls.", "waiting": 20},
            #  {"name": "Teriyaki Beef", "price": 1100, "image_url": "https://simplehomeedit.com/wp-content/uploads/2023/11/Speedy-Beef-Teriyaki-9.webp", "cuisine": "Japanese", "decsription":"Grilled meat glazed with sweet soy sauce", "waiting": 10},
            #  {"name": "Tuna Sashimi", "price": 1250, "image_url": "https://getfish.com.au/cdn/shop/articles/Step_3_-_Tuna_Sashimi.png?v=1717040042", "cuisine": "Japanese", "decsription":"Sliced raw fish, served with soy sauce", "waiting": 12}
         ],
         "Dessert": [
              {"name": "Green Tea Ice Cream", "price": 300, "image_url": "https://foodbyjonister.com/wp-content/uploads/2016/08/gtmatcha.jpg", "cuisine": "Japanese", "decsription":"Sweet Matcha ice cream", "waiting": 5},
            #   {"name": "Mochi", "price": 450, "image_url": "https://jasmineandtea.com/wp-content/uploads/2021/06/ice-cream-mochi-768x1024.jpg", "cuisine": "Japanese", "decsription":"Soft chewy dumplings filled with red bean paste", "waiting": 5}
         ],
         "Kids Menu": [
             {"name": "Kid's Sushi Roll", "price": 700, "image_url": "https://kidseatincolor.com/wp-content/uploads/2022/04/Avocado-Sushi-Roll.jpg", "cuisine": "Japanese", "decsription":"foodie eats", "waiting": 8},
            #  {"name": "Onigiri", "price": 450, "image_url": "https://moribyan.com/wp-content/uploads/2023/01/IMG_8680-2-735x1024.jpg", "cuisine": "Japanese", "decsription":"Rice balls with Tuna or Salmon fillings", "waiting": 5}
         ],
         "Snacks": [
             {"name": "Tempura", "price": 800, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRG09VdSKMlO8VhwgFLSZQRZhg_fAvYPKwT5Q&s", "cuisine": "Japanese", "decsription":"Deep fried Tempura", "waiting": 17},
            #  {"name": "Taiyaki", "price": 650, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR1jRLprtwTQ-OQDzpoRJUDrB0aoUsBnPbezg&s", "cuisine": "Japanese", "decsription":"Fish pastry filled with red bean paste", "waiting": 15}
         ],
         "Drinks": [
             {"name": "Matcha Latte", "price": 300, "image_url": "https://munchingwithmariyah.com/wp-content/uploads/2020/06/IMG_0748.jpg", "cuisine": "Japanese", "decsription":"Matcha espresso", "waiting": 5},
            #  {"name": "Sakura Tea", "price": 200, "image_url": "https://c8.alamy.com/comp/TD3H9G/cherry-blossom-tea-cup-of-fresh-pink-cherry-blossom-tea-and-cherry-blossoms-on-the-table-TD3H9G.jpg", "cuisine": "Japanese", "decsription":"Made with cherry blossom petals", "waiting": 10}
         ]
     }
    },

    {"name": "Mayora Indian cuisine", "image_url": "https://res.cloudinary.com/hz3gmuqw6/image/upload/c_fill,q_auto,w_750/f_auto/tk-traditional-indian-foods-to-taste-in-2022-phpEXAXNS",
        "menus": {
         "Starter": [
            #  {"name": "Samosa", "price": 250, "image_url": "https://www.ohmyveg.co.uk/wp-content/uploads/2021/10/Samosa-1-e1722866243103-720x720.jpg", "cuisine": "Indian", "description": "Deep fried pastry with mince meat stuffings", "waiting": 5},

             {"name": "Pan Puri", "price": 400, "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Pani_Puri1.JPG", "cuisine": "Indian", "description": "Deep fried balls with meat filling", "waiting": 9}
         ],
         "Main Course": [
             {"name": "Butter Chicken", "price": 1200, "image_url": "https://foodess.com/wp-content/uploads/2022/10/Foodess-Best-Butter-Chicken-1-2.jpg", "cuisine": "Indian","description": "Grilled chicken made with yoghurt and spices", "waiting": 25},
            #  {"name": "Goan Fish Curry", "price": 1000, "image_url": "https://satyamskitchen.com/wp-content/uploads/2021/05/website-700x525.jpg", "cuisine": "Indian", "description": "Coastal flavours and aromas", "waiting": 20},
            #  {"name": "Wazwan", "price": 1100, "image_url": "https://img.atlasobscura.com/b8dKI3n1Fm8gDa1jsKufrb8u65MJqteJqYuosNeWiXw/rs:fill:580:580:1/g:ce/q:81/sm:1/scp:1/ar:1/aHR0cHM6Ly9hdGxh/cy1kZXYuczMuYW1h/em9uYXdzLmNvbS91/cGxvYWRzL3RoaW5n/X2ltYWdlcy9iZjBh/NjQzNC03YzQyLTQ3/ZDktYjQxYi03NTkw/ZmFhNDIxMjlmYjU2/ZmU4ZmQyOTBjYzIw/Mzdfd2F6d2FuX21h/cnJ5YW1fMi5qcGc.jpg", "cuisine": "Indian", "description": "Roasted Lamb made with dreid fruits", "waiting": 25}
         ],
         "Desert": [
            #   {"name": "Jalebi", "price": 400, "image_url": "https://i0.wp.com/binjalsvegkitchen.com/wp-content/uploads/2023/10/Instant-Jalebi-H3.jpg?resize=600%2C904&ssl=1", "cuisine": "Indian", "description": "Deep fried, crisp sweets soaked in saffron infused sugar", "waiting": 5},

              {"name": "Kulfi", "price": 400, "image_url": "https://thebigmansworld.com/wp-content/uploads/2022/07/kulfi-ice-cream-recipe.jpg", "cuisine": "Indian", "description": "Ice cream with cardamon, saffron and pistachios", "waiting": 9}
         ],
         "Kids Menu": [
             {"name": "Butter Chicken", "price": 1000, "image_url": "https://foodess.com/wp-content/uploads/2022/10/Foodess-Best-Butter-Chicken-1-2.jpg", "cuisine": "Indian", "description": "Grilled chicken made with yoghurt and spices served with Naan", "waiting": 8},

            #  {"name": "Pan Puri", "price": 400, "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Pani_Puri1.JPG", "cuisine": "Indian", "description": "Deep fried balls with meat filling", "waiting": 9}
         ],
         "Snacks": [
            #  {"name": "Bhajia", "price": 600, "image_url": "https://www.jayne-rain.com/wp-content/uploads/2020/01/potato-bhajia-5.jpg", "cuisine": "Indian", "description": "Deep fried potatoes", "waiting": 10},
             {"name": "Dhokla", "price": 400, "image_url": "https://rakskitchen.net/wp-content/uploads/2011/09/khaman-besan.jpg", "cuisine": "Indian", "description": "Steamed cakecserved with green chutney", "waiting": 10}
         ],
         "Drinks": [
             {"name": "Masala chai", "price": 450, "image_url": "https://cdn.shopify.com/s/files/1/0528/5173/6769/files/1080-X-683-pxl-A12.jpg?v=1654750025", "cuisine": "Indian", "description": "Black tea spiced with cardamon, cinnamon, black pepper and cloves", "waiting": 5},

            #  {"name": "Laasi", "price": 400, "image_url": "https://assets.bonappetit.com/photos/6046f566051c297ccfc14827/1:1/w_2560%2Cc_limit/Holi-Mango-Lassi.jpg", "cuisine": "Indian", "description": "Thick Yoghurt flavoured with fruits", "waiting": 5}
         ]
        }
    },

    {"name": "Steak House Supreme", "image_url": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/27/dd/c2/22/tomahawk-wagyu.jpg",
        "menus": {
         "Starter": [
            #  {"name": "Shrimp cocktails", "price": 1450, "image_url": "https://www.foodandwine.com/thmb/eJbvl3xF29aslGsseo5ekZrmL0s=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Dirty-Martini-Shrimp-Cocktail-FT-Recipe0624-17d9fd13705a402da5d673053929ba6a.jpg", "cuisine": "American", "description": "Chilled shrimp served with cocktail horseradish sauce", "waiting": 10},

             {"name": "Stuffed Mushrooms", "price": 1000, "image_url": "https://natashaskitchen.com/wp-content/uploads/2023/12/stuffed-mushrooms-sq.jpg", "cuisine": "American", "description": "Mushrooms filled cheese, garlic, bradcrumbs and herbs", "waiting": 10}
         ],
         "Main Course": [
             {"name": "Ribeye Steak", "price": 1200, "image_url": "https://tatyanaseverydayfood.com/wp-content/uploads/2019/06/Ribeye-Steak-Dinner-4-of-4-768x1024.jpg", "cuisine": "American","description": "Beef griled to perfection served with mashed potatoes or vegetables", "waiting": 25},

            #  {"name": "Porterhouse Steak", "price": 1000, "image_url": "https://d21klxpge3tttg.cloudfront.net/wp-content/uploads/2021/03/Reverse-seared-porterhouse-poblano-crema.jpg", "cuisine": "American", "description": "Large cut of tenderloin and strip steak", "waiting": 20},
            #  {"name": "T-Bone steak", "price": 1100, "image_url": "https://richmeats.capetown/wp-content/uploads/2017/03/T-Bone-1.jpg", "cuisine": "American", "description": "Tenderloin grilled to perfetion", "waiting": 25}
         ],
         "Desert": [
            #   {"name": "Cheese cake", "price": 700, "image_url": "https://www.inspiredtaste.net/wp-content/uploads/2024/04/New-York-Cheesecake-Recipe-Video.jpg", "cuisine": "American", "description": "Creamy cheesecake topped with fruit, caramel and chocolate sauce", "waiting": 5},
              {"name": "Creme Brulee", "price": 800, "image_url": "https://www.recipetineats.com/tachyon/2016/09/Creme-Brulee_8-SQ.jpg", "cuisine": "American", "description": "Silky  custard topped with a layer of caramelized sugar", "waiting": 9}
         ],
         "Kids Menu": [
            #  {"name": "Mini Steaks", "price": 1000, "image_url": "https://www.lecremedelacrumb.com/wp-content/uploads/2019/03/steak-potatoes-skillet-3.jpg", "cuisine": "American", "description": "Mini steaks", "waiting": 8},
             {"name": "Chicken tenders", "price": 800, "image_url": "https://foxeslovelemons.com/wp-content/uploads/2023/05/Buttermilk-Chicken-Tenders-6.jpg", "cuisine": "American", "description": "Crisp breaded chicken strips", "waiting": 10}
         ],
         "Snacks": [
             {"name": "Mini Quesadillas", "price": 600, "image_url": "https://s23209.pcdn.co/wp-content/uploads/2022/05/Mini-Chicken-Quesadillas211015_DAMN-DELICIOUS_Mini-Chicken-Quesadillas_030-760x1140.jpg", "cuisine": "American", "description": "Small cheesy tortillas", "waiting": 10},
            #  {"name": "Fruit kabobs", "price": 400, "image_url": "https://i2.wp.com/lmld.org/wp-content/uploads/2024/02/Rainbow-Fruit-Skewers-10.jpg", "cuisine": "American", "description": "Skewed pieces of fresh fruit", "waiting": 10}
         ],
         "Drinks": [
             {"name": "Lemonade", "price": 550, "image_url": "https://images.squarespace-cdn.com/content/v1/5ed13dd3465af021e2c1342b/a5b1e544-ee89-4268-b9af-ab49e9cc7006/IMG_1986+%281%29.jpg", "cuisine": "American", "description": "Creamy drink made with ice cream and milk", "waiting": 5},
            #  {"name": "Strawberry Margarita", "price": 900, "image_url": "https://creative-culinary.com/wp-content/uploads/strawberry-margarita-1.jpg", "cuisine": "American", "description": "Cocktail made with tequila, lime and orange liquer", "waiting": 5}
         ]
        }
    },

    {"name": "L'Atelier de paris", "image_url": "https://www.themanual.com/wp-content/uploads/sites/9/2021/06/french-cuisine-featured-image.jpg?fit=1340%2C782&p=1",
        "menus": {
         "Starter": [
             {"name": "Escargot de Bourgogne", "price": 2500, "image_url": "https://images.sbs.com.au/dims4/default/628e6ba/2147483647/strip/true/crop/1200x675+0+63/resize/1280x720!/quality/90/?url=http%3A%2F%2Fsbs-au-brightspot.s3.amazonaws.com%2Fdrupal%2Ffood%2Fpublic%2Fimg_7379-snails.jpg", "cuisine": "French", "description": "Snails cooked in butter, parley and wine", "waiting": 10},

            #  {"name": "French Onion soup", "price": 600, "image_url": "https://www.gimmesomeoven.com/wp-content/uploads/2015/01/French-Onion-Soup-Recipe-1-1.jpg", "cuisine": "French", "description": "Savoory soup with caramelized onions", "waiting": 10}
         ],
         "Main Course": [
             {"name": "Coq au vin", "price": 2800, "image_url": "https://images.immediate.co.uk/production/volatile/sites/30/2012/01/coq-au-vin-3740fe3.jpg?resize=768,574", "cuisine": "French","description": "Braised chicken in red wine, mushrooms, onions and garlic", "waiting": 25},
            #  {"name": "Ratatouille", "price": 3300, "image_url": "https://cdn.apartmenttherapy.info/image/upload/f_jpg,q_auto:eco,c_fill,g_auto,w_1500,ar_1:1/k%2FPhoto%2FRecipes%2F2024-07-ratatouille%2FRatatouille-", "cuisine": "French", "description": "Vegetable stew of zuchinni, eggplant, among others flavured with herbs", "waiting": 20},
            #  {"name": "Duck Confit", "price": 2100, "image_url": "https://www.sevenhillswinery.com/wp-content/uploads/2019/09/duck-confit_1920x900.jpg", "cuisine": "French", "description": "Duck leg slow-cooked in its own fat until tender", "waiting": 25}
         ],
         "Desert": [
              {"name": "Tarte Tatin", "price": 700, "image_url": "https://media-cdn2.greatbritishchefs.com/media/ioskqxie/img12633.jpg", "cuisine": "French", "description": "Caramelized upside down apple tart served with a scoop of ice-cream", "waiting": 15},
            #   {"name": "Mousse au Chocolat", "price": 800, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSVn5rJ-St5NCU3ChfItjxjdW9NrqXDVsBHCQ&s", "cuisine": "French", "description": "A fluffy chocolate mousse", "waiting": 9}
         ],
         "Kids Menu": [
             {"name": "Mini Steaks", "price": 1000, "image_url": "https://www.lecremedelacrumb.com/wp-content/uploads/2019/03/steak-potatoes-skillet-3.jpg", "cuisine": "French", "description": "Mini steaks", "waiting": 8},
            #  {"name": "Chicken tenders", "price": 800, "image_url": "https://foxeslovelemons.com/wp-content/uploads/2023/05/Buttermilk-Chicken-Tenders-6.jpg", "cuisine": "French", "description": "Crisp breaded chicken strips", "waiting": 10}
         ],
         "Snacks": [
             {"name": "Pomme Frites", "price": 600, "image_url": "https://www.joyfulhealthyeats.com/wp-content/uploads/2023/03/Crispy-Air-Fryer-Pomme-Frites-web-12.jpg", "cuisine": "French", "description": "Crispy french fries", "waiting": 10},
            #  {"name": "Gratin Dauphinois", "price": 400, "image_url": "https://www.delscookingtwist.com/wp-content/uploads/2019/04/French-Gratin-Dauphinois_6.jpg", "cuisine": "French", "description": "thily slicd potatoes, milk, cheese and cream cheese", "waiting": 10}
         ],
         "Drinks": [
            #  {"name": "Wine", "price": 950, "image_url": "https://winery.ph/cdn/shop/articles/WPH_Blog_Hero_Graphics_1_1500x901.jpg?v=1620291667", "cuisine": "French", "description": "Red White or Mulled", "waiting": 5},

             {"name": "Kir Royale", "price": 900, "image_url": "https://www.lemontreedwelling.com/wp-content/uploads/2023/05/kir-royale-featured.jpg", "cuisine": "French", "description": "Cocktail made with creme de cassis and champagne effect", "waiting": 5}
         ]
        }
    },

    {"name": "Casa de Sabor", "image_url": "https://www.facts-about-mexico.com/wp-content/uploads/2022/01/shutterstock-lunamaria-1080x675.jpg",
        "menus": {
         "Starter": [
             {"name": "Guacamole", "price": 250, "image_url": "https://californiaavocado.com/wp-content/uploads/2020/07/Guacamole-Autentico-1.jpeg", "cuisine": "Mexican", "description": "Creamy dip made fromavocadoes, tomatoes and onions", "waiting": 10},

            #  {"name": "Queso fundido", "price": 500, "image_url": "https://www.budgetbytes.com/wp-content/uploads/2023/01/Queso-Fundido-V1.jpg", "cuisine": "Mexican", "description": "Melted cheese served with chorio or mushrooms", "waiting": 10}
         ],
         "Main Course": [
            #  {"name": "Enchiladas", "price": 1200, "image_url": "https://images.immediate.co.uk/production/volatile/sites/30/2024/02/BeefEnchiladas-68c9381.jpg", "cuisine": "Mexican","description": "Corn tortillas filled wit meat, cheese or beans", "waiting": 25},
            #  {"name": "Burritos", "price": 1500, "image_url": "https://images.themodernproper.com/production/posts/BreakfastBurritos_13.jpg?w=1200&q=82&auto=format&fit=crop&dm=1712004278&s=74d57595cd6412657b898c59bb8f17dd", "cuisine": "Mexican", "description": "Large tortilla wrapped stuffed.", "waiting": 20},

             {"name": "Chiles Rellenos", "price": 1850, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSU5gfAV3U88Z34QnEV_yJYKNjJfbPLm2fApw&s", "cuisine": "Mexican", "description": "Roasted poblano peppers stuffed with cheese or meat", "waiting": 25}
         ],
         "Desert": [
              {"name": "Churros", "price": 700, "image_url": "https://hips.hearstapps.com/hmg-prod/images/churros-index-661d4692d05e4.jpg?crop=0.8888888888888888xw:1xh;center,top&resize=1200:*", "cuisine": "Mexican", "description": "Freid dough pastries coated with cinnamon sugar", "waiting": 5},

            #   {"name": "Tres Leche Cake", "price": 800, "image_url": "https://www.rainbownourishments.com/wp-content/uploads/2022/04/vegan-tres-leches-cake-1.jpg", "cuisine": "Mexican", "description": "A moist cake soaked in mixture of milk", "waiting": 9}
         ],
         "Kids Menu": [
            #  {"name": "Soft Tacos", "price": 1000, "image_url": "https://www.bama.no/siteassets/fotoware/2022/12/bama-sotpotettaco-05763.jpg?width=750&height=750&mode=crop", "cuisine": "Mexican", "description": "soft tortillas", "waiting": 8},
             {"name": "Tamales", "price": 800, "image_url": "https://keviniscooking.com/wp-content/uploads/2023/08/Pork-Tamales-Rojos-sauce.jpg", "cuisine": "Mexican", "description": "Doudh filled with cheese or shredded chicken", "waiting": 10}
         ],
         "Snacks": [
            #  {"name": "Mexican Rice", "price": 600, "image_url": "https://www.howtocook.recipes/wp-content/uploads/2021/01/Mexican-rice-recipe-500x500.jpg", "cuisine": "Mexican", "description": "Fluffy rice", "waiting": 10},
             {"name": "Pico de Gallo", "price": 400, "image_url": "https://cookieandkate.com/images/2018/09/best-pico-de-gallo-recipe-2.jpg", "cuisine": "Mexican", "description": "Fresh salsa made from tomatoes, onions, cilantro, lime and chilli", "waiting": 10}
         ],
         "Drinks": [
            #  {"name": "Horchata", "price": 550, "image_url": "https://www.foodandwine.com/thmb/fa4Ny43jN22ouDZKSNAMN4Dqu_Q=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Horchata-Explainer-FT-BLOG0923-7b252e8f459f43c29655339daeb62a82.jpg", "cuisine": "Mexican", "description": "Sweet, creamy drink made from rice, cinnamon and vanilla, served cold", "waiting": 5},

             {"name": "Aqua Fresca", "price": 900, "image_url": "https://www.shape.com/thmb/7MZzTVFIq-WQJm3rsh3d_Rdi9pc=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/agua-fresca-shutterstock_2023599671-2000-aadf4aef373740dfa2bbaeb3cd88278c.jpg", "cuisine": "Mexican", "description": "Made from fruits mixed with water, refreshing", "waiting": 5}
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

    NUM_CUSTOMERS = 5
    MAX_ORDERS = 5

    user_data = []
    owners = [
        {"name": "James Karanja", "email": "james.karanja@example.com", "password": "owner01", "role": "Owner"},
        {"name": "Susan Mwangi", "email": "susan.mwangi@example.com", "password": "owner02", "role": "Owner"},
        {"name": "David Kimani", "email": "david.kimani@example.com", "password": "owner03", "role": "Owner"},
        {"name": "Lucy Wanjiru", "email": "lucy.wanjiru@example.com", "password": "owner04", "role": "Owner"},
        {"name": "John Odhiambo", "email": "john.odhiambo@example.com", "password": "owner05", "role": "Owner"},
        {"name": "Esther Njeri", "email": "esther.njeri@example.com", "password": "owner06", "role": "Owner"},
    ]

    for owner in owners:
        owner["password"] = generate_password_hash(owner["password"])

    owner_users = [User(**owner) for owner in owners]
    db.session.add_all(owner_users)
    for _ in range(NUM_CUSTOMERS):
        user_data.append({
            "name": fake.name(),
            "email": fake.unique.email(),
            "password": generate_password_hash("customer123"),
            "role": "Customer"
        })


    customer_users = [User(**data) for data in user_data]
    db.session.add_all(customer_users)

    db.session.commit()

    owners = User.query.filter_by(role='Owner').all()
    customers = User.query.filter_by(role='Customer').all()


    print(f"✅ {owners} Owners and {NUM_CUSTOMERS} Customers added successfully!")


# Fetch owners from the database after insertion
    owners = User.query.filter_by(role='Owner').all()

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

                description = menu_item.get("description", "No description available")
                menu_item_db = MenuItem(
                    name=menu_item["name"],
                    price=menu_item["price"],
                    image_url=menu_item.get("image_url", ""),
                    cuisine=menu_item["cuisine"],
                    category=category,
                    description=description,

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

        
    orders = []
    order_count = 0
    # MAX_ORDERS = 20  # Set max orders limit

    random.shuffle(customers)

    for customer in customers:
        if order_count >= MAX_ORDERS:
            break

        num_orders = random.randint(1, 3)  # Each customer can have 1-3 orders
        for _ in range(num_orders):
            if order_count >= MAX_ORDERS:
                break

            order_items = []  # Store order items as a list of dicts
            total_price = 0.0  # Initialize total price

            for _ in range(random.randint(1, 3)):  # Each order has 1-3 items
                menu_item = random.choice(menu_items)
                quantity = random.randint(1, 20)
                item_price = menu_item.price * quantity  # Calculate item total price
                
                order_items.append({
                    "menu_item_id": menu_item.id,
                    "menu_item_name": menu_item.name,
                    "menu_item_price": menu_item.price,
                    "menu_item_image": menu_item.image_url,
                    "quantity": quantity,
                    "payment_method": random.choice(payment_methods),
                    "total_price": round(item_price, 2)  # Ensure price is rounded
                })
                
                total_price += item_price  # Accumulate total order price
            
            order = Order(
                customer_id=customer.id,
                outlet_id=random.choice(outlets).id,
                status=random.choice(order_statuses),
                table_number=random.randint(1, 20),
                order_items=order_items,  # Store JSON order items
                total_price=round(total_price, 2)  # Ensure proper total price
            )
            orders.append(order)
            order_count += 1

    db.session.add_all(orders)
    db.session.commit()

    print(f"✅ Database seeded successfully with {len(orders)} Orders!")




    bookings = []
    booked_tables = set()  # Track booked tables

    for _ in range(10):
        future_booking_time = datetime.now(timezone.utc) + timedelta(
            days=random.randint(1, 10),  
            hours=random.randint(1, 24)
        )

        table_number = random.randint(1, 20)  # Generate table number
        while table_number in booked_tables:  # Ensure unique booked tables
            table_number = random.randint(1, 20)

        booked_tables.add(table_number) 

        booking = TableBooking(
            customer_id=random.choice(customers).id,  # Assuming `customers` list exists
            table_number=table_number,
            booking_time=future_booking_time,
            available=False  # Mark as booked
        )
        bookings.append(booking)

    db.session.add_all(bookings)
    db.session.commit()


    # Get available tables (Tables 1-20 that are NOT in booked_tables)
    all_tables = set(range(1, 21))
    available_tables = list(all_tables - booked_tables)

    print("Available Tables:", available_tables)  # Debugging: Shows available tables

    
    print("✅ Database successfully seeded with Table Booking data!")



    
    print("Database seeded successfully!")