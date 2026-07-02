package hu.unideb.inf.szakdolgozat

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

class Verification : AppCompatActivity() {

    private lateinit var verifyFingerprintButton: Button
    private lateinit var verifyFaceButton: Button
    private lateinit var verifyVoiceButton: Button
    private lateinit var verifyUnlockButton: Button
    private lateinit var backButton: Button

    private lateinit var fingerprintStatusText: TextView
    private lateinit var faceStatusText: TextView
    private lateinit var voiceStatusText: TextView

    private var fingerprintVerified = false
    private var faceVerified = false
    private var voiceVerified = false
    private lateinit var username: String
    private var isDoorOpen = false

    private val client = SSLTools.getUnsafeOkHttpClientBuilder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.verify_user)

        username = intent.getStringExtra("USERNAME") ?: ""

        verifyFingerprintButton = findViewById(R.id.verifyFingerprintButton)
        verifyFaceButton = findViewById(R.id.verifyFacePictureButton)
        verifyVoiceButton = findViewById(R.id.verifyVoiceButton)
        verifyUnlockButton = findViewById(R.id.verifyUnlockButton)
        backButton = findViewById(R.id.verifyBackButton)

        fingerprintStatusText = findViewById(R.id.fingerprintVerifiedTextView)
        faceStatusText = findViewById(R.id.faceVerifiedTextView)
        voiceStatusText = findViewById(R.id.voiceVerifiedTextView)

        verifyFingerprintButton.setOnClickListener {
            sendVerificationCommand("verify_fingerprint") { success ->
                runOnUiThread {
                    fingerprintVerified = success
                    fingerprintStatusText.text = if (success) "Ujjlenyomat: OK ✅" else "Nincs egyezés ❌"
                    fingerprintStatusText.setTextColor(if (success) android.graphics.Color.GREEN else android.graphics.Color.RED)
                    checkVerificationStatus()
                }
            }
        }

        verifyFaceButton.setOnClickListener {
            sendVerificationCommand("verify_facepicture") { success ->
                runOnUiThread {
                    faceVerified = success
                    faceStatusText.text = if (success) "Arcfelismerés: OK ✅" else "Nincs egyezés ❌"
                    faceStatusText.setTextColor(if (success) android.graphics.Color.GREEN else android.graphics.Color.RED)
                    checkVerificationStatus()
                }
            }
        }

        verifyVoiceButton.setOnClickListener {
            sendVerificationCommand("verify_voice") { success ->
                runOnUiThread {
                    voiceVerified = success
                    voiceStatusText.text = if (success) "Hangazonosítás: OK ✅" else "Nincs egyezés ❌"
                    voiceStatusText.setTextColor(if (success) android.graphics.Color.GREEN else android.graphics.Color.RED)
                    checkVerificationStatus()
                }
            }
        }

        verifyUnlockButton.setOnClickListener { toggleDoorState() }
        backButton.setOnClickListener { finish() }
        checkVerificationStatus()
    }

    private fun sendVerificationCommand(command: String, callback: (Boolean) -> Unit) {
        val url = "https://172.20.10.5:5000/command?cmd=$command&username=$username"
        val request = Request.Builder().url(url).build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread { Toast.makeText(this@Verification, "Hálózati hiba!", Toast.LENGTH_SHORT).show() }
                callback(false)
            }
            override fun onResponse(call: Call, response: Response) {
                val body = response.body?.string()
                if (response.isSuccessful && body != null) {
                    val json = JSONObject(body)
                    callback(json.optBoolean("match", false))
                } else { callback(false) }
            }
        })
    }

    private fun checkVerificationStatus() {
        verifyUnlockButton.isEnabled = fingerprintVerified && faceVerified && voiceVerified
        verifyUnlockButton.alpha = if (verifyUnlockButton.isEnabled) 1.0f else 0.5f

        if (verifyUnlockButton.isEnabled && !isDoorOpen) {
            verifyUnlockButton.text = "Zár kinyitása 🔓"
        }
    }

    private fun toggleDoorState() {
        val action = if (isDoorOpen) "lock" else "unlock"
        val url = "https://172.20.10.5:5000/command?cmd=$action&username=$username"
        val request = Request.Builder().url(url).build()

        // Hálózati kérés küldése a Pi-nek
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread { Toast.makeText(this@Verification, "Hálózati hiba a relé vezérlésekor!", Toast.LENGTH_SHORT).show() }
            }
            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    runOnUiThread {
                        if (action == "unlock") {
                            isDoorOpen = true
                            verifyUnlockButton.text = "Zár bezárása 🔒"
                            verifyUnlockButton.setBackgroundColor(android.graphics.Color.parseColor("#d9534f")) // Pirosas szín, hogy feltűnő legyen
                            Toast.makeText(this@Verification, "Zár kinyitva!", Toast.LENGTH_SHORT).show()
                        }
                        else {
                            isDoorOpen = false
                            verifyUnlockButton.text = "Zár kinyitása 🔓"
                            verifyUnlockButton.setBackgroundColor(android.graphics.Color.parseColor("#8d7a6b")) // Eredeti gomb szín
                            Toast.makeText(this@Verification, "Zár bezárva!", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
                else {
                    runOnUiThread { Toast.makeText(this@Verification, "Szerver hiba a parancs végrehajtásakor!", Toast.LENGTH_SHORT).show() }
                }
            }
        })
    }
}