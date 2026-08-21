const { test, expect } = require('@playwright/test');

test('OKGO Super Admin Login', async ({ page }) => {
    await page.goto('http://192.168.1.33:3001');

    await page.locator('input[type="email"]')
    .fill(process.env.OKGO_EMAIL);

await page.locator('input[type="password"]')
    .fill(process.env.OKGO_PASSWORD);

    await page.getByRole('button', { name: 'Sign in' }).click();

    await page.waitForURL(
        url => !url.pathname.includes('/login'),
        { timeout: 15000 }
    );

    await page.screenshot({
        path: 'screenshots/super-admin-dashboard.png',
        fullPage: true
    });
});