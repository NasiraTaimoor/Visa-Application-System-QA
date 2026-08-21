const { test, expect } = require('@playwright/test');

test('OKGO Dashboard Test', async ({ page }) => {

    // Open Login Page
    await page.goto('file:///C:/Users/DELL/Downloads/OKGO%20Demo/OKGO%20Demo/OKGO%20Visa%20Platform.html');

    // Login
    await page.locator('input[type="email"]').fill('tom@okgo.ae');
    await page.locator('input[type="password"]').fill('123456');

    await page.screenshot({
        path: 'screenshots/01_Login.png',
        fullPage: true
    });

    await page.getByRole('button', { name: 'Sign in' }).click();

    // Wait for dashboard
    await page.waitForLoadState('networkidle');

    await page.screenshot({
        path: 'screenshots/02_Dashboard.png',
        fullPage: true
    });

    // Verify Welcome Text
    await expect(page.getByText('Good morning, Tom')).toBeVisible();

    // Verify Dashboard Cards
await expect(page.getByText('Total Applications')).toBeVisible();

await expect(page.getByText('Approved').first()).toBeVisible();

await expect(
    page.getByText('Under Processing', { exact: true }).first()
).toBeVisible();

await expect(
    page.getByText('Rejected', { exact: true }).first()
).toBeVisible();

    // Verify Left Menu
    await expect(page.getByText('Total Applications')).toBeVisible();

await expect(page.getByText('Approved').first()).toBeVisible();

await expect(page.getByText('Under Processing').first()).toBeVisible();

await expect(page.getByText('Rejected').first()).toBeVisible();

    // Verify Recent Applications
    await expect(page.getByText('Recent Applications')).toBeVisible();

    // Verify Alerts
    await expect(page.getByText('Alerts')).toBeVisible();

    // Verify Credit
    await expect(page.getByText('AED 412,500')).toBeVisible();

    // Verify Quota
    await expect(page.getByText('318 quota left')).toBeVisible();

    // Click New Application
    await page.getByRole('button', { name: '+ New Application' }).click();

    await page.waitForLoadState('networkidle');

    await page.screenshot({
        path: 'screenshots/03_New_Application.png',
        fullPage: true
    });

});