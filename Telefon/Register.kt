package hu.unideb.inf.szakdolgozat

import android.app.ProgressDialog
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

class Register : AppCompatActivity() {
    private lateinit var client: OkHttpClient
    private lateinit var usernameEdit: EditText
    private lateinit var passwordEdit: EditText

    private var fingerprintData: String? = null
    private var faceImagePath: String? = null
    private var voiceModelPath: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.register_profile)

        client = SSLTools.getUnsafeOkHttpClientBuilder()
            .connectTimeout(20, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()

        usernameEdit = findViewById(R.id.registerUsernameTextText)
        passwordEdit = findViewById(R.id.registerPasswordTextTextPassword)

        findViewById<Button>(R.id.saveFingerprintButton).setOnClickListener { captureFingerprint() }
        findViewById<Button>(R.id.saveFacePictureButton).setOnClickListener { captureFaceImage() }
        findViewById<Button>(R.id.saveVoiceButton).setOnClickListener { captureVoice() }

        findViewById<Button>(R.id.registerButton).setOnClickListener { registerUser() }
        findViewById<Button>(R.id.registerBackButton).setOnClickListener { finish() }
    }

    private fun captureFingerprint() {
        val request = Request.Builder()
            .url("https://172.20.10.5:5000/command?cmd=capture_fingerprint")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread { Toast.makeText(this@Register, "Hiba: ${e.message}", Toast.LENGTH_SHORT).show() }
            }
            override fun onResponse(call: Call, response: Response) {
                val body = response.body?.string()
                runOnUiThread {
                    if (response.isSuccessful && body != null) {
                        fingerprintData = body
                        Toast.makeText(this@Register, "Ujjlenyomat rögzítve! ✅", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }

    private fun captureFaceImage() {
        val request = Request.Builder()
            .url("https://172.20.10.5:5000/command?cmd=capture_face")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread { Toast.makeText(this@Register, "Hiba: ${e.message}", Toast.LENGTH_SHORT).show() }
            }
            override fun onResponse(call: Call, response: Response) {
                val body = response.body?.string()
                runOnUiThread {
                    if (response.isSuccessful && body != null) {
                        faceImagePath = body
                        Toast.makeText(this@Register, "Arckép rögzítve! ✅", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }

    private fun captureVoice() {
        val user = usernameEdit.text.toString().trim()
        if (user.isEmpty()) {
            Toast.makeText(this, "Adj meg egy nevet a hanghoz!", Toast.LENGTH_SHORT).show()
            return
        }

        val dialog = ProgressDialog(this).apply {
            setMessage("Hang rögzítése... Beszélj!")
            show()
        }

        val request = Request.Builder()
            .url("https://172.20.10.5:5000/command?cmd=capture_voice&username=$user")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    dialog.dismiss()
                    Toast.makeText(this@Register, "Hiba: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
            override fun onResponse(call: Call, response: Response) {
                val body = response.body?.string()
                runOnUiThread {
                    dialog.dismiss()
                    if (response.isSuccessful && body != null) {
                        val json = JSONObject(body)
                        // JAVÍTÁS: model_path helyett path
                        voiceModelPath = json.optString("path")
                        Toast.makeText(this@Register, "Hang rögzítve! ✅", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }

    private fun registerUser() {
        val username = usernameEdit.text.toString()
        val password = passwordEdit.text.toString()

        if (username.isEmpty() || password.isEmpty() || fingerprintData == null || faceImagePath == null || voiceModelPath == null) {
            Toast.makeText(this, "Minden adat (ujj, arc, hang) kötelező!", Toast.LENGTH_LONG).show()
            return
        }

        try {
            val json = JSONObject().apply {
                put("username", username)
                put("password", password)
                put("fingerprint", JSONObject(fingerprintData!!))
                put("face_image", JSONObject(faceImagePath!!))
                put("voice_model", JSONObject().apply {
                    put("path", voiceModelPath)
                })
            }

            val request = Request.Builder()
                .url("https://172.20.10.5:5000/register")
                .post(json.toString().toRequestBody("application/json".toMediaType()))
                .build()

            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    runOnUiThread { Toast.makeText(this@Register, "Szerver hiba!", Toast.LENGTH_SHORT).show() }
                }
                override fun onResponse(call: Call, response: Response) {
                    runOnUiThread {
                        if (response.code == 201) {
                            Toast.makeText(this@Register, "Sikeres regisztráció!", Toast.LENGTH_SHORT).show()
                            finish()
                        } else {
                            Toast.makeText(this@Register, "Hiba: ${response.code}. Ellenőrizd az adatokat!", Toast.LENGTH_LONG).show()
                        }
                    }
                }
            })
        } catch (e: Exception) {
            Log.e("RegisterError", "JSON hiba: ${e.message}")
        }
    }
}