import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/registration.html');
  });

  test('should show registration form by default', async ({ page }) => {
    await expect(page.locator('#page-title')).toContainText('LyricAI Studio');
    await expect(page.locator('#submit-btn')).toContainText('CREATE ACCOUNT');
  });

  test('should switch to login mode', async ({ page }) => {
    await page.click('#tab-login');
    await expect(page.locator('#submit-btn')).toContainText('WELCOME BACK');
    // Ensure the name fields are hidden in login mode
    await expect(page.locator('#name-fields')).toHaveClass(/.*hidden.*/);
  });

  test('should show error on failed login', async ({ page }) => {
    await page.click('#tab-login');
    await page.fill('#email', 'wrong@example.com');
    await page.fill('#password', 'wrongpassword');
    
    // Mock the API response for failed login
    await page.route('**/login', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid credentials' })
      });
    });

    await page.click('#submit-btn');
    await expect(page.locator('#error-message')).toBeVisible();
    await expect(page.locator('#error-message')).toContainText('Invalid credentials');
  });

  test('should redirect to editor on successful login', async ({ page }) => {
    await page.click('#tab-login');
    await page.fill('#email', 'test@example.com');
    await page.fill('#password', 'password123');

    await page.route('**/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ access_token: 'mock-token' })
      });
    });

    // Mock initial editor data to prevent redirect back
    await page.route('**/me', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ 
            first_name: 'Test', 
            last_name: 'User', 
            email: 'test@example.com',
            contribution_level: 'Free',
            stats: { total_songs: 0 }
          })
        });
      });

    await page.click('#submit-btn');
    await expect(page).toHaveURL(/.*index.html/);
  });
});
