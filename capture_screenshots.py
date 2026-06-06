import os
from playwright.sync_api import sync_playwright

inject_mac_ui = """() => {
    // If captureArea already exists, just return to prevent double injection
    if (document.getElementById('mac-capture-area')) return;

    const captureArea = document.createElement('div');
    captureArea.id = 'mac-capture-area';
    captureArea.style.padding = '40px';
    captureArea.style.background = 'transparent';
    captureArea.style.width = '800px';
    captureArea.style.minHeight = '760px';
    captureArea.style.height = 'max-content';
    captureArea.style.boxSizing = 'border-box';
    captureArea.style.display = 'flex';
    captureArea.style.flexDirection = 'column';

    const macWindow = document.createElement('div');
    macWindow.style.borderRadius = '12px';
    macWindow.style.overflow = 'hidden';
    macWindow.style.boxShadow = '0 25px 50px -12px rgba(0,0,0,0.5)';
    macWindow.style.border = '1px solid #333';
    macWindow.style.backgroundColor = '#0f0f11';
    macWindow.style.width = '100%';
    macWindow.style.flex = '1';
    macWindow.style.display = 'flex';
    macWindow.style.flexDirection = 'column';

    const titlebar = document.createElement('div');
    titlebar.style.display = 'flex';
    titlebar.style.alignItems = 'center';
    titlebar.style.padding = '14px 20px';
    titlebar.style.background = '#1a1a1f';
    titlebar.style.borderBottom = '1px solid #2e2e36';
    
    titlebar.innerHTML = `
      <div style="width: 12px; height: 12px; border-radius: 50%; background: #ff5f56; margin-right: 8px;"></div>
      <div style="width: 12px; height: 12px; border-radius: 50%; background: #ffbd2e; margin-right: 8px;"></div>
      <div style="width: 12px; height: 12px; border-radius: 50%; background: #27c93f;"></div>
    `;

    macWindow.appendChild(titlebar);

    const app = document.getElementById('app');
    
    const appContainer = document.createElement('div');
    appContainer.style.flex = '1';
    appContainer.style.overflow = 'visible';
    appContainer.style.position = 'relative';
    appContainer.style.display = 'flex';
    appContainer.style.flexDirection = 'column';

    const style = document.createElement('style');
    style.innerHTML = '.page-center { flex: 1 !important; display: flex !important; flex-direction: column !important; justify-content: center !important; }';
    document.head.appendChild(style);

    app.parentNode.insertBefore(captureArea, app);
    appContainer.appendChild(app);
    
    app.style.flex = '1';
    app.style.display = 'flex';
    app.style.flexDirection = 'column';
    app.style.width = '100%';

    macWindow.appendChild(appContainer);
    captureArea.appendChild(macWindow);
    
    document.body.style.background = 'transparent';
    document.body.style.height = 'max-content';
    document.documentElement.style.height = 'max-content';
}
"""

def main():
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    os.makedirs(assets_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 880, 'height': 800})
        page = context.new_page()

        print("Navigating to login page...")
        page.goto('http://localhost:5173/')
        page.wait_for_timeout(500)
        
        # Inject the Mac UI
        print("Injecting Mac UI...")
        page.evaluate(inject_mac_ui)
        wrapper = page.locator('#mac-capture-area')

        print("Capturing login_page.png...")
        wrapper.screenshot(path=os.path.join(assets_dir, 'login_page.png'), omit_background=True)

        print("Logging in as Admin...")
        page.fill('input[type="email"]', 'admin@example.com')
        page.fill('input[type="password"]', 'password123')
        page.click('button[type="submit"]')

        print("Waiting for /orders...")
        page.wait_for_url('**/orders')
        page.wait_for_timeout(1000)
        print("Capturing admin_orders.png...")
        wrapper.screenshot(path=os.path.join(assets_dir, 'admin_orders.png'), omit_background=True)

        print("Navigating to Products...")
        page.click('text=Products')
        page.wait_for_url('**/products')
        page.wait_for_timeout(1000)
        print("Capturing admin_products.png...")
        wrapper.screenshot(path=os.path.join(assets_dir, 'admin_products.png'), omit_background=True)

        # Capture Github social preview (1600x800)
        print("Capturing github-social-preview.png...")
        page.set_viewport_size({"width": 1650, "height": 850})
        page.evaluate('''() => {
            const el = document.getElementById('mac-capture-area');
            el.style.width = '1600px';
            el.style.height = '800px';
        }''')
        page.wait_for_timeout(500)
        wrapper.screenshot(path=os.path.join(assets_dir, 'github-social-preview.png'), omit_background=True)
        
        # Restore size
        page.evaluate('''() => {
            const el = document.getElementById('mac-capture-area');
            el.style.width = '800px';
            el.style.height = 'max-content';
        }''')
        page.set_viewport_size({"width": 880, "height": 800})

        print("Navigating to Contacts...")
        page.click('text=Contacts')
        page.wait_for_url('**/contacts')
        page.wait_for_timeout(1000)
        print("Capturing admin_contacts.png...")
        wrapper.screenshot(path=os.path.join(assets_dir, 'admin_contacts.png'), omit_background=True)

        print("Navigating to Reports...")
        page.click('text=Reports')
        page.wait_for_url('**/reports')
        page.wait_for_timeout(1000)
        print("Capturing admin_reports.png...")
        wrapper.screenshot(path=os.path.join(assets_dir, 'admin_reports.png'), omit_background=True)

        print("Logging out...")
        page.click('text=Sign out')
        page.wait_for_url('**/')
        
        print("Logging in as Manager...")
        page.fill('input[type="email"]', 'manager@example.com')
        page.fill('input[type="password"]', 'password123')
        page.click('button[type="submit"]')

        page.wait_for_url('**/orders')
        page.wait_for_timeout(1000)
        print("Capturing manager_orders.png...")
        wrapper.screenshot(path=os.path.join(assets_dir, 'manager_orders.png'), omit_background=True)

        print("Done capturing screenshots.")
        browser.close()

if __name__ == '__main__':
    main()
