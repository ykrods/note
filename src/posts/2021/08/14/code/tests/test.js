/**
 * firebase realtime database のルールの検証コード
 *
 * - 普通にアプリをテストする際は firebase.json の中で指定したルールファイルが
 *   エミュレータに適用されるため、 loadDatabaseRules を使う必要はない
 *   ( テストデータを一時投入する場合に、 firebase-admin を使う代わりに
 *     一時的にルールを書き換えるのに使うのはまぁアリかもしれない？
 *
 * - emulator は事前に立ち上げておく必要アリ
 */

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

test("簡単な書き込み成功例", async(ctx) => {
  await applyRules({
    ".write": true
  });

  const db = ctx.app.database();
  await db.ref(`foo`).set({ bar: "baz" });
  assert.ok(true);
});

test("簡単な書き込みの失敗例", async (ctx) => {
  await applyRules({
    ".write": false
  });

  const db = ctx.app.database();
  await assertPermissionDenied(() => {
    return db.ref(`foo`).set({ bar: "baz" });
  });
});

test("上書き・削除を禁止", async (ctx) => {
  await applyRules({
    items: {
      "$item": {
        ".write": "!data.exists()"
      }
    }
  });
  const db = ctx.app.database();

  // arrange
  const ref = await db.ref("items").push({ name: "foo" });

  // overwite
  await assertPermissionDenied(() => {
    return ref.set({ name: "bar" });
  });

  // add field
  await assertPermissionDenied(() => {
    return ref.update({ foo: 0 });
  });

  // remove
  await assertPermissionDenied(() => {
    return ref.remove();
  });

  // equivalent to remove
  await assertPermissionDenied(() => {
    return ref.set(null);
  });
});

test("上書きは禁止するが削除は可能", async (ctx) => {
  await applyRules({
    items: {
      "$item": {
        ".write": "!data.exists() || !newData.exists()"
      }
    }
  });
  const db = ctx.app.database();

  // prepare
  const ref = await db.ref("items").push({ name: "foo" });

  await assertPermissionDenied(() => {
    return ref.set({ name: "bar" });
  });

  await ref.remove();

  // 削除されたので書き込み可能になる
  await ref.set({ name: "bar" });

  await ref.set(null);
  assert.ok(true);
});

test("バリデーション", async (ctx) => {
  await applyRules({
    "items": {
      "$item": {
        ".write": true,
        ".validate": "newData.hasChildren(['name', 'num'])",
        "name": { ".validate": "newData.isString()" },
        "num": { ".validate": "newData.isNumber()" },
        "$other": { ".validate": false },
      }
    }
  });
  const db = ctx.app.database();

  await db.ref("items").push({ name: "foo", num: 10 });

  await assertPermissionDenied(() => {
    return db.ref("items").push({ name: 0, num: 10 });
  });

  await assertPermissionDenied(() => {
    return db.ref("items").push({ name: "foo", num: "x" });
  });

  await assertPermissionDenied(() => {
    return db.ref("items").push({ name: "foo" });
  });

  // $other のテスト
  await assertPermissionDenied(() => {
    return db.ref("items").push({ foo: "bar" });
  });

  await assertPermissionDenied(() => {
    return db.ref("items").push({ name: "n", num: 1, foo: "bar" });
  });

  assert.ok(true);
});

test("バリデーション(範囲)", async (ctx) => {
  await applyRules({
    "items": {
      "$item": {
        ".write": true,
        ".validate": "newData.hasChildren(['name', 'num'])",
        "name": {
          ".validate": "newData.isString() && " +
            "1 < newData.val().length && newData.val().length < 10"
        },
        "num": {
          ".validate": "newData.isNumber() && " +
            "0 < newData.val() && newData.val() < 100"
        },
        "$other": { ".validate": false },
      }
    }
  });
  const db = ctx.app.database();

  await db.ref("items").push({ name: "foo", num: 10 });

  await assertPermissionDenied(() => {
    return db.ref("items").push({ name: "a", num: 10 });
  });

  await assertPermissionDenied(() => {
    return db.ref("items").push({ name: "0123456789", num: 10 });
  });

  await assertPermissionDenied(() => {
    return db.ref("items").push({ name: "foo", num: 0 });
  });

  assert.ok(true);
});

test("フィールドごとの書き込み制御", async (ctx) => {
  await applyRules({
    "comments": {
      "$comment": {
        ".write": "(!data.child('name').exists() && !data.child('body').exists()) || (data.child('name').val() === newData.child('name').val() && data.child('body').val() === newData.child('body').val())",
      }
    }
  });
  const db = ctx.app.database();

  const ref = await db.ref("comments").push({ name: "foo", body: "xxxx" });
  await ref.update({ fav: 10 });

  await assertPermissionDenied(() => {
    return ref.update({ name: "bar" });
  });
});


test(".write の分割", async (ctx) => {
  await applyRules({
    "comments": {
      "$comment": {
        "name": { ".write": "!data.exists()" },
        "body": { ".write": "!data.exists()" },
        "fav": { ".write": "(!data.exists() && newData.val() === 0) || newData.val() === data.val() + 1" }
      }
    }
  });
  const db = ctx.app.database();

  // const ref = await db.ref("comments").push({ name: "foo", body: "xxxx" });
  const ref = await db.ref("comments").push()
  await ref.update({ name: "foo", body: "xxxx" });

  await assertPermissionDenied(() => {
    return ref.update({ name: "bar" });
  });

  await ref.update({ fav: 0 });

  await assertPermissionDenied(() => {
    return ref.update({ fav: 100 });
  });

  assert.ok(true);
});

test.run();
