# Inventory Management System - Frontend

A Vue 3 single-page application built with Vite and styled using vanilla CSS.

## Architecture

- `src/views/` - Page-level Vue components (`LoginView`, `OrdersView`, `ProductsView`, `ContactsView`, `ReportsView`)
- `src/components/` - Shared UI components (`NavBar`)
- `src/router/` - Client-side routing with navigation guards
- `src/composables/` - Reusable composition logic (`useWhoAmI`)
- `src/utils/` - Global helper modules and HTTP client configuration (`api.js`)
- `src/App.vue` - Root application component
- `src/main.js` - Application entry point

## Scripts

Install dependencies:
```bash
npm install
```

Start the development server:
```bash
npm run dev
```

Build the application for production:
```bash
npm run build
```
