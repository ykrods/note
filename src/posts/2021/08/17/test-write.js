const { test } = require("uvu");
const assert = require("uvu/assert");
const firebase = require("@firebase/rules-unit-testing");

const projectId = "example";
const databaseName = "example-db";

function applyRules(rules) {
  return firebase.loadDatabaseRules({
    databaseName,
    rules: JSON.stringify({ rules }),
  });
}

async function resetDB(app) {
  await applyRules({ ".read": true, ".write": true })
  await app.database().ref("/").set({});
}

async function assertPermissionDenied(fn) {
  try {
    await fn();
    assert.unreachable();
  } catch(error) {
    assert.equal(error.code, "PERMISSION_DENIED");
  }
}

test.before(async (ctx) => {
  console.log("setUp");
  ctx.app = await firebase.initializeTestApp({
    projectId,
    databaseName,
    // auth: { uid: "alice", email: "alice@exapmle.com" },
  });
});

test.after(async () => {
  await Promise.all(firebase.apps().map(app => app.delete()));
  console.log("tearDown");
});

test.after.each(async (ctx) => {
  await resetDB(ctx.app);
});

test("nazo", async (ctx) => {
  await applyRules({
    "themes": {
      "$theme": {
        "color": {
          ".write": true,
          ".validate": "newData.isString()"
        },
        "backgroundColor": {
          ".write": true,
          ".validate": "newData.isString()"
        },
      }
    }
  });
  const db = ctx.app.database();

  await db.ref().update({
    "themes/light/color": "black",
    "themes/light/backgroundColor": "white",
  })

  await db.ref('themes/light').remove();
});


test.run();
