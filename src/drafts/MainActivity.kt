package com.example.mysafapplication

import android.app.Activity
import android.content.ContentUris
import android.content.ContentValues
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.view.Menu
import android.view.MenuItem
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.google.android.material.floatingactionbutton.FloatingActionButton
import java.io.File
import java.io.FileOutputStream
import java.io.FileWriter
import java.util.*

/**
 * SDKバージョンを加味しつつ、 MediaStore でファイルを保存するサンプル
 *
 * * getExternalStorageDirectory が非推奨 になった件の対応
 * * MainActivity は Android Studio の自動生成のものを流用
 *
 * 仕様上の注意
 *
 * * Android の Files アプリから参照・削除できるので確実にファイルが残るわけではない
 * * アプリ固有のデータはアプリ固有のディレクトリ（ただしアンインストール時に消える）に入れた方が良いと書いてある
 *   のであまり行儀の良い使い方ではないかもしれない
 *
 * 実装上のポイント
 *
 * * コレクションに追加するときは DISPLAY_NAME に拡張子を含まないのにクエリするときは拡張子必要なのが罠
 * * マニフェストに ``android:requestLegacyExternalStorage="true"`` を追加して、targetSdkVersion 29 でビルドする
 *
 * メモ
 *
 * * Device File Explorer で ``/storage/emulated`` 以下が ``ls: /storage/emulated: Permission denied``
 *   のようなエラーメッセージが表示される場合、ADV Manager で端末リセット(Wipe Data) を行うと解決する場合がある。
 *   また、 ``/sdcard`` や ``/storage/self/primary`` 等では表示できる場合がある
 *
 * * 作成したファイル or ディレクトリが表示されない場合、親ディレクトリを右クリック > Synchronize で表示される場合がある
 * * shouldShowRequestPermissionRationale がどういう条件で値が変わるのかよくわからん
 */
class MainActivity : AppCompatActivity() {
    private val permission = android.Manifest.permission.WRITE_EXTERNAL_STORAGE
    private val activityRequestCode = 108

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setSupportActionBar(findViewById(R.id.toolbar))

        findViewById<FloatingActionButton>(R.id.fab).setOnClickListener {

            saveToPersistentStorage("${Date()}")
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        return when (item.itemId) {
            R.id.action_settings -> true
            else -> super.onOptionsItemSelected(item)
        }
    }

    override fun onRequestPermissionsResult(
            requestCode: Int,
            permissions: Array<out String>,
            grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == activityRequestCode) {
            if (grantResults.isEmpty() or (grantResults[0] == PackageManager.PERMISSION_DENIED)) {
                return
            }
            // ほんとは content をメンバ変数とかにおいとく
            saveFile("${Date()}")
        }
    }

    private fun saveToPersistentStorage(content: String) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) {
            // パーミッション不要で書き込み可能
            saveFile(content)
        } else if (Build.VERSION.SDK_INT in Build.VERSION_CODES.M .. Build.VERSION_CODES.P) {
            // SDK API 22 (Android 6.0 Marshmallow) 以降はパーミッションが必要
            saveFileLegacyExternalStorage(this, content)
        } else {
            // SDK API 29 以降
            saveFileByMediaStore(content)
        }
    }

    /**
     * 書き込み権限がある前提で外部ストレージにファイルを保存する
     */
    private fun saveFile(content :String) {
        val dataDir = Environment.getExternalStorageDirectory().path + "/MyApp/data"

        if (!File(dataDir).exists()) {
            File(dataDir).mkdirs()
        }

        FileWriter("$dataDir/info", false).use {
            it.write(content)
        }

        println(dataDir)
    }

    /**
     *   SDK API 22 ~ 28 のパーミッションを取得して外部ストレージにファイルを保存する
     */
    @RequiresApi(Build.VERSION_CODES.M)
    private fun saveFileLegacyExternalStorage(activity: Activity, content: String) {
        val context = activity as Context

        when {
            context.checkSelfPermission(permission) == PackageManager.PERMISSION_GRANTED -> {
                saveFile(content)
            }
            shouldShowRequestPermissionRationale(permission) -> {
                AlertDialog.Builder(context)
                    .setMessage(R.string.request_permission_rationale_message)
                    .setPositiveButton(R.string.ok) { _, _ ->
                        ActivityCompat.requestPermissions(
                                activity,
                                arrayOf(permission),
                                activityRequestCode,
                        )
                    }
                    .create()
                    .show()
            }
            else -> {
                ActivityCompat.requestPermissions(
                        this,
                        arrayOf(permission),
                        activityRequestCode,
                )
            }
        }
    }


    /**
     * MediaStore を利用してファイルを保存するための Uri を取得する
     *
     * ファイルが既に存在する場合はその Uri を返す（上書きされる）
     */
    private fun dataUri(): Uri? {

        val collection = MediaStore.Files.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
        val relativePath = "${Environment.DIRECTORY_DOCUMENTS}/MyApp/data/"

        // query params
        val projection = arrayOf(
                MediaStore.Files.FileColumns._ID,
                MediaStore.Files.FileColumns.DISPLAY_NAME
        )
        val selection = "${MediaStore.Files.FileColumns.RELATIVE_PATH} = ? AND ${MediaStore.Files.FileColumns.DISPLAY_NAME} = ?"
        val selectionArgs = arrayOf(relativePath, "info.txt")

        contentResolver.query(
                collection,
                projection,
                selection,
                selectionArgs,
                null
        )?.use { cursor ->

            return when (cursor.count) {
                0 -> {
                    val values = ContentValues().apply {
                        put(MediaStore.MediaColumns.DISPLAY_NAME, "info")
                        put(MediaStore.MediaColumns.MIME_TYPE, "text/plain")
                        put(MediaStore.MediaColumns.RELATIVE_PATH, relativePath)
                        // put(MediaStore.MediaColumns.IS_PENDING, 1)
                    }

                    contentResolver.insert(collection, values)
                }
                else -> {
                    cursor.moveToFirst()
                    val idx = cursor.getColumnIndex(MediaStore.Files.FileColumns._ID)

                    ContentUris.withAppendedId(collection, cursor.getLong(idx))
                }
            }
        }

        return null
    }

    /**
     * MediaStore を利用してファイルを保存する
     */
    private fun saveFileByMediaStore(content: String) {
        val uri = dataUri() ?: return
        println(uri)
        contentResolver.openFileDescriptor(uri, "w", null).use {
            FileOutputStream(it!!.fileDescriptor).use { outputStream ->
                outputStream.write(content.toByteArray())
            }
        }
    }
}
