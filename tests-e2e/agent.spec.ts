import { test, expect } from '@playwright/test';

test.describe('Agent PRO Workspace', () => {
  test.beforeEach(async ({ page, context }) => {
    // Grant clipboard permissions
    await context.grantPermissions(['clipboard-read', 'clipboard-write']);

    // Set initial state in localStorage
    await page.addInitScript(() => {
      window.localStorage.setItem('lyricai_token', 'mock-agent-token');
      window.localStorage.setItem('lyricai_title', 'Test Song Title');
      window.localStorage.setItem('lyricai_original', 'Original lyrics here');
      window.localStorage.setItem('lyricai_translation', 'Literal translation here');
    });

    // Mock user info
    await page.route('**/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ 
            first_name: 'Agent', 
            last_name: 'Tester', 
            email: 'agent@tester.com',
            contribution_level: 'Pro',
            stats: { total_songs: 10 }
        })
      });
    });

    await page.goto('/agent.html');
  });

  test('should initialize with data from editor', async ({ page }) => {
    await expect(page.locator('#song-title-display')).toHaveText('Test Song Title');
    await expect(page.locator('#manuscript-body')).toContainText('Literal translation here');
  });

  test('should run full analysis (Rocinante + Euryale)', async ({ page }) => {
    // Mock Harmony API
    await page.route('**/webhook/analyze-harmony', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          key: "G Minor",
          bpm: "95",
          chords_verse: "Gm - Eb - Bb - F",
          chords_chorus: "Cm - Dm - Gm"
        })
      });
    });

    // Mock Poet Agent (Rocinante) API
    await page.route('**/webhook/poet-agent', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          poetDraft: "Draft by Rocinante\nBeautiful and rhymed."
        })
      });
    });

    await page.click('#analyze-manuscript-btn');

    // Check Harmony results
    await expect(page.locator('#harmony-key')).toHaveText('G Minor');
    await expect(page.locator('#harmony-bpm')).toHaveText('95 BPM');
    await expect(page.locator('#chords-verse')).toHaveText('Gm - Eb - Bb - F');

    // Check Edited Results
    await expect(page.locator('#result-body')).toContainText('Draft by Rocinante');
    
    // Check Status Badge
    await expect(page.locator('#status-check')).toBeVisible();
    await expect(page.locator('#status-check')).toContainText('Verified by Rocinante');
  });

  test('should polish results using Claude', async ({ page }) => {
    // Pre-populate with a Rocinante draft to test polishing
    await page.evaluate(() => {
        window.localStorage.setItem('lyricai_refined', 'Draft from earlier');
    });
    await page.reload();

    // Mock Literary Editor (Claude) API
    await page.route('**/webhook/literary-editor', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          editor_output: "Final Polished version by Claude\nMasterpiece level."
        })
      });
    });

    await page.click('#deep-analyze-btn');

    await expect(page.locator('#result-body')).toContainText('Polished version by Claude');
    await expect(page.locator('#status-check')).toContainText('Polished by Claude');
  });

  test('should handle copy functionality', async ({ page }) => {
    // Provide some text to copy
    await page.evaluate(() => {
        document.getElementById('result-body').innerText = "Copy me!";
    });

    await page.click('#copy-refined-btn');
    await expect(page.locator('#copy-refined-btn')).toHaveText('COPIED!');
  });
});
