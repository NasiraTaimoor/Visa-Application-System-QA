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

await page.screenshot({
    path: 'screenshots/login-result.png',
    fullPage: true
});

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

// Open Agency Management
await page.goto('http://192.168.1.33:3001/dashboard/agencies');

await expect(
    page.getByRole('heading', {
        name: 'Agency Management',
        exact: true
    })
).toBeVisible({ timeout: 15000 });

// Generate unique test data
const uniqueId = Date.now();

// Company identity
await page.getByLabel('Company name').fill(`OKGO Test Agency ${uniqueId}`);
await page.getByLabel('Trade name').fill(`OKGO Trade ${uniqueId}`);
await page.getByLabel('Register number').fill(`REG-${uniqueId}`);
await page.locator('#licenseNumber').fill(`LIC-${uniqueId}`);
await page.getByLabel('Legal type').fill('Limited Liability Company');
await page.locator('#mainLicenseNumber').fill(`MAIN-${uniqueId}`);
// HTML date inputs require YYYY-MM-DD
await page.getByLabel('Contract expiry date').fill('2030-12-31');

// Contact details
await page.getByLabel('Address').fill('Business Bay, Dubai');
await page.getByLabel('City').fill('Dubai');

await page.getByLabel('Country').click();

await page.getByRole('option', {
    name: 'United Arab Emirates',
    exact: true
}).click();

await page.getByLabel('Phone number').fill('+971501234567');
await page.getByLabel('Email').fill(`agency.${uniqueId}@example.com`);

// Banking details
await page.getByLabel('Currency').click();

await page.getByRole('option', {
    name: 'AED',
    exact: true
}).click();

await page.getByLabel('Bank name').fill('Test Bank UAE');
await page.getByLabel('Account number').fill(`AE${uniqueId}`);
await page.getByLabel('Bank code').fill('TESTAEAD');
await page.getByLabel('Bank contact person').fill('Ahmed Test');

// Evidence before submission
await page.screenshot({
    path: 'screenshots/03-create-agency-form.png',
    fullPage: true
});

// Submit the form
await page.getByRole('button', {
    name: 'Create agency',
    exact: true
}).click();

// Verify successful creation
await expect(
    page.getByText(/agency created successfully/i)
).toBeVisible({ timeout: 15000 });

await page.screenshot({
    path: 'screenshots/04-agency-created.png',
    fullPage: true
});
});