import { type Page, expect, test } from "@playwright/test";

// The interface the way a first-time user meets it: menus, accounts, private uploads, failures,
// and the phone layout. No model is needed; the stack runs without an API key in CI.

const FIXTURE = "e2e/fixtures/review-board-notes.pdf";
// An upload without a title in its metadata is named after its file.
const TITLE = "review-board-notes";

async function open(page: Page) {
  await page.goto("/");
  await page.evaluate(() => localStorage.clear());
  await page.goto("/");
  await expect(page.locator("#question")).toBeVisible();
}

async function createAccount(page: Page, email: string) {
  await page.locator('header button[aria-controls="sign-in"]').click();
  const form = page.locator("form#sign-in");
  await form.getByRole("button", { name: "Create an account" }).click();
  await form.locator("input[type=email]").fill(email);
  await form.locator("input[type=password]").fill("browser-test-pass");
  await form.getByRole("button", { name: "Create account" }).click();
  await expect(page.locator("header")).toContainText(email);
}

test("the sign-in menu closes like any menu", async ({ page }) => {
  await open(page);
  const trigger = page.locator('header button[aria-controls="sign-in"]');
  const form = page.locator("form#sign-in");

  await trigger.click();
  await expect(form.locator("input[type=email]")).toBeFocused();
  const box = await form.boundingBox();
  const width = page.viewportSize()?.width ?? 0;
  expect(box && box.x >= 0 && box.x + box.width <= width + 1).toBeTruthy();

  await page.keyboard.press("Escape");
  await expect(form).toBeHidden();
  await expect(trigger).toBeFocused();

  await trigger.click();
  await page.locator("#question").click();
  await expect(form).toBeHidden();

  await trigger.click();
  await page.getByRole("button", { name: "New conversation" }).click();
  await expect(form).toBeHidden();
});

test("an upload stays private to its account", async ({ page }, info) => {
  test.skip(info.project.name === "phone", "one viewport is enough for accounts");
  test.setTimeout(150_000); // ingestion alone may take up to a minute
  const owner = `owner-${Date.now()}@callslip.invalid`;
  await open(page);
  await createAccount(page, owner);

  await page.locator("input[type=file]").setInputFiles(FIXTURE);
  const mine = page.locator(".doc-own", { hasText: TITLE });
  await expect(mine).toBeVisible();
  await expect(mine).not.toContainText(/Queued|Processing/, { timeout: 60_000 });
  await expect(mine).not.toContainText("Failed");
  await expect(mine).toContainText("1 page, 1 passage");

  // Another account, then nobody signed in: neither sees it.
  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page.locator(".docs")).not.toContainText(TITLE);
  await createAccount(page, `other-${Date.now()}@callslip.invalid`);
  await expect(page.locator(".docs")).not.toContainText(TITLE);
  await page.getByRole("button", { name: "Sign out" }).click();

  // Its owner signs back in, sees it, and deletes it.
  await page.locator('header button[aria-controls="sign-in"]').click();
  await page.locator("form#sign-in input[type=email]").fill(owner);
  await page.locator("form#sign-in input[type=password]").fill("browser-test-pass");
  await page.locator("form#sign-in").getByRole("button", { name: "Sign in" }).click();
  await expect(mine).toBeVisible();
  page.once("dialog", (d) => d.accept());
  await mine.getByRole("button", { name: /^Delete / }).click();
  await expect(mine).toHaveCount(0);
});

test("a wrong password and a file that is not a PDF are explained", async ({ page }, info) => {
  test.skip(info.project.name === "phone", "one viewport is enough for messages");
  await open(page);
  await page.locator('header button[aria-controls="sign-in"]').click();
  await page.locator("form#sign-in input[type=email]").fill(`nobody-${Date.now()}@callslip.invalid`);
  await page.locator("form#sign-in input[type=password]").fill("not-the-password");
  await page.locator("form#sign-in").getByRole("button", { name: "Sign in" }).click();
  await expect(page.locator("form#sign-in [role=alert]")).toHaveText(
    "The email or the password is not right.",
  );
  await page.keyboard.press("Escape");

  await page.locator("input[type=file]").setInputFiles({
    name: "notes.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("not really a pdf"),
  });
  await expect(page.locator(".docs .notice")).toContainText("notes.pdf:");
});

