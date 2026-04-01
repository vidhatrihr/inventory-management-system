# Inventory Management System — Project Report

**Stack:** Flask (Python) · SQLite · Vue 3 (Vite) · Pure CSS  
**Demo credentials:**

- Admin: `admin@example.com` / `password123`
- Manager: `manager@example.com` / `password123`

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Structure](#2-project-structure)
3. [Backend](#3-backend)
   - 3.1 [Dependencies](#31-dependencies)
   - 3.2 [app.py — Entry Point](#32-apppy--entry-point)
   - 3.3 [models.py — Database Models](#33-modelspy--database-models)
   - 3.4 [populate_db.py — Seed Data](#34-populate_dbpy--seed-data)
   - 3.5 [routes/auth.py — Auth Blueprint](#35-routesauthpy--auth-blueprint)
   - 3.6 [routes/products.py — Products Blueprint](#36-routesproductspy--products-blueprint)
   - 3.7 [routes/orders.py — Orders Blueprint](#37-routesorderspy--orders-blueprint)
   - 3.8 [routes/contacts.py — Contacts Blueprint](#38-routescontactspy--contacts-blueprint)
4. [Frontend](#4-frontend)
   - 4.1 [index.html](#41-indexhtml)
   - 4.2 [main.js](#42-mainjs)
   - 4.3 [App.vue](#43-appvue)
   - 4.4 [router/index.js — Client-Side Routing](#44-routerindexjs--client-side-routing)
   - 4.5 [style.css — Global Styles](#45-stylecss--global-styles)
   - 4.6 [LoginView.vue](#46-loginviewvue)
   - 4.7 [DashboardView.vue](#47-dashboardviewvue)
5. [Business Logic & Data Flow](#5-business-logic--data-flow)
6. [API Reference](#6-api-reference)
7. [Running the Application](#7-running-the-application)

---

## 1. Project Overview

The Inventory Management System is a role-based web application for tracking stock, recording orders, and managing supplier and customer contacts. The system supports two roles:

- **Admin** — full access to all tabs: Orders, Products, Contacts, and Reports
- **Manager** — restricted to the Orders tab only (can create and view orders)

Key capabilities include:

- Log in with a role-assigned account
- Add, edit, and delete products with cost price, selling price, stock quantity, and a safety stock threshold
- Receive low-stock warnings when a product's quantity falls below its safety stock level
- Record incoming orders (stock received from a supplier) and outgoing orders (stock dispatched to a customer)
- Automatically adjust product stock quantities when an order is submitted
- Manage supplier and customer contact records
- View a reports summary showing total inventory value and product count

---

## 2. Project Structure

```
inventory-management-system/
├── .gitignore                           # excludes private/ folder
├── backend/
│   ├── app.py                           # Flask app — config, db, blueprints
│   ├── models.py                        # database tables as Python classes
│   ├── populate_db.py                   # seed function — demo data
│   ├── requirements.txt                 # pip packages
│   ├── app.db                           # SQLite database (auto-created)
│   └── routes/
│       ├── __init__.py                  # makes routes/ a Python package
│       ├── auth.py                      # register, login, logout, me
│       ├── products.py                  # product CRUD endpoints
│       ├── orders.py                    # order creation and listing
│       └── contacts.py                  # supplier and customer CRUD
└── frontend/
    ├── index.html                       # HTML shell
    ├── vite.config.js                   # Vite configuration
    ├── package.json                     # npm dependencies and scripts
    └── src/
        ├── main.js                      # creates Vue app, mounts it
        ├── style.css                    # all CSS — global and component styles
        ├── App.vue                      # root Vue component
        ├── router/
        │   └── index.js                 # URL → component mapping
        └── views/
            ├── LoginView.vue            # /  — login page
            └── DashboardView.vue        # /dashboard — main app
```

---

## 3. Backend

The backend is a Flask web server that exposes a REST API. It runs on port **5000**. The frontend communicates with it exclusively via HTTP requests.

### 3.1 Dependencies

Defined in `requirements.txt`:

| Package            | Purpose                                                         |
| ------------------ | --------------------------------------------------------------- |
| `flask`            | Web framework — handles HTTP routing                            |
| `flask-cors`       | Allows the frontend (port 5173) to call the backend (port 5000) |
| `flask-login`      | Manages user sessions — tracks who is logged in                 |
| `flask-sqlalchemy` | ORM — lets us write Python classes instead of raw SQL           |
| `werkzeug`         | Bundled with Flask — used for password hashing                  |

Install with: `pip install -r requirements.txt`

---

### 3.2 `app.py` — Entry Point

This is the first file Flask runs. It wires everything together.

**What it does, step by step:**

1. **Creates the Flask app** and sets a `secret_key`. The secret key is used to sign session cookies — without it, sessions don't work.

2. **Configures session cookies** for cross-site requests:
   - `SESSION_COOKIE_SAMESITE="None"` — allows the cookie to be sent from a different origin (the Vite dev server at port 5173)
   - `SESSION_COOKIE_SECURE=True` — cookie is only sent over HTTPS
   - `SESSION_COOKIE_HTTPONLY=True` — JavaScript in the browser cannot read the cookie (security measure)

3. **Sets the database URI** to `sqlite:///app.db`. SQLite creates this file automatically inside the `backend/` folder on first run.

4. **Configures CORS** with `supports_credentials=True` and restricts it to `http://localhost:5173`. This is required because the browser blocks cross-origin requests with cookies by default.

5. **Initialises Flask-SQLAlchemy** by calling `db.init_app(app)`. This connects the `db` object from `models.py` to this specific Flask app.

6. **Configures Flask-Login** with a `LoginManager`. The `load_user` function is called by Flask-Login on every request to load the currently logged-in user from the database using their ID stored in the session cookie.

7. **Registers blueprints** under the `/api` URL prefix. All API URLs will start with `/api/`.

8. **Inside `app_context()`**: Creates all database tables (if they don't exist yet), then calls `seed_db()` to insert demo data on a fresh database.

9. **Starts the server** on port 5000 in debug mode (auto-reloads on code changes).

---

### 3.3 `models.py` — Database Models

Each class here represents one table in the SQLite database. Flask-SQLAlchemy translates these Python classes into SQL `CREATE TABLE` statements.

**`db = SQLAlchemy()`**  
Creates the database object. It is initialised inside `app.py` with `db.init_app(app)`.

#### `User` table (`users`)

| Column     | Type    | Details                                                   |
| ---------- | ------- | --------------------------------------------------------- |
| `id`       | Integer | Primary key, auto-incremented                             |
| `name`     | String  | User's display name                                       |
| `email`    | String  | Unique — no two users share an email                      |
| `password` | String  | Stores a **hashed** password, never plain text            |
| `role`     | String  | Either `'admin'` or `'manager'` — defaults to `'manager'` |

`UserMixin` is inherited from Flask-Login. It provides default implementations for methods Flask-Login needs (e.g. `is_authenticated`, `get_id`).

#### `Product` table (`products`)

| Column          | Type    | Details                                                  |
| --------------- | ------- | -------------------------------------------------------- |
| `id`            | Integer | Primary key, auto-incremented                            |
| `name`          | String  | Product display name                                     |
| `category`      | String  | e.g. Electronics, Stationery, Furniture                  |
| `cost_price`    | Float   | Price at which the product was purchased                 |
| `selling_price` | Float   | Price at which the product is sold                       |
| `quantity`      | Integer | Current stock level — adjusted by orders                 |
| `safety_stock`  | Integer | Minimum desired stock level — triggers low-stock warning |

**Relationships on `Product`:**

- `order_items` — links to many `OrderItem` rows; used to trace which orders involved this product

#### `Supplier` table (`suppliers`)

| Column    | Type    | Details                         |
| --------- | ------- | ------------------------------- |
| `id`      | Integer | Primary key, auto-incremented   |
| `name`    | String  | Supplier company or person name |
| `contact` | String  | Email or phone                  |

**Relationships on `Supplier`:**

- `orders` — links to many `Order` rows for incoming orders from this supplier

#### `Customer` table (`customers`)

| Column    | Type    | Details                         |
| --------- | ------- | ------------------------------- |
| `id`      | Integer | Primary key, auto-incremented   |
| `name`    | String  | Customer company or person name |
| `contact` | String  | Email or phone                  |

**Relationships on `Customer`:**

- `orders` — links to many `Order` rows for outgoing orders to this customer

#### `Order` table (`orders`)

| Column        | Type    | Details                                                                 |
| ------------- | ------- | ----------------------------------------------------------------------- |
| `id`          | Integer | Primary key, auto-incremented                                           |
| `order_type`  | String  | Either `'incoming'` (stock received) or `'outgoing'` (stock dispatched) |
| `date`        | String  | ISO date string, e.g. `'2024-03-01'`                                    |
| `supplier_id` | Integer | Foreign key → `suppliers.id` — set for incoming orders                  |
| `customer_id` | Integer | Foreign key → `customers.id` — set for outgoing orders                  |

**Relationships on `Order`:**

- `supplier` — the linked `Supplier` object (or `None` for outgoing orders)
- `customer` — the linked `Customer` object (or `None` for incoming orders)
- `items` — list of `OrderItem` rows; cascade `all, delete-orphan` means items are automatically deleted if the order is deleted

#### `OrderItem` table (`order_items`)

The join table between `Order` and `Product`. Each row records one product and its quantity within a specific order.

| Column       | Type    | Details                                         |
| ------------ | ------- | ----------------------------------------------- |
| `id`         | Integer | Primary key, auto-incremented                   |
| `order_id`   | Integer | Foreign key → `orders.id`                       |
| `product_id` | Integer | Foreign key → `products.id`                     |
| `quantity`   | Integer | How many units of the product are in this order |

**How relationships work:**  
`back_populates` connects the two sides of a relationship. For example, `Order.items` and `OrderItem.order` point to each other. Accessing `order.items` automatically runs a SQL query and returns all `OrderItem` objects belonging to that order.

---

### 3.4 `populate_db.py` — Seed Data

Defines a single function: `seed_db()`. It is imported and called in `app.py` every time the server starts.

**Safety check — the first line inside the function:**

```python
if User.query.count() > 0:
    return
```

This counts how many users exist. If the count is greater than zero, the database already has data — so the function returns immediately without doing anything. This prevents duplicate data from being inserted on every restart.

**What it seeds (on a fresh database):**

1. Creates two users: **Admin** (`admin@example.com`, role `'admin'`) and **Manager** (`manager@example.com`, role `'manager'`), both with the password `password123` stored as a hash.
2. Calls `db.session.flush()` after each set of inserts — this sends the INSERTs to the database without committing, which assigns IDs so they can be used as foreign keys in subsequent inserts.
3. Creates two suppliers: **TechParts Ltd** and **OfficeWorld**.
4. Creates two customers: **Acme Corp** and **BuildRight**.
5. Creates four products across different categories: USB Hub, Notebook, Webcam, and Desk Lamp. The Webcam's quantity (8) is deliberately seeded below its safety stock (10), triggering a low-stock warning immediately on load.
6. Creates one **incoming order** dated `2024-03-01` from TechParts Ltd, containing 20 USB Hubs and 5 Webcams.
7. Creates one **outgoing order** dated `2024-03-05` to Acme Corp, containing 3 USB Hubs and 10 Notebooks.
8. Calls `db.session.commit()` to permanently save everything.

---

### 3.5 `routes/auth.py` — Auth Blueprint

Handles user registration, login, logout, and session verification. All routes are mounted under `/api`.

#### `POST /api/register`

1. Reads `name`, `email`, `password`, and optional `role` from the JSON body.
2. Checks if a user with that email already exists — returns `400` if so.
3. Creates a new `User` with a hashed password using `generate_password_hash`.
4. Saves to the database and calls `login_user(user)` to immediately start a session.
5. Returns `200` with a success message.

#### `POST /api/login`

1. Looks up the user by email.
2. If the user does not exist or `check_password_hash` returns `False`, returns `401 Unauthorized`.
3. Calls `login_user(user)` — Flask-Login sets the session cookie.
4. Returns `200` with the user's `name`, `email`, and `role`. The frontend stores the role in a reactive ref to control which tabs are visible.

#### `POST /api/logout`

Decorated with `@login_required`. Calls `logout_user()` which clears the session. Returns `200`.

#### `GET /api/me`

Decorated with `@login_required`. Returns the current user's `name`, `email`, and `role`. Called by the dashboard on mount to verify the session is still valid and to get the user's role.

---

### 3.6 `routes/products.py` — Products Blueprint

Handles full CRUD (Create, Read, Update, Delete) for inventory products. All routes require login (`@login_required`).

#### Helper: `product_to_dict(p)`

Converts a `Product` object to a plain dictionary for JSON serialisation. Adds a computed field `low_stock` — a boolean that is `True` when `quantity < safety_stock`. This is calculated on the fly at serialisation time and never stored in the database.

#### `GET /api/products`

Returns all products as a JSON array. Called on dashboard mount and after every order submission to refresh stock levels.

#### `POST /api/products`

Creates a new product from the JSON body. Fields: `name`, `category`, `cost_price`, `selling_price`, and optionally `quantity` and `safety_stock` (both default to `0`). Returns the created product.

#### `PUT /api/products/<id>`

Updates all fields of an existing product by ID. The frontend sends all fields (not just changed ones), so the route overwrites every column. Returns the updated product.

#### `DELETE /api/products/<id>`

Deletes a product by ID. Note: the route does not currently check whether the product is referenced by existing order items — deleting a product that appears in past orders would orphan those `OrderItem` rows.

---

### 3.7 `routes/orders.py` — Orders Blueprint

Handles order creation and listing. All routes require login.

#### Helper: `order_to_dict(o)`

Serialises an `Order` object into a nested dictionary. The shape is:

```json
{
  "id": 1,
  "order_type": "incoming",
  "date": "2024-03-01",
  "supplier": { "id": 1, "name": "TechParts Ltd" },
  "customer": null,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "USB Hub",
      "quantity": 20,
      "cost_price": 300.0,
      "selling_price": 500.0
    }
  ]
}
```

Both `cost_price` and `selling_price` are included per item so the frontend can calculate order value in future without an additional lookup.

#### `GET /api/orders`

Returns all orders. Each order includes its items and the linked supplier or customer name. Displayed in the Order History table on the dashboard.

#### `POST /api/orders`

This is the most complex route. It:

1. Reads `order_type`, `date`, `supplier_id` or `customer_id`, and an `items` array from the JSON body.
2. Creates the `Order` row and calls `db.session.flush()` to get the `order.id`.
3. Iterates over each item in `items`:
   - Fetches the `Product` by `product_id` — skips if not found.
   - Casts `quantity` to an integer.
   - **Adjusts stock:** if `order_type` is `'incoming'`, adds the quantity to `product.quantity`; if `'outgoing'`, subtracts it. This is the core stock-tracking logic.
   - Creates an `OrderItem` linking the order, product, and quantity.
4. Commits everything in a single transaction. If the commit fails, no stock is modified and no order is saved.
5. Returns the full serialised order.

---

### 3.8 `routes/contacts.py` — Contacts Blueprint

Handles CRUD for suppliers and customers. All routes require login.

#### Helper functions: `supplier_to_dict(s)`, `customer_to_dict(c)`

Convert model objects to plain dictionaries with `id`, `name`, and `contact`.

#### Supplier routes

- `GET /api/suppliers` — returns all suppliers
- `POST /api/suppliers` — creates a new supplier from `name` and `contact`
- `PUT /api/suppliers/<id>` — updates a supplier's name and/or contact
- `DELETE /api/suppliers/<id>` — deletes a supplier. Before deleting, queries `Order.query.filter_by(supplier_id=supplier_id).count()`. If any orders reference this supplier, returns `400` with a message rather than deleting, preventing referential integrity violations.

#### Customer routes

Mirror the supplier routes exactly:

- `GET /api/customers`
- `POST /api/customers`
- `PUT /api/customers/<id>`
- `DELETE /api/customers/<id>` — same guard: blocks deletion if the customer has any linked orders.

---

## 4. Frontend

The frontend is a single-page application (SPA) built with Vue 3 and Vite. It runs on port **5173** in development. All data comes from the Flask API — the frontend holds no server state of its own between page reloads.

### 4.1 `index.html`

The HTML shell for the entire application. It contains one `<div id="app"></div>` which is the mount point Vue takes over. It also:

- Links the **Inter** font from Google Fonts with `preconnect` for fast loading
- Sets the page `<title>` to "Inventory Management"
- Loads `/src/main.js` as an ES module via `<script type="module">`

Everything the user sees is rendered by Vue inside the `#app` div. The HTML file itself is never changed after the app loads.

---

### 4.2 `main.js`

The JavaScript entry point. Three things happen here:

1. `createApp(App)` — creates the Vue application, using `App.vue` as the root component
2. `app.use(router)` — registers the Vue Router plugin so all components can use `<RouterView>` and `useRouter()`
3. `app.mount('#app')` — attaches the Vue app to the `<div id="app">` in `index.html`

`import './style.css'` is also here — this imports the global stylesheet so it is bundled by Vite and applied to the entire page.

---

### 4.3 `App.vue`

The root component. It contains only:

```html
<template>
  <RouterView />
</template>
```

`<RouterView>` is a Vue Router placeholder. It renders whichever component matches the current URL. When the URL is `/`, it renders `LoginView`; when the URL is `/dashboard`, it renders `DashboardView`. `App.vue` itself adds no layout or styling — it is purely a routing container.

---

### 4.4 `router/index.js` — Client-Side Routing

Defines the URL-to-component map for the application.

```
/           →  LoginView.vue
/dashboard  →  DashboardView.vue
```

**`createWebHistory`** is used instead of hash-based routing, so URLs look like `/dashboard` rather than `/#/dashboard`. This requires the Vite dev server (or production web server) to serve `index.html` for all routes — Vite handles this automatically in development.

There is no navigation guard in the router itself. Instead, authentication is enforced inside `DashboardView`'s `onMounted` hook by calling `GET /api/me` — if the session is invalid, Vue Router redirects to `/`.

---

### 4.5 `style.css` — Global Styles

All CSS lives in one file. It uses **CSS custom properties** (variables) defined on `:root` so that every component uses a consistent design language.

**Design tokens:**

| Variable        | Value     | Purpose                             |
| --------------- | --------- | ----------------------------------- |
| `--bg`          | `#0f0f11` | Page background — near-black        |
| `--surface`     | `#18181c` | Cards and sections                  |
| `--surface-alt` | `#222228` | Nested surfaces, input backgrounds  |
| `--border`      | `#2e2e36` | All borders and dividers            |
| `--accent`      | `#5af5b9` | Primary highlight — mint green      |
| `--text`        | `#e8e8ee` | Main body text                      |
| `--text-muted`  | `#7a7a8c` | Labels, secondary information       |
| `--danger`      | `#f55a5a` | Errors, warnings, delete actions    |
| `--radius`      | `8px`     | Consistent border-radius everywhere |
| `--gap`         | `1.5rem`  | Consistent spacing between sections |

**Notable utility classes:**

- `.page-center` — full-viewport flexbox centering, used by `LoginView`
- `.card` — styled container for the login form
- `.dashboard` — max-width constrained, centered page wrapper
- `.tabs` / `.tab` / `.tab.active` — the tab bar with an accent underline on the active tab
- `.section` — a bordered, padded content block used throughout the dashboard
- `.grid-form` — responsive multi-column form grid using `auto-fit` with a 150px minimum column width
- `.low-stock` — applies `--danger` color to text; used on product rows and quantity cells
- `.btn-primary` — the mint-green call-to-action button (black text on accent background)
- `.btn-danger` — transparent button with a red border; fills red on hover
- `.empty` — centered muted text for empty table states

---

### 4.6 `LoginView.vue`

The login page rendered at `/`. It contains a centered card with email and password inputs.

**Reactive state:**

| Variable   | Type      | Purpose                                     |
| ---------- | --------- | ------------------------------------------- |
| `email`    | `ref('')` | Bound to the email input                    |
| `password` | `ref('')` | Bound to the password input                 |
| `error`    | `ref('')` | Displays a red error message below the form |

**`login()` function:**

1. Clears any previous error message.
2. Sends `POST /api/login` with `email` and `password` as JSON. `credentials: 'include'` is required so the browser accepts and stores the session cookie.
3. If `res.ok` is false, sets `error.value` to the API's message (e.g. "Invalid credentials") and returns early.
4. On success, calls `router.push('/dashboard')` — Vue Router replaces the current URL and renders `DashboardView`.

**Template structure:**

```
.page-center
  └── .card
        ├── <h1> Welcome back
        ├── <p> Log in to manage your inventory
        ├── <form @submit.prevent="login">
        │     ├── Email input (v-model="email")
        │     ├── Password input (v-model="password")
        │     └── Submit button
        └── <p v-if="error" class="error-msg">
```

`@submit.prevent` prevents the default browser form submission (which would cause a page reload). The form is submitted programmatically via `login()` instead.

---

### 4.7 `DashboardView.vue`

The main application view, rendered at `/dashboard`. It is a large single-file component that manages all data and all four tab views.

#### Reactive State

| Variable       | Type                          | Purpose                                                  |
| -------------- | ----------------------------- | -------------------------------------------------------- |
| `user`         | `ref({ name: '', role: '' })` | Stores the logged-in user's name and role                |
| `activeTab`    | `ref('orders')`               | Controls which tab panel is visible                      |
| `products`     | `ref([])`                     | Full list of products from the API                       |
| `orders`       | `ref([])`                     | Full list of orders from the API                         |
| `suppliers`    | `ref([])`                     | Full list of suppliers from the API                      |
| `customers`    | `ref([])`                     | Full list of customers from the API                      |
| `productForm`  | `ref({...})`                  | Bound to the add/edit product form                       |
| `orderForm`    | `ref({...})`                  | Bound to the new order form                              |
| `tempItem`     | `ref({...})`                  | Holds the product and quantity being added to an order   |
| `supplierForm` | `ref({...})`                  | Bound to the add supplier form                           |
| `customerForm` | `ref({...})`                  | Bound to the add customer form                           |
| `API`          | constant                      | Base URL `http://localhost:5000/api`                     |
| `opts`         | constant                      | `{ credentials: 'include' }` — reused in all fetch calls |

#### Computed Properties

**`inventoryValue`**  
Uses `Array.reduce()` to sum `product.quantity * product.cost_price` across all products. This gives the total cost value of current stock. Recalculates automatically whenever `products` changes.

#### `onMounted()` — Data Loading

Runs once when the component is first rendered. Calls `GET /api/me` to verify the session. If the response is not `ok` (401), immediately redirects to `/`. On success, sets `user.value` with the name and role, then concurrently loads all four data sets using `Promise.all`:

```
Promise.all([loadProducts(), loadOrders(), loadSuppliers(), loadCustomers()])
```

Using `Promise.all` fires all four requests simultaneously rather than sequentially, reducing total load time.

#### Data Loader Functions

**`loadProducts()`** — `GET /api/products` → sets `products.value`  
**`loadOrders()`** — `GET /api/orders` → sets `orders.value`  
**`loadSuppliers()`** — `GET /api/suppliers` → sets `suppliers.value`  
**`loadCustomers()`** — `GET /api/customers` → sets `customers.value`

Each function is standalone so it can be called individually to refresh only the data that changed (e.g. after adding a product, only `loadProducts()` is called, not all four).

#### Product Functions

**`editProduct(p)`**  
Copies a product object into `productForm` using the spread operator (`{ ...p }`). Because the form now has a non-null `id`, the template switches the heading to "Edit Product" and the submit button to "Update".

**`clearProductForm()`**  
Resets all form fields to their defaults and sets `id` back to `null`, switching the form back to "Add New Product" mode.

**`saveProduct()`**  
Checks `productForm.value.id` to determine whether to use `PUT` (edit) or `POST` (create). Sends the request, then calls `clearProductForm()` and `loadProducts()`.

**`deleteProduct(id)`**  
Sends `DELETE /api/products/{id}`, then calls `loadProducts()`.

#### Order Functions

**`addOrderItem()`**  
Validates that a product is selected and quantity is at least 1. Checks whether the product is already in `orderForm.items` — if so, increments the existing item's quantity rather than adding a duplicate. Resets `tempItem` after adding.

**`removeOrderItem(index)`**  
Splices the item at the given index out of `orderForm.items`.

**`getProdName(id)`**  
Looks up a product name by ID in the local `products` array. Used to display readable product names in the in-progress order item list.

**`submitOrder()`**  
Validates that `orderForm.items` is not empty (alerts if so). Sends `POST /api/orders` with the full order object. After success, resets items, supplier/customer selection, then calls both `loadOrders()` and `loadProducts()`. Loading products is essential here because the order submission mutated stock quantities on the server.

#### Contact Functions

**`addSupplier()`** / **`addCustomer()`**  
Send `POST` with the respective form data, then reset the form and reload contacts.

**`deleteSupplier(id)`** / **`deleteCustomer(id)`**  
Send `DELETE` to the respective endpoint, then reload contacts. If the server returns `400` (contact has existing orders), the error is silently swallowed — the UI does not currently display the error message to the user.

#### `logout()`

Sends `POST /api/logout`, then calls `router.push('/')`.

#### `fmtCurrency(amount)`

A helper function. Returns `'₹' + Number(amount).toFixed(2)`. Used in the Reports tab to display the inventory value.

#### Template Structure

```
.dashboard
  ├── .dashboard-header          ← "Welcome, Admin (admin)" + Sign out button
  ├── .tabs                      ← Orders | Products* | Contacts* | Reports*
  │                                (* only visible to admin role)
  │
  ├── [Orders tab]
  │     ├── .section (Create New Order)   ← hidden for admin role
  │     │     ├── Type select, Date input
  │     │     ├── Supplier or Customer select (conditional on order type)
  │     │     ├── Product + Qty picker with Add button
  │     │     ├── Items list with Remove buttons
  │     │     └── Submit Order button (disabled when no items)
  │     └── .section (Order History)
  │           └── Table: ID | Type | Date | Partner | Items
  │
  ├── [Products tab — admin only]
  │     ├── .section (Add / Edit Product form)
  │     └── .section (Inventory Items table)
  │           └── Rows show ⚠️ Low badge and red qty when below safety stock
  │
  ├── [Contacts tab — admin only]
  │     ├── .section (Suppliers) — add form + list with delete
  │     └── .section (Customers) — add form + list with delete
  │
  └── [Reports tab — admin only]
        └── .section
              ├── Total Inventory Value (Cost) card
              └── Total Products Checked card
```

**Role-based tab visibility:**  
The Products, Contacts, and Reports tabs are rendered with `v-if="user.role === 'admin'"`. A manager logging in will only ever see the Orders tab — the other three tabs are not rendered in the DOM at all, not merely hidden.

**Order type conditional fields:**  
Inside the order form, the supplier select uses `v-if="orderForm.order_type === 'incoming'"` and the customer select uses `v-if="orderForm.order_type === 'outgoing'"`. Only one is visible at a time, and whichever is hidden also has its value ignored by the server.

**Low-stock visual feedback:**  
In the Products table, each row checks `p.low_stock` (the boolean returned by the API). If true, a `⚠️ Low` badge is appended next to the product name, and the quantity cell receives the `low-stock` class (red text).

---

## 5. Business Logic & Data Flow

### Login Flow

```
User fills form → POST /api/login
  → Server finds user by email
  → check_password_hash() verifies password
  → login_user() — session cookie set
  → 200 OK with { name, email, role }
  → Frontend redirects to /dashboard
```

### Dashboard Load Flow

```
Vue mounts DashboardView
  → GET /api/me (verify session)
      → 401: redirect to /
      → 200: set user.name and user.role
  → Promise.all([loadProducts, loadOrders, loadSuppliers, loadCustomers])
      → all four arrays populated simultaneously
  → computed inventoryValue calculates automatically
  → template renders with all data; tabs filtered by role
```

### Create Order Flow

```
Admin/Manager builds order form:
  → selects order type (incoming / outgoing)
  → selects supplier or customer
  → adds one or more products with quantities

User clicks Submit Order → submitOrder()
  → POST /api/orders
  → Server creates Order row (flush to get ID)
  → For each item:
      → fetch Product
      → if incoming: product.quantity += qty
      → if outgoing: product.quantity -= qty
      → create OrderItem row
  → db.session.commit() (atomic — all or nothing)
  → 200 OK
  → Frontend calls loadOrders() + loadProducts()
  → Order appears in history; stock quantities updated in table
```

### Add Product Flow

```
Admin fills product form → saveProduct()
  → POST /api/products (new) or PUT /api/products/{id} (edit)
  → Server creates / updates Product row
  → 200 OK
  → clearProductForm() resets form to 'Add' mode
  → loadProducts() refreshes the inventory table
  → low_stock computed server-side and returned in response
```

### Delete Supplier / Customer Flow

```
Admin clicks Delete → deleteSupplier(id) or deleteCustomer(id)
  → DELETE /api/suppliers/{id} or /api/customers/{id}
  → Server counts orders referencing this contact
      → count > 0: return 400 (contact has orders, cannot delete)
      → count = 0: delete row, return 200
  → loadSuppliers() or loadCustomers() refreshes the list
```

### Session Persistence

The browser stores the session as a cookie. On every API call, `credentials: 'include'` ensures the cookie is sent automatically. Flask-Login reads the cookie, looks up the user ID in the session, and calls `load_user()` to fetch the full `User` object from the database — making it available as `current_user` in any route.

### Password Security

Passwords are never stored as plain text. `generate_password_hash('password123')` produces something like:

```
pbkdf2:sha256:600000$Xk3...xyz...abc
```

This string encodes the algorithm, number of iterations, salt, and hash. `check_password_hash(stored_hash, 'password123')` re-runs the same algorithm and compares — returning `True` only on a match. Even if the database is leaked, the passwords cannot be reversed.

### Low-Stock Detection

The `low_stock` field is not stored in the database. It is computed in `product_to_dict()` every time a product is serialised:

```python
'low_stock': p.quantity < p.safety_stock
```

This means the warning is always current — no separate cron job or trigger is needed. As soon as a product's `quantity` drops below `safety_stock` (e.g. after an outgoing order), the next call to `GET /api/products` will return `low_stock: true` for that product.

---

## 6. API Reference

All endpoints are prefixed with `/api`. All responses are JSON with the shape `{ "data": ..., "message": "..." }`.

### Auth

| Method | URL             | Auth | Request Body                       | Response                                   |
| ------ | --------------- | ---- | ---------------------------------- | ------------------------------------------ |
| `POST` | `/api/register` | No   | `{ name, email, password, role? }` | `{ message }`                              |
| `POST` | `/api/login`    | No   | `{ email, password }`              | `{ message, data: { name, email, role } }` |
| `POST` | `/api/logout`   | Yes  | —                                  | `{ message }`                              |
| `GET`  | `/api/me`       | Yes  | —                                  | `{ data: { name, email, role } }`          |

### Products

| Method   | URL                  | Auth | Request Body                                                              | Response                     |
| -------- | -------------------- | ---- | ------------------------------------------------------------------------- | ---------------------------- |
| `GET`    | `/api/products`      | Yes  | —                                                                         | `{ data: [ ...products ] }`  |
| `POST`   | `/api/products`      | Yes  | `{ name, category, cost_price, selling_price, quantity?, safety_stock? }` | `{ message, data: product }` |
| `PUT`    | `/api/products/<id>` | Yes  | `{ name, category, cost_price, selling_price, quantity, safety_stock }`   | `{ message, data: product }` |
| `DELETE` | `/api/products/<id>` | Yes  | —                                                                         | `{ message }`                |

### Orders

| Method | URL           | Auth | Request Body                                                                          | Response                   |
| ------ | ------------- | ---- | ------------------------------------------------------------------------------------- | -------------------------- |
| `GET`  | `/api/orders` | Yes  | —                                                                                     | `{ data: [ ...orders ] }`  |
| `POST` | `/api/orders` | Yes  | `{ order_type, date, supplier_id?, customer_id?, items: [{ product_id, quantity }] }` | `{ message, data: order }` |

### Contacts

| Method   | URL                   | Auth | Request Body          | Response                               |
| -------- | --------------------- | ---- | --------------------- | -------------------------------------- |
| `GET`    | `/api/suppliers`      | Yes  | —                     | `{ data: [ ...suppliers ] }`           |
| `POST`   | `/api/suppliers`      | Yes  | `{ name, contact? }`  | `{ message, data: supplier }`          |
| `PUT`    | `/api/suppliers/<id>` | Yes  | `{ name?, contact? }` | `{ message, data: supplier }`          |
| `DELETE` | `/api/suppliers/<id>` | Yes  | —                     | `{ message }` or `400` if orders exist |
| `GET`    | `/api/customers`      | Yes  | —                     | `{ data: [ ...customers ] }`           |
| `POST`   | `/api/customers`      | Yes  | `{ name, contact? }`  | `{ message, data: customer }`          |
| `PUT`    | `/api/customers/<id>` | Yes  | `{ name?, contact? }` | `{ message, data: customer }`          |
| `DELETE` | `/api/customers/<id>` | Yes  | —                     | `{ message }` or `400` if orders exist |

**Auth = Yes** means the request must include the session cookie. Without it, Flask-Login returns `401 Unauthorized`.

---

## 7. Running the Application

### Start the Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

On first run:

- Creates `app.db` in the `backend/` folder
- Creates all tables (`users`, `products`, `suppliers`, `customers`, `orders`, `order_items`)
- Seeds the database with demo users, products, suppliers, customers, and orders
- Prints:
  ```
  Database seeded.
    Admin:   admin@example.com / password123
    Manager: manager@example.com / password123
  ```
- Flask listens on `http://localhost:5000`

On subsequent runs:

- Tables already exist — `db.create_all()` is a no-op
- `seed_db()` sees `User.query.count() > 0` and returns immediately
- Server starts normally

### Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite starts a dev server at `http://localhost:5173`.

Open `http://localhost:5173` in a browser. Log in with either demo account:

- `admin@example.com` / `password123` — access to all four tabs (Orders, Products, Contacts, Reports)
- `manager@example.com` / `password123` — access to the Orders tab only
