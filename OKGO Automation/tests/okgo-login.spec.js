const { test, expect } = require('@playwright/test');

test('OKGO Super Admin Login with OTP', async ({ page }) => {
    // Open application
    await page.goto('http://192.168.1.33:3001');

    // Enter login details
    await page.locator('input[type="email"]')
        .fill(process.env.OKGO_EMAIL);

    await page.locator('input[type="password"]')
        .fill(process.env.OKGO_PASSWORD);

    await page.getByRole('button', { name: 'Sign in' }).click();

    // Verify OTP page opened
    await expect(page).toHaveURL(/verify-otp/, {
        timeout: 15000
    });

    await expect(
        page.getByText('Enter your one-time code')
    ).toBeVisible();

    // Enter the current OTP
    await page.getByLabel('One-time code')
        .fill(process.env.OKGO_OTP);

    await page.screenshot({
        path: 'screenshots/01-otp-page.png',
        fullPage: true
    });

    // Submit OTP
    await page.getByRole('button', {
        name: 'Verify',
        exact: true
    }).click();

    // Confirm successful OTP verification
    await expect(page).not.toHaveURL(/verify-otp/, {
        timeout: 15000
    });

    await page.screenshot({
        path: 'screenshots/02-super-admin-dashboard.png',
        fullPage: true
    });
});