## FOODIE.EATS backend phase5-Final Project
This repository has the backend code for the phase 5 final project. 
## Backend developers
- [George Yegon](https://github.com/georgeyegon) <br>
- [Sifa Gakeni](https://github.com/Gakeniii)
## Postgresql
For the database, our group used Postgres which was a requirement to host our data for the app.<br>
We also used Flask for the tables and relationships as well.


Just in case the app stops fetching, know it is because our free subscription for Postgres on Render comes to an end on the 19th of MARCH.<br>
If that happens feel free to run the app locally on your machine, by cloning the repository and installing the virtual environment

`pipenv install; pipenv shell`

running the migrations

`flask db init`

`flask db migrate -m "Recreated migrations"`

`flask db upgrade`

run the seed data
`python seed.py` <br>
change the database from the database URI to sqlite://db


and start the server

`flask run`
## Endpoints
  - User endpoints use Postman to insert the Authorization and access keys - /users /users/:id
  - Outlet endpoints - /outlets /outlet/:id
  - Menu endpoints - /menu_items /menu_items/:id
  - Reservation endpoints - /bookings /bookings/:id
  - Orders endpoints - /orders /orders/:id

## Functionality 
This code enables the user to <br>
- Sign in log in and log out
- View all outlets
- Make an order that will persist in the database
- View the cart and check with the order they made
- Reserve a table
- With socket.io the owner can make updates on the client's orders and the client's order is automatically updated with a notification
- the owner can see the orders and reservations fetched from the database
- see their outlets and also add an outlet
- The owner can add, edit, and delete a menu and the changes will appear in the database
