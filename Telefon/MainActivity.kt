package hu.unideb.inf.szakdolgozat

import android.app.ProgressDialog
import android.content.Intent
import android.os.Bundle
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

class MainActivity : AppCompatActivity() {

    private val client = SSLTools.getUnsafeOkHttpClientBuilder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        val usernameET = findViewById<EditText>(R.id.mainUsernameInput)
        val passwordET = findViewById<EditText>(R.id.mainPasswordInput)
        val loginBtn = findViewById<Button>(R.id.mainLoginButton)
        val toRegBtn = findViewById<Button>(R.id.mainToRegisterButton)

        loginBtn.setOnClickListener {
            val user = usernameET.text.toString().trim()
            val pass = passwordET.text.toString().trim()

            if (user.isEmpty() || pass.isEmpty()) {
                Toast.makeText(this, "Kérlek töltsd ki az összes mezőt!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            authenticateUser(user, pass)
        }

        toRegBtn.setOnClickListener {
            startActivity(Intent(this, Register::class.java))
        }
    }

    private fun authenticateUser(username: String, password: String) {
        val progressDialog = ProgressDialog(this).apply {
            setMessage("Bejelentkezés...")
            setCancelable(false)
            show()
        }

        val json = JSONObject().apply {
            put("username", username)
            put("password", password)
        }

        val request = Request.Builder()
            .url("https://172.20.10.5:5000/login")
            .post(json.toString().toRequestBody("application/json".toMediaType()))
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    progressDialog.dismiss()
                    Toast.makeText(this@MainActivity, "Hiba: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
            override fun onResponse(call: Call, response: Response) {
                runOnUiThread {
                    progressDialog.dismiss()
                    if (response.isSuccessful) {
                        val intent = Intent(this@MainActivity, Verification::class.java)
                        intent.putExtra("USERNAME", username)
                        startActivity(intent)
                    } else {
                        Toast.makeText(this@MainActivity, "Hibás adatok!", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }
}