test("a question without a configured model says so and keeps the text", async ({ page }, info) => {
  test.skip(!!process.env.HAS_MODEL, "only meaningful without an API key");
  test.skip(info.project.name === "phone", "one viewport is enough for this message");
  await open(page);
  await page.locator("#question").fill("What does the review board require?");
  await page.locator("#question").press("Enter");
  await expect(page.locator(".talk [role=alert]")).toContainText("Answering is not configured");
  await expect(page.locator("#question")).toHaveValue("What does the review board require?");
});

test("an unreachable server gives a plain message, and Try again recovers", async ({ page }) => {
  await open(page);
  await page.route("**/api/sessions/*/runs", (route) => route.abort());
  await page.locator("#question").fill("Is anyone there?");
  await page.locator("#question").press("Enter");
  await expect(page.locator(".talk [role=alert]")).toHaveText(
    "Could not reach the server. Check your connection and try again.",
  );
  await expect(page.locator("#question")).toHaveValue("Is anyone there?");

  await page.route("**/api/documents", (route) => route.abort());
  await page.reload();
  const message = page.locator(".docs [role=alert]");
  await expect(message).toContainText("Could not reach the server");
  await page.unroute("**/api/documents");
  await message.getByRole("button", { name: "Try again" }).click();
  await expect(message).toHaveCount(0);
});

test("on a phone the question comes before the library", async ({ page }, info) => {
  test.skip(info.project.name !== "phone", "phone layout only");
  await open(page);
  const top = async (sel: string) => (await page.locator(sel).boundingBox())?.y ?? Infinity;
  expect(await top(".talk")).toBeLessThan(await top(".docs"));
  expect(await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)).toBe(0);
});

test("where guests cannot upload, a signed-out visitor is told to sign in", async ({ page }) => {
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({ json: { email: null, guest_uploads: false } }),
  );
  await open(page);
  await expect(page.locator(".docs")).toContainText("Sign in to upload your own PDFs.");
  await expect(page.locator(".docs input[type=file]")).toHaveCount(0);
});

test("with every scrollbar showing, nothing scrolls sideways", async ({ page }, info) => {
  await open(page);
  const widths = info.project.name === "phone" ? [0] : [1440, 1100];
  for (const width of widths) {
    if (width) await page.setViewportSize({ width, height: 800 });
    // A scrollbar takes width from its panel; show each one as a long list would.
    const sideways = await page.evaluate(() => {
      const all = [...document.querySelectorAll<HTMLElement>("*")];
      for (const el of all) if (getComputedStyle(el).overflowY === "auto") el.style.overflowY = "scroll";
      return all
        .filter((el) => ["auto", "scroll"].includes(getComputedStyle(el).overflowX))
        .filter((el) => el.scrollWidth > el.clientWidth + 1)
        .map((el) => `${el.tagName.toLowerCase()}.${el.className}`);
    });
    expect(sideways, `at ${width || "phone"} width`).toEqual([]);
  }
});

test("a question pasted past the limit says it was cut", async ({ page }) => {
  await open(page);
  const box = page.locator("#question");
  await box.focus();
  await page.keyboard.insertText("Explain the governance function. ".repeat(80));
  await expect(box).toHaveValue(/^Explain/);
  expect((await box.inputValue()).length).toBe(2000);
  await expect(page.locator(".limit-hint")).toHaveText("Up to 2,000 characters; longer text is cut off.");
  await box.press("Backspace");
  await expect(page.locator(".limit-hint")).toHaveCount(0);
});
