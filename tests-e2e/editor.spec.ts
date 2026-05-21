import { test, expect } from '@playwright/test';

test.describe('Editor Workspace', () => {
  test.beforeEach(async ({ page }) => {
    // Set mock token to simulate logged-in state
    await page.addInitScript(() => {
      window.localStorage.setItem('lyricai_token', 'mock-token');
    });

    // Mock user info API with full expected structure
    await page.route('**/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ 
            first_name: 'John', 
            last_name: 'Doe', 
            email: 'john@example.com',
            contribution_level: 'Pro',
            stats: { total_songs: 5 }
        })
      });
    });

    await page.goto('/index.html');
  });

  test('should display user name and avatar', async ({ page }) => {
    // Wait for the name to be set by JS
    await expect(page.locator('#user-name')).toContainText('John Doe', { timeout: 10000 });
    await expect(page.locator('#user-info')).toBeVisible();
  });

  test('should allow entering song details', async ({ page }) => {
    const titleInput = page.locator('#song-title-input');
    const lyricsInput = page.locator('#lyrics-input');

    await titleInput.fill('My Awesome Song');
    await lyricsInput.fill('These are the lyrics of the song\nWith multiple lines.');

    await expect(titleInput).toHaveValue('My Awesome Song');
    await expect(lyricsInput).toHaveValue(/These are the lyrics/);
  });

  test('should toggle library sidebar', async ({ page }) => {
    // Mock songs list for sidebar
    await page.route('**/songs', async route => {
        if (route.request().method() === 'GET') {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([{ id: '1', title: 'Test Song', lyrics: 'Test', updated_at: new Date() }])
            });
        } else {
            await route.continue();
        }
    });

    await page.click('#toggle-library-btn');
    // The class -translate-x-full should be removed when sidebar is shown
    await expect(page.locator('#library-sidebar')).not.toHaveClass(/.*-translate-x-full.*/);
    
    await page.click('#close-library-btn');
    // Check if it's hidden again
    await expect(page.locator('#library-sidebar')).toHaveClass(/.*-translate-x-full.*/);
  });

  test('should run analysis and display results', async ({ page }) => {
    await page.fill('#lyrics-input', 'Test lyrics for analysis');
    
    // Mock the analysis API with correct endpoint and payload keys
    await page.route('**/webhook/analyze-lyrics', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          structure_output: "Standard Verse-Chorus-Verse",
          mood_output: "Energetic and uplifting",
          metaphors_output: "The sun is a golden coin",
          poet_output: "Тестовый перевод лирики",
          musical_data: {
            key: "C Major",
            bpm: "120"
          }
        })
      });
    });

    // Mock save call that triggers automatically after analysis
    await page.route('**/songs', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'new-song-id' })
        });
      });

    await page.click('#analyze-btn');
    
    await expect(page.locator('#mood-output')).toContainText('Energetic');
    await expect(page.locator('#poet-output')).toContainText('Тестовый перевод');
  });
});
