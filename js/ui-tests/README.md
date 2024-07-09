# Testing ipyaladin interactively

## Setup and run the tests

At the root of the repo (not here):

```sh
npm install
pip install .
pip install jupyterlab
npx playwright install chromium
npx playwright test
```

There is also a GUI to see the tests execute steps by steps:

```sh
npx playwright test --ui
```

## How to extend the tests

We have access to [Playwright](https://playwright.dev/docs/intro) and
[Galata](https://github.com/jupyterlab/jupyterlab/tree/main/galata)' s APIs.

The interactive tests generation of playwright can be useful:

```sh
npx playwright codegen playwright.dev
```

but it does not know about all the helpers methods that Galata introduces to help with
notebooks testing.

## Debug

```sh
npx playwright test my_test.spec.js --debug
```

## Update the snapshots

Open the test server

```sh
npm run start-test-server
```

then update the snapshots

```sh
npx playwright test --update-snapshots
```
