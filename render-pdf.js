// render-pdf.js — Render HTML to A4 PDF via Playwright native print engine.
const { chromium } = require("playwright");
const path = require("path");

(async () => {
  const [, , inputHtml, outputPdf] = process.argv;
  if (!inputHtml || !outputPdf) {
    console.error("Usage: node render-pdf.js input.html output.pdf");
    process.exit(1);
  }
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    deviceScaleFactor: 1,
    viewport: { width: 1240, height: 1754 },
  });
  const page = await context.newPage();
  await page.goto("file://" + path.resolve(inputHtml), { waitUntil: "networkidle" });
  await page.pdf({
    path: outputPdf,
    format: "A4",
    margin: { top: "0.75in", bottom: "0.75in", left: "0.75in", right: "0.75in" },
    printBackground: true,
    preferCSSPageSize: true,
  });
  await browser.close();
  console.log(`PDF generated: ${outputPdf}`);
})();
