import os
from playwright.sync_api import sync_playwright

def main():
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    os.makedirs(assets_dir, exist_ok=True)

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # Login page screenshot
        print("Navigating to login page...")
        page.goto('http://localhost:5173/')
        page.wait_for_timeout(500)
        print("Capturing login_page.png...")
        page.screenshot(path=os.path.join(assets_dir, 'login_page.png'))

        # Login as Admin
        print("Logging in as Admin...")
        page.fill('input[type="email"]', 'admin@example.com')
        page.fill('input[type="password"]', 'password123')
        page.click('button[type="submit"]')

        # Wait for navigation to orders
        print("Waiting for /orders...")
        page.wait_for_url('**/orders')
        page.wait_for_timeout(1000)
        print("Capturing admin_orders.png...")
        page.screenshot(path=os.path.join(assets_dir, 'admin_orders.png'))

        # Navigate to Products
        print("Navigating to Products...")
        page.click('text=Products')
        page.wait_for_url('**/products')
        page.wait_for_timeout(1000)
        print("Capturing admin_products.png...")
        page.screenshot(path=os.path.join(assets_dir, 'admin_products.png'))

        # Navigate to Contacts
        print("Navigating to Contacts...")
        page.click('text=Contacts')
        page.wait_for_url('**/contacts')
        page.wait_for_timeout(1000)
        print("Capturing admin_contacts.png...")
        page.screenshot(path=os.path.join(assets_dir, 'admin_contacts.png'))

        # Navigate to Reports
        print("Navigating to Reports...")
        page.click('text=Reports')
        page.wait_for_url('**/reports')
        page.wait_for_timeout(1000)
        print("Capturing admin_reports.png...")
        page.screenshot(path=os.path.join(assets_dir, 'admin_reports.png'))

        # Logout and login as Manager
        print("Logging out...")
        page.click('text=Sign out')
        page.wait_for_url('**/')
        
        print("Logging in as Manager...")
        page.fill('input[type="email"]', 'manager@example.com')
        page.fill('input[type="password"]', 'password123')
        page.click('button[type="submit"]')

        # Wait for manager dashboard
        page.wait_for_url('**/orders')
        page.wait_for_timeout(1000)
        print("Capturing manager_orders.png...")
        page.screenshot(path=os.path.join(assets_dir, 'manager_orders.png'))

        print("Done capturing screenshots.")
        browser.close()

if __name__ == '__main__':
    main()
