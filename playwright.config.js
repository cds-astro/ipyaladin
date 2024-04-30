/**
 * Configuration for Playwright using default from @jupyterlab/galata
 */
const baseConfig = require("@jupyterlab/galata/lib/playwright-config");

module.exports = {
  ...baseConfig,
  testDir: "./js/ui-tests",
  webServer: {
    command: "npm run start-test-server",
    url: "http://localhost:8888/lab",
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI,
  },
  expect: {
    toMatchSnapshot: { maxDiffPixelRatio: 0.02 }, // allow 2% difference on snapshots
  },
};
