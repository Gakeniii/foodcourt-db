## FOODIE.EATS backend phase5-Final Project
This repository has the backend code for the phase 5 final project. 
## Backend developers
- [George Yegon](https://github.com/georgeyegon) <br>
- [Sifa Gakeni](https://github.com/Gakeniii)
## Postgresql
For the database, our group used Postgres which was a requirement to host our data for the app.<br>
We also used Flask for the tables and relationships as well.


We used NeonDB to host our postgres since renders free version was expiring and it made the app faster and a better UI/UX for the user.

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
