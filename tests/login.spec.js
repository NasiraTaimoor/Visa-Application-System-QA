const { test, expect } = require('@playwright/test');

test('OKGO Login Test', async ({ page }) => {

  // Open application
  await page.goto('file:///C:/Users/DELL/Downloads/OKGO%20Demo/OKGO%20Demo/OKGO%20Visa%20Platform.html');

  // Enter email
  await page.locator('input[type="email"]').fill('tom@okgo.ae');

  // Enter password
  await page.locator('input[type="password"]').fill('123456');

  // Click Sign In
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Wait for the next page to load
  await page.waitForLoadState('networkidle');

  // Take screenshot
  await page.screenshot({
    path: 'login-success.png',
    fullPage: true
  });
 

});